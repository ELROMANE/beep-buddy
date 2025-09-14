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
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[WARN] Camera could not be opened for analysis.")
        return None, None
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("[WARN] Could not read frame from camera.")
        return None, None
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    avg_brightness = np.mean(gray)
    # Haar cascade for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    face_detected = len(faces) > 0
    return avg_brightness, face_detected


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
                play_sound("assets/sounds/listening.wav")  # Play listening sound before listening
                user_input = listen_here()
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

            play_sound("assets/sounds/listening.wav")  # Play listening sound before listening
            user_input = listen_here()
            print(f"[DEBUG] Heard: {user_input}")
            if not user_input:
                speak_here("Please say something! Make sure your mic is on and speak clearly.")
                continue

            if "help" in user_input.lower():
                help_msg = ("You can say: 'tired' (sleep), 'quizme', 'opencamera', 'shutup', 'bye', or just talk to me!")
                speak_here(help_msg)
                continue

            if "tired" in user_input.lower():
                try:
                    play_sound("assets/sounds/lala.wav")  # Tired beep sound
                except Exception as e:
                    print(f"[WARN] Tired sound missing: {e}")
                speak_here("I'm tired. Going to sleep.")
                if arduino_connected:
                    r2.beep()
                awake = False
                continue

            if "shutup" in user_input.lower():
                speak_here("Okay, I'll be quiet now.")
                break

            if "quizme" in user_input.lower():
                try:
                    quiz_prompt = "Generate a fun, simple quiz question for a child. Only give the question, not the answer."
                    quiz_question = ask_prompt(quiz_prompt)
                    print("Quiz question:", quiz_question)
                    speak_here(quiz_question)
                    user_answer = listen_here()
                    if not user_answer:
                        speak_here("I didn't hear your answer. Let's try again later!")
                        continue
                    check_prompt = f"The question was: '{quiz_question}'. The answer given was: '{user_answer}'. Is this correct? Reply only with 'yes' or 'no'."
                    check_result = ask_prompt(check_prompt).strip().lower()
                    if check_result.startswith("yes"):
                        speak_here("Awesome! You got it right!")
                        play_sound("assets/sounds/lala.wav")
                    else:
                        speak_here("Nice try! Want to try another one later?")
                except Exception as e:
                    print(f"Quiz error: {e}")
                    speak_here("Sorry, I couldn't do a quiz right now.")
                continue

            if "opencamera" in user_input.lower():
                # Only analyze face and lighting when user requests camera
                avg_brightness, face_detected = analyze_face_and_lighting()
                if avg_brightness is not None and avg_brightness < 60:
                    speak_here("Warning: The lighting is dim. Please turn on a light or move to a brighter area for better interaction.")
                if avg_brightness is not None:
                    print(f"[DEBUG] Average brightness: {avg_brightness:.2f}")
                if face_detected is not None and not face_detected:
                    speak_here("I can't see your face. Please make sure you are in front of the camera.")
                cap = cv2.VideoCapture(0)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        cv2.imshow('Camera', frame)
                        cv2.waitKey(3500)
                        cv2.destroyAllWindows()
                    cap.release()
                    speak_here("Camera opened!")
                else:
                    speak_here("Camera could not be opened.")
                continue

            if "time" in user_input.lower():
                current_time = time.strftime('%I:%M %p')
                speak_here(f"The current time is {current_time}.")
                continue

            try:
                r2_reply = ask_prompt(user_input)
            except Exception as e:
                print(f"Error with Cerebras API: {e}")
                speak_here("Sorry, I couldn't get a response from my brain right now.")
                continue
            print("R2D2:", r2_reply)
            try:
                if not r2_reply.strip():
                    speak_here("Sorry, I didn't get that.")
                else:
                    speak_here(r2_reply)
                    # Only delay after AI-generated response
                    word_count = len(r2_reply.split())
                    delay = min(max(word_count * 0.3, 1), 10)
                    time.sleep(delay)
            except Exception as e:
                print(f"TTS error: {e}")
                speak_here("Sorry, I couldn't speak that out loud.")
            # If reply is too long, summarize and present to user
            if 'r2_reply' in locals() and len(r2_reply.split()) > 30:
                summary_prompt = f"Summarize this in 20 words or less for a child: {r2_reply}"
                try:
                    summary = ask_prompt(summary_prompt)
                    print("Summary:", summary)
                    speak_here(f"Summary: {summary}")
                except Exception as e:
                    print(f"Summary error: {e}")
                    speak_here("Sorry, I couldn't summarize that.")
            time.sleep(0.5)  # Small pause to ensure TTS finishes before next listen

            # Emotion/tone detection for sound and actions
            # (Removed voice-based mood analysis)

            if "bye" in user_input.lower():
                speak_here("Goodbye! See you soon!")
                break
    except KeyboardInterrupt:
        print("\n[R2D2] Shutting down. Goodbye!")
        speak_here("Goodbye! See you soon!")


if __name__ == "__main__":
    main()