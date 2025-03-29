import os
import tempfile
import requests
from PIL import Image
import torch
from transformers import pipeline
import pytesseract  # Make sure you have Tesseract installed!

# Initialize detector with Colab GPU optimization
detector = pipeline(
    model="google/owlv2-base-patch16-ensemble",
    task="zero-shot-object-detection",
    device="cuda" if torch.cuda.is_available() else "cpu"
)

def detect_and_crop(img):
    # Detect license plates
    detections = detector(img, candidate_labels=["license plate", "vehicle registration plate"])

    if not detections:
        return None, "No plate detected"

    # Select highest confidence detection
    best = max(detections, key=lambda x: x['score'])
    box = best['box']

    # Convert to integers for cropping
    xmin, ymin, xmax, ymax = map(int, [box['xmin'], box['ymin'], box['xmax'], box['ymax']])
    
    # Crop and return
    return img.crop((xmin, ymin, xmax, ymax)), f"Detected with {best['score']:.2f} confidence"

def download_image(url: str) -> str:
    """
    Downloads an image from the provided URL and saves it to a temporary file.
    Returns the path to the downloaded image.
    """
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/58.0.3029.110 Safari/537.3"
        )
    }
    try:
        response = requests.get(url, stream=True, headers=headers)
        response.raise_for_status()  # Raise an error on bad status
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        temp_file.close()
        print("📥 Image downloaded to:", temp_file.name)
        return temp_file.name
    except Exception as e:
        temp_file.close()
        os.unlink(temp_file.name)
        print("🚫 Error downloading image:", e)
        raise

def perform_ocr(cropped_img: Image.Image) -> str:
    """
    Performs OCR on the provided cropped image to extract license plate text.
    Returns the extracted text.
    """
    ocr_result = pytesseract.image_to_string(cropped_img)
    extracted_text = ocr_result.strip()
    print("🔍 OCR extracted:", extracted_text)
    return extracted_text

def process_license_plate(url: str) -> str:
    """
    Full pipeline: downloads the image from URL, detects & crops license plate,
    performs OCR, and cleans up resources.
    Returns the OCR result (extracted license plate characters).
    """
    temp_img_path = download_image(url)
    try:
        img = Image.open(temp_img_path)
        cropped_img, detection_msg = detect_and_crop(img)
        print("📸", detection_msg)
        if cropped_img is None:
            return "No license plate detected in the image."
        plate_text = perform_ocr(cropped_img)
        return plate_text if plate_text else "No text found on the license plate."
    finally:
        if os.path.exists(temp_img_path):
            os.unlink(temp_img_path)
            print("🗑️ Temporary image file deleted.")
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            print("🧹 GPU cache cleared.")


if __name__ == "__main__":
    # Get the image URL from the terminal
    image_url = input("Enter the image URL: ").strip()
    try:
        result = process_license_plate(image_url)
        print("🚗 License Plate Text:", result)
    except Exception as e:
        print("😢 Something went wrong:", e)
