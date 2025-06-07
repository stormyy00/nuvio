from fastapi import FastAPI,  HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
app = FastAPI()
import logging
from typing import Optional, Dict
from app.clone.clone import EnchancedWebsiteScraper

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



scraper = EnchancedWebsiteScraper()
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
    """Clone a website using the enhanced multi-stage process"""
    try:
        logger.info(f"Starting enhanced clone process for: {request.url}")
        
        # Step 1: Extract comprehensive design context
        logger.info("Extracting comprehensive DOM structure...")
        design_context = await scraper.extract_comprehensive_dom(request.url)
        
        if not design_context:
            raise HTTPException(status_code=400, detail="Failed to extract website data")
        
        # Step 2: Capture multiple screenshots
        logger.info("Capturing screenshots...")
        screenshots = await scraper.capture_multiple_screenshots(request.url)
        
        # Step 3: Generate HTML using multi-stage process
        logger.info("Generating HTML clone using multi-stage process...")
        cloned_html = await scraper.generate_clone_html_multistage(design_context, screenshots)
        
        if not cloned_html:
            raise HTTPException(status_code=500, detail="Failed to generate HTML clone")
        
        logger.info("Enhanced clone process completed successfully")
        
        metadata = {
            "original_url": str(request.url),
            "content_sections_extracted": len(design_context.get('content_sections', [])),
            "navigation_elements": len(design_context.get('navigation_structure', [])),
            "visual_elements_found": len(design_context.get('visual_elements', {}).get('images', [])),
            "layout_type": design_context.get('layout_analysis', {}).get('structure_type', 'unknown'),
            "has_screenshots": len(screenshots) > 0,
            "responsive_detected": design_context.get('responsive_indicators', {}).get('count', 0) > 0,
            "interactive_elements": design_context.get('interactive_elements', {}),
            "generation_method": "multi-stage"
        }
        
        return CloneResponse(
            success=True,
            html=cloned_html,
            metadata=metadata
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Enhanced clone process failed: {e}")
        return CloneResponse(
            success=False,
            error=str(e),
            metadata={"error_type": type(e).__name__}
        )

@app.post("/fallback", response_model=CloneResponse)
async def clone_website_legacy(request: CloneRequest):
    """Fallback to single-stage cloning if multi-stage fails"""
    try:
        logger.info(f"Starting legacy clone process for: {request.url}")
        
        # Extract design context
        design_context = await scraper.extract_comprehensive_dom(request.url)
        
        if not design_context:
            raise HTTPException(status_code=400, detail="Failed to extract website data")
        
        # Capture single screenshot
        screenshots = await scraper.capture_multiple_screenshots(request.url)
        screenshot = screenshots.get('desktop') if screenshots else None
        
        # Use the original single-pass generation method
        # You'll need to add this method to your EnhancedWebsiteScraper class
        cloned_html = await scraper.generate_clone_html_single_pass(design_context, screenshot)
        
        logger.info("Legacy clone process completed")
        
        return CloneResponse(
            success=True,
            html=cloned_html,
            metadata={
                "original_url": str(request.url),
                "generation_method": "single-pass-legacy",
                "has_screenshot": screenshot is not None
            }
        )
        
    except Exception as e:
        logger.error(f"Legacy clone process failed: {e}")
        return CloneResponse(
            success=False,
            error=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
