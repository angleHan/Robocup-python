#!/usr/bin/python2.7 
# -*- coding: utf-8 -*-  
from naoqi import ALProxy
import threading

class leds(threading.Thread):
    '''
    感谢石金桃童鞋的色彩起名....
    '''
    def __init__(self,led_proxy):
        #self.leds=ALProxy("ALLeds",ROBOTIP,9559)
        threading.Thread.__init__(self)
        self.leds=led_proxy
        pass
    
    def run(self):
        while True:
            pass
        pass
    
    #设置胸口颜色为绿色
    def set_chest_green(self):
        self.set_chest_off()
        self.leds.on("ChestLedsGreen")
        print("Green")
        pass
    
    #纯蓝
    def set_chest_blue(self):
        self.set_chest_off()
        self.leds.on("ChestLedsBlue")
        print("BLUE")

        pass
    
    #纯红
    def set_chest_red(self):
        self.set_chest_off()
        self.leds.on("ChestLedsRed")
        print("RED")

        pass
    
    #关闭
    def set_chest_off(self):
        self.leds.off("ChestLeds")
        print("BLACK")

        pass
    
    #海洋蓝
    def set_chest_seablue(self):
        self.set_chest_off()
        self.leds.on("ChestLedsBlue")
        self.leds.on("ChestLedsGreen")
        pass
    
    #黄色
    def set_chest_yellow(self):
        self.set_chest_off()
        self.leds.on("ChestLedsGreen")
        self.leds.on("ChestLedsRed")
        print("YELLOW")
        pass
    
    #紫色
    def set_chest_purple(self):
        self.set_chest_off()
        self.leds.on("ChestLedsBlue")
        self.leds.on("ChestLedsRed")
        print("PURPLE")
        pass
    
    def set_chest_white(self):
        self.set_chest_off()
        self.leds.on("ChestLedsBlue")
        self.leds.on("ChestLedsRed")
        self.leds.on("ChestLedsGreen")
        print("WHITE")
        pass
    
    def set_chest_led(self, previous_led_color, led_color):
        
        # 若两次队伍颜色不同，再进行LED颜色设置
        # 以防止闪烁
        if previous_led_color != led_color:
            
            # 修改机器人LED的颜色
            if led_color == 'BLUE' :
                # 在这里设置左脚LED为蓝色
                # setLED(leftFootRed, 0.f, 0.f, 1.f);
                self.set_chest_blue() #胸口蓝色
                #pass

            elif led_color == 'RED':
                # 在这里设置左脚LED为红色
                # setLED(leftFootRed, 1.f, 0.f, 0.f);
                self.set_chest_red() #胸口红色
                #pass
            elif led_color == 'YELLOW':
                # 在这里设置左脚LED为黄色
                # setLED(leftFootRed, 1.f, 1.f, 0.f);
                self.set_chest_yellow() #胸口黄色
                #pass
            elif led_color == 'WHITE':
                self.set_chest_white()
            elif led_color == 'GREEN':
                self.set_chest_green()
            else:
                # 在这里设置左脚LED为黑色，即关闭LED
                # setLED(leftFootRed, 0.f, 0.f, 0.f);
                self.set_chest_off() #胸口黑色
        pass

    


    