import io
import os
from google.cloud import vision

def extract_text_from_images(images, debug_folder=None):
    client = vision.ImageAnnotatorClient()
    full_text = ""
    for i, image in enumerate(images):
        if debug_folder:
            debug_path = os.path.join(debug_folder, f"debug_page_{i+1}.png")
            image.save(debug_path, format="PNG")
        with io.BytesIO() as output:
            image.save(output, format="PNG")
            image_content = output.getvalue()
        vision_image = vision.Image(content=image_content)
        response = client.text_detection(image=vision_image)
        if response.text_annotations:
            full_text += response.text_annotations[0].description + "\n"
    return full_text
