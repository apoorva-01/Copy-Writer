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

    def detect_text_regions_with_tesseract(self, image_path):
        """
        Hybrid approach: Use text clustering to find content centers, then expand to full visual boundaries.
        Returns full visual sections with their text content.
        """
        if not self.tesseract_available:
            print("❌ Tesseract OCR not available")
            return None
        try:
            # Preprocess the image for better OCR results
            preprocessed_image = self._preprocess_for_ocr(image_path)
            img_width, img_height = preprocessed_image.size
            
            print("🔄 Step 1a: Extracting text elements with OCR...")
            # --- OCR text extraction ---
            data = pytesseract.image_to_data(
                preprocessed_image, 
                output_type=pytesseract.Output.DICT,
                config='--psm 3'  # Automatic page segmentation
            )
            text_elements = []
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                conf = int(data['conf'][i])
                if conf < 30 or not text:
                    continue
                text_elements.append({
                    'text': text,
                    'x': data['left'][i],
                    'y': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i],
                    'confidence': conf
                })
            print(f"🔍 Found {len(text_elements)} text elements (OCR)")
            
            if not text_elements:
                return []
            
            print("🔄 Step 1b: Clustering text into content sections...")
            # --- Text-based clustering by vertical position ---
            text_clusters = self._cluster_text_elements(text_elements, img_width, img_height)
            print(f"🎯 Clustered into {len(text_clusters)} content sections")
            
            print("🔄 Step 1c: Using text boundaries with padding for precise section sizing...")
            # --- Use text boundaries with padding instead of expanded visual boundaries ---
            components = []
            for idx, cluster in enumerate(text_clusters):
                # Get text boundaries from cluster
                min_x = min([elem['x'] for elem in cluster['elements']])
                min_y = min([elem['y'] for elem in cluster['elements']])
                max_x = max([elem['x'] + elem['width'] for elem in cluster['elements']])
                max_y = max([elem['y'] + elem['height'] for elem in cluster['elements']])
                
                # Add padding around text boundaries
                padding = 15  # 15px padding on all sides
                padded_min_x = max(0, min_x - padding)
                padded_min_y = max(0, min_y - padding)
                padded_max_x = min(img_width, max_x + padding)
                padded_max_y = min(img_height, max_y + padding)
                
                # Combine all text in proper reading order
                cluster['elements'].sort(key=lambda e: (e['y'], e['x']))
                combined_text = ' '.join([elem['text'] for elem in cluster['elements']])
                avg_confidence = sum([elem['confidence'] for elem in cluster['elements']]) / len(cluster['elements'])
                
                # Use padded text boundaries
                text_width = padded_max_x - padded_min_x
                text_height = padded_max_y - padded_min_y
                
                x_percent = (padded_min_x / img_width) * 100
                y_percent = (padded_min_y / img_height) * 100
                width_percent = (text_width / img_width) * 100
                height_percent = (text_height / img_height) * 100
                
                components.append({
                    'text': combined_text,
                    'bounding_box': {
                        'x': x_percent,
                        'y': y_percent,
                        'width': width_percent,
                        'height': height_percent
                    },
                    'pixel_coords': {
                        'x': padded_min_x,
                        'y': padded_min_y,
                        'width': text_width,
                        'height': text_height
                    },
                    'visual_section_index': idx+1,
                    'section_id': f"content_section_{idx+1}",
                    'word_count': len(combined_text.split()) if combined_text else 0,
                    'element_count': len(cluster['elements']),
                    'confidence': avg_confidence,
                    'text_boundaries': {
                        'x': padded_min_x,
                        'y': padded_min_y,
                        'width': text_width,
                        'height': text_height
                    },
                    'has_text': True,
                    'cluster_center_y': cluster['center_y']
                })
                
                print(f"📦 Section {idx+1}: {len(cluster['elements'])} elements, "
                      f"x={padded_min_x}px-{padded_max_x}px, y={padded_min_y}px-{padded_max_y}px "
                      f"(size={text_width}x{text_height}px, +{padding}px padding)")
            
            print(f"✅ Created {len(components)} sections with padded text sizing")
            return components
            
        except Exception as e:
            print(f"❌ Error in hybrid text clustering pipeline: {str(e)}")
            return None

    def _cluster_text_elements(self, text_elements, img_width, img_height):
        """
        Cluster text elements by vertical proximity to form content sections.
        Uses conservative thresholds to avoid merging distinct sections.
        """
        if not text_elements:
            return []
        
        # Sort elements by Y then X position for natural reading order
        sorted_elements = sorted(text_elements, key=lambda e: (e['y'], e['x']))
        
        clusters = []
        current_cluster = None
        
        # Clustering thresholds
        # Vertical thresholds are based on image height
        base_threshold = max(40, img_height * 0.05)
        max_vertical_gap = 60
        # Horizontal threshold to detect columns
        # TODO: This could be made more dynamic (e.g., based on avg character width)
        max_horizontal_gap = 70 # in pixels

        for element in sorted_elements:
            elem_center_y = element['y'] + (element['height'] / 2)
            
            if current_cluster is None:
                # Start first cluster
                current_cluster = {
                    'elements': [element],
                    'min_y': element['y'],
                    'max_y': element['y'] + element['height'],
                    'center_y': elem_center_y,
                    'texts': [element['text']]
                }
            else:
                # --- Heuristics for dynamic clustering ---
                # Be more willing to group small text elements or build up new, small clusters.
                is_new_element_small = len(element['text'].split()) <= 3
                is_cluster_small = len(current_cluster['elements']) <= 2

                # If we have a small new element or a small cluster, be more lenient with grouping.
                # This helps group small, related text without merging large, distinct blocks.
                vertical_gap_allowance = max_vertical_gap * 1.5 if is_new_element_small or is_cluster_small else max_vertical_gap
                horizontal_gap_allowance = max_horizontal_gap * 1.5 if is_new_element_small or is_cluster_small else max_horizontal_gap
                
                # 1. Check vertical proximity
                distance_to_cluster = abs(elem_center_y - current_cluster['center_y'])
                vertical_gap = element['y'] - current_cluster['max_y']
                is_vertically_close = distance_to_cluster < base_threshold and vertical_gap < vertical_gap_allowance

                # 2. Check horizontal proximity
                cluster_max_x = max(e['x'] + e['width'] for e in current_cluster['elements'])
                horizontal_gap = element['x'] - cluster_max_x
                is_horizontally_close = horizontal_gap < horizontal_gap_allowance

                # 3. Check for explicit content-based separators
                should_separate = self._should_create_new_section(
                    current_cluster, element, vertical_gap
                )
                
                # Add to cluster ONLY if both vertically and horizontally close
                # This handles both paragraphs (vertically close, horizontally reset)
                # and columns (vertically similar, horizontally separated)
                if is_vertically_close and is_horizontally_close and not should_separate:
                    # Add to current cluster
                    current_cluster['elements'].append(element)
                    current_cluster['min_y'] = min(current_cluster['min_y'], element['y'])
                    current_cluster['max_y'] = max(current_cluster['max_y'], element['y'] + element['height'])
                    current_cluster['texts'].append(element['text'])
                    # Update cluster center (weighted average)
                    total_elements = len(current_cluster['elements'])
                    current_cluster['center_y'] = (
                        (current_cluster['center_y'] * (total_elements - 1) + elem_center_y) / total_elements
                    )
                else:
                    # Finish current cluster and start new one
                    clusters.append(current_cluster)
                    current_cluster = {
                        'elements': [element],
                        'min_y': element['y'],
                        'max_y': element['y'] + element['height'],
                        'center_y': elem_center_y,
                        'texts': [element['text']]
                    }
        
        # Don't forget the last cluster
        if current_cluster:
            clusters.append(current_cluster)
        
        return clusters

    def _should_create_new_section(self, current_cluster, new_element, gap_size):
        """
        Determine if a new element should start a new section based on content patterns.
        Helps prevent merging distinct sections like FAQ, Key Ingredients, etc.
        """
        new_text = new_element['text'].lower().strip()
        
        # Check for section header patterns that indicate new content sections
        section_headers = [
            'faq', 'frequently asked questions', 'key ingredients', 'ingredients',
            'how to use', 'directions', 'benefits', 'features', 'about',
            'testimonials', 'reviews', 'what is', 'why choose', 'specifications',
            'details', 'description', 'overview', 'summary', 'highlights'
        ]
        
        # If new element looks like a section header, create new section
        for header in section_headers:
            if header in new_text and len(new_text) < 50:  # Short text likely to be headers
                return True
        
        # Check for significant gap that suggests section break
        if gap_size > 80:  # Large gap = likely new section
            return True
        
        # Check current cluster content to see if it's already substantial
        cluster_word_count = sum(len(text.split()) for text in current_cluster['texts'])
        if cluster_word_count > 25:  # Current cluster already has substantial content
            # Be more likely to start new section
            if gap_size > 45:  # Lower threshold for new section
                return True
        
        # Check for pattern changes (short text after long text or vice versa)
        current_avg_length = sum(len(text) for text in current_cluster['texts']) / len(current_cluster['texts'])
        new_text_length = len(new_text)
        
        # If there's a significant length pattern change + reasonable gap
        if abs(current_avg_length - new_text_length) > 20 and gap_size > 35:
            return True
        
        return False

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
                f"Section {i+1}: '{section['text']}'"
                f" [Position: {section['bounding_box']['y']:.1f}% from top, {len(section['text'].split())} words]"
                for i, section in enumerate(grouped_sections)
            ])
            
            prompt = f"""
            Analyze these pre-grouped webpage sections for copywriting effectiveness and purpose.
            Each section has already been intelligently grouped by visual proximity.
            
            WEBPAGE SECTIONS TO ANALYZE:
            {sections_summary}
            
            For each section, provide copywriting analysis focusing on:
            
            1. **Communication Goal**: What is this section trying to achieve? 
               (e.g., "build trust", "highlight benefits", "create urgency", "call to action", "social proof")
            
            2. **Copywriting Purpose**: Detailed explanation of the section's role in the customer journey
            
            3. **Effectiveness**: How well does the current text achieve its purpose?
            
            4. **Improvement Strategy**: What copywriting structure would be more effective?
            
            Return a JSON array where each object has:
            - id: "section_1", "section_2", etc.
            - type: primary communication goal (e.g., "hero", "benefits", "social_proof", "cta") 
            - purpose: detailed copywriting analysis
            - text_structure: recommended structure for maximum effectiveness
            - location: simple position description
            - current_text: the actual content from the section
            - copywriting_score: effectiveness rating 1-10
            - improvement_notes: specific suggestions for better copywriting
            
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
            
            response = self.gemini_model.generate_content([prompt, pil_image])
            
            # Parse response
            response_text = response.text
            
            # Extract JSON from response
            try:
                start = response_text.find('[')
                end = response_text.rfind(']') + 1
                if start != -1 and end != 0:
                    json_str = response_text[start:end]
                    sections = json.loads(json_str)
                    
                    # Add bounding boxes from original grouped sections
                    for i, section in enumerate(sections):
                        if i < len(grouped_sections):
                            section['bounding_box'] = grouped_sections[i]['bounding_box']
                        else:
                            section['bounding_box'] = {"x": 0, "y": 0, "width": 100, "height": 100}
                    
                    print(f"🧠 Gemini provided copywriting analysis for {len(sections)} sections")
                    return sections
                else:
                    print("❌ Could not find valid JSON in Gemini response")
                    return None
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"Response text: {response_text[:500]}...")
                return None
                
        except Exception as e:
            print(f"❌ Error with Gemini copywriting analysis: {str(e)}")
            return None

    def analyze_page_sections(self, image_path):
        """
        Analyze an uploaded image to identify sections and their purposes.
        Uses Tesseract OCR + OpenCV visual sections + Gemini for copywriting analysis.
        This is the ONLY pipeline used - no OpenAI fallback as per user request.
        """
        print("🚀 Starting Tesseract OCR + OpenCV Visual Sections + Gemini pipeline")
        
        # Check if both tools are available
        if not self.tesseract_available:
            return [{
                'id': 'section_1',
                'type': 'error',
                'purpose': 'Tesseract OCR not available. Please install: brew install tesseract (macOS)',
                'text_structure': 'Tesseract installation required',
                'location': 'Configuration error',
                'current_text': '',
                'bounding_box': {"x": 0, "y": 0, "width": 100, "height": 100}
            }]
            
        if not self.gemini_model:
            return [{
                'id': 'section_1',
                'type': 'error', 
                'purpose': 'Gemini API not available. Please check your GEMINI_API_KEY.',
                'text_structure': 'Gemini API setup required',
                'location': 'Configuration error',
                'current_text': '',
                'bounding_box': {"x": 0, "y": 0, "width": 100, "height": 100}
            }]

        try:
            # Step 1: Get precise text regions with Tesseract OCR (free!)
            print("🔍 Step 1: Detecting text regions with Tesseract OCR...")
            text_regions = self.detect_text_regions_with_tesseract(image_path)
            
            if not text_regions or len(text_regions) == 0:
                print("❌ Tesseract OCR returned no text regions")
                return [{
                    'id': 'section_1',
                    'type': 'error',
                    'purpose': 'No text detected by Tesseract OCR. Image may be blank or have no readable text.',
                    'text_structure': 'No text found',
                    'location': 'Full image',
                    'current_text': '',
                    'bounding_box': {"x": 0, "y": 0, "width": 100, "height": 100}
                }]
            
            print(f"✅ Tesseract OCR detected {len(text_regions)} visual regions")
            
            # Step 2: Use all visual regions directly (including empty ones)
            print("🎯 Step 2: Using all visual regions directly (including empty sections)...")
            
            # Use text_regions directly as visual_sections (they now represent visual regions with mapped text)
            visual_sections = text_regions
            
            if not visual_sections or len(visual_sections) == 0:
                print("❌ No visual regions detected")
                return [{
                    'id': 'section_1',
                    'type': 'error',
                    'purpose': 'No visual regions detected by OpenCV.',
                    'text_structure': 'No regions found',
                    'location': 'Full image',
                    'current_text': '',
                    'bounding_box': {"x": 0, "y": 0, "width": 100, "height": 100}
                }]
            
            print(f"✅ Using all {len(visual_sections)} visual regions (text + empty sections)")
                
            # Step 3: Analyze visual sections with Gemini (focused on copywriting)
            print("🧠 Step 3: Analyzing visual sections with Gemini for copywriting insights...")
            sections = self.analyze_grouped_sections_with_gemini(visual_sections, image_path)
            
            if not sections or len(sections) == 0:
                print("❌ Gemini analysis failed or returned no sections")
                # Return the visual sections as fallback
                fallback_sections = []
                for i, section in enumerate(visual_sections):
                    section_type = 'content' if section.get('has_text', False) else 'empty'
                    fallback_sections.append({
                        'id': f'section_{i+1}',
                        'type': section_type,
                        'purpose': f'Visual region {section.get("visual_section_index", i+1)} (Gemini analysis failed)',
                        'text_structure': 'Direct visual region mapping' if section.get('has_text', False) else 'Empty visual region',
                        'location': f'Visual region {section.get("visual_section_index", i+1)} at {section["bounding_box"]["y"]:.1f}% from top',
                        'current_text': section.get('text', ''),
                        'bounding_box': section['bounding_box'],
                        'has_text': section.get('has_text', False),
                        'word_count': section.get('word_count', 0),
                        'element_count': section.get('element_count', 0)
                    })
                return fallback_sections
            
            print(f"✅ Gemini analyzed {len(sections)} visual sections for copywriting insights")
            
            # Step 4: Ensure all required fields exist
            for section in sections:
                if 'bounding_box' not in section or not isinstance(section['bounding_box'], dict):
                    section['bounding_box'] = {"x": 0, "y": 0, "width": 100, "height": 100}
                else:
                    bbox = section['bounding_box']
                    for coord in ['x', 'y', 'width', 'height']:
                        if coord not in bbox:
                            bbox[coord] = 0
            
            print("🎯 Visual section pipeline completed successfully!")
            return sections
                
        except Exception as e:
            print(f"❌ Error in visual section pipeline: {str(e)}")
            return [{
                'id': 'section_1',
                'type': 'error',
                'purpose': f'Pipeline error: {str(e)}',
                'text_structure': 'Error occurred',
                'location': 'Pipeline failure',
                'current_text': '',
                'bounding_box': {"x": 0, "y": 0, "width": 100, "height": 100}
            }]
    
 