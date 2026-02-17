#!/usr/bin/python3
#

import sys
import serial 
import time
import re
import json 

VERSION = "1.5"
    
ttySpeed = 115200
ttyPort = ""
icType = ""
libraryName = 'icLibrary.txt'

arduinoWait = 2
DEBUG = False

def log(message):
    if (DEBUG):
        print(message)

def writeSerial(port, message):
    port.write (str.encode(message + "\r\n"))
#    time.sleep(arduinoWait)

def readlnSerial(port):
    return str(ser.readline().decode("utf-8"))
    
def countMutations(confString):
    count = 0
    return [int(s) for s in str.split(confString) if s.isdigit()]

def loadDefinitions(libraryName):
    icData = ""
    icDataStr = ""
    with open(libraryName) as file: 
        for line in file:
            if (line.startswith("#") or not(line.strip())):
                continue
            icDataStr += line.strip().replace("\n", "").replace("\r", "")
#    print (icDataStr)
    icData = json.loads(icDataStr)
    vers = icData["version"]
    print (" >>>> icLibrary loaded version: " + vers)
    return icData
    
    
def getDefinition(lib, type):
    value = ""
    for dev in lib["devices"]:
#        print("The dev is: ", dev)
        devDef = dev["device"]
        devType = devDef["type"]
#        print("dev: " , devDef, "  type: ", devType)

        if (devType == type):
            value = str(devDef)
            print (" >>>> icData found for " + type)
            break

    return value
        
def findQueryPins(config):
    pinDefs = config[2:]
    queryPins = []
    pins = (pinDefs.split(','))
    pinCount = 1
    for p in pins:
#        print(" p: " + p)
        if (p == 'Q' or p == 'q' or p == '-'):
            queryPins.append(pinCount)
        pinCount += 1
    return queryPins
    
def findExercisePins(icConf):
    usedExercisePins = []
    normalisedConfig = replaceChars(icConf.get("config"), "Cc")
#    print("normalisedConfig: " + normalisedConfig)
    allExercisePins = re.findall(r'\d+', normalisedConfig)
    queryPins = findQueryPins(normalisedConfig)
    for p in queryPins:
        mutation = icConf.get('M' + str(p))
#        print("Mutation: " + 'M' + str(p) + " " + str(mutation))
        usedExercisePins += (re.findall(r'\d+', mutation))
    uniqueList = list(set(usedExercisePins))
    uniqueList = [int(x) for x in uniqueList]
    uniqueList.sort()
#    print("ExePins: " + str(uniqueList))
    usedExercisePins = uniqueList
    return usedExercisePins
    
# "C:1,2,C,4,Q,Q,G,Q,Q,10,C,12,13,V"
def replaceChars(configStr, replaceChars):
    pins = configStr[2:].split(',')
#    print(str(pins))
    pinIndex = 0
    for rc in list(replaceChars):
        for pin in pins:
            if pins[pinIndex] == rc:
                pins[pinIndex] = str(pinIndex+1)
            pinIndex += 1
        pinIndex = 0
    return configStr[:2] + ",".join(pins)

def int2bits(value, size):
#    print("int2bits: " + str(value) + ", " + str(size))
    bitPattern = ""
    bitIndex = size - 1
    while (bitIndex >= 0):
        bit = value & 1 << bitIndex
        if bit == 0:
            bitPattern += "0"
        else:
            bitPattern += "1"
        bitIndex -= 1
    return bitPattern

def template2query(pattern, template, exercisePinList):
    bitPattern = pattern[::-1]
#    print(str(pinPatternValue) + " " + bitPattern)
    bitIndex = 0
    query = template
    for bit in bitPattern:
#        print(bit + " " + query + " " + str(bitIndex), end='')
        query = re.sub('%' + str(exercisePinList[bitIndex]) + '%', bit, query, 1)
        bitIndex += 1
#        print()
    query = re.sub(r'%\d+%', '0', query)
    return query
    
def pinDef2evalPattern(pinDefMod, ep, logicValue):
	pinDefMod = re.sub(r'!(\d+)', r'not(\1)', pinDefMod)
	pinDefMod = re.sub(r'(\d+)', r'%\1%', pinDefMod)
	pinDefMod = re.sub(r'[%]+', r'%', pinDefMod)
	pinDefMod = re.sub('!', 'not', pinDefMod)
	pinDefMod = re.sub('not(True)', 'False', pinDefMod) # optimizers
	pinDefMod = re.sub('not(False)', 'True', pinDefMod)
	pinDefMod = re.sub('%' + str(ep) + '%', logicValue, pinDefMod)   
	return pinDefMod
	 
def query2result(query, pattern, queryPinList, icConf):
    bitPattern = pattern[::-1]
    normalisedQuery = replaceChars(query, 'Cc')
    expectedResultTemplate = re.sub('Q:', 'R:', normalisedQuery)
#    exercisePinList = re.findall(r'\d+', icConf.get("config"))
    exercisePinList = findExercisePins(icConf)
#    print(exercisePinList)
    
    for qp in queryPinList:
        pinDef = icConf.get('M' + str(qp))
        pinDefMod = pinDef
        epIndex = 0
        for ep in exercisePinList:
            if bitPattern[epIndex] == '0':
                 logicValue = 'False'
            else:
               logicValue = 'True'    

            pinDefMod = pinDef2evalPattern(pinDefMod, ep, logicValue)
#            print("ep/qp: "+ str(ep) + "/" + str(qp) + "  " + bitPattern[epIndex] + "  " + pinDef + "  " + pinDefMod)
            epIndex += 1

        if eval(pinDefMod):
            expectVal = 'H'
        else:
            expectVal = 'L'
        expectedResultTemplate = re.sub('-', expectVal, expectedResultTemplate, 1) # this assumes the query pins are 'in order'
        expectedResultTemplate = re.sub(r'%\d+%', "0", expectedResultTemplate)  # clean up unused exercise pins
    return expectedResultTemplate


