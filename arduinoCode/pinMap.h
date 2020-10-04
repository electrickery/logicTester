// pin mapping from IC (adding one) to Arduino, power pins are 0

#define MAX_PINCOUNT 16
#define EXERCISE_PINCOUNT 14
#define QUERY_PINCOUNT 10

byte pins14[] = { 13, 12, 11, 10, 9, 8, 0, 2, 3, 4, 5, 6, 7, 0 };

byte pins16[] = { A0, 13, 12, 11, 10, 9, 8, 0, 7, 6, 5, 4, 3, 2, A1, 0 };

byte *pinMap;
