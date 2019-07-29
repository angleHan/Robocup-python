#!/usr/bin/python2.7 
# -*- coding: utf-8 -*-
import threading
import time
from postures.lyingback2sit import *
from postures.lyingbelly2sit import *
from postures.sit2ready import *


import stand_init
'''

ZZU-DROID团队
模块功能：
    用于摔倒后起身动作的完成。

'''

class fall_manager(threading.Thread):

    #全局变量-线程的每次运行都需要判断全局变量，如果是RUN，则正确运行，PAUSE则暂停等，如果有其他的状态则在下面新增即可。
    RUNNING_STATE_RUN=0
    RUNNING_STATE_STOP=1

    CURRENT_STATE=RUNNING_STATE_RUN
    #入口为实例化的ALMOTION

    FALL_FLAG=False

    inwait=False
    wait_time=0

    def __init__(self,motion_proxy,posture_proxy):
        threading.Thread.__init__(self)
        self.motion_proxy=motion_proxy
        self.posture_proxy=posture_proxy
        self.motion_proxy.setFallManagerEnabled(False) #关闭自带的摔倒检测，用于启动我们自己的摔倒检测
        
        pass
    
    def run(self):
        #线程启动的函数
        while True:
            if self.CURRENT_STATE==self.RUNNING_STATE_RUN:
                #这里写线程运行时的代码
                current_posture=self.get_robot_posture()
                # print("Posture:",current_posture)
                if current_posture=="Unknown" or current_posture=="SittingOnChair":
                    #未知或者坐在椅子上，即即将摔倒，这个时候放松所有关节到1%
                    #self.set_stiffness_whole_body(0.01) #设置全部关节放松
                    self.set_stiffness_head(0.01)
                    self.set_stiffness_arms(0.01)
                    if self.inwait==True:
                        #如果处于Unknown状态，持续计时
                        if time.time()-self.wait_time>2:
                            #已经等了2秒,如果这个时候还没有LyingBack的话，就LyingBelly了。
                            self.FALL_FLAG=True
                            self.lyingbelly_to_stand()
                            self.inwait=False
                            self.wait_time=0
                            pass
                    elif self.inwait==False:
                        self.wait_time=time.time()
                        self.inwait=True
                        pass
                    pass
                elif current_posture=="LyingBack":
                    self.inwait=False #重置等待进度
                    self.wait_time=0
                    self.FALL_FLAG=True
                    self.lyingback_to_stand()
                    pass
                elif current_posture=="LyingBelly":
                    self.inwait=False
                    self.FALL_FLAG=True
                    self.wait_time=0
                    self.lyingbelly_to_stand()
                    pass
                elif current_posture=="Standing":
                    self.FALL_FLAG=False
                
                pass
            elif self.CURRENT_STATE==self.RUNNING_STATE_STOP:
                while self.self.CURRENT_STATE==self.RUNNING_STATE_STOP:
                    pass
                break
        pass
    
    def change_state(self,state):
        self.CURRENT_STATE=state
        pass

    def __del__(self):
        #析构函数
        pass
    
    def get_robot_posture(self):
        current_posture = self.posture_proxy.getPostureFamily()
        return current_posture
    
    def lyingback_to_stand(self):
        #躺在地上，则需要从躺着起身
        self.set_stiffness_whole_body(1)
        time.sleep(1) #等待它躺好了
        #此处加起身动作
        do_lyingback2sit(self.motion_proxy)
        #动作完成后，准备standinit
        self.set_stiffness_arms(0.01)
        #standinit
        if not stand_init.stand_init(self.posture_proxy):
            #如果没有起身成功
            self.set_stiffness_whole_body(0.01)#再让关节全部放松，这个之后会趴着起来
        else:
            self.set_stiffness_arms(0.01)
        #起身结束
        time.sleep(1)
        pass
    
    def lyingbelly_to_stand(self):
        #趴在地上，则需要从趴着起身
        time.sleep(1) #等待它趴好了
        print("趴着！")
        self.set_stiffness_whole_body(1)
        #此处加起身动作
        do_lyingbelly2sit(self.motion_proxy)
        #动作完成后，准备standinit
        self.set_stiffness_arms(0.01)
        #standinit
        if not stand_init.stand_init(self.posture_proxy):
            #如果没有起身成功
            self.set_stiffness_whole_body(0.01)#再让关节全部放松，这个之后会趴着起来
        else:
            self.set_stiffness_arms(0.01)
        #起身结束
        time.sleep(1)
        pass

    def set_stiffness_whole_body(self,stiffness,duration=0.2):
        #设置全身关节刚度，一般用于摔倒前一瞬间和摔倒后准备起身
        #刚度stiffness从0%~100%，即0~1
        #默认sleep时间是duration=0.2s
        self.motion_proxy.post.stiffnessInterpolation("Head", stiffness, duration)
        self.motion_proxy.post.stiffnessInterpolation("LArm", stiffness, duration)
        self.motion_proxy.post.stiffnessInterpolation("RArm", stiffness, duration)
        self.motion_proxy.post.stiffnessInterpolation("LLeg", stiffness, duration)
        self.motion_proxy.post.stiffnessInterpolation("RLeg", stiffness, duration)
        time.sleep(duration)
        pass
    
    def set_stiffness_arms(self,stiffness=0.01,duration=0.2):
        #设置胳膊关节刚度，一般用于初始状态行走
        #默认刚度stiffness=0.01
        self.motion_proxy.post.stiffnessInterpolation("LArm", stiffness, duration)
        self.motion_proxy.post.stiffnessInterpolation("RArm", stiffness, duration)
        time.sleep(duration)
        pass
    
    def set_stiffness_head(self,stiffness=0.01,duration=0.2):
        self.motion_proxy.post.stiffnessInterpolation("Head", stiffness, duration)
        time.sleep(duration)
        pass
    
    def set_stiffness_legs(self,stiffness=0.01,duration=0.2):
        #设置腿部关节刚度，一般用于摔倒起身后
        #默认刚度stiffness=0.01
        self.motion_proxy.post.stiffnessInterpolation("LArm", stiffness, duration)
        self.motion_proxy.post.stiffnessInterpolation("RArm", stiffness, duration)
        time.sleep(duration)
        pass