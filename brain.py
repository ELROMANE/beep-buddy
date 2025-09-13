# --- Import Necessary Libraries ---
import serial # For communicating with the Arduino
import time   # For adding small delays
import speech_recognition as sr # For listening to the microphone (pip install SpeechRecognition)
import cv2    # For capturing camera footage (pip install opencv-python)
import requests # For making the API call to Cerebras (pip install requests)
import subprocess # For using the macOS 'say' command for Text-to-Speech

# --- ARDUINO SETUP ---
# Establish a connection to the Arduino over USB.
# CRITICAL: You MUST find the correct serial port your Arduino is on.
# On macOS, it's usually something like '/dev/tty.usbmodemXXXX' or '/dev/tty.usbserial-XXXX'.
# Check in Arduino IDE: Tools > Port
arduino = serial.Serial('/dev/cu.usbmodem1101', 9600, timeout=1)
time.sleep(2) # Wait a moment for the connection to stabilize

# --- CEREBRAS API FUNCTION ---
def get_ai_response(user_prompt):
    """
    Sends a prompt to the Cerebras API and returns the generated text response.
    Replace 'YOUR_CEREBRAS_API_KEY' with your actual key.
    The structure of this request might need to change based on Cerebras's specific API format.
    """
    url = "https://api.cerebras.ai/v1/chat/completions" # Example endpoint, check Cerebras docs
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer "
    }
    data = {
        "model": "cerebras-model-name", # e.g., "llama-3-70b"
        "messages": [{"role": "user", "content": user_prompt}],
        "max_tokens": 100
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status() # Raises an error for bad status codes (4xx, 5xx)
        # Parse the JSON response to extract the AI's text
        ai_message = response.json()['choices'][0]['message']['content']
        return ai_message
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return "I'm having trouble thinking right now. Let's try again later!"

# --- SEND COMMAND TO ARDUINO ---
def send_arduino_command(command):
    """
    Sends a simple string command (e.g., "BEEP") to the Arduino over the serial connection.
    The Arduino code is waiting for these commands to trigger actions.
    """
    print(f"Sending to Arduino: {command}")
    arduino.write(f"{command}\n".encode()) # The '\n' is the "newline" character the Arduino reads with `readStringUntil('\n')`

# --- TEXT-TO-SPEECH FUNCTION ---
def speak(text):
    """
    Uses the built-in macOS 'say' command to speak the provided text aloud.
    You could also use a library like `pyttsx3` for more control.
    """
    print(f"AI says: {text}")
    subprocess.call(['say', text])

# --- SIMPLIFIED EMOTION/TONE DETECTION (HACKATHON MODE) ---
# In a real project, you'd use ML models. For a hackathon, we'll use simple inputs.

def detect_emotion_from_camera():
    """
    Placeholder for emotion detection.
    For a real demo, you could use a library like `deepface` or `fer`.
    For now, we'll just prompt the user in the terminal.
    """
    # cap = cv2.VideoCapture(0)
    # ret, frame = cap.read()
    # ... complex AI model code would go here ...
    # cap.release()
    # return "happy" # Placeholder

    emotion = input("Quick! How are you feeling? (happy/sad/surprised/angry): ").lower()
    return emotion

def detect_tone_from_microphone():
    """
    Placeholder for tone analysis.
    Real-world, you'd use speech-to-text and then analyze the text sentiment.
    For now, we'll just get text input.
    """
    # recognizer = sr.Recognizer()
    # with sr.Microphone() as source:
    #     print("Listening...")
    #     audio = recognizer.listen(source)
    #     text = recognizer.recognize_google(audio)
    # ... sentiment analysis on `text` ...
    # return "excited" # Placeholder

    user_text = input("What would you like to say to R2D2? ")
    return user_text

# --- MAIN DEMO LOOP ---
print("🤖 R2D2 AI Assistant is booting up!")
speak("Hello I am ready!")

try:
    while True:
        # 1. Get user input (simplified for the hackathon)
        input("\nPress Enter to start interaction...")

        # 2. "Detect" emotion from camera
        emotion = detect_emotion_from_camera()
        # 3. "Detect" tone/text from microphone
        user_speech = detect_tone_from_microphone()

        # 4. Craft a prompt for the AI based on the user's state
        prompt_for_ai = f"""
        You are a friendly, helpful, and funny droid like R2D2. Your partner is a human.
        My analysis shows the human is feeling {emotion}. They just said: "{user_speech}".
        Respond in a short, personal, and appropriate way. Crack a joke if they are happy, or give supportive advice if they are sad.
        Keep your response to one or two sentences.
        """
        print(f"\nSending to AI: {prompt_for_ai}")

        # 5. Get the AI's brilliant response
        ai_response = get_ai_response(prompt_for_ai)

        # 6. Have the Mac speak the response
        speak(ai_response)

        # 7. Command the Arduino body to react!
        #    Make it beep and tilt its head while speaking for a lively effect.
        send_arduino_command("BEEP")
        send_arduino_command("TILT")
        time.sleep(1) # Wait for actions to finish

        # Optional: Add some movement
        # send_arduino_command("FWD")
        # time.sleep(1)
        # send_arduino_command("STOP")

except KeyboardInterrupt:
    print("\nShutting down...")
finally:
    # Clean up the serial connection to avoid errors
    arduino.close()