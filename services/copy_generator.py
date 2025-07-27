import os
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
                'gemini-1.5-pro',
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
    
#     def generate_initial_copy(self, section, brand_data, product_data, additional_context=''):
#         """
#         Step 1: Generate initial copy based on brand/product knowledge, strictly following the new style and module library
#         """
#         # If no OpenAI client, raise error
#         if not self.client:
#             raise Exception("OpenAI API key not configured. Please add OPENAI_API_KEY to your .env file.")
        
#         # Summarize brand data to reduce token usage
#         brand_summary = ""
#         if isinstance(brand_data, dict):
#             for key, value in brand_data.items():
#                 if value and key != 'brand_name':
#                     # Limit each field to 200 characters
#                     brand_summary += f"{key}: {str(value)[:200]}...\n"
        
#         prompt = f"""
# You are an expert conversion copywriter. Write high-converting copy for this landing page section.

# STYLE RULES:
# - Be concrete & specific (no vague claims)
# - Use customer language from reviews/interviews
# - Clear, scannable sentences (2-3 lines max)
# - Every claim needs proof/evidence
# - Create conflict/contrast in narrative
# - Focus on benefits, not features
# - Cut ruthlessly - every word must persuade

# SECTION TO WRITE:
# - Purpose: {section.get('purpose', '')}
# - Type: {section.get('type', '')}
# - Structure: {section.get('text_structure', '')}
# - Location: {section.get('location', '')}

# BRAND CONTEXT:
# {brand_summary}

# ADDITIONAL CONTEXT:
# {additional_context[:500] if additional_context else ''}

# OUTPUT: Clean, compelling copy text (no HTML tags). Use line breaks for structure and readability.
# """
        
#         response = self.client.chat.completions.create(
#             model="gpt-4o",
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=1200,
#             temperature=0.7
#         )
        
