# handles the stt and tts

import speech_recognition as sr
import pyttsx3
import simpleaudio as sa
import threading
import time
from movement_sim import tilt_head

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

tts_interrupted = False

def interrupt_tts():
    global tts_interrupted
    tts_interrupted = True

def _speak_with_interrupt(text):
    global tts_interrupted
    if tts_interrupted:
        return
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[ERROR] TTS error: {e}")


def speak_long_text(text, max_chunk_size=100):
    """
    Speak long text in chunks, and allow interruption if user starts speaking.
    """
    global tts_interrupted
    tts_interrupted = False
    words = text.split()
    if len(words) <= max_chunk_size:
        _speak_with_interrupt(text)
        return
    chunks = []
    current_chunk = []
    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= max_chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    for i, chunk in enumerate(chunks):
        if tts_interrupted:
            print("[TTS] Interrupted by user speech.")
            break
        if i > 0:
            speak_here("Continuing...")
            time.sleep(0.5)
        _speak_with_interrupt(chunk)
        time.sleep(1)


def monitor_for_speech():
    global tts_interrupted
    r = sr.Recognizer()
    with sr.Microphone() as source:
        while not tts_interrupted:
            try:
                audio = r.listen(source, timeout=0.5, phrase_time_limit=1)
                try:
                    text = r.recognize_google(audio)
                    if text:
                        print("[TTS] User interrupted with speech:", text)
                        tts_interrupted = True
                        break
                except sr.UnknownValueError:
                    pass
            except sr.WaitTimeoutError:
                pass


def speak_with_interrupt(text):
    global tts_interrupted
    tts_interrupted = False
    tts_thread = threading.Thread(target=speak_long_text, args=(text,))
    monitor_thread = threading.Thread(target=monitor_for_speech)
    tts_thread.start()
    monitor_thread.start()
    tts_thread.join()
    monitor_thread.join()
    if tts_interrupted:
        print("[INFO] Switching to listening mode due to user interruption.")
        # You can call listen_here() or your listening logic here


def listen_here():
    """
    Capture mic input and return text using Google Speech Recognition with tuned thresholds.
    Also moves the servo head when listening starts.
    """
    tilt_head()  # Move the head when listening starts
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
    Convert text to speech with natural pacing like Siri/Google Assistant
    """
    if not text or text.strip() == "":
        print("[WARN] Empty text provided to TTS")
        return
        
    try:
        print(f"[TTS] 🗣️ Speaking: {text}")
        
        # Brief pause before speaking (feels more natural)
        time.sleep(0.3)
        
        engine.say(text)
        engine.runAndWait()
        
        # Small pause after speaking (like natural conversation rhythm)
        time.sleep(0.5)
        
    except Exception as e:
        print(f"[ERROR] TTS error: {e}")
        # Fallback: just print the text
        print(f"[FALLBACK] Would have said: {text}")
        time.sleep(1)  # Still add pause for natural rhythm


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