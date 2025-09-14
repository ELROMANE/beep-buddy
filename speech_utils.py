# handles the stt and tts

import speech_recognition as sr
import pyttsx3
import simpleaudio as sa

engine = pyttsx3.init('nsss')

recognizer = sr.Recognizer()

def listen_here():
    '''
    Capture mic input and return text using Google Speech Recognition with tuned thresholds.
    '''

    r = sr.Recognizer()
    r.energy_threshold = 150  # Lower for more sensitivity, adjust as needed
    r.pause_threshold = 0.7   # Adjust for your speaking style
    with sr.Microphone() as source:
        print("Speak now...")
        try:
            audio = r.listen(source, timeout=7)
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start")
            return ""
        try:
            text = r.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return ""
        

def speak_here(text):
    engine.say(text)
    engine.runAndWait()


def play_sound(file_path):
    '''
    play a sound file
    '''
    wave_obj = sa.WaveObject.from_wave_file(file_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()  # Wait until sound has finished playing