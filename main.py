# the main code for R2D2

# File imports
from cerebras_api import ask_prompt
from speech_utils import listen_here, speak_here, play_sound
import movement_sim as r2

# library imports
import cv2
import time
import numpy as np


def is_arduino_connected():
    try:
        import serial
        from movement_sim import ARDUINO_PORT, BAUD_RATE
        ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
        ser.close()
        return True
    except Exception:
        return False


def analyze_emotion(text):
    prompt = (
        "Read the following message and respond with ONLY ONE WORD from this list: happy, sad, excited, angry, neutral. "
        "No explanation, no punctuation, just the word. Message: '" + text + "'"
    )
    emotion = ask_prompt(prompt).strip().lower()
    allowed = {"happy", "sad", "excited", "angry", "neutral"}
    # Fallback to neutral if not recognized
    if emotion not in allowed:
        return "neutral"
    return emotion


def analyze_face_and_lighting():
    cap = None
    try:
        # Try different camera indices
        for i in range(3):  # Try camera indices 0, 1, 2
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"[INFO] Camera found at index {i}")
                break
            cap.release()
        
        if not cap or not cap.isOpened():
            print("[WARN] No camera could be opened for analysis.")
            return None, None
        
        # Give camera time to initialize
        time.sleep(1)
        
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Could not read frame from camera.")
            return None, None
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        avg_brightness = np.mean(gray)
        
        # Haar cascade for face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)  # Adjusted parameters
        face_detected = len(faces) > 0
        
        return avg_brightness, face_detected
        
    except Exception as e:
        print(f"[ERROR] Camera analysis failed: {e}")
        return None, None
    finally:
        if cap:
            cap.release()


