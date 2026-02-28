from src.predict import predict_image
from PIL import Image

img = Image.open("dataset/biodegradable/O_1.jpg")

result, confidence = predict_image(img)

print("Prediction:", result)
print("Confidence:", confidence)