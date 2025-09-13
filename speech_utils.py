# handles the stt and tts
import speech_recognition as sr
import pyttsx3
import simpleaudio as sa


recognizer = sr.Recognizer()
engine = pyttsx3.init()

def listen_here():
    '''
    captuer mic input
    return text
    '''

    with sr.Microphone() as source:
        print("Speak mf...")
        audio = recognizer.listen(source, timeout = 4)
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return ""