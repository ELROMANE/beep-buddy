import serial
import time

ARDUINO_PORT = '/dev/tty.usbmodem1101'  # Update this to your Arduino's port
BAUD_RATE = 9600
ser = None  # Global serial connection

def init_serial():
    """Open or re-open serial connection safely."""
    global ser
    try:
        # If already open, reuse it
        if ser and ser.is_open:
            return ser

        # Otherwise try opening a new one
        ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Let Arduino reset after opening port
        print(f"[OK] Connected to Arduino on {ARDUINO_PORT}")
        return ser

    except serial.SerialException as e:
        print(f"[ERROR] Could not open serial port {ARDUINO_PORT}: {e}")
        ser = None
        return None


def send_command(cmd):
    """Send a single-character command to Arduino, with auto-reconnect."""
    s = init_serial()
    if not s:
        print("[ERROR] Serial not connected.")
        return

    try:
        s.write(cmd.encode())
    except serial.SerialException as e:
        print(f"[ERROR] Write failed: {e}. Attempting reconnect...")
        # Close and retry once
        try:
            s.close()
        except:
            pass
        time.sleep(1)
        init_serial()
        if ser:
            ser.write(cmd.encode())


# === Servo Control Commands ===
def tilt_head():
    send_command('T')

def look_left():
    send_command('L')

def look_right():
    send_command('R')

def neutral():
    send_command('S')

def beep():
    send_command('B')
