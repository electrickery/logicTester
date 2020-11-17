
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

# 74365
#pinDef = "(!(!1)&(!15))|(2&((!1)&(!15)))"  # M3 74365
#bitPatternList = ['00000000', '10000000', '01000000', '11000000', '00000001', '10000001', '01000001', '11000001'] 
#exercisePinList = [1, 2, 4, 6, 10, 12, 14, 15] # 74365

# 74150
#"C:1,2,3,4,5,6,7,8,9,Q,11,G,13,14,15,16,17,18,19,20,21,22,23,V"
#   0 0 0 0 0 0 0 0 0   0    0  0  0  0  0  0  0  0  0  0  0
#pinDef = "9|(!9|(!(( 11)&( 13)&( 14)&( 15))&(!8)))|(!9|(!(( 11)&( 13)&( 14)&(!15))&(!7)))|(!9|(!(( 11)&( 13)&(!14)&( 15))&(!6)))|(!9|(!(( 11)&( 13)&(!14)&(!15))&(!5)))|(!9|(!(( 11)&(!13)&( 14)&( 15))&(!4)))|(!9|(!(( 11)&(!13)&( 14)&(!15))&(!3)))|(!9|(!(( 11)&(!13)&(!14)&( 15))&(!2)))|(!9|(!(( 11)&(!13)&(!14)&(!15))&(!1)))|(!9|(!((!11)&( 13)&( 14)&( 15))&(!23)))|(!9|(!((!11)&( 13)&( 14)&(!15))&(!22)))|(!9|(!((!11)&( 13)&(!14)&( 15))&(!21)))|(!9|(!((!11)&( 13)&(!14)&(!15))&(!20)))|(!9|(!((!11)&(!13)&( 14)&( 15))&(!19)))|(!9|(!((!11)&(!13)&( 14)&(!15))&(!18)))|(!9|(!((!11)&(!13)&(!14)&(!15))&(!16)))"
#pinDef = "9|(!9|(!((!11)&(!13)&(!14)&(!15))&(!8)))"
#bitPatternList = ['000000000000000000000', '000000001000000000000', '000000011000000000000', '000000101000000000000', '000000100000000000000', '000000010100000000000', '000000100100000000000', '000000100000100000000', '000000000000100000000', '111111110000111111111']
#exercisePinList = [1,2,3,4,5,6,7,8,9,11,13,14,15,16,17,18,19,20,21,22,23]
#bitHeader0       = 'iiiiiiiisddddiiiiiiii'
#bitHeader2       = '76543210SDCBA54321098'
#bitHeader1       = '         1111111111'
#bitHeader2       = '123456789134567890123'

# 74154
#                                           0 1 2 3 4 5 6 7 8 9 0 G 1 2 3 4 5 G1 G2  D  C  B  A
#{"type": "74154", "pins": 24, "config": "C:Q,Q,Q,Q,Q,Q,Q,Q,Q,Q,Q,G,Q,Q,Q,Q,Q,18,19,20,21,22,23,V", "M1": "", "M2": "", "M3": "", "M4": "", "M5": "", "M6": "", "M7": "", "M8": "", "M9": "", "M10": "", "M11": "", "M12": "", "M13": "", "M14": "", "M15": "" }
#pinDef = "(18|19|23|22|21|20)"
#exercisePinList = [18,19,20,21,22,23]
#bitPatternList = ['000011', '000001','000010', '000000', '000001']
#bitHeader0 = 'iiiiii'
#bitHeader1 = ''
#bitHeader2 = 'GGDCBA'

# 74157
#"config": "C:1,2,3,Q,5,6,Q,G,Q,10,11,Q,13,14,15,V", "M4": "15|((!1)&(2))|((1)&(3))", "M7": "15|((!1)&(5))|((1)&(5))", "M9": "15|((!1)&(11))|((1)&(12))", "M12": "15|((!1)&(14))|((1)&(13))"
#pinDef = "(!15)&(((!1)&2)|((1)&3))"
#exercisePinList = [1, 2, 3, 15]
#bitPatternList = ['0001', '0000', '0100', '0110', '0010', '1000', '1100', '1110', '1010']

#bitHeader0 = 's  s'
#bitHeader1 = 'eabt    y'

# 74151
#"config": "C:1,2,3,4,Q,Q,7,G,9,10,11,12,13,14,15,V"
pinDef = "(!7|(!((9)|(10)|(11))&4)|(!((9)|(10)|(!11))&3|(!((9)|(!10)|(11))&2)|(!((9)|(!10)|(!11)))&1|(!((!9)|(10)|(11)))&15|(!((!9)|(10)|(!11)))&14|(!((!9)|(!10)|(11)))&13|(!(!((!9)|(!10)|(!11)))&12)))"
exercisePinList = [1,2,3,4,7,9,10,11,12,13,14,15]
bitPatternList = ['000000000000', '000100000000', '001000010000', '000000010000', '010000100000', '000000100000', '100000110000', '000000110000']
bitHeader0 =      '      111111'
bitHeader1 =      '123479012345'
bitHeader2 =      "3210SCBA7654"
print(pinDef)
print(bitHeader0)
print(bitHeader1)
print(bitHeader2)

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
	result = eval(pinDefMod)
	level = 'L'
	if (result): level = 'H'
	print(bitPattern + " = " + str(result) + " " + level)
