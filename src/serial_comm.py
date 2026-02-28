import serial
import time

SERIAL_PORT = "COM4"   # change to your port
BAUD_RATE = 115200

# Create global connection
arduino = None

def get_connection():
    global arduino
    if arduino is None or not arduino.is_open:
        arduino = serial.Serial(SERIAL_PORT, BAUD_RATE)
        time.sleep(2)  # wait for ESP32 reset
    return arduino

def send_to_esp32(label):
    try:
        arduino = get_connection()

        if label == "BIO":
            arduino.write(b'B')
        elif label == "NONBIO":
            arduino.write(b'N')

        arduino.flush()
        time.sleep(0.5)   # IMPORTANT delay

        return True

    except Exception as e:
        print("Serial error:", e)
        return False