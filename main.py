# the main code for R2D2

# File imports
from cerebras_api import ask_prompt
from speech_utils import listen_here, speak_here, play_sound
import movement_sim as r2

# library imports
import cv2
import time
import numpy as np
import json
import os
from datetime import datetime
import threading
import pygame
import random

# Initialize pygame mixer for music
pygame.mixer.init()

# Global conversation history
conversation_history = []
MAX_CONVERSATION_LENGTH = 100

# Encouragement messages
ENCOURAGEMENT_MESSAGES = [
    "Hey, I can see you might be feeling down. Remember, you're amazing and things will get better!",
    "I notice you look a bit sad. You know what? You're stronger than you think, and I believe in you!",
    "Cheer up! Every day is a new opportunity, and you have so much to offer the world!",
    "I can see something's bothering you. Remember, it's okay to feel sad sometimes - you're human and that's beautiful!",
    "You look like you need a smile today. Here's a virtual hug from your robotic friend who cares about you!",
    "Hey there, I see that expression. Just remember - storms don't last forever, but strong people like you do!",
    "Looking a bit blue? That's totally okay! Want to talk about it, or should I tell you a joke instead?",
    "I can sense you're not feeling your best. Just know that you matter, you're valued, and tomorrow is full of possibilities!"
]

def save_conversation(user_input, bot_response):
    """Save conversation to history and file"""
    global conversation_history
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conversation_entry = {
        "timestamp": timestamp,
        "user": user_input,
        "bot": bot_response
    }
    
    conversation_history.append(conversation_entry)
    
    # Keep only last 100 conversations
    if len(conversation_history) > MAX_CONVERSATION_LENGTH:
        conversation_history = conversation_history[-MAX_CONVERSATION_LENGTH:]
    
    # Save to file
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/conversation_history.json", "w") as f:
            json.dump(conversation_history, f, indent=2)
        print(f"[DEBUG] Conversation saved. Total entries: {len(conversation_history)}")
    except Exception as e:
        print(f"[ERROR] Could not save conversation: {e}")

def load_conversation_history():
    """Load conversation history from file"""
    global conversation_history
    try:
        if os.path.exists("data/conversation_history.json"):
            with open("data/conversation_history.json", "r") as f:
                conversation_history = json.load(f)
            print(f"[INFO] Loaded {len(conversation_history)} previous conversations")
    except Exception as e:
        print(f"[ERROR] Could not load conversation history: {e}")
        conversation_history = []

def is_arduino_connected():
    try:
        import serial
        from movement_sim import ARDUINO_PORT, BAUD_RATE
        ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
        ser.close()
        return True
    except Exception:
        return False

def analyze_emotion(text):
    prompt = (
        "Read the following message and respond with ONLY ONE WORD from this list: happy, sad, excited, angry, neutral. "
        "No explanation, no punctuation, just the word. Message: '" + text + "'"
    )
    emotion = ask_prompt(prompt).strip().lower()
    allowed = {"happy", "sad", "excited", "angry", "neutral"}
    # Fallback to neutral if not recognized
    if emotion not in allowed:
        return "neutral"
    return emotion

