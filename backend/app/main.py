from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
app = FastAPI()
import logging
from typing import Optional, Dict

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.clone.clone import WebsiteScraper

scraper = WebsiteScraper()
class CloneRequest(BaseModel):
    url: HttpUrl

class CloneResponse(BaseModel):
    success: bool
    html: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.post("/clone", response_model=CloneResponse)
async def clone_website(request: CloneRequest):
    """Clone a website based on its URL"""
    try:
        logger.info(f"Starting clone process for: {request.url}")
        
        # Step 1: Extract design context
        logger.info("Extracting DOM structure...")
        dom_context = await scraper.extract_dom_structure(request.url)
        
        # Step 2: Capture screenshot (optional, for future use)
        logger.info("Capturing screenshot...")
        screenshot = await scraper.capture_screenshot(request.url)
        
        # Step 3: Prepare design context
        design_context = {
            "url": str(request.url),
            "dom_structure": dom_context,
            "has_screenshot": screenshot is not None
        }
        
        # Step 4: Generate HTML clone
        logger.info("Generating HTML clone...")
        cloned_html = await scraper.generate_clone_html(design_context)
        
        logger.info("Clone process completed successfully")
        
        return CloneResponse(
            success=True,
            html=cloned_html,
            metadata={
                "original_url": str(request.url),
                "elements_extracted": len(dom_context.get('main_content', [])),
                "stylesheets_found": len(dom_context.get('stylesheets', [])),
                "has_screenshot": screenshot is not None
            }
        )
        
    except Exception as e:
        logger.error(f"Clone process failed: {e}")
        return CloneResponse(
            success=False,
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