# https://stackoverflow.com/questions/34327719/get-keys-from-json-in-python
def get_simple_keys(data):
    result = []
    for key in data.keys():
        if type(data[key]) != dict:
            result.append(key)
        else:
            result += get_simple_keys(data[key])
    return result
    
########################################################################


if len(sys.argv) <= 2:
    print("Usage " + sys.argv[0] + " <port> <device>")
    exit(1)
if len(sys.argv) > 1:
    ttyPort = sys.argv[1]
if len(sys.argv) > 2:
    icType = sys.argv[2]

resetMode = False
if (len(sys.argv) > 3 and sys.argv[3] == "-r"):
    resetMode = True
  
print ("I.C. tester controller version: " + VERSION)
print ("ttyPort: " + ttyPort + " at " + str(ttySpeed) + " Baud")
print ("IC: " + icType)


icLib = loadDefinitions(libraryName)
icConfStr = getDefinition(icLib, icType)

if (not(icConfStr)):
    print("ERROR: '" + icType + "' not found in library " + libraryName)
    exit()
else:
    print("device definition: '" + icConfStr + "'")

icConf = json.loads(icConfStr.replace('\'', '"'))

ser = serial.Serial(ttyPort, ttySpeed, timeout=2)  # open serial port
log("> " + readlnSerial(ser).strip())

if (resetMode):
    writeSerial(ser, 'R')
    exit()

# Send IC configuration to Arduino
configStr = icConf.get("config")
if (configStr):
        log("< " + configStr)
        writeSerial(ser, configStr)
        time.sleep(arduinoWait)
        log("> " + readlnSerial(ser).strip())


        # Exercise loop init
        exercisePinList = re.findall(r'[\dCc]+', configStr[2:])
        usedExercisePinList = findExercisePins(icConf)
        exercisePinCount = len(exercisePinList)
        usedExercisePinCount = len(usedExercisePinList)
        #print("Exercising " + str(exercisePinCount) + " " + str(exercisePinList))

        queryPinList = findQueryPins(configStr)
        queryPinCount = len(queryPinList)
        #print("Querying " + str(queryPinCount) + " " + str(queryPinList))

        pinInventory = exercisePinCount + queryPinCount + 2
        if pinInventory != icConf.get("pins"):
            print ("ERROR: mismatch between specified pins: " + str(icConf.get("pins")) + " and found pins: " + str(pinInventory))
            exit(1)

        configStrMod = re.sub(r'(\d+)', r'%\1%', replaceChars(configStr, 'Cc'))
        queryStrTempl = re.sub(r'[Qq]', '-', configStrMod)
        queryStrTempl = re.sub('C:', 'Q:', queryStrTempl, 1)
        #print("  c: " + configStrMod + "  q: " + queryStrTempl)

        exerciseCount = pow(2, usedExercisePinCount)
        #exerciseCount = 3

        #print(" used exe-pins: " + str(usedExercisePinCount) + " , exercise count: " + str(exerciseCount))

        pinPatternValue = 0
        errorCount = 0
        # start the loop
        for value in range (exerciseCount):
            pattern = int2bits(value, usedExercisePinCount)
            queryStr = template2query(pattern, queryStrTempl, usedExercisePinList)
            
            log("< " + queryStr)
            writeSerial(ser, (queryStr))

            actualResult   = readlnSerial(ser).strip()
            expectedResult = query2result(queryStr, pattern, queryPinList, icConf)

            log("> " + actualResult)

            if (actualResult == expectedResult):
                print (str(value + 1) + "/" + str(exerciseCount) + " " + actualResult + " Ok")
            else:
                errorCount += 1
                print("Err[" + str(errorCount) + "] '" + actualResult   + "' actual")
                print("Err[" + str(errorCount) + "] '" + expectedResult + "' expected")

        resetStr = "R"

        log("< " + resetStr)
        writeSerial(ser, resetStr)

        log("> " + readlnSerial(ser).strip())
        if errorCount:
            print("testing " + icType + "; " + str(errorCount) + " errors")
        else:
            print("testing " + icType + " OK.")

else:
        errorCount = 0
        print("Imperative format detected")
        keys = get_simple_keys(icConf)
        for rawCmd in keys:
            expectedResult = str(icConf.get(rawCmd))
            chkCmd = re.sub("\d+_", "", rawCmd)
            if not(chkCmd.startswith('C:') or chkCmd.startswith('Q:')):
                continue
            splitCmd  = re.split("_", rawCmd, 1)
            cmd = splitCmd[1]
            prefix = splitCmd[0]
            print(prefix + "_" + cmd + "   " + expectedResult)
            writeSerial(ser, cmd)
            actualResult   = readlnSerial(ser).strip()
            if expectedResult != actualResult:
                errorCount += 1
                print("Err[" + str(errorCount) + "] '" + actualResult   + "' actual")
                print("Err[" + str(errorCount) + "] '" + expectedResult + "' expected")
                
        if errorCount:
            print("testing " + icType + "; " + str(errorCount) + " errors")
        else:
            print("testing " + icType + " OK.")


# find the I.C. definition in the library
# send the config to the Arduino
# loop through
## generate a bit pattern for all the exercise pins
## fill the query-template with the exercise logic levels
## fill the expected result template with exercise logic levels
## calculate the values for the query pins (convert to Python logic expression and evaluate)
## fill the expected result template with query logic levels
## send the query to the Arduino
## retrieve the response from the Arduino
## compare the expected result with the actual result
# declare result and exit
