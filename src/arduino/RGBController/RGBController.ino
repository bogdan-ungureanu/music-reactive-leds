#include <Arduino.h>

const int red_pin = 11;
const int green_pin = 10;
const int blue_pin = 9;

void SetColorLED(int r, int g, int b)
{
  analogWrite(red_pin, r);
  analogWrite(green_pin, g);
  analogWrite(blue_pin, b);
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(5000);
  pinMode(red_pin, OUTPUT);
  pinMode(green_pin, OUTPUT);
  pinMode(blue_pin, OUTPUT);
}

void loop() {
  String r, g, b;
  
    while(Serial.available()<3) {}
      r = Serial.read();
      g = Serial.read();
      b = Serial.read();

    SetColorLED(r.toInt(),g.toInt(),b.toInt());
}
