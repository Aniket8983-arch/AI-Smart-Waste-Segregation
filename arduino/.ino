#include <ESP32Servo.h>

Servo segregator;
int servoPin = 18; // Connect your Signal wire to GPIO 18

void setup() {
  Serial.begin(115200);
  segregator.attach(servoPin);
  segregator.write(90); // Start at center/neutral
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();

    if (command == 'B') {
      // Move to Biodegradable bin
      segregator.write(45); 
      delay(2000); // Wait for waste to fall
      segregator.write(90); // Reset
    } 
    else if (command == 'N') {
      // Move to Non-Biodegradable bin
      segregator.write(135); 
      delay(2000);
      segregator.write(90);
    }
  }
}