#         return response.choices[0].message.content.strip()
    
    # def apply_framework(self, initial_copy, section, brand_data):
    #     """
    #     Step 2: Pass the initial copy through the copywriter framework
    #     """
    #     # If no OpenAI client, raise error
    #     if not self.client:
    #         raise Exception("OpenAI API key not configured. Please add OPENAI_API_KEY to your .env file.")
        
    #     try:
    #         prompt = f"""
    #         {self.framework_prompt}
            
    #         ORIGINAL COPY:
    #         {initial_copy}
            
    #         SECTION CONTEXT:
    #         - Purpose: {section.get('purpose', '')}
    #         - Type: {section.get('type', '')}
    #         - Text Structure: {section.get('text_structure', '')}
            
    #         BRAND CONTEXT:
    #         - Target Audience: {brand_data.get('company_info', {}).get('target_audience', '')}
    #         - Key Messages: {brand_data.get('company_info', {}).get('unique_selling_proposition', '')}
            
    #         TASK:
    #         Rewrite the original copy to follow the copywriter framework above. Ensure it:
    #         1. Has strong sales psychology (hook, problem, solution, benefits)
    #         2. Creates the right rhythm and flow
    #         3. Builds conflict and tells a story
    #         4. Addresses objections naturally within the flow
    #         5. Maintains the required text structure for the section
    #         6. Drives toward action (when appropriate for the section type)
            
    #         Make this compelling sales copy that follows proven copywriting principles while serving the section's specific purpose.
    #         """
            
    #         response = self.client.chat.completions.create(
    #             model="gpt-4",
    #             messages=[{"role": "user", "content": prompt}],
    #             max_tokens=600,
    #             temperature=0.7
    #         )
            
    #         return response.choices[0].message.content.strip()
            
    #     except Exception as e:
    #         print(f"Error applying framework: {str(e)}")
    #         raise Exception(f"Failed to apply copywriting framework: {str(e)}")
    
    # def apply_brand_voice(self, framework_copy, brand_data):
    #     """
    #     Step 3: Apply brand voice and tonality to the framework copy
    #     """
    #     # If no OpenAI client, raise error
    #     if not self.client:
    #         raise Exception("OpenAI API key not configured. Please add OPENAI_API_KEY to your .env file.")
        
    #     try:
    #         brand_voice = brand_data.get('brand_voice', {})
            
    #         prompt = f"""
    #         CURRENT COPY:
    #         {framework_copy}
            
    #         BRAND VOICE GUIDELINES:
    #         - Tone: {brand_voice.get('tone', 'Professional and approachable')}
    #         - Style: {brand_voice.get('style', 'Clear and direct')}
    #         - Avoid: {brand_voice.get('avoid', 'Overly salesy language')}
            
    #         BRAND PERSONALITY:
    #         - Brand: {brand_data.get('brand_name', '')}
    #         - Target Audience: {brand_data.get('company_info', {}).get('target_audience', '')}
            
    #         TASK:
    #         Rewrite the copy to perfectly match this brand's voice and tonality. 
            
    #         Key requirements:
    #         1. Keep all the sales psychology and framework structure intact
    #         2. Adjust word choice, sentence style, and phrasing to match the brand voice
    #         3. Use language that resonates with the target audience
    #         4. Avoid anything listed in the "avoid" section
    #         5. Make it sound authentically like this brand would speak
    #         6. Maintain the same length and structure
            
    #         The copy should feel like it was written by someone who truly understands this brand's personality and how they communicate with their customers.
    #         """
            
    #         response = self.client.chat.completions.create(
    #             model="gpt-4",
    #             messages=[{"role": "user", "content": prompt}],
    #             max_tokens=600,
    #             temperature=0.6
    #         )
            
    #         return response.choices[0].message.content.strip()
            
    #     except Exception as e:
    #         print(f"Error applying brand voice: {str(e)}")
    #         raise Exception(f"Failed to apply brand voice: {str(e)}")
    
    # def _format_faqs_objections(self, brand_data):
    #     """Helper function to format FAQs and objections for the prompt"""
    #     formatted = "COMMON QUESTIONS AND OBJECTIONS:\n"
        
    #     faqs = brand_data.get('faqs', [])
    #     for faq in faqs[:3]:  # Limit to top 3 FAQs
    #         formatted += f"Q: {faq.get('question', '')}\nA: {faq.get('answer', '')}\n"
        
    #     objections = brand_data.get('objections', [])
    #     for objection in objections[:3]:  # Limit to top 3 objections
    #         formatted += f"Objection: {objection.get('objection', '')}\nResponse: {objection.get('response', '')}\n"
        
    #     return formatted
    


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
        print(f"📥 OUTPUT FROM CALL #2 (Gemini):")
        
        json_content = response.text.strip()
        finish_reason = response.candidates[0].finish_reason if response.candidates else None
        
        print(f"Response: {json_content}")
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
                        print(f"✅ Added crop_image to {section_name}: {sections_with_crops[section_name]}")
            
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

    def generate_final_html(self, sections, structured_data, image_path):
        """
        NEW Step 2: Generate pixel-perfect HTML using structured data and original screenshot
        """
        if not self.client:
            raise Exception("OpenAI API key not configured. Please add OPENAI_API_KEY to your .env file.")
        
        # Encode image for vision API
        import base64
        with open(image_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        # No need to format, pass structured_data and sections directly
        print(f"📥 INPUT TO CALL #3:")
        print(f"Generated Copy Data Available: {'Yes' if structured_data else 'No'}")
        print(f"Original Sections: {len(sections)} sections identified")
        prompt = f"""
You are an expert HTML developer and copywriter. Create pixel-perfect HTML that matches the uploaded screenshot VISUALLY while using the PROVIDED STRUCTURED DATA for all content.

GENERATED COPY DATA (USE THIS FOR ALL TEXT CONTENT):
{structured_data}

CRITICAL INSTRUCTIONS:
1. Use the screenshot ONLY for visual reference - layout, fonts, colors, spacing, positioning
2. Use the GENERATED COPY DATA for ALL text content - DO NOT extract text from the screenshot
3. Match each section from the generated copy data to the corresponding visual section in the screenshot
4. For sections with "copy_options", use the FIRST/HIGHEST CONFIDENCE option's "generated_text"
5. For sections with direct "generated_text", use that text
6. Follow the "text_structure" requirements for each section's formatting
7. Place each section's generated copy in the correct visual location as shown in screenshot

VISUAL REQUIREMENTS:
- Match screenshot layout, fonts, colors, spacing exactly
- Generate complete, valid HTML with inline CSS
- Make content fit naturally within the designed sections
- Professional, conversion-focused presentation

CONTENT REQUIREMENTS:
- Use ONLY the generated copy data for text content
- DO NOT invent new copy or extract from screenshot  
- Use the highest confidence "generated_text" from each section's copy options array
- If no copy_options array exists, use the direct "generated_text" field
- Maintain the exact copy and messaging provided in the generated data

OUTPUT REQUIREMENTS:
- Return ONLY the complete HTML document code
- NO explanatory text, comments, or descriptions
- NO markdown code blocks or formatting
- Start directly with <!DOCTYPE html> and end with </html>
- Do not include any text like "This HTML document..." or similar explanations
- Pure HTML code only that can be directly used in a browser

Generate the HTML now:
"""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                        }
                    ]
                }
            ],
            max_tokens=2000,
            temperature=0.2
        )
        
        html_content = response.choices[0].message.content.strip()
        
        # Extract HTML from markdown code blocks if present
        if html_content.startswith('```html'):
            # Remove opening ```html
            html_content = html_content[7:]
            # Remove closing ```
            if html_content.endswith('```'):
                html_content = html_content[:-3]
        elif html_content.startswith('```'):
            # Remove opening ``` (any language)
            html_content = html_content[3:]
            # Remove closing ```
            if html_content.endswith('```'):
                html_content = html_content[:-3]
        
        # Clean up any remaining whitespace
        html_content = html_content.strip()
        
        print(f"📤 HTML GENERATION OUTPUT:")
        print(f"Original length: {len(response.choices[0].message.content)}")
        print(f"Cleaned length: {len(html_content)}")
        print(f"Starts with <html>: {html_content.lower().startswith('<html')}")
        
        return html_content

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
As an expert copywriter and marketing strategist, analyze this product document and extract structured marketing data.

