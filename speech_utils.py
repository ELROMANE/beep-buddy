# handles the stt and tts
engine = pyttsx3.init('nsss')

import speech_recognition as sr
import pyttsx3
import simpleaudio as sa


recognizer = sr.Recognizer()

def listen_here():
    '''
    captuer mic input
    return text
    '''

    with sr.Microphone() as source:
        print("Speak mf...")
        audio = recognizer.listen(source, timeout = 7)
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.WaitTimeoutError:
            print("Really Really")
            return ""
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