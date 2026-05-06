from app.gate_utils import gate_decision
from app.crop_utils import predict_crop
from app.disease_utils import predict_disease


def pipeline_decision(img_path: str, gate_threshold=0.5, crop_threshold=0.8):
    gate_result = gate_decision(img_path, threshold=gate_threshold)

    if gate_result["status"] != "Plant detected":
        return gate_result

    crop_result = predict_crop(img_path)

    final_result = {
        **gate_result,
        **crop_result
    }

    crop_label = crop_result["crop_prediction"]
    crop_confidence = crop_result["crop_confidence"]

    # Stop if crop prediction confidence is too low
    if crop_confidence < crop_threshold:
        final_result["status"] = "Unknown crop detected"
        final_result["message"] = "Low confidence in crop classification. Prediction aborted."
        return final_result

    # Stop if crop is not one of the supported disease classes
    if crop_label not in ["Cassava", "Maize"]:
        final_result["status"] = "Unsupported plant detected"
        final_result["message"] = f"{crop_label} detected, but no disease model is available."
        return final_result

    disease_result = predict_disease(img_path, crop_label)

    final_result.update(disease_result)
    final_result["status"] = "Detected"
    final_result["message"] = f"{crop_label} disease classification completed."

    return final_result