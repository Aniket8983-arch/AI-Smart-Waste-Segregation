#include <ESP32Servo.h>

Servo segregator;
int servoPin = 18;

void setup() {
  Serial.begin(115200);
  segregator.attach(servoPin);
  segregator.write(90);
  Serial.println("ESP32 Ready");
}

void loop() {
  if (Serial.available()) {
    char command = Serial.read();

    Serial.print("Received: ");
    Serial.println(command);

    if (command == 'B') {
      Serial.println("Moving BIO");
      segregator.write(45);
      delay(2000);
      segregator.write(90);
    }

    else if (command == 'N') {
      Serial.println("Moving NONBIO");
      segregator.write(135);
      delay(2000);
      segregator.write(90);
    }
  }
}
