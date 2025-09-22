# handles the stt and tts

import speech_recognition as sr
import pyttsx3
import time

# Initialize TTS engine
try:
    engine = pyttsx3.init('nsss')  # macOS
except:
    engine = pyttsx3.init()  # Default

engine.setProperty('rate', 180)
engine.setProperty('volume', 0.9)


def listen_here():
    """
    Capture mic input and return text using Google Speech Recognition.
    """
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("[INFO] Listening... Speak now!")
            audio = r.listen(source, timeout=10, phrase_time_limit=8)
            try:
                text = r.recognize_google(audio, language='en-US')
                print(f"[SUCCESS] You said: '{text}'")
                return text.strip()
            except sr.UnknownValueError:
                print("[WARN] Could not understand audio.")
                return ""
            except sr.RequestError as e:
                print(f"[ERROR] Google Speech Recognition error: {e}")
                return ""
    except Exception as e:
        print(f"[ERROR] Microphone error: {e}")
        return ""


def speak_here(text):
    """
    Convert text to speech.
    """
    if not text or text.strip() == "":
        print("[WARN] Empty text provided to TTS")
        return
    try:
        print(f"[TTS] 🗣️ Speaking: {text}")
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[ERROR] TTS error: {e}")
        print(f"[FALLBACK] Would have said: {text}")


if __name__ == "__main__":
    print("Testing speech recognition...")
    test_text = listen_here()
    if test_text:
        print("Microphone is working!")
        speak_here("Hello, this is a test of the text to speech system.")
    else:
        print("Please check your microphone settings.")