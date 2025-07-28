import os
import json
from openai import OpenAI
import google.generativeai as genai

class CopyGenerator:
    def __init__(self):
        # OpenAI setup
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            self.client = OpenAI(api_key=openai_api_key)
        else:
            self.client = None
            print("⚠️  OpenAI API key not found - OpenAI features will not work without it")
        
        # Gemini setup
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            
            # System instruction for Gemini
            system_instruction = """You are an expert copywriter and conversion optimization specialist. Your expertise includes:

- Advanced sales psychology and persuasion techniques
- Brand voice adaptation and tone matching
- High-converting copy generation with specific psychological triggers
- JSON formatting and structured data output
- Understanding of different audience segments and their pain points

CORE COPYWRITING PRINCIPLES (Follow these religiously):

1. Concrete & Falsifiable: Every claim must be a specific, verifiable fact that creates a mental image. Replace vague adjectives ("high quality") with provable details ("heavy-duty aluminum frames"). If you can't see it or prove it, cut it.

2. Customer's Language First: Build copy from the exact phrasing, metaphors, and pain points found in customer reviews and interviews. This makes the copy unique and impossible for a competitor to steal.

3. Clarity Above All: The primary goal is to be understood in seconds. Use short sentences and paragraphs (max 2-3 lines) to make the copy scannable and easy to follow.

4. Benefit, Then Proof: Every claim must answer the reader's "So what?" by connecting to a meaningful benefit, then immediately provide proof (data, testimonials, specifics). Don't just talk; point to the evidence.

5. Create Conflict: Frame the narrative by contrasting the new way with the old way, your product with a competitor, or through surprising juxtapositions. A story needs conflict.

6. Complete the Story Arc: Guide the reader from their painful "before" state to the desirable "after" state, with the product as the clear bridge.

7. Serve, Don't Sell: Frame the copy as a generous offer that will improve the reader's life, not a demand for their money. This builds rapport.

8. Prioritize Rhythm: Use parallelism and repetition deliberately to make phrases pleasing and memorable.

9. Cut Relentlessly: Eliminate every word, sentence, or idea that isn't doing persuasive work. "Word-shaped air" weakens your argument.

10. Focus CTAs on the Payoff: Calls to action must promise what the user will get, not what they must do (e.g., "Get My Plan" vs. "Submit").

Always follow instructions precisely and return exactly the format requested. Focus on creating compelling, conversion-focused copy that matches the brand's voice and resonates with their target audience."""

            self.gemini_model = genai.GenerativeModel(
                'gemini-1.5-flash',
                system_instruction=system_instruction
            )
            print("✅ Gemini API configured successfully with system instructions")
        else:
            self.gemini_model = None
            print("⚠️  Gemini API key not found - Gemini features will not work without it")
        
        # Define the copywriter framework template
        # self.framework_prompt = """
        # COPYWRITER FRAMEWORK:
        
        # Your copy must follow these essential elements:
        # 1. HOOK - Start with something that grabs attention and creates curiosity
        # 2. PROBLEM/PAIN - Identify the specific problem your audience faces
        # 3. AGITATION - Make them feel the pain of not solving this problem
        # 4. SOLUTION - Present your product/service as the perfect solution
        # 5. BENEFITS - Focus on benefits, not features (what's in it for them)
        # 6. SOCIAL PROOF - Include credibility indicators when relevant
        # 7. OBJECTION HANDLING - Address their likely concerns or hesitations
        # 8. URGENCY/SCARCITY - Create a reason to act now (when appropriate)
        # 9. CLEAR CTA - Tell them exactly what to do next
        
        # RHYTHM AND FLOW:
        # - Vary sentence length for better readability
        # - Use short, punchy sentences for impact
        # - Create natural breaks and breathing room
        # - Build momentum toward the call to action
        
        # CONFLICT AND STORY:
        # - Present a clear before/after scenario
        # - Show transformation or improvement
        # - Create emotional connection with the reader
        # - Make the reader the hero of their own story
        # """
    
    # ============================================
    # NEW 2-STEP COPY GENERATION PIPELINE
    # ============================================

    def extract_structured_product_data_batched(self, sections, brand_data, additional_context='', batch_size=25):
        """
        Process sections in batches to handle very large numbers of sections.
        Useful when you have 40+ sections that might exceed token limits.
        """
        if len(sections) <= batch_size:
            # If sections fit in one batch, use the regular method
            return self.extract_structured_product_data(sections, brand_data, additional_context)
        
        print(f"🔄 PROCESSING {len(sections)} SECTIONS IN BATCHES OF {batch_size}")
        
        all_sections_data = []
        overall_ideas = []
        
        # Process sections in batches
        for i in range(0, len(sections), batch_size):
            batch_sections = sections[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(sections) + batch_size - 1) // batch_size
            
            print(f"📦 PROCESSING BATCH {batch_num}/{total_batches} ({len(batch_sections)} sections)")
            
            try:
                batch_result = self.extract_structured_product_data(batch_sections, brand_data, additional_context)
                
                if 'sections' in batch_result:
                    all_sections_data.extend(batch_result['sections'])
                if 'ideas' in batch_result:
                    overall_ideas.append(batch_result['ideas'])
                    
                print(f"✅ BATCH {batch_num} COMPLETED - {len(batch_result.get('sections', []))} sections processed")
                
            except Exception as e:
                print(f"❌ BATCH {batch_num} FAILED: {e}")
                # Continue with other batches
                continue
        
        # Combine results
        combined_result = {
            'sections': all_sections_data,
            'ideas': '; '.join(overall_ideas) if overall_ideas else "Multiple batches processed successfully."
        }
        
        print(f"🎯 BATCHED PROCESSING COMPLETE: {len(all_sections_data)} total sections generated")
        return combined_result

    def extract_structured_product_data(self, sections, brand_data, additional_context=''):
        """
        NEW Step 1: Generate compelling copy for each section using brand context
        Returns JSON with section-based copy data (using Gemini)
        """
        if not self.gemini_model:
            raise Exception("Gemini API key not configured. Please add GEMINI_API_KEY to your .env file.")
        
        # Summarize brand data
        brand_summary = ""
        if isinstance(brand_data, dict):
            for key, value in brand_data.items():
                if value and key != 'brand_name':
                    brand_summary += f"{key}: {str(value)}...\n"
        
        # Format sections for copy generation and preserve crop images
        sections_with_crops = {}  # Store crop_image data for later use
        sections_summary = ""
        for section in sections:
            section_id = section.get('id', '')
            # Store crop_image data
            if 'crop_image' in section:
                sections_with_crops[section_id] = section['crop_image']
            
            sections_summary += f"Section ID: {section_id}\n"
            sections_summary += f"Purpose: {section.get('purpose', '')}\n"
            sections_summary += f"Text Structure: {section.get('text_structure', '')}\n"
            sections_summary += f"Location: {section.get('location', '')}\n"
            sections_summary += f"Current Text: {section.get('current_text', 'No existing text')}\n\n"
        
        # Adjust number of options and token limit based on section count
        num_sections = len(sections)
        if num_sections <= 3:
            options_per_section = "3-4"
            max_tokens = 8000
        elif num_sections <= 5:
            options_per_section = "3"
            max_tokens = 12000
        elif num_sections <= 10:
            options_per_section = "2-3"
            max_tokens = 20000
        elif num_sections <= 20:
            options_per_section = "2"
            max_tokens = 30000
        else:
            # For very large numbers of sections, reduce options per section
            options_per_section = "2"
            max_tokens = 50000
            
        print(f"📥 INPUT TO CALL #2:")
        print(f"Total length of brand_data (as string): {len(str(brand_data))}")
        # print(f"Brand Data: {brand_data}")
        # print(f"Brand Data Keys: {list(brand_data.keys()) if brand_data else 'None'}")
        print(f"Sections: {num_sections} sections to generate copy for")
        print(f"Max tokens allocated: {max_tokens}")
        print(f"Additional Context: {additional_context[:100]}..." if additional_context else "Additional Context: None")
        
        prompt = f"""
You are an expert copywriter and conversion optimization specialist. Your job is to IMPROVE the existing copy in each section by making it more compelling, brand-aligned, and conversion-focused.

SECTIONS TO IMPROVE:
{sections_summary}

CURRENT COPY: Current Text in SECTIONS TO IMPROVE

ADDITIONAL CONTEXT:
{additional_context[:500] if additional_context else ''}

BRAND VOICE GUIDELINES:
- Tone: Professional and approachable
- Style: Clear and direct
- Avoid: Overly salesy language

BRAND PERSONALITY:
Brand: {brand_data.get('brand_name', '')}
Target Audience: {brand_data.get('company_info', {}).get('target_audience', '')}
            
TASK:
Rewrite the CURRENT COPY to perfectly match this brand's voice and tonality. 
            
Key requirements:
1. Keep all the sales psychology and framework structure intact
2. Adjust word choice, sentence style, and phrasing to match the brand voice
3. Use language that resonates with the target audience
4. Avoid anything listed in the "avoid" section
5. Make it sound authentically like this brand would speak
6. Maintain the same length and structure
            
The copy should feel like it was written by someone who truly understands this brand's personality and how they communicate with their customers.

CRITICAL INSTRUCTIONS:
- Each section has "Current Text" which is the EXISTING content that needs improvement
- DO NOT ignore the current text - use it as your starting point and make it better
- If current text is empty/missing, create new copy that fits the purpose and structure
- Keep the core message and intent of the current text but enhance clarity, persuasion, and brand alignment
- Generate {options_per_section} improved versions per section, ranked by conversion potential

TASK: Return a JSON object with this structure:

{{
  "ideas": "Overall strategic insights and improvement recommendations across all sections based on current content analysis",
  "sections": [
    {{
      "section_name": "section1",
      "communicates": "what this section is trying to communicate",
      "text_structure": "text structure needed for this section",
      "copy_options": [
        {{
          "generated_text": "improved version of current text with highest conversion potential",
          "confidence": 95,
          "justification": "specific improvements made to current text and why this converts better"
        }},
        {{
          "generated_text": "alternative improved version of current text",
          "confidence": 87,
          "justification": "different approach to improving the current text"
        }},
        {{
          "generated_text": "third improved version", 
          "confidence": 82,
          "justification": "another way to enhance the existing content"
        }},
        {{
          "generated_text": "fourth improved version",
          "confidence": 78,
          "justification": "additional improvement approach"
        }}
      ]
    }},
    {{
      "section_name": "section2",
      "communicates": "what this section is trying to communicate", 
      "text_structure": "text structure needed for this section",
      "copy_options": [
        {{
          "generated_text": "best improved version for section 2",
          "confidence": 93,
          "justification": "how this improves upon the current text"
        }}
      ]
    }}
  ]
}}

IMPROVEMENT GUIDELINES:
- Generate {options_per_section} improved versions per section, sorted by conversion confidence (highest first)
- Confidence scores should be 70-100, reflecting realistic conversion potential
- Justifications should explain specific improvements made to the current text and conversion tactics used
- Use brand context and additional context to make improvements relevant and authentic
- Match the text structure requirements for each section
- For the "ideas" field, provide strategic insights about the overall content strategy and potential improvements
- Focus on different improvement approaches: clarity, urgency, social proof, benefits, emotional triggers, etc.
- Make each option distinctly different in approach while maintaining brand voice
- If current text is weak or missing, create strong foundational copy that serves the section purpose

OUTPUT: Valid JSON only, no additional text or formatting.
"""

        response = self.gemini_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.3,
            )
        )
        # print(f"📥 OUTPUT FROM CALL #2 (Gemini):")
        
        json_content = response.text.strip()
        finish_reason = response.candidates[0].finish_reason if response.candidates else None
        
        # print(f"Response: {json_content}")
        print(f"Finish reason: {finish_reason}")
        
        # Check if response was truncated
        if finish_reason and finish_reason.name == 'MAX_TOKENS':
            raise Exception("Gemini response was truncated due to length limit. The copy generation is too long. Please try again or reduce the number of sections.")
        
        # Extract JSON from markdown code blocks if present (similar to HTML fix)
        if json_content.startswith('```json'):
            # Remove opening ```json
            json_content = json_content[7:]
            # Remove closing ```
            if json_content.endswith('```'):
                json_content = json_content[:-3]
        elif json_content.startswith('```'):
            # Remove opening ``` (any language)
            json_content = json_content[3:]
            # Remove closing ```
            if json_content.endswith('```'):
                json_content = json_content[:-3]
        
        # Clean up any remaining whitespace
        json_content = json_content.strip()
        
        print(f"📤 CLEANED JSON CONTENT:")
        print(f"Original length: {len(response.text)}")
        print(f"Cleaned length: {len(json_content)}")
        print(f"Starts with {{: {json_content.startswith('{')}")
        print(f"Ends with }}: {json_content.endswith('}')}")
        
        try:
            import json
            parsed_data = json.loads(json_content)
            sections_generated = len(parsed_data.get('sections', []))
            sections_expected = len(sections)
            
            print(f"✅ JSON PARSING SUCCESS - Found {sections_generated} sections")
            
            # Check if all sections were generated
            if sections_generated < sections_expected:
                print(f"⚠️  WARNING: Only {sections_generated}/{sections_expected} sections were generated")
                print(f"📊 COMPLETION RATE: {(sections_generated/sections_expected)*100:.1f}%")
                
                # If significantly fewer sections were generated, it might be a token limit issue
                if sections_generated < sections_expected * 0.8:  # Less than 80% completion
                    print(f"🚨 POSSIBLE TOKEN LIMIT REACHED - Consider:")
                    print(f"   - Reducing number of sections per batch")
                    print(f"   - Current token limit: {max_tokens}")
                    print(f"   - Finish reason: {finish_reason}")
            
            # Add crop_image data back to sections
            if 'sections' in parsed_data and sections_with_crops:
                for section in parsed_data['sections']:
                    section_name = section.get('section_name', '')
                    if section_name in sections_with_crops:
                        section['crop_image'] = sections_with_crops[section_name]
                        # print(f"✅ Added crop_image to {section_name}: {sections_with_crops[section_name]}")
            
            return parsed_data
        except json.JSONDecodeError as e:
            print(f"❌ JSON PARSING FAILED: {e}")
            print(f"Content length: {len(json_content)}")
            print(f"Last 100 chars: ...{json_content[-100:]}")
            
            # Check if response was likely truncated (additional check)
            if not json_content.strip().endswith('}'):
                raise Exception("OpenAI response appears to be incomplete (doesn't end with '}'}). The response may have been truncated. Please try again.")
            else:
                raise Exception(f"Failed to parse JSON response: {str(e)}. Please try again.")

    def generate_copy_from_document(self, document_content, brand_data, additional_context=''):
        """Generate marketing copy directly from document content - similar to image pipeline"""
        try:
            print("\n" + "="*50)
            print("🔍 DOCUMENT COPY GENERATION - CREATING MARKETING CONTENT")
            print("="*50)
            
            # Step 1: First, detect if there are multiple products in the document
            detection_prompt = f"""
Analyze this document and determine if it contains information about multiple products or just one product.

DOCUMENT CONTENT:
{document_content[:3000]}

Instructions:
1. Look for clear product separations (headings, product names, different sections)
2. Count how many distinct products are described
3. If multiple products exist, provide their names and where they appear in the document

Respond with ONLY a JSON object:
{{
    "multiple_products": true/false,
    "product_count": number,
    "products": [
        {{
            "name": "product name",
            "start_text": "first few words where this product appears",
            "description": "brief description"
        }}
    ]
}}
"""

            print("🔍 STEP 1A: Detecting products in document...")
            
            if self.gemini_model:
                detection_response = self.gemini_model.generate_content(
                    detection_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=1000,
                        temperature=0.1,
                    )
                )
                detection_raw = detection_response.text
            else:
                detection_response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": detection_prompt}],
                    max_tokens=1000,
                    temperature=0.1
                )
                detection_raw = detection_response.choices[0].message.content.strip()
            
            # Parse detection results
            try:
                import json
                import re
                
                json_match = re.search(r'\{.*\}', detection_raw, re.DOTALL)
                if json_match:
                    detection_data = json.loads(json_match.group(0))
                else:
                    detection_data = {"multiple_products": False, "product_count": 1}
                    
                print(f"📊 Product detection: {detection_data.get('product_count', 1)} products found")
                
            except Exception as e:
                print(f"⚠️ Detection parsing failed: {e}")
                detection_data = {"multiple_products": False, "product_count": 1}
            
            # Step 1B: Extract marketing data based on detection results
            if detection_data.get("multiple_products", False) and detection_data.get("product_count", 1) > 1:
                print(f"🎯 Processing {detection_data['product_count']} products separately...")
                return self._process_multiple_products(document_content, brand_data, additional_context, detection_data)
            else:
                print("📝 Processing as single product...")
                return self._process_single_product(document_content, brand_data, additional_context)
            
        except Exception as e:
            print(f"❌ Error in document copy generation: {e}")
            import traceback
            traceback.print_exc()
            
            # Try to provide more specific error information
            if "gemini" in str(e).lower():
                error_msg = f"Gemini API error: {str(e)}. Please check your API key and quota."
            elif "openai" in str(e).lower():
                error_msg = f"OpenAI API error: {str(e)}. Falling back to basic processing."
            else:
                error_msg = f"Processing error: {str(e)}"
            
            return {
                'final_html': f'<html><body><h1>Error</h1><p>{error_msg}</p></body></html>',
                'section_copy_data': {},
                'success': False,
                'error': str(e)
            }

    def _process_single_product(self, document_content, brand_data, additional_context):
        """Process document as a single product"""
        try:
            product_analysis_prompt = f"""
You are an expert copywriter creating detailed, conversion-focused product descriptions.

DOCUMENT CONTENT:
{document_content[:8000]}  # Use more content for better analysis

BRAND CONTEXT:
- Brand: {brand_data.get('brand_name', 'Unknown')}
- Voice: {brand_data.get('brand_voice', 'Professional and engaging')}
- Target Audience: {brand_data.get('target_audience', 'General audience')}
- Key Messages: {brand_data.get('key_messages', 'Focus on value and benefits')}

ADDITIONAL CONTEXT:
{additional_context}

TASK: Create a comprehensive product analysis and return ONLY valid JSON:

{{
    "product_name": "extracted product name",
    "claims": [
        "Natural ingredients",
        "Aluminum-free", 
        "For sensitive skin"
    ],
    "main_description": "Compelling 2-3 sentence product description that hooks the reader and communicates core benefits. Focus on transformation and results.",
    "key_benefits": [
        {{
            "title": "All-Day Performance",
            "description": "Specific benefit explanation with proof points and ingredients that make this possible",
            "supporting_ingredients": ["Key ingredient 1", "Key ingredient 2"]
        }},
        {{
            "title": "Gentle & Effective", 
            "description": "Another key benefit with specific details and proof",
            "supporting_ingredients": ["Supporting ingredient 1", "Supporting ingredient 2"]
        }},
        {{
            "title": "Long-lasting Results", 
            "description": "Third benefit with specifics and evidence",
            "supporting_ingredients": ["Active ingredient 1", "Active ingredient 2"]
        }}
    ],
    "instructions": "Clear, specific usage instructions",
    "volume": "Product size/volume if mentioned",
    "why_it_works": "2-3 sentences explaining the science or reasoning behind why this product is effective",
    "copy_variations": [
        {{
            "angle": "Performance-focused",
            "headline": "Alternative headline emphasizing results",
            "description": "Why this angle works for performance-oriented customers"
        }},
        {{
            "angle": "Natural/Clean",
            "headline": "Headline emphasizing natural ingredients", 
            "description": "Why this approach resonates with health-conscious buyers"
        }},
        {{
            "angle": "Problem-solution",
            "headline": "Headline addressing specific pain point", 
            "description": "Why this angle works for problem-aware customers"
        }}
    ],
    "competitive_advantages": ["unique advantage 1", "unique advantage 2"],
    "target_audience_insights": "Specific insights about who this product is for and their motivations",
    "emotional_triggers": ["desire trigger", "fear trigger", "aspiration trigger"]
}}

Focus on extracting specific ingredients, benefits, and proof points from the document. Make the analysis comprehensive and conversion-focused.
"""

            print("🧠 STEP 1B: Analyzing single product for detailed marketing insights...")
            
            # Use Gemini for document analysis
            if self.gemini_model:
                analysis_response = self.gemini_model.generate_content(
                    product_analysis_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=3000,
                        temperature=0.3,
                    )
                )
                raw_response = analysis_response.text
            else:
                # Fallback to OpenAI if Gemini is not available
                analysis_response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": product_analysis_prompt}],
                    max_tokens=3000,
                    temperature=0.3
                )
                raw_response = analysis_response.choices[0].message.content.strip()
            
            import json
            import re
            
            print(f"🔍 Raw AI response length: {len(raw_response)} characters")
            print(f"🔍 Response preview: {raw_response[:300]}...")
            
            try:
                # Try to extract JSON from the response if it's wrapped in markdown
                json_match = re.search(r'```json\s*(.*?)\s*```', raw_response, re.DOTALL)
                if json_match:
                    json_content = json_match.group(1)
                    print("📝 Found JSON in markdown code block")
                else:
                    # Try to find JSON between curly braces
                    json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                    if json_match:
                        json_content = json_match.group(0)
                        print("📝 Found JSON in response")
                    else:
                        json_content = raw_response
                        print("📝 Using full response as JSON")
                
                marketing_data = json.loads(json_content)
                print(f"✅ Marketing analysis complete: {marketing_data.get('product_name', 'Product')} identified")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {str(e)}")
                print(f"🔍 Attempted to parse: {json_content[:500]}...")
                
                # Enhanced fallback - try to extract key information manually
                marketing_data = self._extract_marketing_data_fallback(document_content, raw_response)
                print("🔄 Using enhanced fallback with manual extraction")

            # Step 2: Generate multiple copy options for each element
            print("📝 STEP 2: Generating multiple copy options for all product elements...")
            copy_options = self._generate_copy_options(marketing_data, brand_data)
            
            # Format the complete product data with all copy options
            structured_product = self._format_product_with_options(marketing_data, copy_options, brand_data)
            
            print(f"✅ STRUCTURED PRODUCT DATA GENERATED")
            print("="*50 + "\n")
            
            return {
                'section_copy_data': {
                    'single_product': True,
                    'product_data': marketing_data,
                    'structured_data': {
                        'products': [structured_product]
                    },
                    'summary': f"Generated structured copy data for {marketing_data.get('product_name', 'Product')}"
                },
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Error processing single product: {e}")
            import traceback
            traceback.print_exc()
            return {
                'final_html': f'Error processing single product: {str(e)}',
                'section_copy_data': {},
                'success': False,
                'error': str(e)
            }

    def _generate_copy_options(self, product_data, brand_data):
        """Generate multiple copy options for each product element"""
        try:
            copy_options_prompt = f"""
You are a professional copywriter. Generate comprehensive copy variations for this product.

PRODUCT DATA:
{json.dumps(product_data, indent=2)}

BRAND: {brand_data.get('brand_name', 'Unknown')}
BRAND VOICE: {brand_data.get('brand_voice', 'Professional and engaging')}

CRITICAL: Return ONLY valid JSON. No markdown, no explanations, no code blocks. Just the JSON object.

Required JSON structure:
{{
    "product_name_options": [
        {{
            "text": "Product Name Option 1",
            "angle": "Direct/Descriptive",
            "confidence": 92,
            "justification": "Clear and straightforward naming that builds trust"
        }},
        {{
            "text": "Product Name Option 2", 
            "angle": "Benefit-focused",
            "confidence": 88,
            "justification": "Emphasizes key benefit in the name"
        }},
        {{
            "text": "Product Name Option 3",
            "angle": "Emotional/Aspirational", 
            "confidence": 85,
            "justification": "Creates emotional connection and desire"
        }},
        {{
            "text": "Product Name Option 4",
            "angle": "Premium/Luxury", 
            "confidence": 83,
            "justification": "Positions as high-end, exclusive product"
        }}
    ],
    "tagline_options": [
        {{
            "text": "Tagline option 1 - transformation focused",
            "angle": "Transformation",
            "confidence": 90,
            "justification": "Focuses on before/after transformation"
        }},
        {{
            "text": "Tagline option 2 - benefit focused",
            "angle": "Benefit-driven",
            "confidence": 87,
            "justification": "Highlights primary benefit"
        }},
        {{
            "text": "Tagline option 3 - emotional",
            "angle": "Emotional",
            "confidence": 84,
            "justification": "Creates emotional resonance"
        }},
        {{
            "text": "Tagline option 4 - authority",
            "angle": "Authority/Expert",
            "confidence": 81,
            "justification": "Builds credibility and expertise"
        }}
    ],
    "description_options": [
        {{
            "text": "Main product description option 1 - problem-solution focused with specific benefits and proof points",
            "angle": "Problem-solution",
            "confidence": 95,
            "justification": "Directly addresses customer pain points with clear solutions"
        }},
        {{
            "text": "Main product description option 2 - ingredient and science focused with technical details",
            "angle": "Science/Ingredient-focused",
            "confidence": 91,
            "justification": "Appeals to ingredient-conscious and research-minded buyers"
        }},
        {{
            "text": "Main product description option 3 - lifestyle and aspiration focused with emotional benefits",
            "angle": "Lifestyle/Aspiration",
            "confidence": 88,
            "justification": "Creates emotional connection and lifestyle appeal"
        }},
        {{
            "text": "Main product description option 4 - social proof and authority focused",
            "angle": "Social Proof/Authority",
            "confidence": 86,
            "justification": "Builds trust through credibility and testimonials"
        }},
        {{
            "text": "Main product description option 5 - unique selling proposition focused",
            "angle": "USP/Differentiation",
            "confidence": 84,
            "justification": "Highlights what makes this product uniquely different"
        }}
    ],
    "instructions_options": [
        {{
            "text": "Simple step-by-step usage instructions",
            "angle": "Simple/Direct",
            "confidence": 94,
            "justification": "Easy to follow, reduces user confusion"
        }},
        {{
            "text": "Detailed usage instructions with expert tips and best practices",
            "angle": "Comprehensive/Expert",
            "confidence": 89,
            "justification": "Builds confidence and ensures optimal results"
        }},
        {{
            "text": "Quick usage guide that connects each step to benefits",
            "angle": "Benefit-oriented",
            "confidence": 87,
            "justification": "Shows why each step matters for results"
        }},
        {{
            "text": "Professional usage instructions with timing and frequency",
            "angle": "Professional/Clinical",
            "confidence": 85,
            "justification": "Appeals to serious users who want precision"
        }}
    ],
    "claims_variations": [
        {{
            "claims": ["Natural ingredients", "Aluminum-free", "For sensitive skin"],
            "angle": "Natural/Clean",
            "confidence": 93,
            "justification": "Appeals to health-conscious consumers"
        }},
        {{
            "claims": ["Clinically tested", "Dermatologist recommended", "Hypoallergenic"],
            "angle": "Clinical/Medical",
            "confidence": 90,
            "justification": "Builds medical credibility and trust"
        }},
        {{
            "claims": ["Long-lasting protection", "24-hour effectiveness", "Superior performance"],
            "angle": "Performance",
            "confidence": 88,
            "justification": "Focuses on functional benefits"
        }},
        {{
            "claims": ["Eco-friendly", "Sustainable packaging", "Cruelty-free"],
            "angle": "Sustainability",
            "confidence": 85,
            "justification": "Appeals to environmentally conscious buyers"
        }}
    ],
    "headline_options": [
        {{
            "text": "Transform Your [Category] Experience",
            "angle": "Transformation",
            "confidence": 92,
            "justification": "Focuses on life-changing results"
        }},
        {{
            "text": "The Science of [Key Benefit]",
            "angle": "Science/Authority",
            "confidence": 89,
            "justification": "Appeals to logic and credibility"
        }},
        {{
            "text": "Finally, [Solution] That Actually Works",
            "angle": "Problem-solution",
            "confidence": 87,
            "justification": "Addresses frustration with previous solutions"
        }},
        {{
            "text": "Discover What [Target Audience] Already Know",
            "angle": "Social Proof/FOMO",
            "confidence": 85,
            "justification": "Creates urgency and social validation"
        }}
    ],
    "call_to_action_options": [
        {{
            "text": "Get Your [Product] Today",
            "angle": "Direct/Simple",
            "confidence": 88,
            "justification": "Clear, straightforward action"
        }},
        {{
            "text": "Experience the Difference",
            "angle": "Benefit-focused",
            "confidence": 91,
            "justification": "Focuses on positive outcome"
        }},
        {{
            "text": "Join Thousands Who've Transformed Their [Category]",
            "angle": "Social Proof",
            "confidence": 89,
            "justification": "Leverages social validation"
        }},
        {{
            "text": "Start Your [Benefit] Journey",
            "angle": "Journey/Process",
            "confidence": 86,
            "justification": "Frames as beginning of positive change"
        }}
    ]
}}

Focus on creating diverse angles that appeal to different customer psychologies, motivations, and decision-making styles. Each option should be substantially different in approach and tone.

IMPORTANT: Return ONLY the JSON object. No other text, no explanations, no markdown formatting.
"""

            print("🎯 Generating multiple copy options for each element...")
            
            if self.gemini_model:
                options_response = self.gemini_model.generate_content(
                    copy_options_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=3000,
                        temperature=0.2,  # Lower temperature for more consistent JSON
                    )
                )
                raw_response = options_response.text
            else:
                options_response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a professional copywriter. Always return valid JSON without any markdown formatting or explanations."},
                        {"role": "user", "content": copy_options_prompt}
                    ],
                    max_tokens=3000,
                    temperature=0.2  # Lower temperature for more consistent JSON
                )
                raw_response = options_response.choices[0].message.content.strip()

            import re
            
            # Parse JSON response with multiple fallback methods
            try:
                # Method 1: Try to find JSON in markdown code blocks
                json_match = re.search(r'```json\s*(.*?)\s*```', raw_response, re.DOTALL)
                if json_match:
                    json_content = json_match.group(1)
                    print("📝 Found JSON in markdown code block")
                else:
                    # Method 2: Try to find JSON between curly braces
                    json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                    if json_match:
                        json_content = json_match.group(0)
                        print("📝 Found JSON in response")
                    else:
                        # Method 3: Try the entire response as JSON
                        json_content = raw_response.strip()
                        print("📝 Using full response as JSON")
                
                copy_options = json.loads(json_content)
                print(f"✅ Generated copy options for all elements")
                return copy_options
                
            except json.JSONDecodeError as json_error:
                print(f"⚠️ JSON parsing failed: {json_error}")
                print(f"🔍 Raw response length: {len(raw_response)} characters")
                print(f"🔍 Response preview: {raw_response[:300]}...")
                print("🔄 Using default copy options instead")
                return self._get_default_copy_options(product_data)
                
        except Exception as e:
            print(f"❌ Error generating copy options: {e}")
            import traceback
            traceback.print_exc()
            return self._get_default_copy_options(product_data)

    def _format_product_with_options(self, product_data, copy_options, brand_data):
        """Format product data with comprehensive copy options for every element"""
        return {
            "product_id": f"product_{hash(product_data.get('product_name', 'product')) % 10000}",
            
            # Product Name with multiple options
            "product_name": {
                "original": product_data.get('product_name', 'Product'),
                "options": copy_options.get('product_name_options', [])
            },
            
            # Taglines - new copy element
            "taglines": {
                "options": copy_options.get('tagline_options', [])
            },
            
            # Headlines - new copy element  
            "headlines": {
                "options": copy_options.get('headline_options', [])
            },
            
            # Claims with variations
            "claims": {
                "original": product_data.get('claims', []),
                "variations": copy_options.get('claims_variations', [])
            },
            
            # Product Description with multiple options
            "description": {
                "original": product_data.get('main_description', ''),
                "options": copy_options.get('description_options', [])
            },
            
            # Key Benefits (preserved from original data)
            "key_benefits": [
                {
                    "title": benefit.get('title', ''),
                    "description": benefit.get('description', ''),
                    "supporting_ingredients": benefit.get('supporting_ingredients', [])
                }
                for benefit in product_data.get('key_benefits', [])
            ],
            
            # Instructions with multiple options
            "instructions": {
                "original": product_data.get('instructions', ''),
                "options": copy_options.get('instructions_options', [])
            },
            
            # Call to Action options - new copy element
            "call_to_action": {
                "options": copy_options.get('call_to_action_options', [])
            },
            
            # Product specifications and details
            "volume": product_data.get('volume', ''),
            "why_it_works": product_data.get('why_it_works', ''),
            
            # Marketing angles and variations
            "copy_variations": product_data.get('copy_variations', []),
            "competitive_advantages": product_data.get('competitive_advantages', []),
            "target_audience_insights": product_data.get('target_audience_insights', ''),
            "emotional_triggers": product_data.get('emotional_triggers', []),
            
            # Brand context
            "brand_context": {
                "brand_name": brand_data.get('brand_name', ''),
                "brand_voice": brand_data.get('brand_voice', ''),
                "target_audience": brand_data.get('target_audience', '')
            },
            
            # Metadata
            "generated_at": json.dumps({
                "timestamp": "generated_timestamp",
                "total_copy_options": (
                    len(copy_options.get('product_name_options', [])) +
                    len(copy_options.get('tagline_options', [])) +
                    len(copy_options.get('headline_options', [])) +
                    len(copy_options.get('description_options', [])) +
                    len(copy_options.get('instructions_options', [])) +
                    len(copy_options.get('call_to_action_options', [])) +
                    len(copy_options.get('claims_variations', []))
                )
            })
        }

    def _get_default_copy_options(self, product_data):
        """Provide comprehensive default copy options if generation fails"""
        product_name = product_data.get('product_name', 'Product')
        description = product_data.get('main_description', 'Premium product designed for optimal results.')
        instructions = product_data.get('instructions', 'Follow product instructions.')
        
        return {
            "product_name_options": [
                {
                    "text": product_name,
                    "angle": "Original",
                    "confidence": 85,
                    "justification": "Original product name"
                },
                {
                    "text": f"Premium {product_name}",
                    "angle": "Quality-focused",
                    "confidence": 80,
                    "justification": "Emphasizes premium quality"
                },
                {
                    "text": f"Professional {product_name}",
                    "angle": "Authority-focused",
                    "confidence": 75,
                    "justification": "Builds professional credibility"
                },
                {
                    "text": f"Advanced {product_name}",
                    "angle": "Innovation-focused",
                    "confidence": 78,
                    "justification": "Suggests cutting-edge technology"
                }
            ],
            "tagline_options": [
                {
                    "text": f"Transform Your Experience with {product_name}",
                    "angle": "Transformation",
                    "confidence": 82,
                    "justification": "Focuses on positive change"
                },
                {
                    "text": f"The Professional Choice for {product_name}",
                    "angle": "Authority",
                    "confidence": 79,
                    "justification": "Builds credibility"
                },
                {
                    "text": f"Experience the Difference",
                    "angle": "Differentiation",
                    "confidence": 76,
                    "justification": "Highlights uniqueness"
                },
                {
                    "text": f"Quality You Can Trust",
                    "angle": "Trust/Reliability",
                    "confidence": 81,
                    "justification": "Builds confidence and trust"
                }
            ],
            "headline_options": [
                {
                    "text": f"Discover the Power of {product_name}",
                    "angle": "Discovery",
                    "confidence": 83,
                    "justification": "Creates curiosity and interest"
                },
                {
                    "text": f"Finally, a {product_name} That Actually Works",
                    "angle": "Problem-solution",
                    "confidence": 86,
                    "justification": "Addresses previous disappointments"
                },
                {
                    "text": f"The Science Behind Better Results",
                    "angle": "Science/Authority",
                    "confidence": 80,
                    "justification": "Appeals to logic and credibility"
                },
                {
                    "text": f"Join Thousands Who've Made the Switch",
                    "angle": "Social Proof",
                    "confidence": 84,
                    "justification": "Leverages social validation"
                }
            ],
            "description_options": [
                {
                    "text": description,
                    "angle": "Original",
                    "confidence": 85,
                    "justification": "Original description"
                },
                {
                    "text": f"Experience the difference with our {product_name.lower()} - designed for optimal results and lasting satisfaction.",
                    "angle": "Experience-focused",
                    "confidence": 80,
                    "justification": "Focuses on user experience"
                },
                {
                    "text": f"Transform your routine with {product_name.lower()} - the professional choice for discerning customers.",
                    "angle": "Transformation-focused",
                    "confidence": 75,
                    "justification": "Emphasizes transformation"
                },
                {
                    "text": f"Discover why professionals choose {product_name.lower()} for superior performance and reliability.",
                    "angle": "Authority/Social Proof",
                    "confidence": 82,
                    "justification": "Builds credibility through professional endorsement"
                },
                {
                    "text": f"Get the results you've been looking for with {product_name.lower()} - scientifically formulated for maximum effectiveness.",
                    "angle": "Science/Results",
                    "confidence": 87,
                    "justification": "Combines scientific credibility with outcome focus"
                }
            ],
            "instructions_options": [
                {
                    "text": instructions,
                    "angle": "Original",
                    "confidence": 85,
                    "justification": "Original instructions"
                },
                {
                    "text": f"For best results: {instructions.lower()}",
                    "angle": "Results-focused",
                    "confidence": 80,
                    "justification": "Emphasizes optimal results"
                },
                {
                    "text": f"Simple to use: {instructions.lower()}",
                    "angle": "Simplicity-focused", 
                    "confidence": 75,
                    "justification": "Emphasizes ease of use"
                },
                {
                    "text": f"Professional application: {instructions.lower()} for maximum effectiveness",
                    "angle": "Professional/Expert",
                    "confidence": 83,
                    "justification": "Appeals to users who want professional results"
                }
            ],
            "claims_variations": [
                {
                    "claims": ["Premium Quality", "Professional Grade", "Trusted by Experts"],
                    "angle": "Authority/Quality",
                    "confidence": 85,
                    "justification": "Builds credibility and quality perception"
                },
                {
                    "claims": ["Scientifically Formulated", "Clinically Tested", "Proven Results"],
                    "angle": "Science/Clinical",
                    "confidence": 88,
                    "justification": "Appeals to evidence-based decision makers"
                },
                {
                    "claims": ["Easy to Use", "Fast Results", "Long-lasting"],
                    "angle": "Convenience/Performance",
                    "confidence": 82,
                    "justification": "Focuses on practical benefits"
                },
                {
                    "claims": ["Natural Ingredients", "Safe Formula", "Gentle Yet Effective"],
                    "angle": "Natural/Safety",
                    "confidence": 86,
                    "justification": "Appeals to health-conscious consumers"
                }
            ],
            "call_to_action_options": [
                {
                    "text": f"Get Your {product_name} Today",
                    "angle": "Direct",
                    "confidence": 85,
                    "justification": "Clear, straightforward action"
                },
                {
                    "text": "Experience the Difference",
                    "angle": "Benefit-focused",
                    "confidence": 88,
                    "justification": "Focuses on positive outcome"
                },
                {
                    "text": "Start Your Transformation",
                    "angle": "Journey/Process",
                    "confidence": 82,
                    "justification": "Frames as beginning of positive change"
                },
                {
                    "text": "Join the Professionals",
                    "angle": "Social Proof/Authority",
                    "confidence": 86,
                    "justification": "Leverages professional endorsement"
                }
            ]
        }

    def _process_multiple_products(self, document_content, brand_data, additional_context, detection_data):
        """Process document containing multiple products"""
        try:
            products_data = []
            
            # Extract detailed data for each product
            for i, product_info in enumerate(detection_data.get('products', [])):
                print(f"🛍️ Processing product {i+1}: {product_info.get('name', 'Unknown')}")
                
                # Create detailed prompt for this specific product
                product_detailed_prompt = f"""
You are an expert copywriter creating detailed, conversion-focused product descriptions. 

PRODUCT TO ANALYZE: {product_info.get('name', 'Product')}
PRODUCT DESCRIPTION: {product_info.get('description', 'N/A')}

FULL DOCUMENT CONTENT:
{document_content}

BRAND CONTEXT:
- Brand: {brand_data.get('brand_name', 'Unknown')}
- Voice: {brand_data.get('brand_voice', 'Professional and engaging')}
- Target Audience: {brand_data.get('target_audience', 'General audience')}

TASK: Create a comprehensive product description following this EXACT format and return ONLY valid JSON:

{{
    "product_name": "{product_info.get('name', 'Product')}",
    "claims": [
        "Natural ingredients",
        "Aluminum-free", 
        "For sensitive skin"
    ],
    "main_description": "Compelling 2-3 sentence product description that hooks the reader and communicates core benefits. Focus on transformation and results.",
    "key_benefits": [
        {{
            "title": "All-Day Freshness",
            "description": "Specific benefit explanation with proof points and ingredients that make this possible",
            "supporting_ingredients": ["Zinc Ricinoleate", "Arrowroot"]
        }},
        {{
            "title": "Soothing & Protecting", 
            "description": "Another key benefit with specific details",
            "supporting_ingredients": ["Tallow", "Coconut Oil"]
        }}
    ],
    "instructions": "Clear usage instructions",
    "volume": "Product size/volume",
    "why_it_works": "2-3 sentences explaining the science or reasoning behind why this product is effective",
    "copy_variations": [
        {{
            "angle": "Performance-focused",
            "headline": "Alternative headline option",
            "description": "Why this angle works for this audience"
        }},
        {{
            "angle": "Natural/Clean",
            "headline": "Another headline option", 
            "description": "Why this approach resonates"
        }}
    ]
}}

Focus on extracting specific ingredients, benefits, and proof points from the document. Make the copy conversion-focused and benefit-driven.
"""
                
                # Get detailed product analysis
                if self.gemini_model:
                    product_response = self.gemini_model.generate_content(
                        product_detailed_prompt,
                        generation_config=genai.types.GenerationConfig(
                            max_output_tokens=2000,
                            temperature=0.3,
                        )
                    )
                    product_raw = product_response.text
                else:
                    product_response = self.client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": product_detailed_prompt}],
                        max_tokens=2000,
                        temperature=0.3
                    )
                    product_raw = product_response.choices[0].message.content.strip()
                
                # Parse detailed product data
                try:
                    import json, re
                    json_match = re.search(r'\{.*\}', product_raw, re.DOTALL)
                    if json_match:
                        product_data = json.loads(json_match.group(0))
                        products_data.append(product_data)
                        print(f"✅ Extracted detailed data for: {product_data.get('product_name', 'Unknown')}")
                    else:
                        print(f"⚠️ Failed to parse JSON for product {i+1}")
                except Exception as e:
                    print(f"⚠️ Error parsing product {i+1}: {e}")
            
            # Generate structured copy options for each product
            print(f"📝 STEP 2: Generating structured copy options for {len(products_data)} products...")
            
            structured_products = []
            
            for i, product_data in enumerate(products_data):
                print(f"🎯 Generating copy options for product {i+1}: {product_data.get('product_name', 'Unknown')}")
                
                # Generate copy options for this product
                copy_options = self._generate_copy_options(product_data, brand_data)
                
                # Format the product with all copy options
                structured_product = self._format_product_with_options(product_data, copy_options, brand_data)
                structured_products.append(structured_product)
            
            print(f"✅ STRUCTURED COPY DATA GENERATED FOR {len(structured_products)} PRODUCTS")
            print("="*50 + "\n")
            
            return {
                'section_copy_data': {
                    'multiple_products': True,
                    'product_count': len(products_data),
                    'products': products_data,  # Keep original data for reference
                    'structured_data': {
                        'products': structured_products
                    },
                    'summary': f"Generated structured copy data for {len(products_data)} products"
                },
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Error processing multiple products: {e}")
            import traceback
            traceback.print_exc()
            return {
                'final_html': f'Error processing multiple products: {str(e)}',
                'section_copy_data': {},
                'success': False,
                'error': str(e)
            }

    def _extract_marketing_data_fallback(self, document_content, ai_response):
        """Fallback method to extract marketing data when JSON parsing fails"""
        try:
            print("🔧 Using fallback extraction method...")
            
            # Extract product name from document or AI response
            product_name = "Product"
            if "product" in document_content.lower():
                # Try to find product name patterns
                import re
                name_patterns = [
                    r'product[:\s]+([A-Za-z0-9\s\-]+)',
                    r'([A-Za-z0-9\s\-]+)\s*[-–]\s*Product',
                    r'^([A-Za-z0-9\s\-]+)(?:\n|\r)',
                ]
                for pattern in name_patterns:
                    match = re.search(pattern, document_content, re.IGNORECASE | re.MULTILINE)
                    if match:
                        product_name = match.group(1).strip()[:50]  # Limit length
                        break
            
            # Extract key benefits and features from document
            benefits = []
            features = []
            
            # Look for bullet points and lists
            lines = document_content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    clean_line = line[1:].strip()
                    if len(clean_line) > 10 and len(clean_line) < 100:
                        if any(word in clean_line.lower() for word in ['benefit', 'advantage', 'help', 'improve', 'better']):
                            benefits.append(clean_line)
                        else:
                            features.append(clean_line)
            
            # Limit to top items
            benefits = benefits[:5] if benefits else ["High-quality solution", "Professional grade", "Reliable performance"]
            features = features[:5] if features else ["Advanced functionality", "User-friendly design", "Comprehensive features"]
            
            # Extract value proposition from first few sentences
            sentences = document_content[:1000].split('.')
            value_prop = sentences[1].strip() if len(sentences) > 1 else "Premium solution designed for your needs"
            value_prop = value_prop[:200]  # Limit length
            
            return {
                "product_name": product_name,
                "key_value_proposition": value_prop,
                "primary_benefits": benefits,
                "key_features": features,
                "target_audience": "Professionals and enthusiasts seeking quality solutions",
                "pain_points_addressed": ["Quality concerns", "Reliability issues", "Performance problems"],
                "competitive_advantages": ["Superior quality", "Professional-grade features", "Proven reliability"],
                "social_proof": ["Trusted by professionals", "Industry-leading performance"],
                "pricing_info": "Premium pricing for premium quality",
                "urgency_elements": ["Limited availability", "Act now"],
                "emotional_triggers": ["Professional success", "Quality assurance", "Peace of mind"],
                "call_to_actions": ["Get Started Today", "Learn More"],
                "marketing_angles": [
                    {
                        "angle": "Quality Focus",
                        "headline": f"Professional-Grade {product_name}",
                        "description": "Emphasis on premium quality and reliability",
                        "copy_suggestions": "Focus on superior materials and craftsmanship"
                    },
                    {
                        "angle": "Results Driven",
                        "headline": f"Get Better Results with {product_name}",
                        "description": "Focus on outcomes and performance",
                        "copy_suggestions": "Highlight specific improvements and benefits"
                    }
                ]
            }
            
        except Exception as e:
            print(f"❌ Fallback extraction failed: {str(e)}")
            return {
                "product_name": "Premium Product",
                "key_value_proposition": "Advanced solution for your needs",
                "primary_benefits": ["High quality", "Great value", "Reliable performance"],
                "marketing_angles": [{"angle": "Quality Focus", "headline": "Premium Quality You Can Trust"}]
            }

 