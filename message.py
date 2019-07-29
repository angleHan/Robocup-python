#!/usr/bin/python2.7 
# -*- coding: utf-8 -*-

'''

ZZU-DROID团队
模块功能：
    用于错误信息的显示处理等。

'''

def thread_error():
    print("无法创建线程，线程错误！")

def announce():
    f=open("about/zzu-droid.txt")
    print(f.read())
    f.close()
    pass