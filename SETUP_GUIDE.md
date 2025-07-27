# Quick Setup Guide - Copywriting Agent

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Add OpenAI API Key
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 3: Run the Application
```bash
python3 app.py
```

Visit `http://localhost:5000` and you're ready to go!

## ✨ Test Without API Key

You can test the core functionality without an OpenAI API key:

```bash
python3 demo.py
```

This will show you:
- ✅ Brand data management (uses mock data)
- ✅ Section identification (uses mock sections)  
- ❌ Copy generation (requires OpenAI API key)

## 🎯 Using the Web Interface

1. **Upload Image**: Drag & drop or click to upload your design screenshot
2. **Select Brand**: Choose from available brands (uses mock data initially)
3. **Select Product**: Pick a product for that brand
4. **Generate Copy**: Click generate and wait 30-60 seconds
5. **Review Results**: See three versions of copy:
   - Initial Copy (brand-specific)
   - Framework Enhanced (sales psychology)
   - Final Copy (brand voice applied)

## 📊 Google Sheets Integration (Optional)

To use real brand data instead of mock data:

1. Create a Google Cloud project
2. Enable Google Sheets API
3. Create service account credentials
4. Add to `.env` (choose one method):

**Option A: JSON String (Recommended)**
```
GOOGLE_SHEETS_ID=your_spreadsheet_id
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"...","private_key_id":"..."}
```

**Option B: File Path**
```
GOOGLE_SHEETS_ID=your_spreadsheet_id
GOOGLE_SERVICE_ACCOUNT_PATH=path/to/credentials.json
```

### Spreadsheet Format

Create sheets named: `[Brand Name] - Brand Data` and `[Brand Name] - Products`

See `README.md` for detailed sheet structure.

## 🔧 Configuration Options

**Environment Variables** (`.env` file):
- `OPENAI_API_KEY` - Required for copy generation
- `GOOGLE_SHEETS_ID` - Optional, uses mock data if not set
- `GOOGLE_SERVICE_ACCOUNT_PATH` - For Google Sheets authentication

## 🎨 How It Works

Your specific copywriting framework:

1. **Image Analysis** → Identifies sections and their purposes
2. **Brand Data Integration** → Pulls relevant brand/product info  
3. **Initial Copy** → Generates product-specific copy
4. **Framework Application** → Applies sales psychology principles
5. **Brand Voice** → Final polish with brand personality

This ensures copy is never generic - it's always specific to your exact product and addresses the right objections.

## 🆘 Need Help?

- Check `README.md` for detailed documentation
- Run `python3 demo.py` to test functionality
- Ensure all dependencies are installed
- Verify your OpenAI API key has credits

## 📁 Project Structure

```
main-copywriteragent/
├── app.py                 # Main Flask application
├── services/
│   ├── image_analyzer.py  # GPT-4 Vision for section analysis
│   ├── brand_data_manager.py # Google Sheets integration
│   └── copy_generator.py  # Multi-step copy generation
├── templates/
│   └── index.html         # Web interface
├── static/
│   └── app.js            # Frontend JavaScript
├── demo.py               # Test script
└── README.md             # Full documentation
```

Ready to generate brand-perfect copy! 🎯 