def main():
    arduino_connected = is_arduino_connected()
    intro_message = "Hey, wassup!"
    speak_here(intro_message)
    print("[R2D2] Assistant started. Say 'hello' to wake me up! (Ctrl+C to exit)")
    print(intro_message)
    awake = not arduino_connected  # If no Arduino, start awake
    
    try:
        while True:
            if not awake:
                print("[INFO] Waiting for wake word 'hello'...")
                try:
                    play_sound("assets/sounds/listening.wav")  # Play listening sound before listening
                except Exception as e:
                    print(f"[WARN] Could not play listening sound: {e}")
                
                user_input = listen_here()
                print(f"[DEBUG] Sleep mode - Heard: '{user_input}'")
                
                if user_input and "hello" in user_input.lower():
                    awake = True
                    try:
                        play_sound("assets/sounds/lala.wav")  # Wake up sound
                    except Exception as e:
                        print(f"[WARN] Wake sound missing: {e}")
                    wake_message = "Yo, I'm awake!"
                    print(wake_message)
                    speak_here(wake_message)
                    if arduino_connected:
                        r2.beep()
                        r2.tilt_head()
                continue

            print("[INFO] Listening for command...")
            try:
                play_sound("assets/sounds/listening.wav")  # Play listening sound before listening
            except Exception as e:
                print(f"[WARN] Could not play listening sound: {e}")
            
            user_input = listen_here()
            print(f"[DEBUG] Awake mode - Heard: '{user_input}'")
            
            if not user_input or user_input.strip() == "":
                speak_here("I didn't catch that. Could you repeat?")
                continue

            # Convert to lowercase for easier matching
            user_lower = user_input.lower()

            if "help" in user_lower:
                help_msg = ("You can say: 'tired' to put me to sleep, 'quizme' for a quiz, 'opencamera' to see through my eyes, 'shutup' to stop me, 'bye' to exit, or just talk to me!")
                speak_here(help_msg)
                continue

            if "tired" in user_lower:
                try:
                    play_sound("assets/sounds/lala.wav")  # Tired beep sound
                except Exception as e:
                    print(f"[WARN] Tired sound missing: {e}")
                speak_here("I'm tired. Going to sleep. Say hello to wake me up!")
                if arduino_connected:
                    r2.beep()
                awake = False
                continue

            if "shutup" in user_lower or "shut up" in user_lower:
                speak_here("Okay, I'll be quiet now.")
                break

            if "quizme" in user_lower or "quiz me" in user_lower:
                try:
                    print("[INFO] Generating quiz question...")
                    quiz_prompt = "Generate a fun, simple quiz question for a child. Only give the question, not the answer."
                    quiz_question = ask_prompt(quiz_prompt)
                    print("Quiz question:", quiz_question)
                    speak_here(quiz_question)
                    
                    print("[INFO] Waiting for answer...")
                    user_answer = listen_here()
                    if not user_answer:
                        speak_here("I didn't hear your answer. Let's try again later!")
                        continue
                    
                    print(f"[DEBUG] User answered: {user_answer}")
                    check_prompt = f"The question was: '{quiz_question}'. The answer given was: '{user_answer}'. Is this correct? Reply only with 'yes' or 'no'."
                    check_result = ask_prompt(check_prompt).strip().lower()
                    
                    if check_result.startswith("yes"):
                        speak_here("Awesome! You got it right!")
                        try:
                            play_sound("assets/sounds/lala.wav")
                        except Exception as e:
                            print(f"[WARN] Success sound missing: {e}")
                    else:
                        speak_here("Nice try! Want to try another one later?")
                except Exception as e:
                    print(f"[ERROR] Quiz error: {e}")
                    speak_here("Sorry, I couldn't do a quiz right now.")
                continue

            if "opencamera" in user_lower or "open camera" in user_lower:
                print("[INFO] Opening camera...")
                # Analyze face and lighting when user requests camera
                avg_brightness, face_detected = analyze_face_and_lighting()
                
                if avg_brightness is not None:
                    print(f"[DEBUG] Average brightness: {avg_brightness:.2f}")
                    if avg_brightness < 60:
                        speak_here("Warning: The lighting is dim. Please turn on a light or move to a brighter area for better interaction.")
                
                if face_detected is not None and not face_detected:
                    speak_here("I can't see your face clearly. Please make sure you are in front of the camera.")
                elif face_detected:
                    speak_here("I can see you! Looking good!")

                # Show camera feed
                cap = None
                try:
                    for i in range(3):  # Try different camera indices
                        cap = cv2.VideoCapture(i)
                        if cap.isOpened():
                            break
                        cap.release()
                    
                    if cap and cap.isOpened():
                        time.sleep(1)  # Let camera initialize
                        ret, frame = cap.read()
                        if ret:
                            cv2.imshow('R2D2 Camera View', frame)
                            speak_here("Camera opened! Press any key to close.")
                            cv2.waitKey(0)  # Wait for key press instead of fixed time
                            cv2.destroyAllWindows()
                        else:
                            speak_here("Camera opened but couldn't capture image.")
                    else:
                        speak_here("Sorry, I cannot access the camera right now.")
                except Exception as e:
                    print(f"[ERROR] Camera error: {e}")
                    speak_here("There was an error with the camera.")
                finally:
                    if cap:
                        cap.release()
                    cv2.destroyAllWindows()
                continue

            if "time" in user_lower:
                current_time = time.strftime('%I:%M %p')
                speak_here(f"The current time is {current_time}.")
                continue

            if "bye" in user_lower or "goodbye" in user_lower:
                speak_here("Goodbye! See you soon!")
                break

            # Handle general conversation
            try:
                print("[INFO] Getting AI response...")
                r2_reply = ask_prompt(user_input)
                print("R2D2:", r2_reply)
                
                if not r2_reply.strip():
                    speak_here("Sorry, I didn't get that.")
                    continue
                
                # Check if response is too long and summarize
                if len(r2_reply.split()) > 30:
                    summary_prompt = f"Summarize this in 20 words or less for a child: {r2_reply}"
                    try:
                        summary = ask_prompt(summary_prompt)
                        print("Summary:", summary)
                        speak_here(summary)
                    except Exception as e:
                        print(f"[ERROR] Summary error: {e}")
                        # Speak first 100 characters if summarization fails
                        short_reply = r2_reply[:100] + "..." if len(r2_reply) > 100 else r2_reply
                        speak_here(short_reply)
                else:
                    speak_here(r2_reply)
                
                # Dynamic delay based on response length
                word_count = len(r2_reply.split())
                delay = min(max(word_count * 0.2, 1), 5)  # Reduced max delay
                time.sleep(delay)
                
            except Exception as e:
                print(f"[ERROR] Error with AI response: {e}")
                speak_here("Sorry, I couldn't process that right now. Try again!")
                continue
                
            # Small pause between interactions
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n[R2D2] Shutting down. Goodbye!")
        speak_here("Goodbye! See you soon!")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        speak_here("Something went wrong. Shutting down.")


if __name__ == "__main__":
    main()