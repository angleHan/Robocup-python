#!/usr/bin/python2.7 
# -*- coding: utf-8 -*-

'''

ZZU-DROID团队
模块功能：
    用于到standinit姿态

'''

def stand_init(posture_proxy):
    posture_proxy.setMaxTryNumber(1) #设置最大尝试次数
    result = posture_proxy.goToPosture("StandInit", 1.2)
    #如果执行成功，返回True，否则返回False
    return result