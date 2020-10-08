/*  IC-test 2 client(Arduino)-server(Python script)
 *   
 *   
 *   Assuming 74LS00 quad NAND
 *   Config command:
 *   C:1,2,Q,4,5,Q,G,Q,9,10,Q,12,13,V
 *   Query command:
 *   Q:0,0,-,0,0,-,G,-,0,0,-,0,0,V
 *   Response:
 *   R:0,0,1,0,0,1,G,1,0,0,1,0.0,V
 *   Q:0,0,-,0,0,-,G,-,0,0,-,0,1,V
 *   R:0,0,1,0,0,1,G,1,0,0,0,1,1,V
 *   ....
 *   Q:1,1,-,1,1,-,G,-,1,1,-,1,1,V
 *   R:1,1,0,1,1,0,G,0,1,1,0,1,1,V
 *  
 */

#include "pinMap.h"

#define DEBUG 0
#define BAUDRATE 115200

#define SERIALBUFSIZE         50
char serialBuffer[SERIALBUFSIZE];
byte setBufPointer = 0;

#define PIN_SEPARATOR   ','
#define EXERCISE_PIN    'E'
#define CLOCK_PIN       'C'
#define INV_CLOCK_PIN   'c'
#define QUERY_PIN       'Q'
#define GROUND_PIN      'G'
#define POWER_PIN       'V'
#define QUERY_CHAR      '-'

#define CLOCK_PULSE     1L

byte pinType[MAX_PINCOUNT];
byte pinCount = 0;

void setup() {
  Serial.begin(BAUDRATE);  
  clearPins();
  delay(10);
  Serial.println("ICtest1.2");
}

void loop() {
    commandCollector();


}

void commandCollector() {
  if (Serial.available() > 0) {
    int inByte = Serial.read();
    switch(inByte) {
    case '.':
//    case '\r':
    case '\n':
      commandInterpreter();
      clearSerialBuffer();
      setBufPointer = 0;
      break;
    case '\r':
      break;  // ignore carriage return
    default:
      serialBuffer[setBufPointer] = inByte;
      setBufPointer++;
      if (setBufPointer >= SERIALBUFSIZE) {
        Serial.println("ERROR: Serial buffer overflow. Cleanup.");
        clearSerialBuffer();
        setBufPointer = 0;
      }
    }
  }
}

void commandInterpreter() {
  byte bufByte = serialBuffer[0];
  
  switch(bufByte) {
    case 'C':
    case 'c':
      configurePins();
      break;
    case 'H':
    case 'h':
    case '?':
      usage();
      break;
    case 'Q':
    case 'q':
      setQueryThePins();
      break;
    case 'R':
    case 'r':
      resetThePins();
      break;
    default:
      Serial.print((char)bufByte);
      Serial.print(" ");
      Serial.println("unsupported");
      return;
  }
}

void usage() {
  Serial.println("ICtest1.0");
  Serial.println("C - configure pins");
  Serial.println("H - this text");
  Serial.println("Q - set and query pins");
  Serial.println("R - reset config and pins");
}

void configurePins() {
  // C:1,2,Q,4,5,Q,G,Q,9,10,Q,12,13,V  (7400)
  // C:1,2,3,4,5,6,Q,G,Q,Q,Q,Q,Q,Q,Q,V (74138)
  clearPins();
  pinCount = getPinDef();
  bool err = 0;
  for (byte i = 0; i < pinCount; i++) {
    logPinConf(i);
    if (pinType[i] == EXERCISE_PIN) {
      pinMode(pinMap[i], OUTPUT);
    } else if (pinType[i] == QUERY_PIN) {
      pinMode(pinMap[i], INPUT_PULLUP);
    } else if (pinType[i] == GROUND_PIN) {
      // ignore
    } else if (pinType[i] == POWER_PIN) {
      // ignore
    } else if (pinType[i] == CLOCK_PIN) { // raising flank clock
      pinMode(pinMap[i], OUTPUT);
      digitalWrite(pinMap[i], LOW);
    } else if (pinType[i] == INV_CLOCK_PIN) { // falling flank clock
      pinMode(pinMap[i], OUTPUT);
      digitalWrite(pinMap[i], HIGH);
    } else {
      Serial.print("ERROR: config ");
      Serial.print(i);
      Serial.print(" ");
      Serial.println((char)pinType[i]);
      err = 1;
    }
  }
  if (err) {
    Serial.println("ERROR");
  } else {
    Serial.println("OK");
  }
}

void logPinConf(byte i) {
  if (!DEBUG) return;
    Serial.print("'");
    Serial.print(i + 1);
    Serial.print(" [");
    Serial.print(pinMap[i]);
    Serial.print("]: ");
    Serial.print((char)pinType[i]);
    Serial.println();
}

