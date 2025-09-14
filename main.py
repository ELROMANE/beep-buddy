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


def main():
    arduino_connected = is_arduino_connected()
    intro_message = "Hey, wassup!"
    speak_here(intro_message)
    print(intro_message)
    awake = not arduino_connected  # If no Arduino, start awake
    while True:
        if not awake:
            user_input = listen_here()
            text_turn = listen_here()
            if text_turn == "type":
                speak_here("Type your prompt:")
                user_text_input = input("What??")

            if user_input and "hello" in user_input or "hello" in user_text_input.lower():
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
            awake = False
            continue

        if "type" in user_input or "type" in user_text_input.lower():
            speak_here("Type your prompt:")
            user_input = input("Type your prompt: ")
            if not user_input:
                continue

        if "shutup" in user_input or "shutup" in user_text_input.lower():
            speak_here("Okay, I'll be quiet now.")
            break

        if "quizme" in user_input or "quizme" in user_text_input.lower():
            speak_here("Quiz mode is coming soon!")
            continue

        if "opencamera" in user_input or "opencamera" in user_text_input.lower():
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

        r2_reply = ask_prompt(user_input)
        print("R2D2:", r2_reply)
        speak_here(r2_reply)
        time.sleep(0.5)  # Small pause to ensure TTS finishes before next listen

        if "happy" in r2_reply.lower():
            play_sound("assets/sounds/lala.wav")
            if arduino_connected:
                r2.tilt_head()
                r2.beep()

        if "bye" in user_input or "bye" in user_text_input.lower():
            speak_here("Goodbye! See you soon!")
            break


if __name__ == "__main__":
    main()