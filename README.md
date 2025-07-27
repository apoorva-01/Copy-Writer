# Copywriting Agent

An AI-powered copywriting tool that generates brand-perfect copy from design screenshots following a proven copywriting framework.

## Features

- **Image Analysis**: Upload design screenshots and automatically identify page sections and their purposes
- **Brand Integration**: Connect to Google Sheets for brand data, voice guidelines, and product information  
- **Multi-Step Copy Generation**: 
  1. Initial copy based on brand/product knowledge
  2. Framework enhancement for sales psychology
  3. Brand voice application for final polish
- **Designer-Friendly UI**: Simple interface for uploading designs and viewing results
- **Google Sheets Integration**: Store brand data and export generated copy

## How It Works

### The Framework Process

1. **Section Analysis**: Upload a design screenshot and the AI identifies each section's purpose (sell benefits, address objections, provide social proof, etc.)

2. **Brand Data Integration**: Pulls relevant brand information, product details, FAQs, and objections from Google Sheets

3. **Initial Copy Generation**: Creates product-specific copy that addresses the right pain points and objections

4. **Framework Application**: Enhances copy using proven sales psychology principles:
   - Hook and attention-grabbing opening
   - Problem identification and agitation
   - Solution presentation with benefits
   - Social proof and objection handling
   - Clear call-to-action

5. **Brand Voice Application**: Final polish to match the brand's specific tone, style, and personality

## Setup Instructions

### Prerequisites

- Python 3.8+
- OpenAI API key
- Google Sheets (optional - will use mock data if not configured)

### Installation

1. Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. (Optional) Set up Google Sheets integration:
   - Create a Google Cloud project
   - Enable Google Sheets API
   - Create service account credentials
   - Download credentials JSON file
   - Set up your spreadsheet with brand data sheets

### Running the Application

```bash
python app.py
```

Visit `http://localhost:5000` to use the copywriting agent.

## Google Sheets Setup (Optional)

If you want to use Google Sheets integration instead of mock data:

### Spreadsheet Structure

Create sheets with the following naming convention:

#### `[Brand Name] - Brand Data` Sheet
| Field | Value |
|-------|--------|
| company_description | Your brand description |
| company_target_audience | Target customer demographics |  
| company_unique_selling_proposition | What makes you different |
| voice_tone | Brand tone (e.g., "Confident, authentic, approachable") |
| voice_style | Writing style guidelines |
| voice_avoid | What to avoid in copy |
| faq_question_1 | Common customer question |
| faq_answer_1 | Answer to question 1 |
| objection_price_too_high | Common objection |
| objection_response_1 | How to address the objection |

#### `[Brand Name] - Products` Sheet
| Product Name | Benefits | Ingredients | Price | Use Cases | Differentiators |
|--------------|----------|-------------|-------|-----------|-----------------|
| Miracle Balm | Hydrating, long-lasting | Natural oils | $28 | Daily wear | Multi-use formula |

### Authentication Options

1. **Service Account JSON String (Recommended)**:
   - Set `GOOGLE_CREDENTIALS_JSON` in `.env` with the full JSON credentials
   - More secure and deployment-friendly

2. **Service Account File**:
   - Set `GOOGLE_SERVICE_ACCOUNT_PATH` in `.env`
   - Download service account JSON from Google Cloud

3. **OAuth (For development)**:
   - Place `credentials.json` in project root
   - First run will open browser for authentication

## Usage

1. **Upload Design**: Drag and drop or click to upload a design screenshot (PNG, JPG, WEBP up to 16MB)

2. **Select Brand & Product**: Choose from your configured brands and products

3. **Generate Copy**: Click "Generate Copy" and wait 30-60 seconds for processing

4. **Review Results**: View three versions of copy for each section:
   - Initial Copy (brand/product-specific)  
   - Framework Enhanced (sales psychology applied)
   - Final Copy (brand voice applied)

5. **Export to Sheets**: Results are automatically saved to Google Sheets (if configured)

## API Endpoints

- `GET /api/brands` - Get available brands
- `GET /api/products/{brand_name}` - Get products for a brand
- `POST /api/analyze-image` - Analyze uploaded image sections
- `POST /api/generate-copy` - Generate copy for sections

## Architecture

- **Backend**: Flask application with three core services:
  - `ImageAnalyzer`: GPT-4 Vision for section identification
  - `BrandDataManager`: Google Sheets integration
  - `CopyGenerator`: Multi-step copy generation pipeline
- **Frontend**: Vanilla JavaScript with modern UI
- **Storage**: Google Sheets for brand data and results

## Customization

### Adding New Copywriting Frameworks

Edit `services/copy_generator.py` and modify the `framework_prompt` to include your preferred copywriting structure.

### Extending Brand Data

Modify `services/brand_data_manager.py` to pull additional fields from your Google Sheets or add new data sources.

## Troubleshooting

### Common Issues

1. **OpenAI API Errors**: Check your API key and ensure you have credits
2. **Google Sheets Connection**: Verify credentials and sheet permissions
3. **Image Analysis Fails**: Ensure image is clear and shows distinct content sections
4. **Slow Performance**: Large images or complex designs take longer to process

### Mock Data Mode

If Google Sheets isn't configured, the app uses mock data for:
- Brands: Jones Road Beauty, Warroad, Sample Brand
- Products: Miracle Balm, Foundation, Mascara
- Sample brand voice and FAQ data

This allows you to test the core functionality without setting up Google Sheets.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with sample images and brands
5. Submit a pull request

## License

MIT License - see LICENSE file for details 