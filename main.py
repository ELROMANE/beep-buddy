# the main code for R2D2

# File imports
from cerebras_api import ask_prompt
from speech_utils import listen_here, speak_here, play_sound
import movement_sim as r2

# library imports
import cv2


def main():
    print("Hi! I'm your R2D2 friend. Say 'Zero' to wake me up, 'quiz me' for a quiz, or just talk to me!")
    awake = False
    while True:
        if not awake:
            user_input = listen_here()
            if user_input and "zero" in user_input.lower():
                awake = True
                play_sound("assets/sounds/lala.wav")  # Wake up sound
                speak_here("I'm awake! How can I help you?")
            continue

        user_input = listen_here()
        if not user_input:
            print("Please say something!")
            continue

        if "tired" in user_input.lower():
            play_sound("assets/sounds/lala.wav")  # Tired beep sound
            speak_here("I'm tired. Going to sleep.")
            awake = False
            continue

        if "type" in user_input.lower():
            user_input = input("Type your prompt: ")

        if "shut up" in user_input.lower():
            speak_here("Okay, I'll be quiet now.")
            break

        if "quiz me" in user_input.lower():
            speak_here("Quiz mode is coming soon!")
            continue

        if "open camera" in user_input.lower():
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if ret:
                cv2.imshow('Camera', frame)
                cv2.waitKey(3500)
                cv2.destroyAllWindows()
            cap.release()
            speak_here("Camera opened!")
            continue

        r2_reply = ask_prompt(user_input)
        print("R2D2:", r2_reply)
        speak_here(r2_reply)

        if "happy" in r2_reply.lower():
            play_sound("assets/sounds/lala.wav")
            r2.tilt_head()
            r2.beep()

        if "bye" in user_input.lower():
            speak_here("Goodbye! See you soon!")
            break


if __name__ == "__main__":
    main()