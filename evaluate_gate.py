from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    ConfusionMatrixDisplay,
)

# =========================
# Paths
# =========================
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
TEST_DIR = BASE_DIR / "gate_test_data"
OUTPUT_DIR = BASE_DIR / "evaluation_outputs" / "gate"

MODEL_PATH = MODELS_DIR / "gate_best_model_v2.keras"
CLASS_JSON = MODELS_DIR / "gate_class_names_v2.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# Load model
# =========================
model = tf.keras.models.load_model(MODEL_PATH)

# =========================
# Load class names JSON
# =========================
with open(CLASS_JSON, "r") as f:
    class_names_json = json.load(f)

print("Loaded class names from JSON:", class_names_json)

# =========================
# Dataset settings
# =========================
img_size = (192, 192)   # change only if your gate model used another size
batch_size = 32

test_ds = tf.keras.utils.image_dataset_from_directory(
    TEST_DIR,
    labels="inferred",
    label_mode="int",
    image_size=img_size,
    batch_size=batch_size,
    shuffle=False,
)

dataset_class_names = test_ds.class_names
print("Dataset class names:", dataset_class_names)

# =========================
# Collect true labels
# =========================
y_true = np.concatenate([y.numpy() for _, y in test_ds])

# =========================
# Predict
# =========================
y_prob = model.predict(test_ds, verbose=1).ravel()
y_pred = (y_prob >= 0.5).astype(int)

# =========================
# Metrics
# =========================
acc = accuracy_score(y_true, y_pred)
prec = precision_score(y_true, y_pred, average="binary", zero_division=0)
rec = recall_score(y_true, y_pred, average="binary", zero_division=0)
f1 = f1_score(y_true, y_pred, average="binary", zero_division=0)

report = classification_report(
    y_true,
    y_pred,
    target_names=dataset_class_names,
    zero_division=0
)

print("\n=== GATE MODEL METRICS ===")
print(f"Accuracy : {acc:.4f}")
print(f"Precision: {prec:.4f}")
print(f"Recall   : {rec:.4f}")
print(f"F1-score : {f1:.4f}")
print("\nClassification Report:\n")
print(report)

# =========================
# Save metrics as TXT
# =========================
metrics_txt_path = OUTPUT_DIR / "gate_metrics_report.txt"
with open(metrics_txt_path, "w") as f:
    f.write("=== GATE MODEL METRICS ===\n")
    f.write(f"Accuracy : {acc:.4f}\n")
    f.write(f"Precision: {prec:.4f}\n")
    f.write(f"Recall   : {rec:.4f}\n")
    f.write(f"F1-score : {f1:.4f}\n\n")
    f.write("=== CLASSIFICATION REPORT ===\n")
    f.write(report)

# =========================
# Save confusion matrix
# =========================
cm = confusion_matrix(y_true, y_pred)

fig, ax = plt.subplots(figsize=(6, 6))
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=dataset_class_names)
disp.plot(ax=ax, values_format="d")
ax.set_title("Gate Model Confusion Matrix")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "gate_confusion_matrix.png", dpi=300, bbox_inches="tight")
plt.close()

# =========================
# Save metrics summary as image
# =========================
fig, ax = plt.subplots(figsize=(8, 4))
ax.axis("off")

metrics_text = (
    "Gate Model Evaluation Metrics\n\n"
    f"Accuracy : {acc:.4f}\n"
    f"Precision: {prec:.4f}\n"
    f"Recall   : {rec:.4f}\n"
    f"F1-score : {f1:.4f}\n"
)

ax.text(
    0.05, 0.95,
    metrics_text,
    fontsize=14,
    va="top",
    ha="left"
)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "gate_metrics_summary.png", dpi=300, bbox_inches="tight")
plt.close()

print(f"\nSaved text report to: {metrics_txt_path}")
print(f"Saved confusion matrix image to: {OUTPUT_DIR / 'gate_confusion_matrix.png'}")
print(f"Saved metrics summary image to: {OUTPUT_DIR / 'gate_metrics_summary.png'}")