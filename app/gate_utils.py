import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"

GATE_MODEL_PATH = MODELS_DIR / "gate_best_model_v2.keras"
GATE_CLASS_NAMES_PATH = MODELS_DIR / "gate_class_names_v2.json"

gate_model = tf.keras.models.load_model(GATE_MODEL_PATH)

with open(GATE_CLASS_NAMES_PATH, "r") as f:
    gate_class_names = json.load(f)


def predict_gate(img_path: str, img_size=(192, 192), threshold=0.5):
    img = image.load_img(img_path, target_size=img_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)

    prob_plant = float(gate_model.predict(img_array, verbose=0)[0][0])

    pred_label = "plant" if prob_plant >= threshold else "nonplant"
    confidence = prob_plant if pred_label == "plant" else (1 - prob_plant)

    return {
        "predicted_label": pred_label,
        "confidence": round(confidence, 4),
        "plant_probability": round(prob_plant, 4),
        "nonplant_probability": round(1 - prob_plant, 4)
    }


def gate_decision(img_path: str, threshold=0.5):
    result = predict_gate(img_path, threshold=threshold)

    if result["predicted_label"] == "nonplant":
        return {
            "status": "Plant data not detected",
            "gate_prediction": result["predicted_label"],
            "gate_confidence": result["confidence"],
            "plant_probability": result["plant_probability"],
            "nonplant_probability": result["nonplant_probability"]
        }

    return {
        "status": "Plant detected",
        "gate_prediction": result["predicted_label"],
        "gate_confidence": result["confidence"],
        "plant_probability": result["plant_probability"],
        "nonplant_probability": result["nonplant_probability"]
    }