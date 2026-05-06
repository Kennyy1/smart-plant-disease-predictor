import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"

# Load models
cassava_model = tf.keras.models.load_model(MODELS_DIR / "cassava_final_model_v1.keras")
maize_model = tf.keras.models.load_model(MODELS_DIR / "maize_final_model_v1.keras")

# Load class names
with open(MODELS_DIR / "cassava_class_names_v1.json", "r") as f:
    cassava_classes = json.load(f)

with open(MODELS_DIR / "maize_class_names_v1.json", "r") as f:
    maize_classes = json.load(f)


def preprocess(img_path: str, img_size=(260, 260)):
    img = image.load_img(img_path, target_size=img_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


def predict_disease(img_path: str, crop_label: str):
    x = preprocess(img_path)

    if crop_label == "Cassava":
        preds = cassava_model.predict(x, verbose=0)[0]
        idx = int(np.argmax(preds))
        confidence = float(preds[idx])
        return {
            "predicted_class": cassava_classes[idx],
            "disease_confidence": round(confidence, 4)
        }

    if crop_label == "Maize":
        preds = maize_model.predict(x, verbose=0)[0]
        idx = int(np.argmax(preds))
        confidence = float(preds[idx])
        return {
            "predicted_class": maize_classes[idx],
            "disease_confidence": round(confidence, 4)
        }

    return {
        "predicted_class": None,
        "disease_confidence": 0.0
    }