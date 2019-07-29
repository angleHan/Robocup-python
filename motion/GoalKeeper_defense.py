#coding:utf-8

#下蹲扑球动作
def GoalKeeper_defense(motion):

	name = list()
	time = list()
	key = list()

	name.append("HeadPitch")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([-0.032256, 0.00762796, -0.0138481, -0.0890141, -0.092082])

	name.append("HeadYaw")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([-0.0107799, -0.0107799, -0.0291878, -0.016916, -0.0337899])

	name.append("LAnklePitch")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([-0.349794, -0.912772, -0.955723, -0.352862, 0.922581])

	name.append("LAnkleRoll")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([0.00924586, 0.0245859, -0.138018, -0.131882, 0.00464392])

	name.append("LElbowRoll")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([-0.121144, -0.113474, -0.170232, -0.0444441, -0.68719])

	name.append("LElbowYaw")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([-0.363599, 1.01393, 1.05382, 1.03081, 1.06149])

	name.append("LHand")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([0.2712, 0.274, 0.2632, 0.2632, 0.2716])

	name.append("LHipPitch")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([-0.449421, -0.875873, -0.696393, -1.53589, -1.52322])

	name.append("LHipRoll")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([0.00924586, 0.0153821, 0.595234, 0.638187, 0.0614019])

	name.append("LHipYawPitch")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([-0.00916195, -0.110406, -0.091998, -0.0981341, -1.10597])

	name.append("LKneePitch")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([0.700996, 1.63213, 1.61833, 1.6306, 0.938765])

	name.append("LShoulderPitch")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([1.48947, 0.770025, 0.802241, 0.641169, 0.555266])

	name.append("LShoulderRoll")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([0.191709, -0.00771189, -0.182588, -0.253151, -0.138102])

	name.append("LWristYaw")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([-1.13674, -1.20577, -1.26559, -1.27019, -1.29474])

	name.append("RAnklePitch")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([-0.354312, -0.819114, -0.713267, -0.378855, 0.9227])

	name.append("RAnkleRoll")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([0.00157595, 0.00310993, 0.372474, 0.150374, 0])

	name.append("RElbowRoll")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([0.14117, 0.145772, 0.15651, 0.124296, 0.665798])

	name.append("RElbowYaw")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([0.624296, -0.711819, -1.4328, -1.41286, -1.41899])

	name.append("RHand")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([0.2712, 0.2844, 0.2692, 0.2692, 0.2888])

	name.append("RHipPitch")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([-0.457173, -0.898967, -0.938849, -1.53404, -1.53097])

	name.append("RHipRoll")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([-0.00762796, 0.073674, -0.619695, -0.624296, -0.15796])

	name.append("RHipYawPitch")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([-0.00916195, -0.110406, -0.091998, -0.0981341, -1.10597])

	name.append("RKneePitch")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([0.705682, 1.62148, 1.59847, 1.59847, 0.840674])

	name.append("RShoulderPitch")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([1.4374, 0.745566, 0.783916, 0.650458, 0.549213])

	name.append("RShoulderRoll")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([-0.190258, 0.056716, 0.208583, 0.299088, 0.228525])

	name.append("RWristYaw")
	time.append([0.0333333, 0.5, 1.33333, 2.33333, 2.66667])
	key.append([0.83292, 1.12131, 1.21795, 1.1796, 1.0124])

	try:
	 	motion.angleInterpolation(name, time, key)
	except BaseException, err:
	  	print err



  	time.sleep(3.0)
'''
待下蹲扑球动作完成并稳定后 用手将球传出
'''

	names = list()
	times = list()
	keys = list()

	names.append("HeadPitch")
	times.append([0.04, 0.4, 1.2])
	keys.append([-0.092082, -0.101286, -0.092082])

	names.append("HeadYaw")
	times.append([0.04, 0.4, 1.2])
	keys.append([-0.0337899, -0.023052, -0.0337899])

	names.append("LAnklePitch")
	times.append([0.04, 0.4, 1.2])
	keys.append([0.922581, 0.922581, 0.922581])

	names.append("LAnkleRoll")
	times.append([0.04, 0.4, 1.2])
	keys.append([0.00464392, -8.26717e-05, 0.00464392])

	names.append("LElbowRoll")
	times.append([0.04, 0.4, 1.2])
	keys.append([-0.68719, -0.052114, -0.68719])

	names.append("LElbowYaw")
	times.append([0.04, 0.4, 1.2])
	keys.append([1.06149, 1.13972, 1.06149])

	names.append("LHand")
	times.append([0.04, 0.4, 1.2])
	keys.append([0.2716, 0.2716, 0.2716])

	names.append("LHipPitch")
	times.append([0.04, 0.4, 1.2])
	keys.append([-1.52322, -1.53589, -1.52322])

	names.append("LHipRoll")
	times.append([0.04, 0.4, 1.2])
	keys.append([0.0614019, 0.154976, 0.0614019])

	names.append("LHipYawPitch")
	times.append([0.04, 0.4, 1.2])
	keys.append([-1.10597, -1.01547, -1.10597])

	names.append("LKneePitch")
	times.append([0.04, 0.4, 1.2])
	keys.append([0.938765, 0.941834, 0.938765])

	names.append("LShoulderPitch")
	times.append([0.04, 0.4, 1.2])
	keys.append([0.555266, -1.0631, 0.555266])

	names.append("LShoulderRoll")
	times.append([0.04, 0.4, 1.2])
	keys.append([-0.138102, 0.796104, -0.138102])

	names.append("LWristYaw")
	times.append([0.04, 0.4, 1.2])
	keys.append([-1.29474, -1.33769, -1.29474])

	names.append("RAnklePitch")
	times.append([0.04, 0.4, 1.2])
	keys.append([0.9227, 0.9227, 0.9227])

	names.append("RAnkleRoll")
	times.append([0.04, 0.4, 1.2])
	keys.append([0, 0, 0])

	names.append("RElbowRoll")
	times.append([0.04, 0.4, 1.2])
	keys.append([0.665798, 0.07214, 0.665798])

	names.append("RElbowYaw")
	times.append([0.04, 0.4, 1.2])
	keys.append([-1.41899, -0.573758, -1.41899])

	names.append("RHand")
	times.append([0.04, 0.4, 1.2])
	keys.append([0.2888, 0.2888, 0.2888])

	names.append("RHipPitch")
	times.append([0.04, 0.4, 1.2])
	keys.append([-1.53097, -1.53404, -1.53097])

	names.append("RHipRoll")
	times.append([0.04, 0.4, 1.2])
	keys.append([-0.15796, -0.145688, -0.15796])

	names.append("RHipYawPitch")
	times.append([0.04, 0.4, 1.2])
	keys.append([-1.10597, -1.01547, -1.10597])

	names.append("RKneePitch")
	times.append([0.04, 0.4, 1.2])
	keys.append([0.840674, 0.900499, 0.840674])

	names.append("RShoulderPitch")
	times.append([0.04, 0.4, 1.2])
	keys.append([0.549213, -0.653443, 0.549213])

	names.append("RShoulderRoll")
	times.append([0.04, 0.4, 1.2])
	keys.append([0.228525, -0.569155, 0.228525])

	names.append("RWristYaw")
	times.append([0.04, 0.4, 1.2])
	keys.append([1.0124, 1.37135, 1.0124])

	try:
	  	motion.angleInterpolationBezier(names, times, keys7)
	except BaseException, err:
	  	print err


	time.sleep(3.0)


