import serial, time

ARDUINO_PORT = '/dev/ttyACM0'  # Update this to your Arduino port
BAUD_RATE = 9600

def send_command(command):
    try:
        with serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout = 1) as ser:
            ser.write(command.encode())
            time.sleep(2)  # wait for the command to be processed
    except Exception as e:
        print(f"Error communicating with Arduino: {e}")

def tilt_head():
    send_command('TILT\n')

def beep():
    send_command('BEEP\n')