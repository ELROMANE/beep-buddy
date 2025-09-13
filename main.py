# the main code for R2D2

from cerebras_api import ask_prompt
from speech_utils import listen_here, speak_here, play_sound
import movement_sim as r2


while True:
    user_input = listen_here()
    if not user_input:
        print("speak something motherfucking fucker")
        user_input = listen_here()

    r2_reply = ask_prompt(user_input)
    print("works>?", r2_reply)

    speak_here(r2_reply)

    if "happy" in r2_reply.lower():
        play_sound("assets/sounds/lala.wav")

