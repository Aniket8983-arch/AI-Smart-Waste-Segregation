import serial
import time

SERIAL_PORT = "COM4"   # Change if needed
BAUD_RATE = 115200

arduino = None

def get_connection():
    global arduino
    if arduino is None or not arduino.is_open:
        arduino = serial.Serial(SERIAL_PORT, BAUD_RATE)
        time.sleep(2)  # Wait for ESP32 reset
        print("Connected to ESP32 on", SERIAL_PORT)
    return arduino


def send_to_esp32(label):
    try:
        arduino = get_connection()

        print("Prediction label received:", label)

        label = label.lower()

        # BIO case
        if "bio" in label and "non" not in label:
            print("Sending B to ESP32")
            arduino.write(b'B')

        # NON-BIO case
        elif "non" in label:
            print("Sending N to ESP32")
            arduino.write(b'N')

        else:
            print("Unknown label. Nothing sent.")
            return False

        arduino.flush()
        time.sleep(0.5)

        return True

    except Exception as e:
        print("Serial error:", e)
        return False
