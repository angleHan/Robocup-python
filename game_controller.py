#!/usr/bin/python2.7 
# -*- coding: utf-8 -*-

import threading
import socket


import message
from naoqi import ALProxy
from motion.fall_manager import *
from motion.kick_ball import *
from motion.move_head import *
from system.leds import *
from motion.move_map import *
from vision.video_analyse import *



"""
This module shows how the GameController Comotionunication protocol can be used
in python and also allows to be changed such that every team using python to
interface with the GC can utilize the new protocol.

.. moduleauthor:: Nils Rokita <0rokita@informatik.uni-hamburg.de>
.. moduleauthor:: Robert Kessler <8kessler@informatik.uni-hamburg.de>

"""

import time
import logging

# Requires construct==2.8.20
"""
Maybe the higher version can run properly,
anyway the version above 2.9 can not and 2.5.3 either.
""" 
from construct import Container, ConstError
from network.gamestate import GameState, ReturnData, GAME_CONTROLLER_RESPONSE_VERSION, TeamInfo, RobotInfo
import struct

from network.game_constant import *


logger = logging.getLogger('game_controller')
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
logger.addHandler(console_handler)

DEFAULT_LISTENING_HOST = '0.0.0.0'
GAME_CONTROLLER_LISTEN_PORT = 3838
GAME_CONTROLLER_ANSWER_PORT = 3939
GAMECONTROLLER_TIMEOUT = 2000       # GameController超时时间
BUTTON_DELAY = 30                   # 按钮状态改变若小于30ms则忽略
ALIVE_DELAY = 1000                  # 每1000ms发送一个保活信号



ROBOT_IP="192.168.178.151"
ROBOT_PORT = 9559
motion_proxy=ALProxy("ALMotion",ROBOT_IP,ROBOT_PORT)
posture_proxy=ALProxy("ALRobotPosture",ROBOT_IP,ROBOT_PORT)
led_proxy=ALProxy("ALLeds",ROBOT_IP,ROBOT_PORT)
cam_proxy=ALProxy("ALVideoDevice",ROBOT_IP,ROBOT_PORT)

#非线程实例化




#启动线程
threads=[] #线程列表

#摔倒检测
fall_manager=fall_manager(motion_proxy,posture_proxy) 
try:
    fall_manager.start()
    threads.append(fall_manager)
except:
    message.thread_error()
#LED控制
led_controller=leds(led_proxy)
try:
    led_controller.start()
    threads.append(led_controller)
except:
    message.thread_error()
#视觉
vision=video_analyse(cam_proxy)




