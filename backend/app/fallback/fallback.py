# old/ first iteration of the code

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from bs4 import BeautifulSoup
import base64
from urllib.parse import urljoin, urlparse
import json
import os
from typing import Optional, Dict, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import google.generativeai as genai
import logging
from dotenv import load_dotenv
import os

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebsiteScraper:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.gemini_model = genai.GenerativeModel('gemini-2.5-pro-preview-06-05')
    
    def get_chrome_options(self):
        """Configure Chrome options for headless browsing"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        return chrome_options
    
    async def capture_screenshot(self, url: str) -> Optional[str]:
        """Capture screenshot of the website"""
        try:
            options = self.get_chrome_options()
            driver = webdriver.Chrome(options=options)
            
            driver.get(str(url))
            # Wait for page to load
            time.sleep(3)
            
            # Take screenshot
            screenshot = driver.get_screenshot_as_png()
            screenshot_b64 = base64.b64encode(screenshot).decode()
            
            driver.quit()
            return screenshot_b64
            
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            return None
    
    async def extract_dom_structure(self, url: str) -> Dict:
        """Extract DOM structure and key elements"""
        try:
        
            options = self.get_chrome_options()
            driver = webdriver.Chrome(options=options)

            driver.get(str(url))
            time.sleep(5) 

            rendered_html = driver.page_source 

            driver.quit()

            soup = BeautifulSoup(rendered_html, 'html.parser')

            dom_info = {
                'title': soup.title.string if soup.title else '',
                'meta_description': self._get_meta_description(soup),
                'stylesheets': self._extract_stylesheets(soup, str(url)),
                'main_content': self._extract_main_content(soup),
                'navigation': self._extract_navigation(soup),
                'layout_structure': self._analyze_layout_structure(soup),
                'color_palette': self._extract_colors(soup),
                'typography': self._extract_typography(soup),
                'images': self._extract_images(soup, str(url))
            }

            return dom_info
            
        except Exception as e:
            logger.error(f"DOM extraction failed: {e}")
            return {}
    
    def _get_meta_description(self, soup):
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '') if meta_desc else ''
    
    def _extract_stylesheets(self, soup, base_url):
        """Extract stylesheet links and inline styles"""
        stylesheets = []
        
        # External stylesheets
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                stylesheets.append({'type': 'external', 'url': full_url})
        
        # Inline styles
        for style in soup.find_all('style'):
            if style.string:
                stylesheets.append({'type': 'inline', 'content': style.string})
        
        return stylesheets
    
    def _extract_main_content(self, soup):
        """Extract main content areas"""
        main_content = []
        
        # Look for semantic HTML elements
        semantic_tags = ['main', 'article', 'section', 'header', 'footer', 'nav', 'aside']
        for tag in semantic_tags:
            elements = soup.find_all(tag)
            for elem in elements:
                main_content.append({
                    'tag': tag,
                    'content': elem.get_text(strip=True)[:500],  # Limit text length
                    'classes': elem.get('class', []),
                    'id': elem.get('id', '')
                })
        
        return main_content
    
    def _extract_navigation(self, soup):
        """Extract navigation structure"""
        nav_info = []
        
        # Find navigation elements
        nav_elements = soup.find_all(['nav', 'ul', 'ol'])
        for nav in nav_elements:
            links = nav.find_all('a')
            if links:
                nav_info.append({
                    'tag': nav.name,
                    'classes': nav.get('class', []),
                    'links': [{'text': link.get_text(strip=True), 'href': link.get('href', '')} 
                             for link in links[:10]]  # Limit to 10 links
                })
        
        return nav_info
    
    def _analyze_layout_structure(self, soup):
        """Analyze the overall layout structure for Tailwind recreation"""
        structure = {
            'has_header': bool(soup.find(['header', 'div'], class_=lambda x: x and 'header' in str(x).lower())),
            'has_footer': bool(soup.find(['footer', 'div'], class_=lambda x: x and 'footer' in str(x).lower())),
            'has_sidebar': bool(soup.find(['aside', 'div'], class_=lambda x: x and any(term in str(x).lower() for term in ['sidebar', 'side']))),
            'grid_layout': bool(soup.find_all(['div'], class_=lambda x: x and any(term in str(x).lower() for term in ['grid', 'col', 'row']))),
            'flex_layout': bool(soup.find_all(['div'], class_=lambda x: x and 'flex' in str(x).lower()))
        }
        return structure
    
    def _extract_colors(self, soup):
        """Extract color information from inline styles and classes"""
        colors = []
        
        # Look for inline styles with colors
        for elem in soup.find_all(style=True):
            style = elem.get('style', '')
            if 'color:' in style or 'background-color:' in style:
                colors.append(style)
        
        return colors[:15]  # Limit to 10 color references
    
    def _extract_typography(self, soup):
        """Extract typography information"""
        typography = {
            'headings': [],
            'fonts': []
        }
        
        # Extract headings
        for i in range(1, 7):
            headings = soup.find_all(f'h{i}')
            for heading in headings[:3]:  # Limit to 3 per level
                typography['headings'].append({
                    'level': i,
                    'text': heading.get_text(strip=True),
                    'classes': heading.get('class', [])
                })
        
        return typography
    
    def _extract_images(self, soup, base_url):
        """Extract image information"""
        images = []
        
        for img in soup.find_all('img')[:10]:  # Limit to 10 images
            src = img.get('src')
            if src:
                full_url = urljoin(base_url, src)
                images.append({
                    'src': full_url,
                    'alt': img.get('alt', ''),
                    'classes': img.get('class', [])
                })
        
        return images
    
    async def generate_clone_html(self, design_context: Dict, screenshot_b64: Optional[str] = None) -> str:
        """Use Gemini to generate HTML based on design context and optional screenshot"""
        try:
            prompt = self._create_cloning_prompt(design_context)
            
            content_parts = [prompt]
            
            if screenshot_b64:
                import io
                import base64
                from PIL import Image

                image_data = base64.b64decode(screenshot_b64)
                image = Image.open(io.BytesIO(image_data))
                content_parts.extend([
                    "\n\nHere's a screenshot of the original website for visual reference:",
                    image
                ])
            
            response = self.gemini_model.generate_content(
                content_parts,
                generation_config=genai.types.GenerationConfig(
                    temperature=1.5,
                    max_output_tokens=8192,
                    candidate_count=1,
                )
            )
            
            html_content = response.text
            
            if "```html" in html_content:
                html_content = html_content.split("```html")[1].split("```")[0]
            elif "<html" in html_content:
                start = html_content.find("<html")
                end = html_content.rfind("</html>") + 7
                if end > 6:  # Make sure </html> was found
                    html_content = html_content[start:end]
            
            return html_content.strip()
            
        except Exception as e:
            logger.error(f"HTML generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"HTML generation failed: {str(e)}")
    
    def _create_cloning_prompt(self, design_context: Dict) -> str:
        """Create a detailed prompt optimized for Gemini to clone the website"""
        context_json = json.dumps(design_context, indent=2)
        
        prompt = f"""
            You are an expert frontend developer and UI/UX designer. Your task is to recreate a website based on the extracted design context below. Create HTML that closely matches the original website's visual appearance, layout, and user experience.

            DESIGN CONTEXT FROM ORIGINAL WEBSITE:
            {context_json}

            YOUR MISSION:
            Create a complete, standalone HTML document that recreates the visual design and layout of the original website.

            SPECIFIC REQUIREMENTS:

            1. **HTML Structure**:
            - Use semantic HTML5 elements (header, nav, main, section, article, footer)
            - Create a clean, well-organized document structure
            - Include proper meta tags and title

            2. **CSS Styling** (embed in <style> tag):
            - Match the color palette and visual hierarchy from the original
            - Recreate typography styles (font families, sizes, weights)
            - Implement responsive layout using modern CSS (Flexbox/Grid)
            - Add hover effects and smooth transitions for better UX
            - Ensure proper spacing, margins, and padding

            3. **Layout Recreation**:
            - Recreate the header/navigation structure
            - Match the main content layout and sections
            - Include sidebar elements if present in original
            - Recreate footer design and content
            - Maintain visual proportions and hierarchy

            4. **Content Strategy**:
            - Use the extracted text content where available
            - Create meaningful placeholder content for missing elements
            - Use placeholder images (via CSS or placeholder services)
            - Maintain the same content structure and flow

            5. **Modern Best Practices**:
            - Mobile-responsive design
            - Clean, readable code structure
            - Fast-loading and optimized
            - Accessible markup with proper ARIA labels
            - Cross-browser compatibility

            6. **Visual Polish**:
            - Add subtle shadows, gradients, or effects that match the original style
            - Ensure consistent spacing and alignment
            - Use appropriate border-radius for modern look
            - Implement smooth animations where appropriate

            CRITICAL INSTRUCTIONS:
            - Output ONLY the complete HTML document with embedded CSS
            - No explanations, comments, or text outside the HTML
            - Make it visually impressive and close to the original
            - Ensure the result is a functional, standalone HTML file
            - Focus on making it look professional and polished

            Generate the complete HTML now:
            """
        return prompt