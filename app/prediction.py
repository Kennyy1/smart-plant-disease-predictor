import shutil
import uuid
from pathlib import Path

from app.pipeline_utils import pipeline_decision

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "app" / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

RECOMMENDATIONS = {
    "Cassava__bacterial_blight": "Use clean planting materials, remove severely infected plants, and improve field sanitation.",
    "Cassava__brown_spot": "Monitor leaf spotting closely and keep the field weed-free to reduce stress on the crop.",
    "Cassava__green_mite": "Inspect the undersides of leaves and apply locally recommended mite control practices when infestation rises.",
    "Cassava__healthy": "The cassava leaf appears healthy. Continue routine monitoring and maintain good farm hygiene.",
    "Cassava__mosaic": "Rogue infected plants early and plant resistant cassava varieties in the next cycle when available.",
    "Corn_(maize)__fall_armyworm": "Scout the field quickly and apply integrated pest management measures before the infestation spreads.",
    "Corn_(maize)__grasshoper": "Check nearby plants for chewing damage and use approved control practices if the attack continues.",
    "Corn_(maize)__healthy": "The maize leaf appears healthy. Keep monitoring for early stress or pest signs.",
    "Corn_(maize)__leaf_beetle": "Watch for additional feeding damage and combine field sanitation with approved beetle control methods.",
    "Corn_(maize)__leaf_blight": "Remove heavily damaged leaves when practical and use resistant seed varieties in future planting seasons.",
    "Corn_(maize)__leaf_spot": "Reduce excess moisture around the crop and follow local extension guidance for leaf spot management.",
    "Corn_(maize)__streak_virus": "Control insect vectors, remove heavily infected plants, and prioritize resistant maize varieties.",
}


def save_upload(upload_file) -> tuple[Path, str]:
    file_ext = Path(upload_file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file type. Upload JPG, JPEG, or PNG.")

    unique_name = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_name

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return file_path, f"/static/uploads/{unique_name}"


def normalize_prediction_result(raw_result: dict, image_url: str) -> dict:
    status = raw_result.get("status", "Prediction unavailable")
    crop_name = raw_result.get("crop_prediction")
    disease_name = raw_result.get("predicted_class")
    confidence = raw_result.get("disease_confidence", raw_result.get("crop_confidence", 0.0))

    if status == "Plant data not detected":
        return {
            "status": "Rejected",
            "display_message": "Rejected: Non-plant image detected.",
            "crop_name": None,
            "disease_name": None,
            "confidence_score": raw_result.get("gate_confidence", 0.0),
            "recommendation": "Please upload a clear leaf image that contains a visible crop leaf.",
            "image_url": image_url,
            "raw_result": raw_result,
        }

    if status in {"Unknown crop detected", "Unsupported plant detected"}:
        return {
            "status": "Unsupported",
            "display_message": "Unsupported crop detected.",
            "crop_name": crop_name,
            "disease_name": None,
            "confidence_score": raw_result.get("crop_confidence", 0.0),
            "recommendation": "This system currently supports cassava and maize leaf disease detection only.",
            "image_url": image_url,
            "raw_result": raw_result,
        }

    recommendation = RECOMMENDATIONS.get(
        disease_name,
        "Review the leaf condition with an agronomy expert if symptoms persist in the field.",
    )
    return {
        "status": "Detected",
        "display_message": "Disease prediction completed successfully.",
        "crop_name": crop_name,
        "disease_name": disease_name,
        "confidence_score": confidence,
        "recommendation": recommendation,
        "image_url": image_url,
        "raw_result": raw_result,
    }


def run_prediction_pipeline(image_path: str, image_url: str) -> dict:
    raw_result = pipeline_decision(image_path)
    return normalize_prediction_result(raw_result, image_url)


def format_label(label: str | None) -> str:
    if not label:
        return "Not available"
    return label.replace("__", " - ").replace("_", " ")
