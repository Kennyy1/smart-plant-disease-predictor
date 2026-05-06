from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import get_current_user, pop_flash_messages
from app.content_assets import assign_unique_static_images, resolve_static_image_path
from app.database import get_db
from app.models import PredictionHistory
from app.prediction import format_label

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

CAROUSEL_SLIDES = [
    {
        "preferred_image": "carouselfarm.jpg",
        "badge": "AI Crop Intelligence",
        "title": "Smart Plant Disease Predictor",
        "subtitle": "AI-powered diagnosis for cassava and maize leaves.",
        "primary_label": "Detect Disease",
        "primary_href": "/detect",
        "secondary_label": "Learn More",
        "secondary_href": "/blog",
    },
    {
        "preferred_image": "carousel2.jpj.jpg",
        "badge": "Faster Decisions",
        "title": "Early Disease Detection",
        "subtitle": "Detect crop diseases before serious yield loss occurs.",
        "primary_label": "Detect Disease",
        "primary_href": "/detect",
        "secondary_label": "View Dashboard",
        "secondary_href": "/dashboard",
    },
    {
        "preferred_image": "carousel3.jpg",
        "badge": "Focused Models",
        "title": "Crop-Specific Diagnosis",
        "subtitle": "Cassava and maize models provide focused predictions.",
        "primary_label": "Learn More",
        "primary_href": "/blog",
        "secondary_label": "View Dashboard",
        "secondary_href": "/dashboard",
    },
    {
        "preferred_image": "carousel4.jpg",
        "badge": "Actionable Insights",
        "title": "Farmer-Friendly Results",
        "subtitle": "Upload a leaf image and receive instant guidance.",
        "primary_label": "Detect Disease",
        "primary_href": "/detect",
        "secondary_label": "View Dashboard",
        "secondary_href": "/dashboard",
    },
]

FEATURED_POSTS = [
    {
        "title": "Cassava Mosaic Disease",
        "excerpt": "Learn how leaf distortion and mosaic patterns can affect cassava yield.",
        "preferred_image": "cassavamossiac.jpg",
    },
    {
        "title": "Maize Leaf Blight",
        "excerpt": "Understand early signs of leaf blight and how farmers can respond quickly.",
        "preferred_image": "maizeblight.jpg",
    },
    {
        "title": "Food Security and Plant Health",
        "excerpt": "See why rapid disease detection matters for harvest quality and farm income.",
        "preferred_image": "cassavaspot.jpg",
    },
]


def get_homepage_slides(current_user) -> list[dict]:
    assigned_images = assign_unique_static_images(
        "carousel",
        [slide.get("preferred_image") for slide in CAROUSEL_SLIDES],
        fallback_name="carouselfarm.jpg",
    )
    fallback_image = resolve_static_image_path("carousel", "carouselfarm.jpg")
    slides: list[dict] = []

    for slide, image_path in zip(CAROUSEL_SLIDES, assigned_images):
        secondary_href = slide["secondary_href"]
        secondary_label = slide["secondary_label"]
        if secondary_href == "/dashboard" and current_user is None:
            secondary_href = "/signup"
            secondary_label = "Get Started"

        slides.append(
            {
                **slide,
                "image_path": image_path,
                "fallback_image_path": fallback_image,
                "secondary_href": secondary_href,
                "secondary_label": secondary_label,
            }
        )

    return slides


def get_featured_posts() -> list[dict]:
    assigned_images = assign_unique_static_images(
        "blog",
        [post.get("preferred_image") for post in FEATURED_POSTS],
        fallback_name="cassavablight.jpg",
    )
    fallback_image = resolve_static_image_path("blog", "cassavablight.jpg")
    posts: list[dict] = []

    for post, image_path in zip(FEATURED_POSTS, assigned_images):
        posts.append(
            {
                **post,
                "image_path": image_path,
                "fallback_image_path": fallback_image,
            }
        )

    return posts


@router.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "current_user": current_user,
            "page_title": "Crop Disease Detection System",
            "flashes": pop_flash_messages(request),
            "carousel_slides": get_homepage_slides(current_user),
            "featured_posts": get_featured_posts(),
        },
    )


@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)

    history = (
        db.query(PredictionHistory)
        .filter(PredictionHistory.user_id == current_user.id)
        .order_by(PredictionHistory.created_at.desc())
        .all()
    )
    recent = history[0] if history else None

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "current_user": current_user,
            "page_title": "Dashboard",
            "flashes": pop_flash_messages(request),
            "total_predictions": len(history),
            "supported_crops": "Cassava and Maize",
            "recent_result": format_label(recent.disease_name) if recent else "No predictions yet",
            "system_accuracy": "Gate: 96.3% | Crop: 84.85%",
            "recent_history": history[:5],
            "format_label": format_label,
        },
    )
