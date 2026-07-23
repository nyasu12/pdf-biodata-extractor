import io
import os
from typing import Any, Dict, Optional

from google.cloud import vision
from PIL import Image, ImageEnhance, ImageFilter


def preprocess(image: Image.Image, settings: Optional[Dict[str, Any]] = None) -> Image.Image:
    settings = settings or {}
    processed = image

    if settings.get("grayscale", True):
        processed = processed.convert("L")

    contrast = float(settings.get("contrast", 1.5))
    if contrast > 0 and contrast != 1.0:
        processed = ImageEnhance.Contrast(processed).enhance(contrast)

    if settings.get("sharpen", True):
        processed = processed.filter(ImageFilter.SHARPEN)

    return processed


def extract_text_from_images(images, debug_folder=None, settings=None):
    settings = settings or {}
    client = vision.ImageAnnotatorClient()
    page_texts = []
    language_hints = settings.get("language_hints") or []

    for i, image in enumerate(images):
        processed = preprocess(image, settings=settings)

        if debug_folder:
            os.makedirs(debug_folder, exist_ok=True)
            debug_path = os.path.join(debug_folder, f"debug_page_{i + 1}.png")
            processed.save(debug_path, format="PNG")

        with io.BytesIO() as output:
            processed.save(output, format="PNG")
            image_content = output.getvalue()

        vision_image = vision.Image(content=image_content)
        kwargs = {"image": vision_image}
        if language_hints:
            kwargs["image_context"] = {"language_hints": language_hints}

        response = client.document_text_detection(**kwargs)

        if response.error.message:
            print(f"[ocr] page {i + 1}: {response.error.message}")
            page_texts.append("")
            continue

        page_text = ""
        if response.full_text_annotation and response.full_text_annotation.text:
            page_text = response.full_text_annotation.text
        elif response.text_annotations:
            page_text = response.text_annotations[0].description

        page_texts.append(page_text)

    return page_texts
