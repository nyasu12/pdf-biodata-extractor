import io
import os
from google.cloud import vision
from PIL import Image, ImageEnhance, ImageFilter

def preprocess(image: Image.Image) -> Image.Image:
    img = image.convert("L")
    img = ImageEnhance.Contrast(img).enhance(1.5)
    img = img.filter(ImageFilter.SHARPEN)
    return img

def extract_text_from_images(images, debug_folder=None):
    client = vision.ImageAnnotatorClient()
    page_texts = []

    for i, image in enumerate(images):
        processed = preprocess(image)

        if debug_folder:
            os.makedirs(debug_folder, exist_ok=True)
            debug_path = os.path.join(debug_folder, f"debug_page_{i+1}.png")
            processed.save(debug_path, format="PNG")

        with io.BytesIO() as output:
            processed.save(output, format="PNG")
            image_content = output.getvalue()

        vision_image = vision.Image(content=image_content)

        response = client.document_text_detection(
            image=vision_image,
            image_context={"language_hints": ["en"]}
        )

        if response.error.message:
            page_texts.append("")
            continue

        page_text = ""
        if response.full_text_annotation and response.full_text_annotation.text:
            page_text = response.full_text_annotation.text
        elif response.text_annotations:
            page_text = response.text_annotations[0].description

        page_texts.append(page_text)

    return page_texts