DOCUMENT CONTENT:
{document_content[:5000]}  # Use more content for better analysis

BRAND CONTEXT:
- Brand: {brand_data.get('brand_name', 'Unknown')}
- Voice: {brand_data.get('brand_voice', 'Professional and engaging')}
- Target Audience: {brand_data.get('target_audience', 'General audience')}
- Key Messages: {brand_data.get('key_messages', 'Focus on value and benefits')}

ADDITIONAL CONTEXT:
{additional_context}

IMPORTANT: You must respond with ONLY a valid JSON object. Do not include any explanatory text before or after the JSON.

Extract comprehensive marketing insights and return ONLY this JSON structure:
{{
    "product_name": "extracted product name",
    "key_value_proposition": "main selling point",
    "primary_benefits": ["benefit 1", "benefit 2", "benefit 3"],
    "key_features": ["feature 1", "feature 2", "feature 3"],
    "target_audience": "refined target audience description",
    "pain_points_addressed": ["pain point 1", "pain point 2"],
    "competitive_advantages": ["advantage 1", "advantage 2"],
    "social_proof": ["testimonial or proof point 1", "testimonial 2"],
    "pricing_info": "pricing details if available",
    "urgency_elements": ["scarcity or urgency elements"],
    "emotional_triggers": ["desire, fear, aspiration triggers"],
    "call_to_actions": ["primary CTA", "secondary CTA"],
    "marketing_angles": [
        {{
            "angle": "angle name",
            "headline": "compelling headline",  
            "description": "why this angle works",
            "copy_suggestions": "specific copy ideas"
        }}
    ]
}}

