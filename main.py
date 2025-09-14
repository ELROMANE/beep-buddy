# the main code for R2D2

from cerebras_api import ask_prompt
from speech_utils import listen_here, speak_here, play_sound
import movement_sim as r2

def main():
    print("Hi! I'm your R2D2 friend. Say 'quiz me' for a quiz, or just talk to me!")
    while True:
        user_input = listen_here()
        if not user_input:
            print("Please say something!")
            continue

        if "quiz me" in user_input.lower():
            # Placeholder for quiz logic
            speak_here("Quiz mode is coming soon!")
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