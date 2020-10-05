#!/usr/bin/python3
#

import sys
import serial 
import time
import re
import json 

VERSION = "1.1"
    
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

def getDefinition(libraryName, type):
    icData = ""
    with open(libraryName) as file: 
        for line in file:
            if (line.startswith("#version ")):
                version = line.replace("#version ", "").strip()
                continue
            if (line.startswith("#") or not(line.strip())):
                continue
    #        print (line.strip())
            pattern = "\"type\": \"" + type + "\""
    #        print (" pattern:" + pattern)
            if (line.startswith(pattern)):
                icData = json.loads("{" + line.strip() +"}")
                print (" >>>> icData defined")
    return icData
    
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
        query = re.sub('%' + exercisePinList[bitIndex] + '%', bit, query, 1)
        bitIndex += 1
#        print()
    return query
    
def query2result(query, pattern, queryPinList, icConf):
    bitPattern = pattern[::-1]
    expectedResultTemplate = re.sub('Q:', 'R:', query)
    exercisePinList = re.findall(r'\d+', icConf.get("config"))
    
    for qp in queryPinList:
        pinDef = icConf.get('M' + str(qp))
        pinDefMod = pinDef
        epIndex = 0
        for ep in exercisePinList:
#            print("pinDefMod: " + pinDefMod)
            pinDefMod = re.sub(r'!(\d+)', r'not(\1)', pinDefMod)
            pinDefMod = re.sub(r'(\d+)', r'%\1%', pinDefMod)
            pinDefMod = re.sub(r'[%]+', r'%', pinDefMod)
            pinDefMod = re.sub('!', 'not', pinDefMod)
            pinDefMod = re.sub('not(True)', 'False', pinDefMod) # optimizers
            pinDefMod = re.sub('not(False)', 'True', pinDefMod)
            if bitPattern[epIndex] == '0':
                logicValue = 'False'
            else:
                logicValue = 'True'    
            pinDefMod = re.sub('%' + ep + '%', logicValue, pinDefMod)
#            print("ep/qp: "+ ep + "/" + str(qp) + "  " + bitPattern[epIndex] + "  " + pinDef + "  " + pinDefMod)
            epIndex += 1
#        if eval(pinDefMod):
            
#        print(" pinDefMod: " + pinDefMod + "  ", end = '')
#        print(str(eval(pinDefMod)))
        if eval(pinDefMod):
            expectVal = '1'
        else:
            expectVal = '0'
        expectedResultTemplate = re.sub('-', expectVal, expectedResultTemplate, 1) # this assumes the query pins are 'in order'
        
    return expectedResultTemplate

#icConf = {"type": "7402", "pins": 14, "config": "C:Q,2,3,Q,5,6,G,8,9,Q,11,12,Q,V", "M1": "!(2|3)",}
#configStr = icConf["config"]

if len(sys.argv) > 1:
    ttyPort = sys.argv[1]
if len(sys.argv) > 2:
    icType = sys.argv[2]
  
print ("I.C. tester version: " + VERSION)
print ("ttyPort: " + ttyPort)
print ("IC: " + icType)

icConf = getDefinition(libraryName, icType)

if (not(icConf)):
    print("ERROR: '" + icType + "' not found in library " + libraryName)
    exit()

ser = serial.Serial(ttyPort, 9600, timeout=2)  # open serial port
log("> " + readlnSerial(ser).strip())

# Send IC configuration to Arduino
configStr = icConf.get("config")
log("< " + configStr)
writeSerial(ser, configStr)
log("> " + readlnSerial(ser).strip())


# Exercise loop init
exercisePinList = re.findall(r'\d+', configStr)
exercisePinCount = len(exercisePinList)
#print("Exercising " + str(exercisePinCount) + " " + str(exercisePinList))
queryPinList = findQueryPins(configStr)
queryPinCount = len(queryPinList)
#print("Querying " + str(queryPinCount) + " " + str(queryPinList))
pinInventory = exercisePinCount + queryPinCount + 2
if pinInventory != icConf.get("pins"):
    print ("ERROR: mismatch between specified pins: " + str(icConf.get("pins")) + " and found pins: " + str(pinInventory))
    exit(1)

configStrMod = re.sub(r'(\d+)', r'%\1%', configStr)
queryStrTempl = re.sub(r'[Qq]', '-', configStrMod)
queryStrTempl = re.sub('C:', 'Q:', queryStrTempl)
#resultStrTempl = re.sub('Q:', 'R:', queryStrTempl)
#print("  c: " + configStrMod + "  q: " + queryStrTempl)

exerciseCount = pow(2, exercisePinCount)
#exerciseCount = 3

#print(" exe-pins: " + str(exercisePinCount) + " , exercise count: " + str(exerciseCount))

pinPatternValue = 0
errorCount = 0
# start tht loop
for value in range (exerciseCount):
    pattern = int2bits(value, exercisePinCount)
    queryStr = template2query(pattern, queryStrTempl, exercisePinList)
    
    log("< " + queryStr)
    writeSerial(ser, (queryStr))

    actualResult   = readlnSerial(ser).strip()
    expectedResult = query2result(queryStr, pattern, queryPinList, icConf)

    log("> " + actualResult)

    if (actualResult == expectedResult):
        print (str(value + 1) + "/" + str(exerciseCount) + " " + actualResult + " Ok")
    else:
        print("Err[" + str(errorCount) + "] '" + actualResult   + "' actual")
        print("Err[" + str(errorCount) + "] '" + expectedResult + "' expected")
        errorCount += 1

resetStr = "R"

log("< " + resetStr)
writeSerial(ser, resetStr)

log("> " + readlnSerial(ser).strip())

if errorCount:
    print("testing " + icType + "; " + str(errorCount) + " errors")
else:
    print("testing " + icType + " OK.")

# generate a bit pattern for all the exercise pins
# fill the query-template with the exercise logic levels
# fill the expected result template with exercise logic levels
# calculate the values for the query pins
# fill the expected result template with query logic levels
# send the query to the Arduino
# retrieve the response from the Arduino
# compare the expected result with the actual result
