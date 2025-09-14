# the main code for R2D2

# File imports
from cerebras_api import ask_prompt
from speech_utils import listen_here, speak_here, play_sound
import movement_sim as r2

# library imports
import cv2
import time


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
    prompt = f"Analyze the following message and tell me if the user sounds happy, sad, excited, or angry: '{text}'"
    emotion = ask_prompt(prompt)
    return emotion.strip().lower()


def main():
    arduino_connected = is_arduino_connected()
    intro_message = "Hey, wassup!"
    speak_here(intro_message)
    print(intro_message)
    awake = not arduino_connected  # If no Arduino, start awake
    while True:
        if not awake:
            user_input = listen_here()
            if user_input and "hello" in user_input.lower():
                awake = True
                play_sound("assets/sounds/lala.wav")  # Wake up sound
                current_time = time.strftime('%I:%M %p')
                wake_message = f"Yo, it's just {current_time}."
                print(wake_message)
                speak_here(wake_message)
                if arduino_connected:
                    r2.beep()
            continue

        user_input = listen_here()
        if not user_input:
            speak_here("Please say something!")
            continue

        if "tired" in user_input.lower():
            play_sound("assets/sounds/lala.wav")  # Tired beep sound
            speak_here("I'm tired. Going to sleep.")
            if arduino_connected:
                r2.beep()
            awake = False
            continue

        if "shutup" in user_input.lower():
            speak_here("Okay, I'll be quiet now.")
            break

        if "quizme" in user_input.lower():
            speak_here("Quiz mode is coming soon!")
            continue

        if "opencamera" in user_input.lower():
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

        try:
            r2_reply = ask_prompt(user_input)
        except Exception as e:
            print(f"Error with Cerebras API: {e}")
            speak_here("Sorry, I couldn't get a response from my brain right now.")
            continue
        print("R2D2:", r2_reply)
        try:
            speak_here(r2_reply)
        except Exception as e:
            print(f"TTS error: {e}")
            speak_here("Sorry, I couldn't speak that out loud.")
        # Calculate delay based on word count, max 10 seconds
        word_count = len(r2_reply.split())
        delay = min(max(word_count * 0.3, 1), 10)  # 0.3s per word, at least 1s, max 10s
        time.sleep(delay)
        # If reply is too long, summarize and present to user
        if word_count > 30:
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
        try:
            emotion = analyze_emotion(r2_reply)
            print("Detected emotion:", emotion)
            # Only trigger if the first word is 'happy' or 'sad'
            first_word = emotion.split()[0] if emotion else ""
            if first_word == "happy":
                play_sound("assets/sounds/lala.wav")
                if arduino_connected:
                    r2.tilt_head()
                    r2.beep()
            elif first_word == "sad":
                speak_here("Don't worry, I'm here for you!")
                if arduino_connected:
                    r2.tilt_head()
        except Exception as e:
            print(f"Emotion analysis error: {e}")

        if "bye" in user_input.lower():
            speak_here("Goodbye! See you soon!")
            break


if __name__ == "__main__":
    main()