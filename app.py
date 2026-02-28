import streamlit as st
import cv2
import os
import csv
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from PIL import Image
from src.predict import predict_image
from src.serial_comm import send_to_esp32

# =========================================================
# CONFIGURATION
# =========================================================
BIO_CAPACITY = 10
NONBIO_CAPACITY = 10

SENDER_EMAIL = "aniketpatil8149@gmail.com"
SENDER_PASSWORD = ""  # Gmail App Password
MANAGER_EMAIL = "manager_email@gmail.com"

st.set_page_config(page_title="Smart Dustbin", layout="centered")

# =========================================================
# EMAIL FUNCTION
# =========================================================
def notify_manager(bin_type):
    try:
        subject = f"🚛 {bin_type} Bin Full - Collection Required"
        body = f"""
        Smart Dustbin Alert

        The {bin_type} bin has reached full capacity.

        Immediate pickup required.

        Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = MANAGER_EMAIL

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, MANAGER_EMAIL, msg.as_string())
        server.quit()

        return True
    except Exception as e:
        print("Email Error:", e)
        return False

# =========================================================
# LOGGING FUNCTION
# =========================================================
def log_data(result):
    file_exists = os.path.isfile("waste_log.csv")

    with open("waste_log.csv", mode="a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["Timestamp", "Waste Type"])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            result
        ])

# =========================================================
# SESSION STATE
# =========================================================
if "bio_count" not in st.session_state:
    st.session_state.bio_count = 0

if "nonbio_count" not in st.session_state:
    st.session_state.nonbio_count = 0

if "points" not in st.session_state:
    st.session_state.points = 0

if "total_scans" not in st.session_state:
    st.session_state.total_scans = 0

# =========================================================
# UI HEADER
# =========================================================
st.title("♻ AI Smart Waste Segregation & Collection System")
st.markdown("Segregation + Predictive Collection Monitoring")

option = st.radio(
    "Select Image Source:",
    ("Upload Image", "Use Camera"),
    horizontal=True
)

image = None

# =========================================================
# UPLOAD MODE
# =========================================================
if option == "Upload Image":

    uploaded_file = st.file_uploader(
        "Upload Waste Image",
        type=["jpg", "png", "jpeg"]
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True)

# =========================================================
# CAMERA MODE
# =========================================================
elif option == "Use Camera":

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
# PREDICTION
# =========================================================
if image is not None:

    with st.spinner("Scanning Waste..."):
        result, confidence = predict_image(image)

    send_to_esp32(result)

    st.session_state.total_scans += 1
    log_data(result)

    if result == "BIO":
        st.session_state.bio_count += 1
        st.session_state.points += 10
        st.success(f"♻ BIODEGRADABLE | Confidence: {round(confidence*100,2)}%")
    else:
        st.session_state.nonbio_count += 1
        st.session_state.points += 5
        st.error(f"🗑 NON-BIODEGRADABLE | Confidence: {round(confidence*100,2)}%")

# =========================================================
# DASHBOARD
# =========================================================
st.markdown("---")
st.markdown("## 📊 Segregation Dashboard")

col1, col2 = st.columns(2)
col1.metric("♻ BIO Count", st.session_state.bio_count)
col2.metric("🗑 NONBIO Count", st.session_state.nonbio_count)

st.markdown("### 🏆 Reward Points")
st.metric("🌟 Points", st.session_state.points)

# =========================================================
# COLLECTION STATUS (10 FLAPS EACH SIDE)
# =========================================================
st.markdown("---")
st.markdown("## 🚛 Collection Status")

bio_fill = (st.session_state.bio_count / BIO_CAPACITY) * 100
nonbio_fill = (st.session_state.nonbio_count / NONBIO_CAPACITY) * 100

if bio_fill > 100:
    bio_fill = 100
if nonbio_fill > 100:
    nonbio_fill = 100

st.markdown("### ♻ BIO Bin Fill")
st.progress(int(bio_fill))
st.write(f"{round(bio_fill,1)}% full")

if bio_fill >= 100:
    st.error("🚛 BIO Bin Full!")
    if notify_manager("BIO"):
        st.success("📧 Manager Notified")

st.markdown("### 🗑 NONBIO Bin Fill")
st.progress(int(nonbio_fill))
st.write(f"{round(nonbio_fill,1)}% full")

if nonbio_fill >= 100:
    st.error("🚛 NONBIO Bin Full!")
    if notify_manager("NONBIO"):
        st.success("📧 Manager Notified")

st.write("Last Updated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))