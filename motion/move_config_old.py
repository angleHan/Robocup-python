#!/usr/bin/python2.7  
# -*- coding: utf-8 -*-  
from naoqi import ALProxy
import almath
import time
from fall_manager import *

class move_config():

    def __init__(self,motion):
        self.motion_proxy=motion
        pass
    

    def move_to(self,x,y,theta):
        #请在此处用move_toward完成move_to的功能
        
        pass
    
    def move_toward(self,x,y,theta):
        # 
        self.motion_proxy.moveToward(x,y,theta,[
            ["MaxStepX",0.06],
            ["MaxStepY",0.120],
            ["MaxStepFrequency",1],
            ["MaxStepTheta", 0.349],
            ["StepHeight",0.015],
            ["Frequency", 1]
        ])
        pass
    
    def move(self,x,y,theta):

        pass
    
    def stop_move(self):
        self.motion_proxy.moveToward(0.0,0.0,0.0)
        pass
    
    def move_init(self):
        self.motion_proxy.wakeUp()
        self.motion_proxy.moveInit()
        pass
    

# ROBOT_IP="192.168.178.123"
# ROBOT_PORT = 9559
# motion_proxy=ALProxy("ALMotion",ROBOT_IP,ROBOT_PORT)
# posture_proxy=ALProxy("ALRobotPosture",ROBOT_IP,ROBOT_PORT)
# fm=fall_manager(motion_proxy,posture_proxy)
# mc=move_config(motion_proxy)

# mc.move_init()
# fm.set_stiffness_arms(0.01)
# fm.set_stiffness_head(0.01)

# print ("ready for moving")

# time.sleep(3)
# mc.move_toward(0,0,-1)
# time.sleep(8)
# mc.stop_move()


