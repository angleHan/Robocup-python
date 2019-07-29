#coding:utf-8
from naoqi import ALProxy
import math
import almath
import time

class Move():
    
    def __init__(self, motionProxy):
        self.motion_proxy = motionProxy
        #初始坐标
        self.init_position = [0,0,0]
        # 初始位置
        self.coordinate_init = [0.66,0,0]
        # 移动前记录位置
        self.previous_position=[0,0,0]
        # 移动过程中记录位置
        self.temp_position=[0,0,0]
        # 当前位置坐标
        self.coordinate_update=[0,0,0]
        #设置是否可以运动
        self.MOVE_FLAG=True
        #判断是否摔倒
        #self.FALL_FLAG=fall_manager.FALL_FLAG
        #球门下方坐标
        self.goal_down=[0,0.68,0]
        #球门上方坐标
        self.goal_up=[0,2.34,0]


    #move为移动函数
    def move_toward(self,x_speed,y_speed,theta_speed):
        #self.motionProxy.moveToward(x_speed,y_speed,theta_speed,[["MaxStepX", 0.02],["MaxStepY",0.02],["MaxStepFrequency",0.5],["StepHeight",0.01]])
        self.motion_proxy.moveToward(x_speed,y_speed,theta_speed,[
            ["MaxStepX",0.06],
            ["MaxStepY",0.120],
            ["MaxStepFrequency",1],
            ["MaxStepTheta", 0.349],
            ["StepHeight",0.015],
            ["Frequency", 1]
        ])
        pass
    
    def stop_move(self):
        self.motion_proxy.moveToward(0.0,0.0,0.0)
        pass
    
    def move_init(self):
        self.motion_proxy.wakeUp()
        self.motion_proxy.moveInit()
        pass

    def Position_Init(self):
        self.init_position=self.get_position()

        return self.init_position
    
    '''
    def Update_WhileFall(self):
        if self.FALL_FLAG == True:
            
            在此处更新当前坐标值
            
            pass
        else:
            self.coordinate_update=self.calculate()
    '''

    #为获得坐标函数
    def get_position(self):
        position=almath.Pose2D(self.motion_proxy.getRobotPosition(True))
        return position


    #更新坐标函数
    def calculate(self):
        self.temp_position=self.get_position()
        robotMove=almath.pose2DInverse(self.init_position)*self.temp_position
        if robotMove.theta>0:
            x_update=self.coordinate_init[1]+robotMove.x
            y_update=self.coordinate_init[0]+robotMove.y
            theta_temp=self.temp_position.theta-self.init_position.theta
            self.coordinate_update=[y_update,x_update,theta_temp]
        else:
            x_update=self.coordinate_init[1]+robotMove.x
            y_update=self.coordinate_init[0]-robotMove.y
            theta_temp=self.temp_position.theta-self.init_position.theta
            self.coordinate_update=[y_update,x_update,theta_temp]

        return self.coordinate_update
    
    def MoveToTheta(self,y,x):
        #self.temp_position=self.get_position()
        #self.coordinate_update=self.calculate()
        # 当目标点在机器人右下方时
        if x-self.coordinate_update[1]<0 and y-self.coordinate_update[0]<0:
            while abs(self.temp_position.theta-self.init_position.theta)-math.pi/2-math.atan(abs((x-self.coordinate_update[1])/(y-self.coordinate_update[0]))) >0.01 and self.MOVE_FLAG==True:
                self.move_toward(0,0,-0.2)
                self.temp_position=self.get_position()
            else:
                self.move_toward(0,0,0)

        # 当目标点在机器人左下方时
        if x-self.coordinate_update[1]<0 and y-self.coordinate_update[0]>0:
            while abs(self.temp_position.theta-self.init_position.theta)-math.pi/2-math.atan(abs((-x+self.coordinate_update[1])/(y-self.coordinate_update[0]))) >0.01 and self.MOVE_FLAG==True:
                self.move_toward(0,0,0.2)
                self.temp_position=self.get_position()
            else:
                self.move_toward(0,0,0)

        # 当目标点在机器人右上方时
        if x-self.coordinate_update[1]>0 and y-self.coordinate_update[0]<0:
            while math.pi/2-abs(self.temp_position.theta-self.init_position.theta)-math.atan(abs((x-self.coordinate_update[1])/(-y+self.coordinate_update[0]))) >0.01 and self.MOVE_FLAG==True:
                self.move_toward(0,0,-0.2)
                self.temp_position=self.get_position()
            else:
                self.move_toward(0,0,0)

        #当目标点在机器人左上方时
        if x-self.coordinate_update[1]>0 and y-self.coordinate_update[0]>0:
            while math.pi/2-abs(self.temp_position.theta-self.init_position.theta)-math.atan(abs((x-self.coordinate_update[1])/(y-self.coordinate_update[0]))) >0.01 and self.MOVE_FLAG==True:
                self.move_toward(0,0,0.2)
                self.temp_position=self.get_position()
            else:
                self.move_toward(0,0,0)

            
    #直接调用该函数即可移动至给定位置
    def next_move(self,y,x):
        
        #self.Update_WhileFall()  #当前坐标值（全局坐标系）
        self.temp_position=self.get_position()
        self.coordinate_update=self.calculate()
        self.MoveToTheta(y,x)


        while (x-self.coordinate_update[1])<-0.01 and (y-self.coordinate_update[0])<-0.01 and self.MOVE_FLAG==True:
            self.move_toward(0.6,0,0)
            self.temp_position=self.get_position()
            self.coordinate_update=self.calculate()
        else:
            self.move_toward(0,0,0)

        while (x-self.coordinate_update[1])<-0.01 and (y-self.coordinate_update[0])>0.01 and self.MOVE_FLAG==True:
            self.move_toward(0.6,0,0)
            self.temp_position=self.get_position()
            self.coordinate_update=self.calculate()
        else:
            self.move_toward(0,0,0)

        while (x-self.coordinate_update[1])>0.01 and (y-self.coordinate_update[0])<-0.01 and self.MOVE_FLAG==True:
            self.move_toward(0.6,0,0)
            self.temp_position=self.get_position()
            self.coordinate_update=self.calculate()
        else:
            self.move_toward(0,0,0)

        while (x-self.coordinate_update[1])>0.01 and (y-self.coordinate_update[0])>0.01 and self.MOVE_FLAG==True:
            self.move_toward(0.6,0,0)
            self.temp_position=self.get_position()
            self.coordinate_update=self.calculate()
        else:
            self.move_toward(0,0,0)

    def Turn_Goal_Theta(self):
        self.coordinate_update=self.calculate()

        theta_now=self.temp_position.theta-self.init_position.theta
        theta_down=math.atan((self.goal_down[1]-self.coordinate_update[1])/(self.goal_down[0]-self.coordinate_update[0]))
        theta_up=math.atan((self.goal_up[1]-self.coordinate_update[1])/(self.goal_up[0]-self.coordinate_update[0]))

        print theta_down
        print theta_up
        print theta_now

        while theta_now+math.pi/2>0.2:
            self.move_toward(0,0,-0.3)
            self.temp_position=self.get_position()
            theta_now=self.temp_position.theta-self.init_position.theta
            print theta_now

        else:
            self.move_toward(0,0,0)
            print "1111"

        #theta_update=self.temp_position.theta-self.init_position.theta
        #print theta_update
        '''
        while not (-abs(theta_up) < theta_now < -abs(theta_down)):
            self.move_toward(0,0,-0.1)
            self.temp_position=self.get_position()
            theta_now=self.temp_position.theta-self.init_position.theta

            print theta_now
        else:
            self.move_toward(0,0,0)
        '''
        
    
    #如果惩罚传入的是True,则moveFlag=False
    def set_penalty(self,flag):
        self.MOVE_FLAG=not flag
        self.move_toward(0,0,0)
        pass

robotIP="192.168.1.106"
motionProxy=ALProxy("ALMotion",robotIP,9559)


test=Move(motionProxy)
test.motion_proxy.wakeUp()
test.Position_Init()

test.move_toward(0.8,0,0.2)
time.sleep(3)
test.move_toward(0,0,0)

test.next_move(1.55,1.5)

test.Turn_Goal_Theta()







