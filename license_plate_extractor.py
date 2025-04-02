import requests
import tempfile
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise Exception("API_KEY not found in environment variables!")

# Easily modifiable API key

def process_license_plate(image_url: str) -> str:
    """
    Downloads an image from the provided URL, sends it to the CircuitDigest
    ANPR API, and returns the extracted license plate text.
    """
    # Download the image
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
    except Exception as e:
        raise Exception("Failed to download image: " + str(e))
    
    # Save the image temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                tmp.write(chunk)
        temp_file_path = tmp.name

    # Prepare API call details
    api_url = "https://www.circuitdigest.cloud/readnumberplate"
    with open(temp_file_path, "rb") as image_file:
        files_payload = {
            "imageFile": (f"{API_KEY}.jpg", image_file, "image/jpg")
        }
        headers = {"Authorization": API_KEY}
        api_response = requests.post(api_url, headers=headers, files=files_payload)
    
    # Process the API response
    if api_response.status_code == 200:
        response_data = api_response.json()
        return response_data.get("data", {}).get("number_plate", "Not found")
    else:
        raise Exception(f"API error {api_response.status_code}: {api_response.text}")
