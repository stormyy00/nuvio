# main implementation of the website cloning service

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import aiohttp
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
import re

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnchancedWebsiteScraper:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")

    def get_chrome_options(self):
        """Configure Chrome options for headless browsing"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        return chrome_options

    async def capture_multiple_screenshots(self, url: str) -> Dict[str, str]:
        """Capture multiple screenshots at different viewport sizes"""
        screenshots = {}
        viewports = {
            "desktop": (1920, 1080),
            "tablet": (768, 1024),
            "mobile": (375, 667),
        }

        try:
            options = self.get_chrome_options()
            driver = webdriver.Chrome(options=options)

            for name, (width, height) in viewports.items():
                driver.set_window_size(width, height)
                driver.get(str(url))
                time.sleep(3)

                screenshot = driver.get_screenshot_as_png()
                screenshots[name] = base64.b64encode(screenshot).decode()

            driver.quit()
            return screenshots

        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            return {}

    async def extract_comprehensive_dom(self, url: str) -> Dict:
        """Enhanced DOM extraction with more detailed analysis"""
        try:
            options = self.get_chrome_options()
            driver = webdriver.Chrome(options=options)
            driver.get(str(url))
            time.sleep(8)

            js_analysis = driver.execute_script(
                """
                return {
                    viewportWidth: window.innerWidth,
                    viewportHeight: window.innerHeight,
                    scrollHeight: document.body.scrollHeight,
                    documentHeight: document.documentElement.scrollHeight,
                    hasFixedElements: Array.from(document.querySelectorAll('*')).some(el => 
                        getComputedStyle(el).position === 'fixed'),
                    computedStyles: Array.from(document.querySelectorAll('*')).slice(0, 50).map(el => ({
                        tag: el.tagName.toLowerCase(),
                        className: el.className,
                        computedStyle: {
                            display: getComputedStyle(el).display,
                            position: getComputedStyle(el).position,
                            backgroundColor: getComputedStyle(el).backgroundColor,
                            color: getComputedStyle(el).color,
                            fontSize: getComputedStyle(el).fontSize,
                            fontFamily: getComputedStyle(el).fontFamily,
                            margin: getComputedStyle(el).margin,
                            padding: getComputedStyle(el).padding,
                            border: getComputedStyle(el).border,
                            borderRadius: getComputedStyle(el).borderRadius
                        }
                    }))
                };
            """
            )

            rendered_html = driver.page_source
            driver.quit()

            soup = BeautifulSoup(rendered_html, "html.parser")

            dom_info = {
                "basic_info": {
                    "title": soup.title.string if soup.title else "",
                    "meta_description": self._get_meta_description(soup),
                    "lang": soup.html.get("lang") if soup.html else "en",
                },
                "layout_analysis": self._analyze_layout_comprehensive(soup),
                "content_sections": self._extract_content_sections(soup),
                "navigation_structure": self._extract_navigation_detailed(soup),
                "visual_elements": self._extract_visual_elements(soup, str(url)),
                "typography_system": self._analyze_typography_system(soup),
                "color_analysis": self._analyze_colors_comprehensive(soup),
                "responsive_indicators": self._detect_responsive_patterns(soup),
                "js_analysis": js_analysis,
                "form_elements": self._extract_forms(soup),
                "interactive_elements": self._extract_interactive_elements(soup),
            }

            return dom_info

        except Exception as e:
            logger.error(f"Enhanced DOM extraction failed: {e}")
            return {}

    def _analyze_layout_comprehensive(self, soup):
        """Comprehensive layout analysis"""
        layout = {
            "structure_type": "unknown",
            "header": self._analyze_header(soup),
            "main_content": self._analyze_main_content(soup),
            "sidebar": self._analyze_sidebar(soup),
            "footer": self._analyze_footer(soup),
            "grid_systems": self._detect_grid_systems(soup),
            "container_patterns": self._analyze_containers(soup),
        }

        if soup.find_all(class_=lambda x: x and "grid" in str(x).lower()):
            layout["structure_type"] = "grid"
        elif soup.find_all(class_=lambda x: x and "flex" in str(x).lower()):
            layout["structure_type"] = "flexbox"
        elif soup.find(
            ["aside", "div"], class_=lambda x: x and "sidebar" in str(x).lower()
        ):
            layout["structure_type"] = "sidebar"
        else:
            layout["structure_type"] = "standard"

        return layout

    def _extract_content_sections(self, soup):
        """Extract and categorize content sections"""
        sections = []

        for section in soup.find_all(["section", "article", "div"], class_=True):
            classes = " ".join(section.get("class", []))

            section_data = {
                "tag": section.name,
                "classes": section.get("class", []),
                "content_type": self._classify_content_type(section, classes),
                "text_content": section.get_text(strip=True)[:300],
                "child_elements": [
                    child.name for child in section.find_all() if child.name
                ][:10],
                "has_background_image": bool(
                    section.find(style=lambda x: x and "background-image" in str(x))
                ),
                "estimated_importance": self._estimate_section_importance(section),
            }
            sections.append(section_data)

        return sections[:25]  

    def _classify_content_type(self, element, classes):
        """Classify the type of content section"""
        text = element.get_text().lower()
        classes_lower = classes.lower()

        if any(term in classes_lower for term in ["hero", "banner", "jumbotron"]):
            return "hero"
        elif any(term in classes_lower for term in ["card", "feature", "service"]):
            return "feature_card"
        elif any(term in classes_lower for term in ["testimonial", "review"]):
            return "testimonial"
        elif any(term in classes_lower for term in ["contact", "form"]):
            return "contact"
        elif any(term in text for term in ["about", "mission", "vision"]):
            return "about"
        elif element.find_all(["h1", "h2", "h3"]):
            return "content_section"
        else:
            return "generic"

    def _analyze_typography_system(self, soup):
        """Analyze typography patterns and hierarchy"""
        typography = {
            "headings": {},
            "body_text": [],
            "font_families": set(),
            "font_sizes": set(),
            "text_colors": set(),
        }

        for level in range(1, 7):
            headings = soup.find_all(f"h{level}")
            if headings:
                typography["headings"][f"h{level}"] = []
                for heading in headings[:3]:
                    typography["headings"][f"h{level}"].append(
                        {
                            "text": heading.get_text(strip=True),
                            "classes": heading.get("class", []),
                            "style": heading.get("style", ""),
                        }
                    )

        return typography

    def _analyze_colors_comprehensive(self, soup):
        """Comprehensive color analysis"""
        colors = {
            "background_colors": [],
            "text_colors": [],
            "border_colors": [],
            "dominant_palette": [],
        }

        for elem in soup.find_all(style=True):
            style = elem.get("style", "")

            bg_match = re.search(r"background-color:\s*([^;]+)", style)
            if bg_match:
                colors["background_colors"].append(bg_match.group(1).strip())

            color_match = re.search(r"(?<![a-z])color:\s*([^;]+)", style)
            if color_match:
                colors["text_colors"].append(color_match.group(1).strip())

        return colors

    async def generate_layout_structure(
        self, design_context: Dict, screenshot_b64: Optional[str] = None
    ) -> str:
        """First pass: Generate overall layout structure"""
        try:
            prompt = f"""
            You are a senior frontend architect. Recreate the full page structure as seen in the REFERENCE SCREENSHOT and described in the DESIGN CONTEXT.

            - Focus only on structural HTML and layout CSS.  
            - Match the placement and hierarchy of all major sections, navigation, and containers in the screenshot.
            - Use semantic HTML5 elements (<header>, <nav>, <main>, <section>, <footer>, etc).
            - Use either CSS Grid or Flexbox for layout in a <style> block.  
            - Do NOT add any colors, images, or detailed styling yet.
            - For content, use <div class="placeholder">Content here</div>.

            REFERENCE SCREENSHOT: (see attached image)  
            DESIGN CONTEXT:
            {json.dumps(design_context['layout_analysis'], indent=2)}

            Your output **must** be a single valid `<!DOCTYPE html>...` document, wrapped in a single `html` code block.  
            Do not include any extra explanation or comments.
            """

            content_parts = [prompt]
            if screenshot_b64:
                import io
                import base64
                from PIL import Image

                image_data = base64.b64decode(screenshot_b64)
                image = Image.open(io.BytesIO(image_data))
                content_parts.extend(["\n\nScreenshot for reference:", image])

            response = self.gemini_model.generate_content(
                content_parts,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=4096,
                ),
            )

            return self._extract_html(response.text)

        except Exception as e:
            logger.error(f"Structure generation failed: {e}")
            raise HTTPException(
                status_code=500, detail=f"Structure generation failed: {str(e)}"
            )

    async def generate_detailed_styling(
        self, base_html: str, design_context: Dict, screenshot_b64: Optional[str] = None
    ) -> str:
        """Second pass: Add detailed styling and visual elements"""
        try:

            def convert_sets(obj):
                if isinstance(obj, set):
                    return list(obj)
                raise TypeError(
                    f"Object of type {type(obj).__name__} is not JSON serializable"
                )

            prompt = f"""
            You are a top-tier UI/UX designer and frontend developer. Enhance the following HTML by **adding full CSS styling** to match the look and feel of the REFERENCE SCREENSHOT.

            - Use all color, typography, spacing, and visual details described in the VISUAL DESIGN CONTEXT.
            - The layout, alignment, and proportions must match the screenshot as closely as possible.
            - Add all visual effects, shadows, borders, background images/gradients, hover/focus states, and transitions visible in the screenshot.
            - The output must be fully responsive for mobile, tablet, and desktop.

            REFERENCE SCREENSHOT: (see attached image)  
            VISUAL DESIGN CONTEXT:
            Typography: {json.dumps(design_context.get('typography_system', {}), indent=2, default=convert_sets)}
            Colors: {json.dumps(design_context.get('color_analysis', {}), indent=2, default=convert_sets)}
            Visual Elements: {json.dumps(design_context.get('visual_elements', {}), indent=2, default=convert_sets)}

            HTML TO STYLE:
            ```html
            {base_html}
            """

            content_parts = [prompt]
            if screenshot_b64:
                import io
                import base64
                from PIL import Image

                image_data = base64.b64decode(screenshot_b64)
                image = Image.open(io.BytesIO(image_data))
                content_parts.extend(["\n\nScreenshot for styling reference:", image])

            response = self.gemini_model.generate_content(
                content_parts,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=6144,
                ),
            )

            return self._extract_html(response.text)

        except Exception as e:
            logger.error(f"Styling generation failed: {e}")
            return base_html  # Return base HTML if styling fails

    async def generate_content_and_interactivity(
        self, styled_html: str, design_context: Dict
    ) -> str:
        """Third pass: Add real content and interactive elements"""
        try:
            prompt = f"""
            You are a frontend engineer and content strategist. Take this styled HTML and inject the real content and JS interactivity.

            INPUT:
            1. Styled HTML:
            ```html
            {styled_html}
            
            CONTENT DATA:
            Content Sections: {json.dumps(design_context.get('content_sections', {}), indent=2)}
            Navigation: {json.dumps(design_context.get('navigation_structure', {}), indent=2)}
            Interactive Elements: {json.dumps(design_context.get('interactive_elements', {}), indent=2)}
            
            ENHANCE WITH:
            1. Replace placeholder content with real extracted content
            2. Add navigation menus with proper links
            3. Add interactive JavaScript for menus, modals, etc.
            4. Add form functionality if present
            5. Add smooth scrolling and animations
            6. Ensure all content matches the original website
            
            Output the complete, functional HTML file.
            """

            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,
                    max_output_tokens=8192,
                ),
            )

            return self._extract_html(response.text)

        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return styled_html  # Return styled HTML if content addition fails

    async def generate_clone_html_multistage(
        self, design_context: Dict, screenshots: Dict[str, str] = None
    ) -> str:
        """Multi-stage HTML generation process"""
        try:
            logger.info("Starting multi-stage HTML generation...")

            # Stage 1: Structure
            logger.info("Stage 1: Generating layout structure...")
            screenshot = screenshots.get("desktop") if screenshots else None
            structure_html = await self.generate_layout_structure(
                design_context, screenshot
            )

            # Stage 2: Styling
            logger.info("Stage 2: Adding detailed styling...")
            styled_html = await self.generate_detailed_styling(
                structure_html, design_context, screenshot
            )

            # Stage 3: Content and Interactivity
            logger.info("Stage 3: Adding content and interactivity...")
            final_html = await self.generate_content_and_interactivity(
                styled_html, design_context
            )

            return final_html

        except Exception as e:
            logger.error(f"Multi-stage generation failed: {e}")
            raise HTTPException(
                status_code=500, detail=f"Multi-stage generation failed: {str(e)}"
            )

    def _extract_html(self, response_text: str) -> str:
        """Extract HTML from AI response"""
        if "```html" in response_text:
            return response_text.split("```html")[1].split("```")[0].strip()
        elif "<html" in response_text:
            start = response_text.find("<html")
            end = response_text.rfind("</html>") + 7
            if end > 6:
                return response_text[start:end].strip()
        return response_text.strip()

    # Add the missing helper methods
    def _get_meta_description(self, soup):
        meta_desc = soup.find("meta", attrs={"name": "description"})
        return meta_desc.get("content", "") if meta_desc else ""

    def _analyze_header(self, soup):
        header = soup.find("header") or soup.find(
            "div", class_=lambda x: x and "header" in str(x).lower()
        )
        return {
            "exists": bool(header),
            "content": header.get_text(strip=True)[:200] if header else "",
        }

    def _analyze_main_content(self, soup):
        main = soup.find("main") or soup.find(
            "div", class_=lambda x: x and "main" in str(x).lower()
        )
        return {
            "exists": bool(main),
            "sections": len(main.find_all(["section", "div"])) if main else 0,
        }

    def _analyze_sidebar(self, soup):
        sidebar = soup.find("aside") or soup.find(
            "div", class_=lambda x: x and "sidebar" in str(x).lower()
        )
        return {"exists": bool(sidebar)}

    def _analyze_footer(self, soup):
        footer = soup.find("footer") or soup.find(
            "div", class_=lambda x: x and "footer" in str(x).lower()
        )
        return {
            "exists": bool(footer),
            "content": footer.get_text(strip=True)[:200] if footer else "",
        }

    def _detect_grid_systems(self, soup):
        grid_elements = soup.find_all(
            class_=lambda x: x
            and any(term in str(x).lower() for term in ["grid", "col", "row"])
        )
        return {
            "count": len(grid_elements),
            "classes": [" ".join(el.get("class", [])) for el in grid_elements[:5]],
        }

    def _analyze_containers(self, soup):
        containers = soup.find_all(class_=lambda x: x and "container" in str(x).lower())
        return {"count": len(containers)}

    def _extract_navigation_detailed(self, soup):
        nav_elements = soup.find_all(
            ["nav", "div"], class_=lambda x: x and "nav" in str(x).lower()
        )
        navigation = []
        for nav in nav_elements[:3]:
            links = [
                {"text": a.get_text(strip=True), "href": a.get("href", "")}
                for a in nav.find_all("a")[:10]
            ]
            navigation.append({"classes": nav.get("class", []), "links": links})
        return navigation

    def _extract_visual_elements(self, soup, base_url):
        images = []
        for img in soup.find_all("img")[:10]:
            images.append(
                {
                    "src": urljoin(base_url, img.get("src", "")),
                    "alt": img.get("alt", ""),
                    "classes": img.get("class", []),
                }
            )
        return {"images": images}

    def _detect_responsive_patterns(self, soup):
        responsive_classes = soup.find_all(
            class_=lambda x: x
            and any(
                term in str(x).lower()
                for term in [
                    "responsive",
                    "mobile",
                    "tablet",
                    "desktop",
                    "sm",
                    "md",
                    "lg",
                    "xl",
                ]
            )
        )
        return {"count": len(responsive_classes)}

    def _extract_forms(self, soup):
        forms = []
        for form in soup.find_all("form")[:3]:
            inputs = [
                {"type": inp.get("type", ""), "name": inp.get("name", "")}
                for inp in form.find_all("input")
            ]
            forms.append({"action": form.get("action", ""), "inputs": inputs})
        return forms

    def _extract_interactive_elements(self, soup):
        interactive = {
            "buttons": len(soup.find_all("button")),
            "links": len(soup.find_all("a")),
            "modals": len(
                soup.find_all(class_=lambda x: x and "modal" in str(x).lower())
            ),
            "dropdowns": len(
                soup.find_all(class_=lambda x: x and "dropdown" in str(x).lower())
            ),
        }
        return interactive

    def _estimate_section_importance(self, section):
        # Simple importance scoring based on position and content
        score = 0
        if section.find(["h1", "h2"]):
            score += 3
        if any(
            term in " ".join(section.get("class", [])).lower()
            for term in ["hero", "main", "primary"]
        ):
            score += 5
        if len(section.get_text(strip=True)) > 100:
            score += 2
        return score

    async def generate_clone_html_single_pass(
        self, design_context: Dict, screenshot_b64: Optional[str] = None
    ) -> str:
        """Single-pass HTML generation for fallback compatibility"""
        try:
            # Extract key information for focused prompting
            layout_type = design_context.get('layout_analysis', {}).get('structure_type', 'standard')
            content_sections = design_context.get('content_sections', [])
            navigation = design_context.get('navigation_structure', [])
            colors = design_context.get('color_analysis', {})
            typography = design_context.get('typography_system', {})
            visual_elements = design_context.get('visual_elements', {})
            interactive_elements = design_context.get('interactive_elements', {})
            
            # Build focused context sections
            key_content = self._extract_key_content(content_sections)
            navigation_summary = self._summarize_navigation(navigation)
            visual_summary = self._summarize_visual_elements(visual_elements, colors)
            
            prompt = f"""You are a senior frontend developer tasked with creating a pixel-perfect clone of a website. 

    WEBSITE ANALYSIS:
    Layout Type: {layout_type}
    Navigation: {navigation_summary}
    Key Content Sections: {key_content}
    Visual Design: {visual_summary}
    Interactive Elements: {json.dumps(interactive_elements, indent=2)}

    REQUIREMENTS:
    1. Create a complete, responsive HTML5 document with embedded CSS and JavaScript
    2. Use semantic HTML5 elements (header, nav, main, section, article, footer)
    3. Implement the exact layout structure identified: {layout_type}
    4. Apply authentic styling that matches the original design
    5. Include all navigation links and interactive elements
    6. Make it fully responsive (mobile-first approach)
    7. Add smooth transitions and hover effects
    8. Ensure accessibility with proper ARIA labels and semantic markup

    SPECIFIC IMPLEMENTATION GUIDELINES:

    LAYOUT ({layout_type}):
    {self._get_layout_instructions(layout_type, design_context)}

    STYLING PRIORITIES:
    1. Color scheme: Extract and apply the dominant color palette
    2. Typography: Implement the heading hierarchy and font choices
    3. Spacing: Use consistent margins, padding, and white space
    4. Visual hierarchy: Emphasize important content sections
    5. Modern aesthetics: Add subtle shadows, rounded corners, and gradients where appropriate

    CONTENT STRATEGY:
    - Use the actual extracted text content, not placeholder text
    - Maintain the original content structure and flow
    - Preserve the relative importance of different sections
    - Include proper image alt texts and captions

    INTERACTIVITY:
    - Implement working navigation menus (including mobile hamburger if needed)
    - Add form validation and submission handling
    - Create smooth scrolling between sections
    - Include modal dialogs or dropdowns where detected
    - Add loading states and micro-animations

    TECHNICAL REQUIREMENTS:
    - Mobile-first responsive design with breakpoints at 768px and 1024px
    - Cross-browser compatibility (modern browsers)
    - Fast loading with optimized CSS
    - Valid HTML5 and semantic markup
    - Accessible design with proper contrast ratios

    OUTPUT FORMAT:
    Provide ONLY the complete HTML document wrapped in ```html code blocks. No explanations or comments outside the code.

    The HTML should be production-ready and visually indistinguishable from the original website."""

            content_parts = [prompt]
            if screenshot_b64:
                import io
                import base64
                from PIL import Image
                
                image_data = base64.b64decode(screenshot_b64)
                image = Image.open(io.BytesIO(image_data))
                content_parts.extend([
                    "\n\nREFERENCE SCREENSHOT: Use this as the visual reference for styling, layout, and content placement:",
                    image
                ])

            response = self.gemini_model.generate_content(
                content_parts,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,  # Lower temperature for more consistent results
                    max_output_tokens=12000,  # Increased for more detailed output
                    top_p=0.8,
                    top_k=40
                ),
            )

            return self._extract_html(response.text)

        except Exception as e:
            logger.error(f"Enhanced HTML generation failed: {e}")
            raise HTTPException(
                status_code=500, detail=f"Enhanced generation failed: {str(e)}"
            )

    def _extract_key_content(self, content_sections: List[Dict]) -> str:
        """Extract and prioritize key content sections"""
        if not content_sections:
            return "No specific content sections identified"
        
        prioritized = sorted(content_sections, key=lambda x: x.get('estimated_importance', 0), reverse=True)
        
        key_sections = []
        for section in prioritized[:8]:  # Top 8 most important sections
            content_type = section.get('content_type', 'generic')
            text_preview = section.get('text_content', '')[:150] + "..." if len(section.get('text_content', '')) > 150 else section.get('text_content', '')
            classes = ', '.join(section.get('classes', []))
            
            key_sections.append(f"- {content_type.upper()}: {text_preview} (Classes: {classes})")
        
        return '\n'.join(key_sections)

    def _summarize_navigation(self, navigation: List[Dict]) -> str:
        """Summarize navigation structure"""
        if not navigation:
            return "No navigation structure detected"
        
        nav_summary = []
        for i, nav in enumerate(navigation[:3]):  # Top 3 navigation elements
            links = nav.get('links', [])
            if links:
                link_texts = [link.get('text', 'Unknown') for link in links[:8]]  # Top 8 links
                nav_summary.append(f"Nav {i+1}: {', '.join(link_texts)}")
        
        return ' | '.join(nav_summary) if nav_summary else "Basic navigation detected"

    def _summarize_visual_elements(self, visual_elements: Dict, colors: Dict) -> str:
        """Summarize visual design elements"""
        summary_parts = []
        
        # Images
        images = visual_elements.get('images', [])
        if images:
            summary_parts.append(f"{len(images)} images detected")
        
        # Colors
        bg_colors = colors.get('background_colors', [])
        text_colors = colors.get('text_colors', [])
        if bg_colors or text_colors:
            color_info = f"Colors: {len(bg_colors)} background, {len(text_colors)} text colors"
            summary_parts.append(color_info)
        
        return ' | '.join(summary_parts) if summary_parts else "Basic visual styling"

    def _get_layout_instructions(self, layout_type: str, design_context: Dict) -> str:
        """Get specific instructions based on layout type"""
        layout_analysis = design_context.get('layout_analysis', {})
        
        instructions = {
            'grid': """
    - Use CSS Grid for the main layout structure
    - Implement responsive grid columns that adapt to screen size
    - Ensure grid items are properly aligned and spaced
    - Use grid-template-areas for complex layouts""",
            
            'flexbox': """
    - Use Flexbox for the primary layout system
    - Implement flexible containers that adapt to content
    - Use justify-content and align-items for proper alignment
    - Create responsive flex directions (column on mobile, row on desktop)""",
            
            'sidebar': """
    - Implement a sidebar layout with main content area
    - Make sidebar collapsible on mobile devices
    - Use appropriate widths (sidebar: 250-300px, main: remaining space)
    - Ensure proper responsive behavior""",
            
            'standard': """
    - Use a traditional box model layout
    - Implement proper container widths and centering
    - Use floats or flexbox for multi-column sections
    - Ensure responsive stacking on mobile devices"""
        }
        
        base_instruction = instructions.get(layout_type, instructions['standard'])
        
        # Add specific details from layout analysis
        header_info = layout_analysis.get('header', {})
        footer_info = layout_analysis.get('footer', {})
        
        if header_info.get('exists'):
            base_instruction += "\n- Include a prominent header section with navigation"
        
        if footer_info.get('exists'):
            base_instruction += "\n- Include a comprehensive footer section"
        
        return base_instruction

    async def generate_clone_html_iterative(
        self, design_context: Dict, screenshot_b64: Optional[str] = None
    ) -> str:
        """Iterative approach: Generate, review, and refine"""
        try:
            # First pass - generate initial HTML
            initial_html = await self.generate_clone_html_enhanced(design_context, screenshot_b64)
            
            # Second pass - review and refine
            refinement_prompt = f"""Review and improve this HTML code for a website clone:

    CURRENT HTML:
    ```html
    {initial_html[:4000]}...
    ```

    IMPROVEMENT AREAS TO FOCUS ON:
    1. Visual polish - Add subtle animations, better spacing, modern design touches
    2. Code quality - Optimize CSS, remove redundancy, improve structure  
    3. Responsiveness - Ensure smooth mobile experience
    4. Accessibility - Add proper ARIA labels, focus states, semantic markup
    5. Performance - Optimize CSS delivery, reduce unused styles

    Provide the complete improved HTML with these enhancements. Focus on making it production-ready and visually stunning."""

            content_parts = [refinement_prompt]
            if screenshot_b64:
                import io
                import base64
                from PIL import Image
                
                image_data = base64.b64decode(screenshot_b64)
                image = Image.open(io.BytesIO(image_data))
                content_parts.extend(["\n\nTarget design reference:", image])

            refined_response = self.gemini_model.generate_content(
                content_parts,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=10000,
                ),
            )

            refined_html = self._extract_html(refined_response.text)
            return refined_html if refined_html and len(refined_html) > len(initial_html) * 0.8 else initial_html

        except Exception as e:
            logger.error(f"Iterative generation failed: {e}")
            # Fallback to single enhanced pass
            return await self.generate_clone_html_enhanced(design_context, screenshot_b64)