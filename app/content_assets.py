from pathlib import Path
from typing import Iterable


REAL_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
SVG_SUFFIX = ".svg"
STATIC_IMAGES_ROOT = Path(__file__).resolve().parent / "static" / "images"


def _list_images(folder: str, include_svg: bool = False) -> list[str]:
    image_dir = STATIC_IMAGES_ROOT / folder
    if not image_dir.exists():
        return []

    allowed_suffixes = set(REAL_IMAGE_SUFFIXES)
    if include_svg:
        allowed_suffixes.add(SVG_SUFFIX)

    return sorted(
        file.name
        for file in image_dir.iterdir()
        if file.is_file() and file.suffix.lower() in allowed_suffixes
    )


def resolve_static_image_path(folder: str, preferred_name: str | None, fallback_name: str | None = None) -> str:
    available_real = _list_images(folder)

    for candidate in (preferred_name, fallback_name):
        if candidate and candidate in available_real:
            return f"images/{folder}/{candidate}"

    if available_real:
        return f"images/{folder}/{available_real[0]}"

    available_any = _list_images(folder, include_svg=True)
    if preferred_name and preferred_name in available_any:
        return f"images/{folder}/{preferred_name}"
    if fallback_name and fallback_name in available_any:
        return f"images/{folder}/{fallback_name}"
    if available_any:
        return f"images/{folder}/{available_any[0]}"

    raise FileNotFoundError(f"No images found in static folder: {folder}")


def assign_unique_static_images(
    folder: str,
    preferred_names: Iterable[str | None],
    fallback_name: str | None = None,
) -> list[str]:
    available_real = _list_images(folder)
    if not available_real:
        fallback_path = resolve_static_image_path(folder, None, fallback_name)
        return [fallback_path for _ in preferred_names]

    unused = available_real.copy()
    assigned: list[str] = []
    preferred_list = list(preferred_names)

    for preferred_name in preferred_list:
        if preferred_name in unused:
            selected = preferred_name
            unused.remove(selected)
        elif unused:
            selected = unused.pop(0)
        elif preferred_name in available_real:
            selected = preferred_name
        elif fallback_name in available_real:
            selected = fallback_name
        else:
            selected = available_real[0]

        assigned.append(f"images/{folder}/{selected}")

    return assigned
