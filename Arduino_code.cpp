#include <Servo.h>

int motorA1 = 9;
int motorA2 = 8;
int motorB1 = 7;
int motorB2 = 6;
int buzzer = 5;

Servo headServo;

void setup() {
  pinMode(motorA1, OUTPUT);
  pinMode(motorA2, OUTPUT);
  pinMode(motorB1, OUTPUT);
  pinMode(motorB2, OUTPUT);
  pinMode(buzzer, OUTPUT);
  
  headServo.attach(10); // Servo pin
  headServo.write(90);  // Neutral position
  
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "FWD") forward();
    else if (cmd == "BACK") back();
    else if (cmd == "TURN") turn();
    else if (cmd == "STOP") stopMotors();
    else if (cmd == "BEEP") beepR2D2();
    else if (cmd == "TILT") tiltHead();
  }
}

void forward() {
  digitalWrite(motorA1, HIGH);
  digitalWrite(motorA2, LOW);
  digitalWrite(motorB1, HIGH);
  digitalWrite(motorB2, LOW);
}

void back() {
  digitalWrite(motorA1, LOW);
  digitalWrite(motorA2, HIGH);
  digitalWrite(motorB1, LOW);
  digitalWrite(motorB2, HIGH);
}

void turn() {
  digitalWrite(motorA1, HIGH);
  digitalWrite(motorA2, LOW);
  digitalWrite(motorB1, LOW);
  digitalWrite(motorB2, HIGH);
}

void stopMotors() {
  digitalWrite(motorA1, LOW);
  digitalWrite(motorA2, LOW);
  digitalWrite(motorB1, LOW);
  digitalWrite(motorB2, LOW);
}

void beepR2D2() {
  tone(buzzer, 1000, 200);
  delay(300);
  tone(buzzer, 1500, 300);
  delay(300);
  tone(buzzer, 800, 150);
  delay(200);
  noTone(buzzer);
}

void tiltHead() {
  headServo.write(60);  // tilt left
  delay(500);
  headServo.write(120); // tilt right
  delay(500);
  headServo.write(90);  // return center
}
