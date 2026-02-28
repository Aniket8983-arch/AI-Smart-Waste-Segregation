import tensorflow as tf
import numpy as np
from PIL import Image

MODEL_PATH = "models/waste_model.h5"

model = tf.keras.models.load_model(MODEL_PATH)

def predict_image(image):

    IMG_SIZE = 224

    image = image.resize((IMG_SIZE, IMG_SIZE))
    img_array = np.array(image) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)[0][0]

    if prediction > 0.5:
        return "NONBIO", float(prediction)
    else:
        return "BIO", float(1 - prediction)