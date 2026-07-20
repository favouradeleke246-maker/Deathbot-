import pytesseract
from PIL import Image
import requests
from io import BytesIO

def extract_text_from_image(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    text = pytesseract.image_to_string(img)
    return text.strip()