Focus on extracting actionable marketing insights from the document. Return ONLY the JSON object, no other text.
"""

            print("🧠 STEP 1B: Analyzing single product for marketing insights...")
            
            # Use Gemini for document analysis
            if self.gemini_model:
                analysis_response = self.gemini_model.generate_content(
                    product_analysis_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=2500,
                        temperature=0.3,
                    )
                )
                raw_response = analysis_response.text
            else:
                # Fallback to OpenAI if Gemini is not available
                analysis_response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": product_analysis_prompt}],
                    max_tokens=2500,
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
            
            # Step 2: Generate final HTML landing page (like the image pipeline)
            html_generation_prompt = f"""
As an expert web developer and conversion copywriter, create a complete, high-converting HTML landing page.

MARKETING DATA:
{json.dumps(marketing_data, indent=2)}

BRAND CONTEXT:
- Brand: {brand_data.get('brand_name', 'Unknown')}
- Voice: {brand_data.get('brand_voice', 'Professional and engaging')}

COPYWRITING REQUIREMENTS:
1. Create compelling headlines that hook the reader immediately
2. Use the extracted benefits and features to build desire
3. Address pain points with empathy and solutions
4. Include social proof and testimonials if available
5. Create urgency and scarcity where appropriate
6. Use clear, action-oriented CTAs
7. Structure content for easy scanning and conversion

TECHNICAL REQUIREMENTS:
1. Complete HTML page with embedded CSS
2. Modern, mobile-responsive design
3. Professional styling with good typography
4. Clear visual hierarchy and white space
5. Prominent call-to-action buttons
6. Landing page optimized for conversions
7. Use the brand name throughout: {brand_data.get('brand_name', 'Unknown')}

Return ONLY the complete HTML code, nothing else. Make it conversion-focused!
"""

            print("🎨 STEP 2: Generating high-converting HTML landing page...")
            
            # Use Gemini for HTML generation
            if self.gemini_model:
                html_response = self.gemini_model.generate_content(
                    html_generation_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=4000,
                        temperature=0.2,
                    )
                )
                html_content = html_response.text
            else:
                # Fallback to OpenAI if Gemini is not available
                html_response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": html_generation_prompt}],
                    max_tokens=4000,
                    temperature=0.2
                )
                html_content = html_response.choices[0].message.content.strip()
            
            # Clean up HTML from markdown if needed
            if html_content.startswith('```html'):
                html_content = html_content[7:]
                if html_content.endswith('```'):
                    html_content = html_content[:-3]
            elif html_content.startswith('```'):
                html_content = html_content[3:]
                if html_content.endswith('```'):
                    html_content = html_content[:-3]
            
            html_content = html_content.strip()
            
            print("✅ HIGH-CONVERTING LANDING PAGE GENERATED")
            print("="*50 + "\n")
            
            return {
                'final_html': html_content,
                'section_copy_data': marketing_data,
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Error processing single product: {e}")
            return self._extract_marketing_data_fallback(document_content, str(e))

    def _process_multiple_products(self, document_content, brand_data, additional_context, detection_data):
        """Process document containing multiple products"""
        try:
            products_data = []
            all_html_sections = []
            
            # Extract data for each product
            for i, product_info in enumerate(detection_data.get('products', [])):
                print(f"🛍️ Processing product {i+1}: {product_info.get('name', 'Unknown')}")
                
                # Create focused prompt for this specific product
                product_specific_prompt = f"""
Extract marketing data for this specific product from the document:

PRODUCT TO FOCUS ON: {product_info.get('name', 'Product')}
PRODUCT DESCRIPTION: {product_info.get('description', 'N/A')}

