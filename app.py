import streamlit as st
import cv2
import numpy as np
from PIL import Image
from src.predict import predict_image
from src.serial_comm import send_to_esp32

st.set_page_config(page_title="AI Smart Waste Segregation", layout="centered")

st.title("♻ AI Smart Waste Segregation System")
st.markdown("### ML Powered + ESP32 Automated System")

option = st.radio(
    "Select Image Source:",
    ("Upload Image", "Use Camera")
)

image = None

# =========================================================
# UPLOAD IMAGE
# =========================================================
if option == "Upload Image":

    uploaded_file = st.file_uploader(
        "Upload Waste Image",
        type=["jpg", "png", "jpeg"]
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

# =========================================================
# CAMERA MODE
# =========================================================
elif option == "Use Camera":

    st.markdown("### Live Scanner Mode")
    st.info("Press 'c' to capture | Press 'q' to quit")

    if st.button("Start Camera"):

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            st.error("Unable to access camera")
        else:

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                height, width, _ = frame.shape

                square_size = min(height, width) // 2
                x1 = width // 2 - square_size // 2
                y1 = height // 2 - square_size // 2
                x2 = x1 + square_size
                y2 = y1 + square_size

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

                cv2.imshow("Smart Dustbin Scanner", frame)

                key = cv2.waitKey(1) & 0xFF

                if key == ord('c'):
                    cropped = frame[y1:y2, x1:x2]
                    image = Image.fromarray(
                        cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
                    )
                    break

                if key == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()

# =========================================================
# PREDICTION + HARDWARE
# =========================================================
if image is not None:

    st.image(image, caption="Scanned Region", width=300)

    with st.spinner("Scanning Waste..."):
        result, confidence = predict_image(image)

    st.success(f"Prediction: {result}")
    st.info(f"Confidence: {round(confidence * 100, 2)}%")

    sent = send_to_esp32(result)

    if sent:
        st.success("Command sent to ESP32 successfully!")
    else:
        st.error("ESP32 not connected or label mismatch!")
