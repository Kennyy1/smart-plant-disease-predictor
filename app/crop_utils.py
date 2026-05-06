import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"

CROP_MODEL_PATH = MODELS_DIR / "enh_crop_gate_final_model_v1.keras"
CROP_CLASS_NAMES_PATH = MODELS_DIR / "enh_crop_gate_class_names_v1.json"

crop_model = tf.keras.models.load_model(CROP_MODEL_PATH)

with open(CROP_CLASS_NAMES_PATH, "r") as f:
    crop_classes = json.load(f)


def predict_crop(img_path: str, img_size=(260, 260)):
    img = image.load_img(img_path, target_size=img_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)

    preds = crop_model.predict(img_array, verbose=0)[0]

    top_idx = int(np.argmax(preds))
    confidence = float(preds[top_idx])
    label = crop_classes[top_idx]

    return {
        "crop_prediction": label,
        "crop_confidence": round(confidence, 4)
    }