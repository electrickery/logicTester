// pin mapping from IC (adding one) to Arduino, power pins are 0

#define MAX_PINCOUNT 16
#define EXERCISE_PINCOUNT 14
#define QUERY_PINCOUNT 10

byte pins14[] =     { 13, 12, 11, 10, 9, 8, 0, 2, 3, 4, 5, 6, 7, 0 };
byte power14 = A5;
byte pins16[] = { A0, 13, 12, 11, 10, 9, 8, 0, 2, 3, 4, 5, 6, 7, A1, 0 };

// not implemented

//byte power16 = ?
byte pins20[] = { A2, A3, A0, 13, 12, 11, 10, 9, 8, 0, 7, 6, 5, 4, 3, 2, A1, A4, A5, 0};

byte *pinMap;