byte getPinDef() {
  byte pinCount = countPins();
  switch(pinCount) {
    case 14:
      pinMap = pins14;
      break;
    case 16:
      pinMap = pins16;
      break;
    default:
      Serial.print("ERROR: pin count ");
      Serial.print(pinCount);
      Serial.println(" unsupported");
      return;
  }
  byte separatorIndex = 0;
  char *parseBuf = &serialBuffer[2];
  String parseStr = parseBuf;
  int pinNum = 0;
  for (int i = 0; i < pinCount; i++) {
    separatorIndex = parseStr.indexOf(PIN_SEPARATOR);
    if (isNumeric(parseStr.charAt(0))) {
        pinType[i] = EXERCISE_PIN;
    } else { 
        pinType[i] = parseStr.charAt(0);
    }
    parseStr = parseStr.substring(separatorIndex + 1);
  }
  return pinCount;
}

byte countPins() { // C:1,2,Q,4,5,Q,G,Q,9,10,Q,12,13,V
  byte pinCount = 0;
  for (int i = 0; i < SERIALBUFSIZE; i++) {
    char c = serialBuffer[i];
    if (i < 2) continue; // ignore the header chars "C:"
      if (serialBuffer[i] == PIN_SEPARATOR) {
        pinCount++;
    }
  }
  return pinCount + 1;
}

void setQueryThePins() { // Q:0,0,-,0,0,-,G,-,0,0,-,0,0,V
  if (pinCount == 0) {
    Serial.println("ERROR: pins not configured");
    return;
  }
  byte separatorIndex = 0;
  char *parseBuf = &serialBuffer[2]; // remove leading 'Q:'
  String parseStr = parseBuf;

  for (int i = 0; i < pinCount; i++) { // setting non-clock pins
    separatorIndex = parseStr.indexOf(PIN_SEPARATOR);
    if (pinType[i] != CLOCK_PIN && pinType[i] != INV_CLOCK_PIN) {
      if (parseStr.charAt(0) == '0' && pinMap[i] != 0) {
          digitalWrite(pinMap[i], 0);
      } else if (parseStr.charAt(0) == '1' && pinMap[i] != 0) {
          digitalWrite(pinMap[i], 1);
      } else { // ignore other pins
          
      }
      parseStr = parseStr.substring(separatorIndex + 1);
    }
  }
  for (int i = 0; i < pinCount; i++) { // setting clock pins
    separatorIndex = parseStr.indexOf(PIN_SEPARATOR);
    if (pinType[i] == CLOCK_PIN && parseStr.charAt(0) == '1' && pinMap[i] != 0) {
        digitalWrite(pinMap[i], HIGH);
        delay(CLOCK_PULSE);
        digitalWrite(pinMap[i], LOW);
    } else if (pinType[i] == INV_CLOCK_PIN && parseStr.charAt(0) == '1' && pinMap[i] != 0) {
        digitalWrite(pinMap[i], LOW);
        delay(CLOCK_PULSE);
        digitalWrite(pinMap[i], HIGH);
    } else { // ignore other pins
        
    }
    parseStr = parseStr.substring(separatorIndex + 1);
  }
  parseStr = parseBuf;
  String response = "R:";
  for (int i = 0; i < pinCount; i++) { // querying
    separatorIndex = parseStr.indexOf(PIN_SEPARATOR);
    logQuery(i);
    if (pinType[i] == GROUND_PIN || pinType[i] == POWER_PIN) {
      response = String(response + (char)pinType[i]);
    } else if (isBoolean(parseStr.charAt(0))) {
      response = String(response + parseStr.charAt(0));
    } else  if (parseStr.charAt(0) == QUERY_CHAR) {
//      response = String(response + digitalRead(pinMap[i]));
      response = String(response + ((digitalRead(pinMap[i])) ? "H" : "L"));
    } else {
      Serial.println("ERROR: unknown pin type or query character");
    }
    parseStr = parseStr.substring(separatorIndex + 1);
    if (i < pinCount -1) response = String(response + ",");
  }
  Serial.println(response);
}

void logQuery(byte i) {
    if (!DEBUG) return;
    Serial.print("'");
    Serial.print(i + 1);
    Serial.print(" [");
    Serial.print(pinMap[i]);
    Serial.print("]: ");
    if (pinType[i] == GROUND_PIN || pinType[i] == POWER_PIN) {
      Serial.println((char)pinType[i]);
    } else {
      Serial.println(digitalRead(pinMap[i]));
    }
}

void resetThePins() {
  pinCount = 0;
  clearPins();
  for (int i = 0; i < MAX_PINCOUNT; i++) {
    pinMode(pinMap[i], INPUT);
  }
  Serial.println("OK");
}

void clearPins() {
  for (int i = 0; i < MAX_PINCOUNT; i++) pinType[i] = 0;
}

void clearSerialBuffer() {
  byte i;
  for (i = 0; i < SERIALBUFSIZE; i++) {
    serialBuffer[i] = 0;
  }
}

bool isNumeric(char c) {
  return (c >= '0' && c <= '9');
}

bool isBoolean(char c) {
  return (c >= '0' && c <= '1');
}
