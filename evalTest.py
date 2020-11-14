
import re


def pinDef2evalPattern(pinDefMod, ep, logicValue):
	pinDefMod = re.sub(r'!(\d+)', r'not(\1)', pinDefMod)
	pinDefMod = re.sub(r'(\d+)', r'%\1%', pinDefMod)
	pinDefMod = re.sub(r'[%]+', r'%', pinDefMod)
	pinDefMod = re.sub('!', 'not', pinDefMod)
	pinDefMod = re.sub('not(True)', 'False', pinDefMod) # optimizers
	pinDefMod = re.sub('not(False)', 'True', pinDefMod)
	pinDefMod = re.sub('%' + str(ep) + '%', logicValue, pinDefMod)
#	print(" pd2ep " + pinDefMod)   
	return pinDefMod

pinDef = "(!(!1)&(!15))|(2&((!1)&(!15)))"  # M3 74365

bitPatternList = ['00000000', '10000000', '01000000', '11000000', '00000001', '10000001', '01000001', '11000001'] 


exercisePinList = [1, 2, 4, 6, 10, 12, 14, 15]

for bitPattern in bitPatternList:
	pinDefMod = pinDef
	epIndex = 0
	for ep in exercisePinList:
		if bitPattern[epIndex] == '0':
			logicValue = 'False'
		else:
			logicValue = 'True'    
		pinDefMod = pinDef2evalPattern(pinDefMod, ep, logicValue)
		epIndex += 1
#		print("ep: " + bitPattern + "  " + logicValue + "  " + pinDefMod)
	print(bitPattern + "  " + pinDef + "  " + " = " + str(eval(pinDefMod)))
