import os
import json
import base64
import traceback
import asyncio
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from services.image_analyzer import ImageAnalyzer
from services.brand_data_manager import BrandDataManager
from services.copy_generator import CopyGenerator
from services.image_cropper import ImageCropper

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize services
image_analyzer = ImageAnalyzer()
brand_data_manager = BrandDataManager()
copy_generator = CopyGenerator()
image_cropper = ImageCropper()

def process_sections_new_pipeline(sections, brand_data, additional_context, image_path):
    """Process all sections through the NEW 2-step pipeline"""
    try:
        # OPENAI CALL #2: Generate copy for all sections using brand context  
        print("\n" + "="*50)
        print("🔍 OPENAI CALL #2 - GENERATING SECTION COPY")
        print("="*50)
        
        # Use batching for large numbers of sections
        num_sections = len(sections)
        if num_sections > 30:
            print(f"🔄 LARGE DATASET DETECTED: {num_sections} sections - using batched processing")
            structured_data = copy_generator.extract_structured_product_data_batched(
                sections, brand_data, additional_context, batch_size=25
            )
        else:
            structured_data = copy_generator.extract_structured_product_data(
                sections, brand_data, additional_context
            )
        
        # OPENAI CALL #3: Generate final HTML using generated copy + original image  
        print("🎨 OPENAI CALL #3 - GENERATING HTML WITH SECTION COPY")
        print("="*50)
        final_html = copy_generator.generate_final_html(
            sections, structured_data, image_path
        )
        print("✅ HTML Generation Complete")
        print("="*50 + "\n")
        
        return {
            'section_copy_data': structured_data,
            'final_html': final_html,
            'success': True
        }
    except Exception as e:
        print(f"Error in new pipeline: {e}")
        return {
            'section_copy_data': None,
            'final_html': f'Error: {str(e)}',
            'success': False,
            'error': str(e)
        }