def detect_facial_emotion(frame):
    """Detect facial emotion using OpenCV and basic analysis"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Load face and smile cascades
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return "no_face_detected"
        
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            
            # Detect smiles
            smiles = smile_cascade.detectMultiScale(roi_gray, 1.8, 20)
            eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 5)
            
            # Simple emotion detection logic
            if len(smiles) > 0:
                return "happy"
            elif len(eyes) < 2:  # Might indicate squinting/sadness
                return "sad"
            else:
                # Analyze brightness in mouth region (bottom third of face)
                mouth_region = roi_gray[int(h*0.6):h, :]
                mouth_brightness = np.mean(mouth_region)
                
                # If mouth region is darker (downturned), might be sad
                if mouth_brightness < np.mean(roi_gray) * 0.9:
                    return "sad"
                else:
                    return "neutral"
        
        return "neutral"
    except Exception as e:
        print(f"[ERROR] Facial emotion detection failed: {e}")
        return "unknown"

def analyze_face_and_lighting():
    cap = None
    try:
        # Try different camera indices
        for i in range(3):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"[INFO] Camera found at index {i}")
                break
            cap.release()
        
        if not cap or not cap.isOpened():
            print("[WARN] No camera could be opened for analysis.")
            return None, None, "no_camera"
        
        # Give camera time to initialize
        time.sleep(1)
        
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Could not read frame from camera.")
            return None, None, "no_frame"
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        avg_brightness = np.mean(gray)
        
        # Haar cascade for face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        face_detected = len(faces) > 0
        
        # Detect facial emotion
        facial_emotion = detect_facial_emotion(frame) if face_detected else "no_face"
        
        return avg_brightness, face_detected, facial_emotion
        
    except Exception as e:
        print(f"[ERROR] Camera analysis failed: {e}")
        return None, None, "error"
    finally:
        if cap:
            cap.release()

def continuous_emotion_monitoring():
    """Background thread to monitor facial expressions"""
    global emotion_check_active
    cap = None
    
    try:
        # Find available camera
        for i in range(3):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                break
            cap.release()
        
        if not cap or not cap.isOpened():
            print("[WARN] Cannot start emotion monitoring - no camera available")
            return
        
        last_encouragement_time = 0
        encouragement_cooldown = 30  # 30 seconds between encouragements
        
        while emotion_check_active:
            ret, frame = cap.read()
            if ret:
                emotion = detect_facial_emotion(frame)
                current_time = time.time()
                
                if (emotion == "sad" and 
                    current_time - last_encouragement_time > encouragement_cooldown):
                    
                    encouragement = random.choice(ENCOURAGEMENT_MESSAGES)
                    print(f"[EMOTION] Detected sadness - offering encouragement")
                    speak_here(encouragement)
                    last_encouragement_time = current_time
            
            time.sleep(2)  # Check every 2 seconds
            
    except Exception as e:
        print(f"[ERROR] Emotion monitoring error: {e}")
    finally:
        if cap:
            cap.release()

def play_music():
    """Play music from assets/music folder"""
    try:
        music_folder = "assets/music"
        if not os.path.exists(music_folder):
            speak_here("Sorry, I don't have any music files available.")
            return
        
        music_files = [f for f in os.listdir(music_folder) 
                        if f.lower().endswith(('.mp3', '.wav', '.ogg'))]
        
        if not music_files:
            speak_here("I found the music folder but there are no music files in it.")
            return
        
        # Choose random song
        song = random.choice(music_files)
        song_path = os.path.join(music_folder, song)
        
        speak_here(f"Playing {song.replace('_', ' ').replace('.mp3', '').replace('.wav', '')}")
        
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        
        print(f"[MUSIC] Now playing: {song}")
        print("[MUSIC] Say 'stop music' to stop playback")
        
    except Exception as e:
        print(f"[ERROR] Music playback error: {e}")
        speak_here("Sorry, I couldn't play music right now.")

def stop_music():
    """Stop music playback"""
    try:
        pygame.mixer.music.stop()
        speak_here("Music stopped.")
        print("[MUSIC] Playback stopped")
    except Exception as e:
        print(f"[ERROR] Could not stop music: {e}")

def speak_long_text(text, max_chunk_size=100):
    """Break long text into smaller chunks and speak them"""
    if not text:
        return
    
    words = text.split()
    if len(words) <= max_chunk_size:
        speak_here(text)
        return
    
    # Break into chunks
    chunks = []
    current_chunk = []
    
    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= max_chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
    
    # Add remaining words
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    # Speak each chunk
    for i, chunk in enumerate(chunks):
        if i > 0:
            speak_here("Continuing...")
            time.sleep(0.5)
        speak_here(chunk)
        time.sleep(1)  # Pause between chunks

def get_all_commands():
    """Return a comprehensive list of all available commands"""
    commands = [
        "'Hello' - Wake me up when I'm sleeping",
        "'Help' - List all available commands",
        "'Tired' - Put me to sleep mode",
        "'Quit', 'Bye', or 'Goodbye' - Exit the program",
        "'Open camera' - Show camera view and analyze lighting",
        "'Quiz me' - Start a fun quiz session",
        "'Play music' or 'Play song' - Play a random song",
        "'Stop music' - Stop current music playback",
        "'What time is it' - Get the current time",
        "'Show history' - Display recent conversation history",
        "'Clear history' - Clear the conversation history",
        "Or just talk to me normally - I'll respond to any conversation!"
    ]
    return commands

def main():
    global emotion_check_active
    emotion_check_active = True
    
    # Load previous conversations
    load_conversation_history()
    
    arduino_connected = is_arduino_connected()
    intro_message = "Hey, wassup! I'm your enhanced R2D2 assistant with conversation memory and emotion detection!"
    speak_here(intro_message)
    print("[R2D2] Enhanced Assistant started. Say 'hello' to wake me up! (Ctrl+C to exit)")
    print(intro_message)
    awake = not arduino_connected  # If no Arduino, start awake
    
    # Start emotion monitoring in background
    emotion_thread = threading.Thread(target=continuous_emotion_monitoring, daemon=True)
    emotion_thread.start()
    
    try:
        while True:
            if not awake:
                print("[INFO] Waiting for wake word 'hello'...")
                try:
                    play_sound("assets/sounds/listening.wav")
                except Exception as e:
                    print(f"[WARN] Could not play listening sound: {e}")
                
                user_input = listen_here()
                print(f"[DEBUG] Sleep mode - Heard: '{user_input}'")
                
                if user_input and "hello" in user_input.lower():
                    awake = True
                    try:
                        play_sound("assets/sounds/lala.wav")
                    except Exception as e:
                        print(f"[WARN] Wake sound missing: {e}")
                    wake_message = "Yo, I'm awake and ready to chat!"
                    print(wake_message)
                    speak_here(wake_message)
                    if arduino_connected:
                        r2.beep()
                        r2.tilt_head()
                continue

            print("[INFO] Listening for command...")
            try:
                play_sound("assets/sounds/listening.wav")
            except Exception as e:
                print(f"[WARN] Could not play listening sound: {e}")
            
            user_input = listen_here()
            print(f"[DEBUG] Awake mode - Heard: '{user_input}'")
            
            if not user_input or user_input.strip() == "":
                speak_here("I didn't catch that. Could you repeat?")
                continue

            user_lower = user_input.lower()

            # Help command - show all commands
            if "help" in user_lower:
                commands = get_all_commands()
                help_msg = "Here are all my available commands: "
                speak_here(help_msg)
                
                for i, command in enumerate(commands, 1):
                    command_msg = f"Command {i}: {command}"
                    print(command_msg)
                    speak_here(command_msg)
                    time.sleep(0.5)  # Small pause between commands
                
                save_conversation(user_input, "Listed all available commands")
                continue

            # Sleep command
            if "tired" in user_lower:
                try:
                    play_sound("assets/sounds/lala.wav")
                except Exception as e:
                    print(f"[WARN] Tired sound missing: {e}")
                response = "I'm tired. Going to sleep. Say hello to wake me up!"
                speak_here(response)
                save_conversation(user_input, response)
                if arduino_connected:
                    r2.beep()
                awake = False
                continue

            # Exit commands
            if any(word in user_lower for word in ["shutup", "shut up", "quit", "bye", "goodbye"]):
                response = "Goodbye! Thanks for chatting with me. See you soon!"
                speak_here(response)
                save_conversation(user_input, response)
                break

            # Music commands
            if "play music" in user_lower or "play song" in user_lower:
                play_music()
                save_conversation(user_input, "Started playing music")
                continue

            if "stop music" in user_lower:
                stop_music()
                save_conversation(user_input, "Stopped music playback")
                continue

            # Quiz command
            if "quizme" in user_lower or "quiz me" in user_lower:
                try:
                    print("[INFO] Generating quiz question...")
                    quiz_prompt = "Generate a fun, simple quiz question for a child. Only give the question, not the answer."
                    quiz_question = ask_prompt(quiz_prompt)
                    print("Quiz question:", quiz_question)
                    speak_here(quiz_question)
                    
                    print("[INFO] Waiting for answer...")
                    user_answer = listen_here()
                    if not user_answer:
                        response = "I didn't hear your answer. Let's try again later!"
                        speak_here(response)
                        save_conversation(user_input, response)
                        continue
                    
                    print(f"[DEBUG] User answered: {user_answer}")
                    check_prompt = f"The question was: '{quiz_question}'. The answer given was: '{user_answer}'. Is this correct? Reply only with 'yes' or 'no'."
                    check_result = ask_prompt(check_prompt).strip().lower()
                    
                    if check_result.startswith("yes"):
                        response = "Awesome! You got it right!"
                        speak_here(response)
                        try:
                            play_sound("assets/sounds/lala.wav")
                        except Exception as e:
                            print(f"[WARN] Success sound missing: {e}")
                    else:
                        response = "Nice try! Want to try another one later?"
                        speak_here(response)
                    
                    save_conversation(f"Quiz: {quiz_question} | Answer: {user_answer}", response)
                except Exception as e:
                    print(f"[ERROR] Quiz error: {e}")
                    response = "Sorry, I couldn't do a quiz right now."
                    speak_here(response)
                    save_conversation(user_input, response)
                continue

            # Camera command with emotion detection
            if "opencamera" in user_lower or "open camera" in user_lower:
                print("[INFO] Opening camera with emotion detection...")
                avg_brightness, face_detected, facial_emotion = analyze_face_and_lighting()
                
                response_parts = []
                
                if avg_brightness is not None:
                    print(f"[DEBUG] Average brightness: {avg_brightness:.2f}")
                    if avg_brightness < 60:
                        response_parts.append("Warning: The lighting is dim. Please turn on a light or move to a brighter area.")
                
                if face_detected:
                    if facial_emotion == "sad":
                        encouragement = random.choice(ENCOURAGEMENT_MESSAGES)
                        response_parts.append(f"I can see you, and I noticed you might be feeling down. {encouragement}")
                    elif facial_emotion == "happy":
                        response_parts.append("I can see you're smiling! That makes me happy too!")
                    else:
                        response_parts.append("I can see you! Looking good!")
                elif face_detected is not None:
                    response_parts.append("I can't see your face clearly. Please make sure you are in front of the camera.")

                # Show camera feed
                cap = None
                try:
                    for i in range(3):
                        cap = cv2.VideoCapture(i)
                        if cap.isOpened():
                            break
                        cap.release()
                    
                    if cap and cap.isOpened():
                        time.sleep(1)
                        ret, frame = cap.read()
                        if ret:
                            cv2.imshow('R2D2 Camera View - Press any key to close', frame)
                            response_parts.append("Camera opened! Press any key to close the window.")
                            cv2.waitKey(0)
                            cv2.destroyAllWindows()
                        else:
                            response_parts.append("Camera opened but couldn't capture image.")
                    else:
                        response_parts.append("Sorry, I cannot access the camera right now.")
                except Exception as e:
                    print(f"[ERROR] Camera error: {e}")
                    response_parts.append("There was an error with the camera.")
                finally:
                    if cap:
                        cap.release()
                    cv2.destroyAllWindows()
                
                full_response = " ".join(response_parts)
                speak_long_text(full_response)
                save_conversation(user_input, full_response)
                continue

            # Time command
            if "time" in user_lower:
                current_time = time.strftime('%I:%M %p')
                response = f"The current time is {current_time}."
                speak_here(response)
                save_conversation(user_input, response)
                continue

            # Conversation history commands
            if "show history" in user_lower or "conversation history" in user_lower:
                if not conversation_history:
                    response = "I don't have any conversation history yet."
                    speak_here(response)
                else:
                    response = f"I have {len(conversation_history)} conversations in my memory. Here are the last 3:"
                    speak_here(response)
                    for conv in conversation_history[-3:]:
                        speak_here(f"You said: {conv['user'][:50]}... I replied: {conv['bot'][:50]}...")
                        time.sleep(1)
                save_conversation(user_input, response)
                continue

            if "clear history" in user_lower:
                conversation_history.clear()
                try:
                    with open("data/conversation_history.json", "w") as f:
                        json.dump([], f)
                except:
                    pass
                response = "I've cleared my conversation history."
                speak_here(response)
                save_conversation(user_input, response)
                continue

            # Handle general conversation
            try:
                print("[INFO] Getting AI response...")
                
                # Include recent conversation context
                context = ""
                if len(conversation_history) > 0:
                    recent_convs = conversation_history[-3:]  # Last 3 conversations
                    context = "Recent conversation context: "
                    for conv in recent_convs:
                        context += f"User: {conv['user']} | Bot: {conv['bot']} | "
                    context += f"Current user input: {user_input}"
                else:
                    context = user_input
                
                r2_reply = ask_prompt(context)
                print("R2D2:", r2_reply)
                
                if not r2_reply.strip():
                    r2_reply = "Sorry, I didn't get that."
                
                # Use the enhanced speaking function for long responses
                speak_long_text(r2_reply, max_chunk_size=80)
                
                # Save conversation
                save_conversation(user_input, r2_reply)
                
                # Dynamic delay based on response length
                word_count = len(r2_reply.split())
                delay = min(max(word_count * 0.1, 0.5), 3)
                time.sleep(delay)
                
            except Exception as e:
                print(f"[ERROR] Error with AI response: {e}")
                response = "Sorry, I couldn't process that right now. Try again!"
                speak_here(response)
                save_conversation(user_input, response)
                continue
                
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n[R2D2] Shutting down. Goodbye!")
        emotion_check_active = False
        final_message = "Goodbye! Thanks for all our conversations!"
        speak_here(final_message)
        save_conversation("System shutdown", final_message)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        emotion_check_active = False
        speak_here("Something went wrong. Shutting down.")
    finally:
        emotion_check_active = False
        pygame.mixer.quit()


if __name__ == "__main__":
    main()