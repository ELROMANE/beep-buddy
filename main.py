# the main code for R2D2

from cerebras_api import ask_prompt
from speech_utils import listen_here, speak_here, play_sound
import movement_sim as r2


while True:
    user_input = listen_here()
    if not user_input:
        print("speak something motherfucking fucker")
        user_input = listen_here()
