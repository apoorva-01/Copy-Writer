import os
import base64
from openai import OpenAI
import google.generativeai as genai
import pytesseract
from PIL import Image as PILImage
from PIL import Image
import json
import cv2
import numpy as np
from services.layout_segmenter import LayoutSegmenter

class ImageAnalyzer:
    def __init__(self):
        # OpenAI setup
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)
        else:
            self.openai_client = None
            print("⚠️  OpenAI API key not found")
        
        # Tesseract OCR setup
        try:
            # Test if tesseract is available
            pytesseract.get_tesseract_version()
            print("✅ Tesseract OCR initialized")
            self.tesseract_available = True
        except Exception as e:
            print(f"⚠️  Tesseract OCR not available: {e}")
            print("   Install with: brew install tesseract (macOS) or apt-get install tesseract-ocr (Linux)")
            self.tesseract_available = False
        
        # Gemini setup
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ Gemini API initialized")
        else:
            self.gemini_model = None
            print("⚠️  Gemini API key not found")
    
        self.layout_segmenter = LayoutSegmenter()

    def _preprocess_for_ocr(self, image_path):
        """Preprocess image to improve OCR accuracy."""
        try:
            # Read the image with OpenCV
            image = cv2.imread(image_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Otsu's thresholding which automatically finds an optimal threshold value
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            print("✅ Image preprocessed for OCR with Otsu's method")
            # Return the processed PIL image for tesseract
            return Image.fromarray(binary)

        except Exception as e:
            print(f"⚠️  Could not preprocess image: {e}")
            # Fallback to original image
            return PILImage.open(image_path)

    def _extract_text_with_tesseract(self, image_path):
        """
        Extracts all text elements from an image using Tesseract OCR.
        This function only extracts text and does not perform clustering.
        """
        if not self.tesseract_available:
            print("❌ Tesseract OCR not available")
            return None
        try:
            preprocessed_image = self._preprocess_for_ocr(image_path)
                
            print("🔄 Step 2a: Extracting all text elements with OCR...")
            data = pytesseract.image_to_data(
                preprocessed_image, 
                output_type=pytesseract.Output.DICT,
                config='--psm 3'
            )
            
            text_elements = []
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                conf = int(data['conf'][i])
                if conf > 30 and text:
                    text_elements.append({
                        'text': text,
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    })
            print(f"🔍 Found {len(text_elements)} total text elements.")
            return text_elements
        except Exception as e:
            print(f"❌ Error in Tesseract text extraction: {str(e)}")
            return None

    def _map_text_to_blocks(self, blocks, text_elements, image_width, image_height):
        """
        Assigns text elements to the visual blocks they fall within.
        """
        # Create final sections by mapping text to the detected blocks
        final_sections = []
        section_counter = 1  # Always start at 1 for first non-empty section
        for i, block in enumerate(blocks):
            block_x, block_y, block_w, block_h = block['x'], block['y'], block['width'], block['height']
            
            contained_text = []
            for text in text_elements:
                # Check if the text center is inside the block
                text_center_x = text['x'] + text['width'] / 2
                text_center_y = text['y'] + text['height'] / 2
                if (block_x < text_center_x < block_x + block_w) and \
                   (block_y < text_center_y < block_y + block_h):
                    contained_text.append(text)
            
            # Sort text in natural reading order (top-to-bottom, left-to-right)
            contained_text.sort(key=lambda t: (t['y'], t['x']))
            combined_text = ' '.join([t['text'] for t in contained_text])

            if combined_text:
                x_percent = (block_x / image_width) * 100
                y_percent = (block_y / image_height) * 100
                width_percent = (block_w / image_width) * 100
                height_percent = (block_h / image_height) * 100

                final_sections.append({
                        'text': combined_text,
                        'bounding_box': {
                            'x': x_percent,
                            'y': y_percent,
                            'width': width_percent,
                            'height': height_percent
                        },
                        'pixel_coords': {
                        'x': block_x,
                        'y': block_y,
                        'width': block_w,
                        'height': block_h
                    },
                    'section_id': f"section_{section_counter}",
                    'word_count': len(combined_text.split())
                })
                section_counter += 1
        
        print(f"✅ Mapped text to {len(final_sections)} visual blocks.")
        return final_sections

    def analyze_page_sections(self, image_path):
        """
        New Pipeline: Detect layout blocks, then map text to them.
        """
        print("🚀 Starting new layout-based analysis pipeline...")
        try:
            image = PILImage.open(image_path)
            img_width, img_height = image.size

            # Step 1: Detect visual layout blocks using the LayoutSegmenter
            print("🔍 Step 1: Detecting visual layout blocks...")
            visual_blocks = self.layout_segmenter.detect_visual_blocks(image_path)
            if not visual_blocks:
                print("❌ No visual blocks detected. Cannot proceed.")
                # Return a single section for the whole page as a fallback
                visual_blocks = [{'x': 0, 'y': 0, 'width': img_width, 'height': img_height}]

            # Step 2: Extract all text elements using Tesseract
            print("\n🔍 Step 2: Extracting all text from image...")
            text_elements = self._extract_text_with_tesseract(image_path)
            if not text_elements:
                print("❌ No text extracted from image. Cannot map to blocks.")
                return [] # Or handle as imag-only sections

            # Step 3: Map text to the detected visual blocks
            print("\n🔍 Step 3: Mapping text to visual blocks...")
            sections_with_text = self._map_text_to_blocks(visual_blocks, text_elements, img_width, img_height)

            # Step 4: Get copywriting analysis from Gemini for the structured sections
            print("\n🧠 Step 4: Analyzing structured sections with Gemini...")
            final_analyzed_sections = self.analyze_grouped_sections_with_gemini(sections_with_text, image_path)

            if not final_analyzed_sections:
                print("❌ Gemini analysis failed. Returning sections with raw text.")
                return sections_with_text

            print("✅ Pipeline completed successfully!")
            return final_analyzed_sections

        except Exception as e:
            print(f"❌ Error in layout-based analysis pipeline: {e}")
            import traceback
            traceback.print_exc()
            return [{'id': 'error', 'purpose': f'Error: {e}', 'text': ''}]

    def analyze_grouped_sections_with_gemini(self, grouped_sections, image_path):
        """
        Use Gemini to analyze pre-grouped sections for copywriting purposes only.
        This method focuses on semantic analysis rather than spatial grouping.
        
        Args:
            grouped_sections: List of already-grouped sections from algorithmic grouping
            image_path: Path to original image for visual context
            
        Returns:
            List of analyzed sections with copywriting insights
        """
        if not self.gemini_model or not grouped_sections:
            return None
            
        try:
            # Create focused analysis prompt (no spatial grouping needed)
            sections_summary = "\n".join([
                f"Section {section.get('section_id', f'section_{i+1}')}: '{section['text']}'"
                f" [Position: {section['bounding_box']['y']:.1f}% from top, {len(section['text'].split())} words]"
                for i, section in enumerate(grouped_sections)
            ])

            prompt = f"""
            Analyze these {len(grouped_sections)} pre-grouped sections for copywriting effectiveness:

            {sections_summary}

            For each section, provide copywriting analysis in this EXACT JSON format:
            [{{
                "id": "section_1",
                "type": "hero/navigation/content/cta/footer",
                "purpose": "Specific copywriting purpose of this section",
                "text_structure": "Required text structure for optimal conversion",
                "location": "Position description",
                "current_text": "Exact text from the section",
                "copywriting_score": 1-10,
                "improvement_notes": "Specific copywriting improvements needed"
            }}]

            Focus purely on copywriting effectiveness - the spatial grouping is already optimized.
            Be specific about WHY certain copywriting approaches would work better.
            
            EXAMPLE structure:
             [{{
                 "id": "section_1",
                 "type": "hero",
                 "purpose": "Primary value proposition to hook visitors and communicate core benefit",
                 "text_structure": "Headline + subheadline + primary benefit + social proof element",
                 "location": "Top of page",
                 "current_text": "...",
                 "copywriting_score": 7,
                 "improvement_notes": "Could be stronger with more specific benefit and urgency"
             }}]
            """
            
            # Upload image to Gemini for visual context
            import PIL.Image
            pil_image = PIL.Image.open(image_path)
            
            # Configure Gemini with higher token limits and better settings
            import google.generativeai as genai
            response = self.gemini_model.generate_content(
                [prompt, pil_image],
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=8192,  # Increased to max to prevent truncation
                    temperature=0.3,
                    candidate_count=1,
                )
            )
            
            # Parse response with better error handling
            response_text = response.text
            print(f"🔍 Gemini response length: {len(response_text)} characters")
            
            # Extract JSON from response with improved logic
            try:
                # First try to find JSON array in markdown code blocks
                import re
                json_match = re.search(r'```json\s*(\[.*?\])\s*```', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    print("📝 Found JSON in markdown code block")
                else:
                    # Try to find JSON array directly
                    start = response_text.find('[')
                    end = response_text.rfind(']') + 1
                    if start != -1 and end != 0 and end > start:
                        json_str = response_text[start:end]
                        print("📝 Found JSON array in response")
                    else:
                        print("❌ Could not find valid JSON array in Gemini response")
                        print(f"Response preview: {response_text[:500]}...")
                        return None
                
                # Attempt to parse, and if it fails, try to repair.
                try:
                    sections = json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"⚠️ Initial JSON parsing failed ({e}). Attempting to repair.")
                    
                    # Find the last complete-looking object and reconstruct the array
                    last_brace = json_str.rfind('}')
                    if last_brace != -1:
                        # Trim to the end of the last object
                        trimmed_json = json_str[:last_brace + 1]
                        
                        # If the original object was inside an array, close the array
                        if trimmed_json.count('[') > trimmed_json.count(']'):
                            json_str = trimmed_json + ']'
                        else:
                            json_str = trimmed_json

                        print(f"🔧 Repaired JSON string. Retrying parse...")
                        sections = json.loads(json_str) # Retry parsing
                    else:
                        raise e # Re-raise if we couldn't fix it

                # Add bounding boxes from original grouped sections
                for i, section in enumerate(sections):
                    if i < len(grouped_sections):
                        section['bounding_box'] = grouped_sections[i]['bounding_box']
                    else:
                        section['bounding_box'] = {"x": 0, "y": 0, "width": 100, "height": 100}

                    # Make sure to preserve the original section_id
                    section['id'] = grouped_sections[i].get('section_id', f"section_{i+1}")
                
                print(f"✅ Gemini provided copywriting analysis for {len(sections)} sections")
                return sections
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"Attempted to parse: {json_str[:200]}...")
                print(f"Full response text: {response_text[:1000]}...")
                
                # Fallback: return sections with basic analysis
                print("🔄 Using fallback analysis...")
                return self._create_fallback_analysis(grouped_sections)
                
        except Exception as e:
            print(f"❌ Error with Gemini copywriting analysis: {str(e)}")
            print(f"🔄 Using fallback analysis...")
            return self._create_fallback_analysis(grouped_sections)
    
    def _create_fallback_analysis(self, grouped_sections):
        """Create basic analysis when Gemini fails"""
        fallback_sections = []
        for i, section in enumerate(grouped_sections):
            fallback_sections.append({
                'id': section.get('section_id', f'section_{i+1}'),
                'type': 'content',
                'purpose': 'Content section requiring copywriting optimization',
                'text_structure': 'Standard text format',
                'location': f"Section {i+1}",
                'current_text': section.get('text', ''),
                'copywriting_score': 5,
                'improvement_notes': 'Requires copywriting analysis - Gemini analysis failed',
                'bounding_box': section.get('bounding_box', {"x": 0, "y": 0, "width": 100, "height": 100})
            })
        return fallback_sections
    
 