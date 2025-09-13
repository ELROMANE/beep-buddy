#include <Servo.h>   // Include the Servo library to control head tilt

// --- Motor driver pins ---
// These pins control the two DC motors (left and right wheels)
int motorA1 = 9;   // Motor A forward
int motorA2 = 8;   // Motor A backward
int motorB1 = 7;   // Motor B forward
int motorB2 = 6;   // Motor B backward

int buzzer = 5;    // Buzzer for R2D2 beeps
Servo headServo;   // Servo object to control the tilting "head"

void setup() {
  // Set motor pins as outputs
  pinMode(motorA1, OUTPUT);
  pinMode(motorA2, OUTPUT);
  pinMode(motorB1, OUTPUT);
  pinMode(motorB2, OUTPUT);
  pinMode(buzzer, OUTPUT);

  // Attach servo to pin 10 and set to neutral (90° = middle position)
  headServo.attach(10);
  headServo.write(90);

  // Start serial communication (Mac will send commands over USB)
  Serial.begin(9600);
}

void loop() {
  // Check if a command has been sent from the Mac
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');  // Read command line
    cmd.trim(); // Remove any extra spaces/newlines

    // Match the command with the correct action
    if (cmd == "FWD") forward();     // Move forward
    else if (cmd == "BACK") back();  // Move backward
    else if (cmd == "TURN") turn();  // Rotate in place
    else if (cmd == "STOP") stopMotors(); // Stop motors
    else if (cmd == "BEEP") beepR2D2();   // Play beep sequence
    else if (cmd == "TILT") tiltHead();   // Tilt head left and right
  }
}

// --- Motor control functions ---

// Move both motors forward
void forward() {
  digitalWrite(motorA1, HIGH);
  digitalWrite(motorA2, LOW);
  digitalWrite(motorB1, HIGH);
  digitalWrite(motorB2, LOW);
}

// Move both motors backward
void back() {
  digitalWrite(motorA1, LOW);
  digitalWrite(motorA2, HIGH);
  digitalWrite(motorB1, LOW);
  digitalWrite(motorB2, HIGH);
}

// Turn in place (left motor forward, right motor backward)
void turn() {
  digitalWrite(motorA1, HIGH);
  digitalWrite(motorA2, LOW);
  digitalWrite(motorB1, LOW);
  digitalWrite(motorB2, HIGH);
}

// Stop all motor movement
void stopMotors() {
  digitalWrite(motorA1, LOW);
  digitalWrite(motorA2, LOW);
  digitalWrite(motorB1, LOW);
  digitalWrite(motorB2, LOW);
}

// --- Sound + Head movement ---

// Make a sequence of tones to mimic R2D2 beeps
void beepR2D2() {
  tone(buzzer, 1000, 200); // frequency = 1000Hz, duration = 200ms
  delay(300);              // wait before next sound
  tone(buzzer, 1500, 300); // higher pitch
  delay(300);
  tone(buzzer, 800, 150);  // lower pitch
  delay(200);
  noTone(buzzer);          // stop sound
}

// Tilt servo left, then right, then back to center
void tiltHead() {
  headServo.write(60);   // tilt left
  delay(500);            // hold for half a second
  headServo.write(120);  // tilt right
  delay(500);
  headServo.write(90);   // return to center
}
