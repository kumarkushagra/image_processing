from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
from license_plate_extractor import process_license_plate

app = FastAPI(title="License Plate Extractor API 😎")

# ------------------------------
# Actual API endpoint (JSON based)
# ------------------------------
class ImageLink(BaseModel):
    url: str

@app.post("/extract_plate")
async def extract_plate(image: ImageLink):
    """
    API endpoint to extract license plate text from an image URL.
    Expected payload: { "url": "<IMAGE_URL>" }
    """
    try:
        result = process_license_plate(image.url)
        return {"plate_text": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ------------------------------
# Testing endpoint (HTML interface)
# ------------------------------
@app.get("/test", response_class=HTMLResponse)
async def test_form():
    """
    Returns an HTML form for testing the image URL input.
    """
    html_content = """
    <html>
        <head>
            <title>License Plate Extractor Test</title>
        </head>
        <body>
            <h2>Enter an Image URL to Extract License Plate</h2>
            <form action="/test" method="post">
                <input type="text" name="url" style="width:400px;" placeholder="Enter image URL here" required>
                <input type="submit" value="Extract">
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/test", response_class=HTMLResponse)
async def test_submit(url: str = Form(...)):
    """
    Accepts the URL from the HTML form, processes it, and returns the result as HTML.
    """
    try:
        result = process_license_plate(url)
        response_html = f"""
        <html>
            <head>
                <title>License Plate Extractor Test</title>
            </head>
            <body>
                <h2>Extraction Result</h2>
                <p><strong>License Plate Text:</strong> {result}</p>
                <a href="/test">Try another image</a>
            </body>
        </html>
        """
        return HTMLResponse(content=response_html)
    except Exception as e:
        response_html = f"""
        <html>
            <head>
                <title>Error</title>
            </head>
            <body>
                <h2>Error Occurred</h2>
                <p>{e}</p>
                <a href="/test">Go Back</a>
            </body>
        </html>
        """
        return HTMLResponse(content=response_html, status_code=400)

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