# Keep old function for backward compatibility
def process_single_section(section, brand_data, product_data, additional_context):
    """Process a single section through the 3-step copywriting framework"""
    try:
        # Step 1: Generate initial copy
        initial_copy = copy_generator.generate_initial_copy(
            section, brand_data, product_data, additional_context
        )
        
        # Step 2: Apply framework
        framework_copy = copy_generator.apply_framework(
            initial_copy, section, brand_data
        )
        
        # Step 3: Apply brand voice
        final_copy = copy_generator.apply_brand_voice(
            framework_copy, brand_data
        )
        
        return {
            'section_id': section['id'],
            'section_type': section['type'],
            'initial_copy': initial_copy,
            'framework_copy': framework_copy,
            'final_copy': final_copy
        }
    except Exception as e:
        print(f"Error processing section {section.get('id', 'unknown')}: {e}")
        return {
            'section_id': section.get('id', 'unknown'),
            'section_type': section.get('type', 'unknown'),
            'initial_copy': f'Error: {str(e)}',
            'framework_copy': f'Error: {str(e)}',
            'final_copy': f'Error: {str(e)}'
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Clean up any existing crops for this base filename
            base_filename = os.path.splitext(filename)[0]
            image_cropper.cleanup_crops(base_filename)
            
            # Analyze the image to identify sections
            sections = image_analyzer.analyze_page_sections(filepath)
            
            # Crop section images
            crop_paths = image_cropper.crop_all_sections(filepath, sections)
            
            # Add crop paths to sections
            for section in sections:
                section_id = section['id']
                if section_id in crop_paths:
                    # Convert to relative path for serving
                    crop_path = crop_paths[section_id]
                    relative_crop_path = os.path.relpath(crop_path, app.config['UPLOAD_FOLDER'])
                    section['crop_image'] = relative_crop_path
                else:
                    section['crop_image'] = None
            
            return jsonify({
                'success': True,
                'sections': sections,
                'image_path': filename  # Frontend will use this for copy generation
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-copy', methods=['POST'])
def generate_copy():
    try:
        data = request.get_json()
        required_fields = ['sections', 'brand_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        sections = data['sections']
        brand_name = data['brand_name']
        additional_context = data.get('additional_context', '')
        image_path = data.get('image_path', '')  # Get image path from request
        
        # Fetch all brand docs context (YouTube, Reddit, FAQ, Persona, etc.)
        # Handle custom brands (those not in the predefined list)
        brand_data = brand_data_manager.get_brand_docs_context(brand_name)
        if not brand_data or not brand_data.get('brand_name'):
            # For custom brands, create minimal brand data structure
            brand_data = {
                'brand_name': brand_name,
                'brand_voice': 'Professional and engaging',
                'target_audience': 'General audience',
                'key_messages': 'Focus on value proposition and benefits'
            }
        
        # NEW PIPELINE: Use 2-step process
        if image_path and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], image_path)):
            full_image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path)
            result = process_sections_new_pipeline(sections, brand_data, additional_context, full_image_path)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'section_copy_data': result['section_copy_data'],
                    'final_html': result['final_html'],
                    'pipeline_version': 'new'
                })
            else:
                return jsonify({'error': result.get('error', 'Unknown error')}), 500
        
        # FALLBACK: Use old 3-step pipeline if no image path
        product_data = None  # Not used in new workflow
        results = []
        max_workers = min(len(sections), 5)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_section = {
                executor.submit(process_single_section, section, brand_data, product_data, additional_context): section
                for section in sections
            }
            
            for future in as_completed(future_to_section):
                section = future_to_section[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Error processing section {section.get('id', 'unknown')}: {e}")
                    results.append({
                        'section_id': section.get('id', 'unknown'),
                        'section_type': section.get('type', 'unknown'),
                        'initial_copy': f'Error: {str(e)}',
                        'framework_copy': f'Error: {str(e)}',
                        'final_copy': f'Error: {str(e)}'
                    })
        
        results.sort(key=lambda x: x['section_id'])
        
        return jsonify({
            'success': True,
            'results': results,
            'sheet_url': None,
            'pipeline_version': 'legacy'
        })
    except Exception as e:
        print("Error in generate_copy:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/brands', methods=['GET'])
def get_brands():
    try:
        brands = brand_data_manager.get_available_brands()
        return jsonify({'brands': brands})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<brand_name>', methods=['GET'])
def get_products(brand_name):
    try:
        products = brand_data_manager.get_brand_products(brand_name)
        return jsonify({'products': products})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Serve uploaded files including cropped section images"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/uploads/crops/<path:filename>')
def serve_crop(filename):
    """Serve cropped section images"""
    crop_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'crops')
    return send_from_directory(crop_folder, filename)

@app.route('/api/recrop-section', methods=['POST'])
def recrop_section():
    """Re-crop a single section with updated coordinates"""
    try:
        data = request.get_json()
        required_fields = ['image_path', 'section_id', 'bounding_box']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        image_path = data['image_path']
        section_id = data['section_id']
        bounding_box = data['bounding_box']
        
        # Construct full image path
        full_image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path)
        
        if not os.path.exists(full_image_path):
            return jsonify({'error': 'Original image not found'}), 404
        
        # Re-crop the section with new coordinates
        crop_path = image_cropper.crop_section(full_image_path, section_id, bounding_box)
        
        if crop_path:
            # Convert to relative path for serving
            relative_crop_path = os.path.relpath(crop_path, app.config['UPLOAD_FOLDER'])
            return jsonify({
                'success': True,
                'crop_image': relative_crop_path,
                'message': f'Section {section_id} re-cropped successfully'
            })
        else:
            return jsonify({'error': 'Failed to crop section'}), 500
            
    except Exception as e:
        print(f"Error re-cropping section: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/process-document', methods=['POST'])
def process_document():
    try:
        print("\n" + "="*50)
        print("📄 DOCUMENT PROCESSING STARTED")
        print("="*50)
        
        document_type = request.form.get('type')
        brand_name = request.form.get('brand_name', '')
        additional_context = request.form.get('additional_context', '')
        
        print(f"Document type: {document_type}")
        print(f"Brand name: {brand_name}")
        print(f"Additional context length: {len(additional_context) if additional_context else 0}")
        
        document_content = ''
        
        if document_type == 'file':
            # Handle file upload
            if 'document' not in request.files:
                print("❌ No document file in request")
                return jsonify({'error': 'No document file provided'}), 400
            
            file = request.files['document']
            if file.filename == '':
                print("❌ Empty filename")
                return jsonify({'error': 'No file selected'}), 400
            
            # Process different file types
            filename = secure_filename(file.filename)
            file_extension = filename.lower().split('.')[-1]
            
            print(f"📎 Processing file: {filename} (type: {file_extension})")
            
            if file_extension in ['txt']:
                document_content = file.read().decode('utf-8')
                print(f"✅ TXT file processed: {len(document_content)} characters")
            elif file_extension in ['docx']:
                document_content = extract_text_from_docx(file)
                print(f"✅ DOCX file processed: {len(document_content)} characters")
            elif file_extension in ['pdf']:
                document_content = extract_text_from_pdf(file)
                print(f"✅ PDF file processed: {len(document_content)} characters")
            else:
                print(f"❌ Unsupported file format: {file_extension}")
                return jsonify({'error': f'Unsupported file format: {file_extension}. Please use TXT, DOCX, or PDF.'}), 400
                
        elif document_type == 'url':
            # Handle Google Docs URL
            url = request.form.get('url', '')
            if not url:
                print("❌ No URL provided")
                return jsonify({'error': 'No URL provided'}), 400
            
            print(f"🔗 Processing URL: {url}")
            document_content = extract_text_from_google_docs_url(url)
            if not document_content:
                print("❌ Failed to extract from Google Docs URL")
                return jsonify({'error': 'Failed to extract content from Google Docs URL. Make sure the document is publicly accessible.'}), 400
            print(f"✅ URL processed: {len(document_content)} characters")
        
        else:
            print(f"❌ Invalid document type: {document_type}")
            return jsonify({'error': 'Invalid document type'}), 400
        
        if not document_content.strip():
            print("❌ No content extracted")
            return jsonify({'error': 'No content could be extracted from the document'}), 400
        
        # print(f"📊 Document content preview (first 200 chars):")
        # print(f"'{document_content[:200]}...'")
        
        # Return raw content for direct copy generation (no sections needed)
        print("✅ DOCUMENT PROCESSING COMPLETED - Ready for copy generation")
        print("="*50 + "\n")
        
        return jsonify({
            'success': True,
            'content': document_content,
            'message': f'Successfully processed document ({len(document_content)} characters)'
        })
    
    except Exception as e:
        print(f"❌ Error processing document: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-copy-from-document', methods=['POST'])
def generate_copy_from_document():
    try:
        data = request.get_json()
        required_fields = ['document_content', 'brand_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        document_content = data['document_content']
        brand_name = data['brand_name']
        additional_context = data.get('additional_context', '')
        
        # Get brand context
        brand_data = brand_data_manager.get_brand_docs_context(brand_name)
        if not brand_data or not brand_data.get('brand_name'):
            # For custom brands, create minimal brand data structure
            brand_data = {
                'brand_name': brand_name,
                'brand_voice': 'Professional and engaging',
                'target_audience': 'General audience',
                'key_messages': 'Focus on value proposition and benefits'
            }
        
        # Generate copy from document content
        result = copy_generator.generate_copy_from_document(
            document_content, brand_data, additional_context
        )
        
        return jsonify({
            'success': True,
            'final_html': result.get('final_html', ''),
            'section_copy_data': result.get('section_copy_data', {}),
            'pipeline_version': 'document'
        })
    
    except Exception as e:
        print(f"Error generating copy from document: {str(e)}")
        return jsonify({'error': str(e)}), 500

def extract_text_from_docx(file):
    """Extract text from DOCX file"""
    try:
        import docx
        doc = docx.Document(file)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return '\n'.join(text)
    except ImportError:
        # Fallback if python-docx is not installed
        return "Error: python-docx library not installed. Please install it to process DOCX files."
    except Exception as e:
        return f"Error extracting text from DOCX: {str(e)}"

def extract_text_from_pdf(file):
    """Extract text from PDF file"""
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(file)
        text = []
        for page in reader.pages:
            text.append(page.extract_text())
        return '\n'.join(text)
    except ImportError:
        # Fallback if PyPDF2 is not installed
        return "Error: PyPDF2 library not installed. Please install it to process PDF files."
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

def extract_text_from_google_docs_url(url):
    """Extract text from Google Docs URL"""
    try:
        # Extract document ID from URL
        doc_id_match = re.search(r'/document/d/([a-zA-Z0-9-_]+)', url)
        if not doc_id_match:
            return None
        
        doc_id = doc_id_match.group(1)
        
        # Try to access the document as plain text
        export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
        
        response = requests.get(export_url, timeout=30)
        if response.status_code == 200:
            return response.text
        else:
            # Try alternative approach
            alt_url = f"https://docs.google.com/document/d/{doc_id}/edit?usp=sharing"
            response = requests.get(alt_url, timeout=30)
            if response.status_code == 200:
                # This is a basic fallback - in production you might want to use Google Docs API
                return "Content extracted from Google Docs (API integration recommended for better extraction)"
            
        return None
    except Exception as e:
        print(f"Error extracting from Google Docs URL: {str(e)}")
        return None

# Section creation function removed - no longer needed for streamlined document processing

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080) 