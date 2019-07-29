#!/usr/bin/python2.7 
# -*- coding: utf-8 -*-  
import threading
import message
from naoqi import ALProxy
from motion.fall_manager import *
from motion.kick_ball import *
from motion.odo_map_rec import *
from motion.move_head import *
from system.leds import *


ROBOT_IP="192.168.123.8"
motion_proxy=ALProxy("ALMotion",ROBOT_IP,9559)
posture_proxy=ALProxy("ALRobotPosture",ROBOT_IP,9559)
led_proxy=ALProxy("ALLeds",ROBOT_IP,9559)





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



def main():
    while True:
        #print("running...")
        if True: #此处判断更改为Ready
            #此处
            led_controller.set_chest_blue() #胸口蓝色
            pass
        elif False: #此处判断更改为Set
            led_controller.set_chest_yellow() #胸口黄色
            pass
        elif False: #此处判断更改为Playing
            led_controller.set_chest_green() #胸口绿色
            pass
        elif False: #此处判断更改为finished
            led_controller.set_chest_off() #胸口关闭
            pass
        elif False: #此处判断更改为Initial
            led_controller.set_chest_off() #胸口关闭
            pass
        elif False: #此处判断更改为Penalized
            led_controller.set_chest_red() #胸口红色
            pass
        pass
    pass

def do_ready():
    #此处写ready时应该做的事情
    pass

def do_set():
    #此处写set时应该做的事情
    pass

def do_playing():
    #此处写playing时应该做的事情
    pass

def do_finished():
    #此处写结束时应该做的事情
    pass

def do_initial():
    #此处写初始化时应该做的事情
    pass

def do_penalized():
    #此处写被惩罚时应该做的事情
    pass


#结束所有进程
def stop_all_threads():
    for t in threads:
        t.change_state(1)
        t.join()    


if __name__=="__main__":
    message.announce()
    #让进程运行
    
    fall_manager.change_state(fall_manager.RUNNING_STATE_RUN)
    motion_proxy.wakeUp()
    posture_proxy.goToPosture("StandInit", 1.2)
    fall_manager.set_stiffness_arms(0.01)

    main()
    stop_all_threads()
    print("程序执行结束")