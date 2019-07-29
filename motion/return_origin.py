import math
import almath
import argparse
from naoqi import ALProxy

def main():
	robotIP = "192.168.1.101"
	PORT = 9559
	motionProxy = ALProxy("ALMotion",robotIP,PORT)
	postureProxy = ALProxy("ALRobotPosture",robotIP,PORT)
	motionProxy.wakeUp()
	postureProxy.goToPosture("Stand",0.5)
	useSensorValues = True
	motionProxy.setMoveArmsEnabled(False, False)
	motionProxy.post.stiffnessInterpolation("LArm", 0, 0.2)
	motionProxy.post.stiffnessInterpolation("RArm", 0, 0.2)

	initRobotPosition = almath.Pose2D(motionProxy.getRobotPosition(True))
	print initRobotPosition
	x1 = 0.5
	y1 = 0.0
	theta1 = 0
	motionProxy.moveTo(x1,y1,theta1,
            [["MaxStepX",0.02],
             ["MaxStepY",0.16],
             ["MaxStepTheta",0.2],
             ["MaxStepFrequency",1],
             ["StepHeight",0.01],
             ["TorsoWx",0.0],
             ["TorsoWy",0.0]])
	theta2 = -almath.PI/2
	motionProxy.moveTo(0,0,theta2)

	x3 = 0.5
	y3 = 0.0
	motionProxy.moveTo(x3,y3,0,
            [["MaxStepX",0.02],
             ["MaxStepY",0.16],
             ["MaxStepTheta",0.2],
             ["MaxStepFrequency",1],
             ["StepHeight",0.01],
             ["TorsoWx",0.0],
             ["TorsoWy",0.0]])

	endRobotPosition = almath.Pose2D(motionProxy.getRobotPosition(True))
	print endRobotPosition
	motionProxy.moveTo(0,0,theta2)
	realRobotPosition = almath.Pose2D(motionProxy.getRobotPosition(True))
	print realRobotPosition

main()