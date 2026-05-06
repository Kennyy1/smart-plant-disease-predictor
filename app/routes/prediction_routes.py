from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import add_flash_message, get_current_user, pop_flash_messages
from app.database import get_db
from app.models import PredictionHistory
from app.prediction import ALLOWED_EXTENSIONS, format_label, run_prediction_pipeline, save_upload

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/detect")
def upload_page(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if current_user is None:
        add_flash_message(request, "warning", "Please log in to make a prediction.")
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="upload.html",
        context={
            "request": request,
            "current_user": current_user,
            "page_title": "Upload Leaf Image",
            "flashes": pop_flash_messages(request),
        },
    )


@router.post("/detect")
async def detect(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    current_user = get_current_user(request, db)
    if current_user is None:
        add_flash_message(request, "warning", "Please log in to make a prediction.")
        return RedirectResponse(url="/login", status_code=303)

    if not file.filename:
        add_flash_message(request, "danger", "Please select an image before submitting.")
        return RedirectResponse(url="/detect", status_code=303)

    try:
        saved_path, image_url = save_upload(file)
        result = run_prediction_pipeline(str(saved_path), image_url)

        if result["status"] == "Detected":
            history = PredictionHistory(
                user_id=current_user.id,
                image_path=image_url,
                crop_name=result["crop_name"],
                disease_name=result["disease_name"],
                confidence_score=result["confidence_score"],
                result_status=result["status"],
                recommendation=result["recommendation"],
            )
            db.add(history)
            db.commit()
            db.refresh(history)
        else:
            history = None

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,
                "current_user": current_user,
                "page_title": "Prediction Result",
                "flashes": pop_flash_messages(request),
                "result": result,
                "history_item": history,
                "format_label": format_label,
            },
        )
    except ValueError as exc:
        add_flash_message(request, "danger", str(exc))
        return RedirectResponse(url="/detect", status_code=303)
    finally:
        await file.close()


@router.post("/predict")
async def predict_api(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload JPG, JPEG, or PNG.")

    try:
        saved_path, image_url = save_upload(file)
        return run_prediction_pipeline(str(saved_path), image_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(exc)}") from exc
    finally:
        await file.close()


@router.get("/history")
def history_page(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if current_user is None:
        add_flash_message(request, "warning", "Please log in to view your history.")
        return RedirectResponse(url="/login", status_code=303)

    history = (
        db.query(PredictionHistory)
        .filter(PredictionHistory.user_id == current_user.id)
        .order_by(PredictionHistory.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "request": request,
            "current_user": current_user,
            "page_title": "Prediction History",
            "flashes": pop_flash_messages(request),
            "history_items": history,
            "format_label": format_label,
        },
    )


@router.get("/history/{prediction_id}")
def history_detail(prediction_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if current_user is None:
        add_flash_message(request, "warning", "Please log in to view prediction details.")
        return RedirectResponse(url="/login", status_code=303)

    item = (
        db.query(PredictionHistory)
        .filter(
            PredictionHistory.id == prediction_id,
            PredictionHistory.user_id == current_user.id,
        )
        .first()
    )
    if item is None:
        add_flash_message(request, "danger", "Prediction record not found.")
        return RedirectResponse(url="/history", status_code=303)

    result = {
        "status": item.result_status,
        "display_message": "Saved prediction record.",
        "crop_name": item.crop_name,
        "disease_name": item.disease_name,
        "confidence_score": item.confidence_score,
        "recommendation": item.recommendation,
        "image_url": item.image_path,
        "raw_result": {},
    }
    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "request": request,
            "current_user": current_user,
            "page_title": "Prediction Detail",
            "flashes": pop_flash_messages(request),
            "result": result,
            "history_item": item,
            "format_label": format_label,
        },
    )