DOCUMENT CONTENT:
{document_content}

BRAND CONTEXT:
- Brand: {brand_data.get('brand_name', 'Unknown')}
- Voice: {brand_data.get('brand_voice', 'Professional and engaging')}

Focus ONLY on information related to "{product_info.get('name', 'Product')}" and return ONLY this JSON:
{{
    "product_name": "{product_info.get('name', 'Product')}",
    "key_value_proposition": "main selling point for this specific product",
    "primary_benefits": ["benefit 1", "benefit 2", "benefit 3"],
    "key_features": ["feature 1", "feature 2", "feature 3"],
    "target_audience": "target audience for this product",
    "pricing_info": "pricing if mentioned for this product",
    "call_to_actions": ["Buy Now", "Learn More"]
}}
"""
                
                # Get product-specific data
                if self.gemini_model:
                    product_response = self.gemini_model.generate_content(
                        product_specific_prompt,
                        generation_config=genai.types.GenerationConfig(
                            max_output_tokens=1500,
                            temperature=0.3,
                        )
                    )
                    product_raw = product_response.text
                else:
                    product_response = self.client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": product_specific_prompt}],
                        max_tokens=1500,
                        temperature=0.3
                    )
                    product_raw = product_response.choices[0].message.content.strip()
                
                # Parse product data
                try:
                    import json, re
                    json_match = re.search(r'\{.*\}', product_raw, re.DOTALL)
                    if json_match:
                        product_data = json.loads(json_match.group(0))
                        products_data.append(product_data)
                        print(f"✅ Extracted data for: {product_data.get('product_name', 'Unknown')}")
                    else:
                        print(f"⚠️ Failed to parse JSON for product {i+1}")
                except Exception as e:
                    print(f"⚠️ Error parsing product {i+1}: {e}")
            
            # Generate combined HTML with all products
            print("🎨 STEP 2: Generating multi-product landing page...")
            
            multi_product_html_prompt = f"""
Create a comprehensive HTML landing page showcasing multiple products from the same brand.

BRAND: {brand_data.get('brand_name', 'Unknown')}
PRODUCTS DATA:
{json.dumps(products_data, indent=2)}

REQUIREMENTS:
1. Create a modern, responsive HTML page with embedded CSS
2. Include a header with brand name
3. Create a section for each product with:
   - Product name as heading
   - Key benefits and features
   - Call-to-action buttons
4. Professional design with good spacing and typography
5. Mobile-responsive layout
6. Use cards or sections to clearly separate each product
7. Include a footer

Return ONLY the complete HTML code.
"""
            
            if self.gemini_model:
                html_response = self.gemini_model.generate_content(
                    multi_product_html_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=5000,
                        temperature=0.2,
                    )
                )
                html_content = html_response.text
            else:
                html_response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": multi_product_html_prompt}],
                    max_tokens=5000,
                    temperature=0.2
                )
                html_content = html_response.choices[0].message.content.strip()
            
            # Clean up HTML
            if html_content.startswith('```html'):
                html_content = html_content[7:]
                if html_content.endswith('```'):
                    html_content = html_content[:-3]
            elif html_content.startswith('```'):
                html_content = html_content[3:]
                if html_content.endswith('```'):
                    html_content = html_content[:-3]
            
            html_content = html_content.strip()
            
            print(f"✅ MULTI-PRODUCT LANDING PAGE GENERATED ({len(products_data)} products)")
            print("="*50 + "\n")
            
            return {
                'final_html': html_content,
                'section_copy_data': {
                    'multiple_products': True,
                    'product_count': len(products_data),
                    'products': products_data,
                    'summary': f"Generated copy for {len(products_data)} products"
                },
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Error processing multiple products: {e}")
            import traceback
            traceback.print_exc()
            return {
                'final_html': f'<html><body><h1>Error</h1><p>Error processing multiple products: {str(e)}</p></body></html>',
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

 