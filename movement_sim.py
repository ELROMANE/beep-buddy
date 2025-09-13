import time
import os

def clear():
    os.system('clear')

def move_forward():
    clear()
    print("""
        🤖
        /|\\   R2 is rolling FORWARD...
        / \\
    """)
    time.sleep(1)

def turn_left():
    clear()
    print("""
         🤖 <
        /|\\   R2 turns LEFT...
        / \\
    """)
    time.sleep(1)

def turn_right():
    clear()
    print("""
        > 🤖
        /|\\   R2 turns RIGHT...
        / \\
    """)
    time.sleep(1)

def stop():
    clear()
    print("""
        🤖
        /|\\   R2 stopped.
        / \\
    """)
    time.sleep(1)
