#!/usr/bin/python2.7 
# -*- coding: utf-8 -*-

import threading
import socket

from __future__ import unicode_literals, print_function

import message
from naoqi import ALProxy
from motion.fall_manager import *
from motion.kick_ball import *
from motion.odo_map_rec import *
from motion.move_head import *
from system.leds import *


"""
This module shows how the GameController Communication protocol can be used
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
from gamestate import GameState, ReturnData, GAME_CONTROLLER_RESPONSE_VERSION, TeamInfo, RobotInfo
import struct

from game_constant import *


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


#非线程实例化
led_controller=leds(led_proxy)



#启动线程
threads=[] #线程列表

fall_manager=fall_manager(motion_proxy,posture_proxy) 
try:
    fall_manager.start()
    threads.append(fall_manager)
except:
    message.thread_error()




class GameStateReceiver(object):

    """ This class puts up a simple UDP Server which receives the
    *addr* parameter to listen to the packages from the game_controller.

    If it receives a package it will be interpreted with the construct data
    structure and the :func:`on_new_gamestate` will be called with the content.

    After this we send a package back to the GC """

    #全局变量-线程的每次运行都需要判断全局变量，如果是RUN，则正确运行，PAUSE则暂停等，如果有其他的状态则在下面新增即可。
    RUNNING_STATE_RUN=0
    RUNNING_STATE_STOP=1

    CURRENT_STATE=RUNNING_STATE_STOP


    def __init__(self, team_number, player_number, addr=(DEFAULT_LISTENING_HOST, GAME_CONTROLLER_LISTEN_PORT), answer_port=GAME_CONTROLLER_ANSWER_PORT):
                
        # Information that is used when sending the answer to the game controller
        self.team_number = team_number                    # 这个是指队伍号team number
        self.player_number = player_number                # 这个是球员号码player number
        self.man_penalize = False                  # 是否处于处罚状态
        self.previous_team_info = None             # 之前的队伍信息
        self.when_packet_was_received = None       # 记录接收到包的时间

        # The address listening on and the port for sending back the robots meta data
        self.gamecontroller_address = addr   # GameController's Address           
        self.answer_port = answer_port       # Answer Port

        # The state and time we received last form the GC
        self.GameState = None               # 这个用于记录GameState类所有的消息
        self.game_state = None              # 这个用于记录game_state的值
        self.previous_game_state = None

        self.game_phase = None            # 记录game phase
        self.previous_game_phase = None 

        self.kicking_team = None            # 记录正在踢球的队伍号
        self.previous_kicking_team = None

        self.team_color = None              # 记录队伍LED颜色
        self.previous_team_color = None

        self.time = None
        self.default_color = TeamColor.BLACK

        self.penalty = None                 # 记录当前惩罚状态
        self.previous_penalty = None

        self.chest_button_pressed = None    # 胸部按钮按压状态，按下去为true
        self.previous_chest_button_pressed = None

        self.left_foot_button_pressed = None    # 左脚按钮按压状态，按下去为true
        self.previous_left_foot_button_pressed = None

        self.right_foot_button_pressed = None    # 右脚按钮按压状态，按下去为true
        self.previous_right_foot_button_pressed = None

        self.when_chest_button_state_changed = None # 胸部按钮状态改变的时间
        self.when_left_foot_button_state_changed = None # 左脚按钮状态改变的时间
        self.when_right_foot_button_state_changed = None # 右脚按钮状态改变的时间

        self.when_packet_was_received = None # 消息包接收时间
        self.when_packet_was_sent = None     # 消息包发送时间

        # The socket and whether it is still running
        self.socket = None
        self.running = True

        self._open_socket()
    
    def _open_socket(self):
        """ 创建socket """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.gamecontroller_address)
        self.socket.settimeout(0.5)
        self.socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def receive_forever(self):
        """ 在循环中等待，直到通过设置'self.running = False'来结束 """
        while self.running:
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

            print (parsed_state)

            # Assign the new package after it parsed successful to the state
            self.previous_game_state = self.GameState
            # 更新previous_team_info
            self.previous_team_info = self.GameState.teams[ 0 if(self.GameState.teams[0].team_number == self.team_number) else 1]

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
            logger.warning("解析错误: 可能使用了旧协议!")
        except Exception as e:
            logger.exception(e)
            pass

    def answer_to_gamecontroller(self, peer):
        """ 向GameController发送生命信号(life sign) """
        return_message = 0 if self.man_penalize else 2

        data = Container(
            header=b"RGrt",                                     # 设置ReturnData消息头
            version=GAME_CONTROLLER_RESPONSE_VERSION,           # 设置该比赛消息结构版本号
            team_number=self.team_number,                       # 设置该球队号码
            player_number=self.player_number,                   # 设置该队员号码
            message=return_message                              # 设置要返回的消息
        )
        try:
            destination = peer[0], GAME_CONTROLLER_ANSWER_PORT
            self.socket.sendto(ReturnData.build(data), destination)
        except Exception as e:
            logger.log("Network Error: %s" % str(e))

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
                team_color = self.default_color

                # 球队颜色！=蓝色and红色and黄色,则置球队颜色=黑色
                if team_color != TeamColor.BLUE \
                    and team_color != TeamColor.RED \
                        and team_color != TeamColor.YELLOW :
                    
                    team_color = TeamColor.BLACK

                self.GameState.teams[0].team_number = self.team_number
                self.GameState.teams[0].team_color = self.team_color
                # 下面这步我也不知道他们想嘎哈
                # 原代码处注释"we don't know better"
                # 原代码：gameCtrlData.teams[1].team_color = team_color ^ 1;
                # lzw改的代码：self.GameState.teams[1].team_color = team_color ^ 1;


                # 这里疑似是在初始化，但我真的不懂这是想嘎哈
                # 这整个if（从队伍号和球员号那里开始的）判断我都搞不懂他们想嘎哈
                if not self.GameState.players_per_team:
                    self.GameState.players_per_team = self.player_number

                # 原代码这里又一个publish()

        # 从发送来的GameState消息包中获取到自己队伍的信息
        team_info = state.teams[0 if (state.teams[0].team_number == self.team_number) else 1]

        # 若球员号小于每队球员数量
        if self.player_number <= self.GameState.players_per_team :
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


    def handleLED(self, state):
        """ Is called with the new game state after receiving a package
            Needs to be implemented or set
            :param state: Game State
        """

        self.time = time.time()

        # 判断消息是否发给了该NAO
        # 团队人数>0 and ALMemory存储的球员编号不空 and 这个编号<=GameController包中的每队球员数目 and 团队人数==gameCtrlData.teams[0 or 1].teamNumber
        if self.team_number != 0 and self.player_number != 0 \
            and self.player_number <= GameStateInfo.PLAYERS_PER_TEAM \
                and (self.team_number == state.teams[0].team_number or self.player_number == state.teams[1].team_number) :
            
            # 从发送来的GameState消息包中获取到自己队伍的信息
            team_info = state.teams[0 if (state.teams[0].team_number == self.team_number) else 1]

            # 这个里面有个secondaryState，我实在看不出来它是啥          -- by lzw
            if state.game_state != self.previous_game_state or state.game_phase != self.previous_game_phase or state.kicking_team != self.previous_kicking_team or team_info.team_color != self.previous_team_color or team_info.players[self.player_number-1].penalty != self.previous_penalty :

                    # 修改机器人LED的颜色
                    if team_info.team_color == TeamColor.BLUE :
                        # 在这里设置左脚LED为蓝色
                        # setLED(leftFootRed, 0.f, 0.f, 1.f);
                        led_controller.set_chest_blue() #胸口蓝色
                        pass

                    elif team_info.team_color == TeamColor.RED:
                        # 在这里设置左脚LED为红色
                        # setLED(leftFootRed, 1.f, 0.f, 0.f);
                        led_controller.set_chest_red() #胸口蓝色
                        pass
                    elif team_info.team_color == TeamColor.YELLOW:
                        # 在这里设置左脚LED为黄色
                        # setLED(leftFootRed, 1.f, 1.f, 0.f);
                        led_controller.set_chest_yellow() #胸口蓝色
                        pass
                    else:
                        # 在这里设置左脚LED为黑色，即关闭LED
                        # setLED(leftFootRed, 0.f, 0.f, 0.f);
                        led_controller.set_chest_off() #胸口蓝色

            # 罚球阶段初始状态下由该队踢球
            if state.game_state == GameStateInfo.STATE_INITIAL \
                and state.game_phase == GamePhase.GAME_PHASE_PENALTYSHOOT \
                    and state.kicking_team == self.team_number :
                # 在这里设置右脚LED为红色
                # setLED(rightFootRed, 0.f, 1.f, 0.f);
                led_controller.set_chest_green() #胸口蓝色
                pass

            # 罚球阶段初始状态下由另一队踢球
            elif state.game_state == GameStateInfo.STATE_INITIAL \
                and state.game_phase == GamePhase.GAME_PHASE_PENALTYSHOOT \
                    and state.kicking_team != self.team_number :
                
                # setLED(rightFootRed, 1.f, 1.0f, 0.f);
                led_controller.set_chest_yellow() #胸口蓝色
                pass

            # 消息包未超时的情况下若队伍处于SET及之前状态且该队是踢球的
            elif (self.time-self.when_packet_was_received) < GAMECONTROLLER_TIMEOUT \
                and state.game_state <= GameStateInfo.STATE_SET \
                    and state.kicking_team == self.team_number:

                # setLED(rightFootRed, 1.f, 1.f, 1.f);
                led_controller.set_chest_white() #胸口蓝色
                pass
            
            else:
                # setLED(rightFootRed, 0.f, 0.f, 0.f);
                led_controller.set_chest_off() #胸口蓝色
                pass


            # 若该名球员处于惩罚状态
            if team_info.players[self.player_number-1].penalty != Penalty.PENALTY_NONE :
                # setLED(chestRed, 1.f, 0.f, 0.f)
                led_controller.set_chest_red() #胸口蓝色
                pass

            else:
                if state.game_state == GameStateInfo.STATE_READY:
                    # setLED(chestRed, 0.f, 0.f, 1.f);
                    led_controller.set_chest_blue() #胸口蓝色
                    pass
                elif state.game_state == GameStateInfo.STATE_SET:
                    # setLED(chestRed, 1.f, 1.0f, 0.f);
                    led_controller.set_chest_yellow() #胸口蓝色
                    pass
                elif state.game_state ==GameStateInfo.STATE_PLAYING:
                    # setLED(chestRed, 0.f, 1.f, 0.f);
                    led_controller.set_chest_green() #胸口蓝色
                    pass
                else:
                    # setLED(chestRed, 0.f, 0.f, 0.f);
                    led_controller.set_chest_off() #胸口蓝色
                    pass

            # ledRequest[4][0] = (int) now;
            # proxy->setAlias(ledRequest);

            self.previous_game_state = state.game_state
            self.previous_game_phase = state.game_phase
            self.previous_kicking_team = state.kicking_team
            self.previous_penalty = team_info.players[self.player_number-1].penalty

        if self.time - self.when_packet_was_received < GAMECONTROLLER_TIMEOUT \
            and self.time - self.when_packet_was_sent >= ALIVE_DELAY \
            and self.when_packet_was_sent == self.time:
            #and send(GAMECONTROLLER_RETURN_MSG_ALIVE):

            pass

        raise NotImplementedError()

    def get_last_state(self):
        return self.GameState, self.time

    def get_time_since_last_package(self):
        return time.time() - self.time

    def stop(self):
        self.running = False

    def set_manual_penalty(self, flag):
        self.man_penalize = flag

    def run(self):
        while True:
            if self.CURRENT_STATE==self.RUNNING_STATE_RUN:
                #这里写线程运行时的代码
                pass
            elif self.CURRENT_STATE==self.RUNNING_STATE_STOP:
                break
                #这里写线程停止时的代码
        pass
    
    def change_state(self,threading_state):
        self.CURRENT_STATE=threading_state
        pass
    
    def get_msg(self):
        #返回是否接收到消息，如果收到了，则返回True,消息内容，否则，回复False,""
        
        return False,""
    
    def __del__(self):
        #析构函数
        pass

    
    def do_ready(self):
        #此处写ready时应该做的事情
        pass

    def do_set(self):
        #此处写set时应该做的事情
        pass

    def do_playing(self):
        #此处写playing时应该做的事情
        pass

    def do_finished(self):
        #此处写结束时应该做的事情
        pass

    def do_initial(self):
        #此处写初始化时应该做的事情
        pass

    def do_penalized(self):
        #此处写被惩罚时应该做的事情
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
    #让进程运行
    
    fall_manager.change_state(fall_manager.RUNNING_STATE_RUN)
    motion_proxy.wakeUp()
    posture_proxy.goToPosture("StandInit", 1.2)
    fall_manager.set_stiffness_arms(0.01)

    #main()
    #stop_all_threads()
    print("程序执行结束")

    # 实例化GameStateReceiver类
    rec = GameStateReceiver(team_number=48, player_number=1)
    rec.receive_forever()
    