#!/usr/bin/python2.7 
# -*- coding: utf-8 -*-  
import threading
import Queue

class memory(threading.Thread):

    #全局变量-线程的每次运行都需要判断全局变量，如果是RUN，则正确运行，PAUSE则暂停等，如果有其他的状态则在下面新增即可。
    RUNNING_STATE_RUN=0
    RUNNING_STATE_STOP=1

    CURRENT_STATE=RUNNING_STATE_STOP

    def __init__(self,memory_proxy):
        threading.Thread.__init__(self)
        self.memory_proxy=memory_proxy
        self.chest_button_msg_queue=Queue.Queue()
        pass
    

    def run(self):
        #线程启动的函数
        while True:
            if self.CURRENT_STATE==self.RUNNING_STATE_RUN:
                self.listen_chest_button() #监听胸部按键
                
                pass
            elif self.CURRENT_STATE==self.RUNNING_STATE_STOP:
                #这里写线程停止时的代码
                break
        pass
    
    def change_state(self,state):
        self.CURRENT_STATE=state
        pass

    def __del__(self):
        #析构函数
        pass
    
    def listen_chest_button(self):
        result=self.memory_proxy.getData()
        if result!=0:
            #说明被按下了
            self.chest_button_msg_queue.put(True)
        pass

    #获取胸部按压记录
    def get_data_chest_button(self):
        if not self.chest_button_msg_queue.empty():
            return self.chest_button_msg_queue.get()
        else:
            return False
        pass


    