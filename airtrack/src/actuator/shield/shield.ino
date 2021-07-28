#define SPEED_PIN 5
#define SPEED 255
#define BAUDRATE 9600
#define DELAY 5000
void setup(){pinMode(SPEED_PIN, OUTPUT);Serial.begin(BAUDRATE);}
void loop(){analogWrite(SPEED_PIN, SPEED);delay(5000);}