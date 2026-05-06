from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import get_current_user, pop_flash_messages
from app.content_assets import assign_unique_static_images, resolve_static_image_path
from app.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

BLOG_POSTS = [
    {
        "title": "Cassava Mosaic Disease",
        "slug": "cassava-mosaic",
        "preferred_image": "cassavamossiac.jpg",
        "excerpt": "A common viral disease that causes mosaic leaf patterns, poor growth, and serious yield loss.",
        "content": "Cassava mosaic disease often shows up as yellow-green patching, leaf distortion, and reduced plant vigor. Farmers can reduce losses by planting clean stem cuttings, removing infected plants early, and choosing tolerant varieties when available.",
    },
    {
        "title": "Cassava Bacterial Blight",
        "slug": "cassava-bacterial-blight",
        "preferred_image": "cassavablight.jpg",
        "excerpt": "This disease causes leaf wilting and stem damage that can weaken cassava fields quickly.",
        "content": "Cassava bacterial blight spreads through infected planting material, rain splash, and field tools. Good sanitation, healthy cuttings, and removing badly affected plants can help manage the disease.",
    },
    {
        "title": "Maize Leaf Blight",
        "slug": "maize-leaf-blight",
        "preferred_image": "maizeblight.jpg",
        "excerpt": "Elongated lesions on maize leaves can reduce photosynthesis and limit grain filling.",
        "content": "Maize leaf blight usually starts as long gray or brown lesions on the leaves. Early field scouting, resistant seed, and proper crop residue management can reduce disease pressure.",
    },
    {
        "title": "Maize Streak Virus",
        "slug": "maize-streak-virus",
        "preferred_image": "maizespot.jpg",
        "excerpt": "Fine yellow streaks on leaves can lead to stunted maize plants and poor cobs.",
        "content": "Maize streak virus is often spread by leafhoppers. Controlling vectors, removing infected volunteer plants, and growing resistant varieties are key to reducing damage.",
    },
    {
        "title": "Fall Armyworm Damage",
        "slug": "fall-armyworm",
        "preferred_image": "cassavaspot.jpg",
        "excerpt": "A major maize pest that feeds aggressively on leaves and young whorls.",
        "content": "Fall armyworm damage may appear as ragged holes, shredded leaves, and frass inside the whorl. Frequent scouting and early integrated pest management are important for protecting yield.",
    },
    {
        "title": "Effects of Plant Diseases on Food Security",
        "slug": "food-security",
        "preferred_image": "maizeblight.jpg",
        "excerpt": "Plant health directly affects harvest quantity, farmer income, and local food availability.",
        "content": "When plant diseases spread unchecked, farmers can lose a large share of expected harvests. Faster diagnosis helps improve intervention timing, reduce waste, and support household and community food security.",
    },
]


def get_blog_posts() -> list[dict]:
    preferred_images = [post.get("preferred_image") for post in BLOG_POSTS]
    assigned_images = assign_unique_static_images("blog", preferred_images, fallback_name="cassavablight.jpg")
    fallback_image = resolve_static_image_path("blog", "cassavablight.jpg")

    posts: list[dict] = []
    for post, image_path in zip(BLOG_POSTS, assigned_images):
        posts.append(
            {
                **post,
                "image_path": image_path,
                "fallback_image_path": fallback_image,
            }
        )
    return posts


@router.get("/blog")
def blog_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        request=request,
        name="blog.html",
        context={
            "request": request,
            "current_user": get_current_user(request, db),
            "page_title": "Plant Disease Blog",
            "flashes": pop_flash_messages(request),
            "posts": get_blog_posts(),
        },
    )
