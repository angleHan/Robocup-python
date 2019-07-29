#!/usr/bin/python2.7 
# -*- coding: utf-8 -*-


from naoqi import ALProxy

#HeadPitch 头高低
#HeadYaw 头左右
def move_head_front(motion):
    motion.setAngles("HeadPitch", 0.366, 1)
    motion.setAngles("HeadYaw",0,1)


def move_head_left(motion):
    motion.setAngles("HeadPitch", 0.366, 1)
    motion.setAngles("HeadYaw",0.523,1)


def move_head_right(motion):
    motion.setAngles("HeadPitch", 0.366, 1)
    motion.setAngles("HeadYaw",-0.523,1)

def get_head_position(motion):
    return motion.getAngles("HeadYaw",True)