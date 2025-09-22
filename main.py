# Minimal R2D2 Assistant Template
# Only wakes up on 'hello' and does nothing else

from speech_utils import listen_here, speak_here


def main():
    awake = False
    print("[R2D2] Minimal Assistant started. Say 'hello' to wake me up! (Ctrl+C to exit)")
    while True:
        if not awake:
            print("[INFO] Waiting for wake word 'hello'...")
            user_input = listen_here()
            print(f"[DEBUG] Sleep mode - Heard: '{user_input}'")
            if user_input and "hello" in user_input.lower():
                awake = True
                print("Yo, I'm awake!")
                speak_here("Yo, I'm awake!")
            continue
        # Assistant does nothing else for now
        print("[INFO] Assistant is awake. Waiting for next command...")
        user_input = listen_here()
        print(f"[DEBUG] Awake mode - Heard: '{user_input}'")
        # No further actions

if __name__ == "__main__":
    main()