class GameStateReceiver(object):

    """ This class puts up a simple UDP Server which receives the
    *addr* parameter to listen to the packages from the game_controller.

    If it receives a package it will be interpreted with the construct data
    structure and the :func:`on_new_gamestate` will be called with the content.

    After this we send a package back to the GC """

    def __init__(self, team_number, player_number, addr=(DEFAULT_LISTENING_HOST, GAME_CONTROLLER_LISTEN_PORT), answer_port=GAME_CONTROLLER_ANSWER_PORT):
                
        # Information that is used when sending the answer to the game controller
        self.team_number = team_number                    # 这个是指队伍号team number
        self.player_number = player_number                # 这个是球员号码player number
        self.man_penalize = False                  # 是否处于处罚状态
        self.previous_team_info = None             # 之前的队伍信息
        self.when_packet_was_received = 0       # 记录接收到包的时间

        # The address listening on and the port for sending back the robots meta data
        self.gamecontroller_address = addr   # GameController's Address           
        self.answer_port = answer_port       # Answer Port

        # The state and time we received last form the GC
        self.GameState = None               # 这个用于记录GameState类所有的消息
        self.game_state = 0              # 这个用于记录game_state的值
        self.previous_game_state = 0

        self.game_phase = 0            # 记录game phase
        self.previous_game_phase = 0 

        self.kicking_team = 0            # 记录正在踢球的队伍号
        self.previous_kicking_team = 0

        self.team_color = 0             # 记录队伍颜色
        self.previous_team_color = 0

        self.led_color = None             # 记录LED颜色
        self.previous_led_color = None

        self.time = 0
        self.default_color = TeamColor.BLACK

        self.penalty = 0                 # 记录当前惩罚状态
        self.previous_penalty = 0

        self.chest_button_pressed = 0    # 胸部按钮按压状态，按下去为true
        self.previous_chest_button_pressed = 0

        self.left_foot_button_pressed = 0    # 左脚按钮按压状态，按下去为true
        self.previous_left_foot_button_pressed = 0

        self.right_foot_button_pressed = 0    # 右脚按钮按压状态，按下去为true
        self.previous_right_foot_button_pressed = 0

        self.when_chest_button_state_changed = 0 # 胸部按钮状态改变的时间
        self.when_left_foot_button_state_changed = 0 # 左脚按钮状态改变的时间
        self.when_right_foot_button_state_changed = 0 # 右脚按钮状态改变的时间

        self.when_packet_was_received = 0 # 消息包接收时间
        self.when_packet_was_sent = 0     # 消息包发送时间

        # The socket and whether it is still running
        self.socket = None
        self.running = True

        # 定位初始化
        self.motion = Move(motion_proxy,fall_manager) # 这是个函数
        self.init_postion = [0,0,0]            # 以机器人坐标系为参考的边界初始位置
        self.init_coordinate = [0,0,0]         # 以全局坐标系为参考的初始位置
        self.ready_position = [0,0,0]          # 以机器人坐标系为参考的Ready位置
        self.ready_coordinate = [0,0,0]        # 以全局坐标系为参考的Ready位置
        self.now_position = [0,0,0]            # 以机器人坐标系为参考的当前位置
        self.now_coordinate = [0,0,0]          # 以全局坐标系为参考的当前位置

        self._open_socket()

        self.last_time_find_ball=0              # 记录上一次找到球的时间
        self.head_move_count=0                  # 扭头计数

    
    def _open_socket(self):
        """ 创建socket """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.gamecontroller_address)
        self.socket.settimeout(0.5)
        self.socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


    def vision_run(self):
        img_bottom=vision.get_img_bottom()
        true_balls_bottom=vision.get_ball_position(img_bottom)
        if len(true_balls_bottom)>0:

            print("bottom!")
            #说明在下方已经找到了
            vision.BALL_FIND_FLAG=vision.BOTTOM_CAMERA
            vision.BALL_X,vision.BALL_Y,vision.BALL_R=true_balls_bottom[0][0],true_balls_bottom[0][1],true_balls_bottom[0][2]
            pass
        else:
            #说明在下方没找到，要搜索上面
            img_top=vision.get_img_top()
            true_balls_top=vision.get_ball_position(img_top)
            if len(true_balls_top)>0:
                #说明在上方的找到了
                print("top!")
                vision.BALL_FIND_FLAG=vision.TOP_CAMERA
                vision.BALL_X,vision.BALL_Y,vision.BALL_R=true_balls_top[0][0],true_balls_top[0][1],true_balls_top[0][2]
                pass
            else:
                #说明都没找到
                vision.BALL_FIND_FLAG=-1
                pass
        pass
    def receive_forever(self):
        """ 在循环中等待，直到通过设置'self.running = False'来结束 """
        while self.running:
            self.vision_run()


            try:
                self.receive_once()
            except IOError as e:
                logger.debug("Error when sending KeepAlive: " + str(e))


    def receive_once(self):
        """ 接收一个消息包并解释它。
            调用:func:`on_new_gamestate`
            给GameController发回消息 """
        try:

            data, peer = self.socket.recvfrom(GameState.sizeof())

            # Throws a ConstError if it doesn't work
            parsed_state = GameState.parse(data)   

            #print (parsed_state)

            if self.GameState != None :
                self.previous_team_info = self.GameState.teams[ 0 if(self.GameState.teams[0].team_number == self.team_number) else 1]
            else:
                self.previous_team_info = None 


            # 更新Game State
            self.GameState = parsed_state
            self.when_packet_was_received = time.time()

            # Call the handler for the package
            self.on_new_gamestate(self.GameState)

            # Answer the GameController
            self.answer_to_gamecontroller(peer)

        except AssertionError as ae:
            logger.error(ae.message)
        except socket.timeout:
            logger.warning("Socket timeout")
        except ConstError:
            logger.warning("解析错误: 可能使用了旧协议!".encode("UTF-8"))
        except Exception as e:
            logger.exception(e)
            pass

    def answer_to_gamecontroller(self, peer):
        """ 向GameController发送生命信号(life sign) """
        return_message = 0 if self.man_penalize else 2

        data = Container(
            header=b"RGrt",                                     # 设置ReturnData消息头
            version=3,           # 设置该比赛消息结构版本号
            team=self.team_number,                       # 设置该球队号码
            player=self.player_number,                   # 设置该队员号码
            message=return_message                              # 设置要返回的消息
        )

        #print ("peer:", peer)

        destination = peer[0], GAME_CONTROLLER_ANSWER_PORT

        self.socket.sendto(ReturnData.build(data), destination)

        # try:
        #     destination = peer[0], GAME_CONTROLLER_ANSWER_PORT
        #     print (destination)
        #     print (data)

        #     test_data = ReturnData.build(data)

        #     print (test_data)
        #     self.socket.sendto(ReturnData.build(data), destination)
        # except Exception as e:
        #     logger.log("Network Error: %s" % str(e))

    def on_new_gamestate(self, state):
        """ Is called with the new game state after receiving a package
            Needs to be implemented or set
            :param state: Game State
        """

        """ Handles the button interface.处理按钮界面
            Resets the internal state when a new team number was set.在设置新团队编号时重置内部状态
            Receives packets from the GameController.
            Initializes gameCtrlData when teamNumber and playerNumber are available.
        """

        #state = GameState.parse(state)
        # 同济给的代码是proxy.getTime()似乎是NAO上的当前时间
        # 现在用这个的话是本地的时间
        self.time = time.time()

        # 处理LED
        self.handleState(state)

        if self.team_number != 0:
            # 他们在这里进行了球员信息的初始化
            #memory->insertData("GameCtrl/teamNumber", 0);
            #init();
            pass


        # 这个条件判断对应同济 if(reveive()) 中的判断，
        # 因为他们的是在判断时才接收消息，
        # 而现在这个程序是在接收到消息之后才会调用本函数，
        # 故不在判断消息是否接收到了
        # 若收到了消息包
        if self.when_packet_was_received == None:
            self.previous_game_state = None              # 在第一次接收到消息包的时候强制LED更新
            self.when_packet_was_received = self.time
            # publish()

        # 若该球员已经有了队伍号和球员号
        if self.team_number and self.player_number:
            # 若self.GameState还没有用过，则将其初始化
            # gameCtrlData.teams[0 and 1].teamNumber!=球队人数
            if self.GameState.teams[0].team_number != self.team_number \
            and self.GameState.teams[1].team_number != self.team_number :

                # 我也不知道default team color是啥颜色      --- by lzw
                team_color = self.team_color

                # 球队颜色！=蓝色and红色and黄色,则置球队颜色=黑色
                if team_color != 'BLUE' \
                    and team_color != 'RED' \
                        and team_color != 'YELLOW' :
                    
                    team_color = 'BLACK'

                self.GameState.teams[0].team_number = self.team_number
                self.GameState.teams[0].team_color = self.team_color

                # 这里疑似是在初始化，但我真的不懂这是想嘎哈
                # 这整个if（从队伍号和球员号那里开始的）判断我都搞不懂他们想嘎哈
                if not self.GameState.players_per_team:
                    self.GameState.players_per_team = self.player_number

                # 原代码这里又一个publish()

        # 从发送来的GameState消息包中获取到自己队伍的信息
        team_info = state.teams[0 if (state.teams[0].team_number == self.team_number) else 1]

        # 若球员号小于每队球员数量
        if self.player_number <= self.GameState.players_per_team :
            #检测胸口按钮是否被按下


            pass
            
            # 这个应该是检测胸前按钮是否被按下的变量
            # bool chest_button_pressed = *buttons[chest] != 0.f;

            # 若chest_button_pressed与self.previous_chest_button_pressed不同（即被按下/已松开）并且
            # 状态变化时长>=30ms
            # if(chest_button_pressed != self.previous_chest_button_pressed and self.time - self.when_chest_button_button_state_changed >= BUTTON_DELAY :
                # 胸口按钮被按 and 最后一次发生状态变化的时刻不为0
                # 这一步是为了忽视第一次被按，比如起来时的
                # if(chest_button_pressed and self.when_chest_button_button_state_changed :
                    # player = self.team.players[self.player_number - 1];
                    # 确定发送包的时刻self.when_packet_was_sent=？？？以及gameCtrlData.state 的状态*/
                    # 若未被处罚*/
                    # if self.player.penalty == RobotInfo.penalty.PENALTY_NONE:
                        # self.player.penalty == RobotInfo.penalty.PENALTY_MANUAL
                        # 现在-接收包的时刻<GAMECONTROLLER_TIMEOUT(2000ms) and send(PENALISE)不空*/
                        # if(now - self.when_packet_was_received < GAMECONTROLLER_TIMEOUT and
                        # send(GAMECONTROLLER_RETURN_MSG_MAN_PENALISE):
                            # self.when_packet_was_sent = now;
            # else:
                # self.player.penalty = RobotInfo.penalty.PENALTY_NONE;
                # if now - self.when_packet_was_received < GAMECONTROLLER_TIMEOUT and
                # send(GAMECONTROLLER_RETURN_MSG_MAN_UNPENALISE))
                    # self.when_packet_was_sent = now;
                # else:
                    # gameCtrlData.state = STATE_PLAYING;

                # publish();

            # self.previous_chest_button_pressed = chest_button_pressed;
            # self.when_chest_button_button_state_changed = now;

        # # 若比赛处于初始阶段
        # if self.GameState.game_state == GameState.game_state.STATE_INITIAL:
        #     # left_foot_button_pressed用于记录左脚上的按钮是否被按下
        #     # bool left_foot_button_pressed = *buttons[leftFootLeft] != 0.f || *buttons[leftFootRight] != 0.f;

        #     # 若左脚按钮状态发生改变且改变时间 > 30ms(BUTTON_DELAY)
        #     if left_foot_button_pressed != self.previous_left_foot_button_pressed and self.time - self.when_left_foot_button_state_changed >= 30:
        #         # 若左脚按钮被按下
        #         if left_foot_button_pressed :
        #             # 循环更新机器人的LED颜色(从BLUE到BLACK)
        #             team_info.team_color = (team_info.team_color+1) % 3
        #             publish()
                
        #         self.previous_left_foot_button_pressed = left_foot_button_pressed
        #         self.when_left_foot_button_state_changed = self.time

        #     # right_foot_button_pressed用于记录右脚上的按钮是否被按下
        #     # bool right_foot_button_pressed = *buttons[rightFootLeft] != 0.f || *buttons[rightFootRight] != 0.f;

        #     # 若右脚按钮状态发生改变且改变时间 > 30ms(BUTTON_DELAY)
        #     if right_foot_button_pressed != self.previous_right_foot_button_pressed and self.time - self.when_right_foot_button_state_changed >= 30:
        #         # 若左脚按钮被按下
        #         if right_foot_button_pressed :
        #             # 循环更新机器人的LED颜色(从BLUE到BLACK)
        #             team_info.team_color = (team_info.team_color+1) % 3
        #             publish()
                
        #         self.previous_right_foot_button_pressed = right_foot_button_pressed
        #         self.when_right_foot_button_state_changed = self.time

        # else:
        #             # fprintf(stderr, "Player number %d too big. Maximum number is %d.\n", *playerNumber, gameCtrlData.playersPerTeam);

        # raise NotImplementedError()


    def handleState(self, state):
        """ Is called with the new game state after receiving a package
            Needs to be implemented or set
            :param state: Game State
        """

        self.time = time.time()


        # 判断消息是否发给了该NAO
        # 团队人数>0 and ALMemory存储的球员编号不空 and 这个编号<=GameController包中的每队球员数目 and 团队人数==gameCtrlData.teams[0 or 1].teamNumber
        if self.team_number != 0 and self.player_number != 0 \
            and self.player_number <= GameStateInfo.PLAYERS_PER_TEAM \
                and (self.team_number == state.teams[0].team_number or self.team_number == state.teams[1].team_number) :
            
            # 从发送来的GameState消息包中获取到自己队伍的信息
            team_info = state.teams[0 if (state.teams[0].team_number == self.team_number) else 1]

            # 若当前Game state、或Game phase、或踢球队伍、或队伍颜色、或惩罚状态，任意一个与之前不同就更新LED颜色
            if state.game_state != self.previous_game_state \
                or state.game_phase != self.previous_game_phase \
                    or state.kicking_team != self.previous_kicking_team \
                        or team_info.team_color != self.previous_led_color \
                            or team_info.players[self.player_number-1].penalty != self.previous_penalty :

                # 修改机器人LED的颜色
                # if self.previous_led_color == None:
                    
                #     if team_info.team_color == 'BLUE' :
                #         #胸口蓝色
                #         self.led_color = 'BLUE'
                #         led_controller.set_chest_led(self.previous_led_color, self.led_color)
                #         #pass

                #     elif team_info.team_color == 'RED':
                #         #胸口红色
                #         self.led_color = 'RED'
                #         led_controller.set_chest_led(self.previous_led_color, self.led_color)
                #         #pass
                #     elif team_info.team_color == 'YELLOW':
                #         #胸口黄色
                #         self.led_color = 'YELLOW'
                #         led_controller.set_chest_led(self.previous_led_color, self.led_color)
                #         #pass
                #     elif team_info.team_color == 'GREEN':
                #         self.led_color = 'GREEN'
                #         led_controller.set_chest_led(self.previous_led_color, self.led_color)
                #     else:
                #         #胸口黑色
                #         self.led_color = 'BLACK'
                #         led_controller.set_chest_led(self.previous_led_color, self.led_color)

                # 罚球阶段初始状态下由该队踢球
                if state.game_state == 'STATE_INITIAL' \
                    and state.game_phase == 'GAME_PHASE_PENALTYSHOOT' \
                        and state.kicking_team == self.team_number :
                    #胸口绿色
                    self.led_color = 'GREEN'
                    led_controller.set_chest_led(self.previous_led_color, self.led_color)
                    #pass

                # 罚球阶段初始状态下由另一队踢球
                elif state.game_state == 'STATE_INITIAL' \
                    and state.game_phase == 'GAME_PHASE_PENALTYSHOOT' \
                        and state.kicking_team != self.team_number :
                    
                    #胸口黄色
                    self.led_color = 'YELLOW'
                    led_controller.set_chest_led(self.previous_led_color, self.led_color)
                    #pass

                elif (self.time-self.when_packet_was_received) < GAMECONTROLLER_TIMEOUT \
                    and (state.game_state != 'STATE_PLAYING' or state.game_state != 'STATE_FINISHED') \
                        and state.kicking_team == self.team_number \
                            and state.game_phase == 'GAME_PHASE_PENALTYSHOOT':

                    #胸口白色
                    self.led_color = 'WHITE'
                    led_controller.set_chest_led(self.previous_led_color, self.led_color)
                    #pass
                
                elif state.game_phase == 'GAME_PHASE_PENALTYSHOOT':
                    #胸口黑色
                    self.led_color = 'BLACK'
                    led_controller.set_chest_led(self.previous_led_color, self.led_color)
                    #pass


                # 若该名球员处于惩罚状态
                if team_info.players[self.player_number-1].penalty != 'PENALTY_NONE' :
                    #胸口红色
                    self.do_penalized()                                                                 #do_penalized

                    #pass

                else:
                    # 通过游戏状态来决定策略
                    # 初始状态
                    if state.game_state == 'STATE_INITIAL':
                        self.do_initial()                                                               #do_initial

                    elif state.game_state == 'STATE_READY':
                        #胸口蓝色
                        self.do_ready()                                                                 #do_ready
                        
                        #pass
                    elif state.game_state == 'STATE_SET':
                        #胸口黄色
                        self.do_set()                                                                   #do_set

                    elif state.game_state == 'STATE_PLAYING':
                        #胸口绿色
                        self.do_playing()                                                               #do_playing

                    else:
                        #胸口黑色
                        self.do_else()

                self.previous_game_state = state.game_state
                self.previous_game_phase = state.game_phase
                self.previous_kicking_team = state.kicking_team
                self.previous_penalty = team_info.players[self.player_number-1].penalty
                self.previous_led_color = self.led_color


            if self.time - self.when_packet_was_received < GAMECONTROLLER_TIMEOUT \
                and self.time - self.when_packet_was_sent >= ALIVE_DELAY \
                and self.when_packet_was_sent == self.time:
                #and send(GAMECONTROLLER_RETURN_MSG_ALIVE):
                self.time = time.time()
                pass

        # raise NotImplementedError()

    def get_last_state(self):
        return self.GameState, self.time

    def get_time_since_last_package(self):
        return time.time() - self.time

    def stop(self):
        self.running = False

    def set_manual_penalty(self, flag):
        self.man_penalize = flag

 

    
    def do_ready(self):
        #此处写ready时应该做的事情
        self.motion.set_penalty(False)
        self.led_color = 'BLUE'
        led_controller.set_chest_led(self.previous_led_color, self.led_color)
        # 若之前不处于惩罚状态
        if self.previous_penalty == 'PENALTY_NONE':
            # 是从准备阶段过来的
            if self.previous_game_state == 'STATE_INITIAL':

                # 当由本队开球时
                if self.kicking_team == self.team_number:
                    # 在这里写走向目的地的代码
                    # 本队中的某一个机器人需走到开球点
                    # ...
                    pass
                # 当不由本队开球时
                elif self.kicking_team != self.team_number:
                    #所有球员都不得接触半场线

                    # 。。。

                    pass

                # 当走到正确的位置后，
                # 获取当前位置
                self.ready_postion = self.motion.get_position()
                pass 
            # 是从运行阶段过来的
            elif self.previous_game_state == 'STATE_PLAYING':
                
                # 走回原来READY的位置
                self.motion.next_move(self.ready_coordinate[0], self.ready_coordinate[1])
                pass
        # 之前处于惩罚状态                        
        else:
            # 走回原来READY的位置
            self.motion.next_move(self.ready_coordinate[0], self.ready_coordinate[1])
            pass

        pass

    def do_set(self):
        #此处写set时应该做的事情
        self.motion.set_penalty(False)
        self.led_color = 'YELLOW'
        led_controller.set_chest_led(self.previous_led_color, self.led_color)
        # 若之前不处于惩罚状态
        if self.previous_penalty == 'PENALTY_NONE':
            # 是从准备阶段过来的
            if self.previous_game_state == 'STATE_READY':
                pass        
        # 之前处于惩罚状态                        
        else:
            # 走回原来READY的位置
            self.motion.next_move(self.ready_coordinate[0], self.ready_coordinate[1])
            pass

        pass

    def do_playing(self):
        #此处写playing时应该做的事情
        self.motion.set_penalty(False)
        self.led_color = 'GREEN'
        led_controller.set_chest_led(self.previous_led_color, self.led_color)
        # 若之前不处于惩罚状态
        if self.previous_penalty == 'PENALTY_NONE':
            # 是从设置阶段过来的
            if self.previous_game_state == 'STATE_SET':

                # 在这里填写进攻决策
                if self.kicking_team == self.team_number:
                    if self.player_number == 1:
                        # 在这里填写守门员的行为
                        pass

                    elif self.player_number != 1 \
                        and self.player_number != 6:
                        # 在这里填写其他球员的行为

                        pass
                
                # 在这里填写防守决策
                elif self.kicking_team != self.team_number:
                    if self.player_number == 1:
                        # 在这里填写守门员的行为
                        pass

                    elif self.player_number != 1 \
                        and self.player_number != 6:
                        # 在这里填写其他球员的行为

                        pass
        # 之前处于惩罚状态                        
        else:
            # 走回原来READY的位置
            robot_penality_position=vision.get_penality_position() 
            if robot_penality_position==vision.PENALITY_COORDINATE_1:
                #于PENALITY_COORDINATE_1位置
                pass
            elif robot_penality_position==vision.PENALITY_COORDINATE_2:
                #于PENALITY_COORDINATE_2位置
                pass
            #self.motion.next_move(self.ready_coordinate[0], self.ready_coordinate[1])
            pass
        
        '''
        Playing视觉部分应该写在这
        '''
        ball_find_flag,x,y,r=vision.get_ball_position_pix()
        print(ball_find_flag,x,y,r)
        head_position=get_head_position(motion_proxy)[0]

        
        if ball_find_flag==vision.BOTTOM_CAMERA:
            #下面摄像头找到了球
            self.head_move_count=0
            if abs(head_position)<0.015:
                
                self.last_time_find_ball=time.time()
                if x>=150 and x<=490 and y>=320 and y<=400 and y>=-6*x+1380 and y>=6*x-2450:
                    print("In Case 1")
                    if x<=355-5:
                        self.motion.move_toward(0,0.4,0)
                    elif x>=355+5:
                        self.motion.move_toward(0,-0.4,0)
                    else:
                        #此处已经到达球前面
                        self.motion.move_toward(0,0,0)
                        time.sleep(2)
                        kick_ball(motion_proxy)
                        move_head_front(motion_proxy)
                elif y>=400:
                    self.motion.move_toward(-0.4,0,0)
                elif x>=150 and x<=490 and y<=330 and y>=-6*x+1380 and y>=6*x-2450:
                    print("In Case 2")
                    self.motion.move_toward(0.4,0,0)
                elif x>=0 and x<=230 and y<=-6*x+1380:
                    print("In Case 3")
                    self.motion.move_toward(0,0,0.3)
                elif x>=410 and x<=640 and y<=6*x-2450:
                    print("In Case 4")
                    self.motion.move_toward(0,0,-0.3)
                    pass
            else:
                motion_proxy.moveTo(0,0,head_position)
                move_head_front(motion_proxy)
                
        elif ball_find_flag==vision.TOP_CAMERA:
            #上面摄像头找到了球
            self.head_move_count=0
            if abs(head_position)<0.015:
                self.last_time_find_ball=time.time()
                if y>=-19/3*x+6190/3 and y>=19/3*x-7300/3:
                    print("In Case 5")
                    self.motion.move_toward(0.5,0,0) 
                elif y<=-19/3*x+6190/3:
                    self.motion.move_toward(0,0,0.174)
                    print("In Case 6")
                elif y<=19/3*x-7300/3:
                    print("In Case 7")
                    self.motion.move_toward(0,0,-0.174)
                pass
            else:
                motion_proxy.moveTo(0,0,head_position)
                move_head_front(motion_proxy)
        elif ball_find_flag==vision.NO_BALL:
            #找不到球
            if self.last_time_find_ball!=0:
                if time.time()-self.last_time_find_ball>2:
                    #如果4s内找不到球,则开始执行扭头程序，甚至转身
                    if self.head_move_count ==0:
                        move_head_front(motion_proxy)
                    elif self.head_move_count==1:
                        move_head_right(motion_proxy)
                    elif self.head_move_count==2:
                        move_head_left(motion_proxy)
                        self.head_move_count=0
                    self.head_move_count+=1

                    pass
                elif time.time()-self.last_time_find_ball>1:
                    #如果1s内找不到球，则停止运动
                    self.motion.move_toward(0,0,0)
            pass
        
                

        

        pass

    def do_else(self):
        #此处写结束时应该做的事情
        self.motion.set_penalty(False)
        self.led_color = 'BLACK'
        led_controller.set_chest_led(self.previous_led_color, self.led_color)
        pass

    def do_initial(self):
        self.motion.set_penalty(False)
        #此处写初始化时应该做的事情
        led_controller.set_chest_led(self.previous_led_color, self.led_color)
        # 获取当前位置
        self.init_postion = self.motion.get_position()
        pass

    def do_penalized(self):
        #此处写被惩罚时应该做的事情
        self.led_color = 'RED'
        led_controller.set_chest_led(self.previous_led_color, self.led_color)
        # 惩罚状态停止一切行动
        self.motion.set_penalty(True)
        
        pass

    #结束所有进程
    def stop_all_threads(self):
        for t in threads:
            t.change_state(1)
            t.join()    




class SampleGameStateReceiver(GameStateReceiver):
    
    def on_new_gamestate(self, state):
        print(state)
        print(state.secondary_state_info)


if __name__ == '__main__':
    message.announce()
    motion_proxy.wakeUp()
    posture_proxy.goToPosture("StandInit", 1.2)
    fall_manager.set_stiffness_arms(0.01)
    move_head_front(motion_proxy)

    #main()
    #stop_all_threads()
    print("程序执行结束")

    # 注意：
    # 守门员的号码必须是1
    # 备用机的号码必须是6
    # 实例化GameStateReceiver类
    rec = GameStateReceiver(team_number=48, player_number=1)
    rec.receive_forever()
    