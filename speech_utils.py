# handles the stt and tts

import speech_recognition as sr
import pyttsx3
import simpleaudio as sa
import threading
import time

# Initialize TTS engine
try:
    engine = pyttsx3.init('nsss')  # macOS
except:
    try:
        engine = pyttsx3.init('sapi5')  # Windows
    except:
        engine = pyttsx3.init()  # Default

# Set TTS properties for better performance
voices = engine.getProperty('voices')
if voices:
    engine.setProperty('voice', voices[0].id)  # Use first available voice
engine.setProperty('rate', 180)  # Adjust speech rate
engine.setProperty('volume', 0.9)

def listen_here():
    """
    Capture mic input and return text using Google Speech Recognition with tuned thresholds.
    """
    r = sr.Recognizer()
    
    # Adjust microphone settings
    r.energy_threshold = 300  # Increased for less sensitivity to background noise
    r.pause_threshold = 1.0   # Increased pause threshold
    r.phrase_threshold = 0.3  # Minimum seconds of speaking audio before considering phrase complete
    r.non_speaking_duration = 0.5  # Seconds of non-speaking audio to keep on both sides
    
    try:
        with sr.Microphone() as source:
            print("[INFO] Adjusting for ambient noise... Please be quiet.")
            r.adjust_for_ambient_noise(source, duration=1)
            print(f"[DEBUG] Energy threshold set to: {r.energy_threshold}")
            
            print("[INFO] Listening... Speak now!")
            try:
                # Listen with timeout and phrase time limit
                audio = r.listen(source, timeout=10, phrase_time_limit=8)
                print("[INFO] Processing audio...")
            except sr.WaitTimeoutError:
                print("[WARN] Listening timed out - no speech detected")
                return ""
            
            try:
                # Try Google Speech Recognition
                text = r.recognize_google(audio, language='en-US')
                print(f"[SUCCESS] You said: '{text}'")
                return text.strip()
                
            except sr.UnknownValueError:
                print("[WARN] Could not understand audio - please speak more clearly")
                return ""
            except sr.RequestError as e:
                print(f"[ERROR] Could not request results from Google Speech Recognition: {e}")
                
                # Fallback to offline recognition if available
                try:
                    text = r.recognize_sphinx(audio)
                    print(f"[SUCCESS] Offline recognition: '{text}'")
                    return text.strip()
                except sr.UnknownValueError:
                    print("[WARN] Offline recognition also failed")
                    return ""
                except sr.RequestError:
                    print("[ERROR] Offline recognition not available")
                    return ""
                    
    except Exception as e:
        print(f"[ERROR] Microphone error: {e}")
        return ""


def speak_here(text):
    """
    Convert text to speech with error handling
    """
    if not text or text.strip() == "":
        print("[WARN] Empty text provided to TTS")
        return
        
    try:
        print(f"[TTS] Speaking: {text}")
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[ERROR] TTS error: {e}")
        # Fallback: just print the text
        print(f"[FALLBACK] Would have said: {text}")


def play_sound(file_path):
    """
    Play a sound file with error handling
    """
    try:
        wave_obj = sa.WaveObject.from_wave_file(file_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()  # Wait until sound has finished playing
        print(f"[SOUND] Played: {file_path}")
    except FileNotFoundError:
        print(f"[WARN] Sound file not found: {file_path}")
    except Exception as e:
        print(f"[ERROR] Could not play sound {file_path}: {e}")


def test_microphone():
    """
    Test function to check if microphone is working
    """
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Testing microphone... Say something!")
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, timeout=5, phrase_time_limit=3)
            text = r.recognize_google(audio)
            print(f"Microphone test successful! Heard: {text}")
            return True
    except Exception as e:
        print(f"Microphone test failed: {e}")
        return False


if __name__ == "__main__":
    # Test the functions when run directly
    print("Testing speech recognition...")
    if test_microphone():
        print("Microphone is working!")
        test_text = "Hello, this is a test of the text to speech system."
        speak_here(test_text)
    else:
        print("Please check your microphone settings.")