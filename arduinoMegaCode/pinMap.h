// pin mapping from IC (adding one) to Arduino, power pins are 0

#define MAX_PINCOUNT 16
#define EXERCISE_PINCOUNT 14
#define QUERY_PINCOUNT 10

// Uno config
//byte pins14[] =     { 13, 12, 11, 10, 9, 8, 0, 2, 3, 4, 5, 6, 7, 0 };
//byte power14 = A5;
//byte pins16[] = { A0, 13, 12, 11, 10, 9, 8, 0, 2, 3, 4, 5, 6, 7, A1, 0 };

// not implemented

//byte power16 = ?
//byte pins20[] = { A2, A3, A0, 13, 12, 11, 10, 9, 8, 0, 7, 6, 5, 4, 3, 2, A1, A4, A5, 0};



// Mega 2560 config
byte pins14[] =   { 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29 };
byte power14  = 7;

byte pins16[] = { 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28 };
byte power16  = 6;

byte pins20[] = { 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26 };
byte power20  = 5;

byte pins24[] = { 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24 };
byte power24  = 4;

byte pins28[] = { 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22 };
byte power28  = 3;


byte *pinMap;
