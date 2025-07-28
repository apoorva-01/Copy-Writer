# Copywriter Agent - AI-Powered Brand-Perfect Copy Generator

A modern web application that uses AI to analyze designs and documents to generate brand-perfect marketing copy. Built with Next.js frontend and Flask API backend.

## 🏗️ Architecture

- **Frontend**: Next.js 14 with TypeScript (deployed on Vercel)
- **Backend**: Flask API with Python (deployed on DigitalOcean)
- **AI**: OpenAI GPT models for copy generation
- **Image Processing**: OpenCV and Tesseract for image analysis
- **File Handling**: Support for images, PDFs, DOCX, and Google Docs

## 🚀 Features

- **Image Analysis**: Upload design screenshots for AI-powered section identification
- **Document Processing**: Extract content from PDFs, DOCX files, and Google Docs
- **Brand Intelligence**: Pre-loaded brand guidelines and voice for accurate copy generation
- **Custom Brands**: Support for custom clients with contextual copy generation
- **Multiple Copy Options**: Generate multiple copy variations with confidence scores
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 📁 Project Structure

```
├── frontend/              # Next.js Frontend Application
│   ├── app/              # Next.js App Router
│   │   ├── globals.css   # Global styles
│   │   ├── layout.tsx    # Root layout
│   │   └── page.tsx      # Main page component
│   ├── public/           # Static assets
│   ├── package.json      # Frontend dependencies
│   ├── next.config.js    # Next.js configuration
│   ├── vercel.json       # Vercel deployment config
│   └── Dockerfile.nextjs # Frontend Docker config
├── backend/               # Flask API Backend
│   ├── services/         # API services
│   │   ├── image_analyzer.py    # Image analysis logic
│   │   ├── copy_generator.py    # Copy generation logic
│   │   ├── brand_data_manager.py # Brand data management
│   │   └── image_cropper.py     # Image cropping utilities
│   ├── static/           # Backend static assets
│   ├── uploads/          # File upload directory
│   ├── app.py           # Flask API main application
│   ├── requirements.txt # Python dependencies
│   ├── Dockerfile       # Backend Docker config
│   └── .env            # Backend environment variables
├── start-dev.sh        # Development startup script
└── deploy-*.md        # Deployment guides
```

## 🛠️ Local Development

### Prerequisites

- Python 3.9+
- Node.js 18+
- Tesseract OCR
- OpenAI API key

### Quick Start

**Option 1: Use the startup script (Recommended)**
```bash
./start-dev.sh
```
This will automatically:
- Set up Python virtual environment in `backend/`
- Install all dependencies for both frontend and backend
- Create environment files if they don't exist
- Start both Flask API and Next.js frontend
- Show you the URLs to access both

### Manual Setup

**Backend Setup (Flask API)**

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   Create `.env` file in `backend/` directory:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   FLASK_ENV=development
   PYTHONPATH=/app
   PORT=8080
   ```

5. **Run Flask API**
   ```bash
   python app.py
   ```
   API will be available at http://localhost:8080

**Frontend Setup (Next.js)**

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Set environment variables**
   Create `.env.local` file in `frontend/` directory:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8080
   ```

4. **Run Next.js development server**
   ```bash
   npm run dev
   ```
   Frontend will be available at http://localhost:3000

## 🚀 Deployment

### Deploy Flask API to DigitalOcean

See [deploy-digitalocean.md](deploy-digitalocean.md) for detailed instructions.

### Deploy Next.js Frontend to Vercel

See [deploy-vercel.md](deploy-vercel.md) for detailed instructions.

### Environment Variables

**Backend (`backend/.env`)**
```
OPENAI_API_KEY=your-openai-api-key
FLASK_ENV=production
PYTHONPATH=/app
PORT=8080
```

**Frontend (`frontend/.env.local`)**
```
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## 🔧 Configuration

### CORS Setup

Update Flask API CORS configuration in `backend/app.py` with your frontend domains:

```python
CORS(app, origins=[
    "http://localhost:3000",  # Development
    "https://your-app.vercel.app",  # Production
    "https://*.vercel.app"  # Preview deployments
])
```

### Brand Data

Add new brands by updating the brand data manager service in `backend/services/brand_data_manager.py`.

## 📊 API Endpoints

- `GET /api/health` - Health check
- `GET /api/brands` - Get available brands
- `POST /api/analyze-image` - Analyze uploaded image
- `POST /api/generate-copy` - Generate copy from sections
- `POST /api/process-document` - Process document upload
- `POST /api/generate-copy-from-document` - Generate copy from document
- `GET /uploads/<filename>` - Serve uploaded files

## 🧪 Testing

### Test Flask API
```bash
cd backend
# Test health endpoint
curl http://localhost:8080/api/health

# Test image upload
curl -X POST -F "image=@test-image.png" http://localhost:8080/api/analyze-image
```

### Test Next.js Frontend
```bash
cd frontend
npm run build
npm start
```

## 🔍 Troubleshooting

### Common Issues

1. **CORS errors**: Check Flask CORS configuration in `backend/app.py`
2. **API connection issues**: Verify `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
3. **File upload failures**: Check file size limits and formats
4. **OCR issues**: Ensure Tesseract is properly installed
5. **Path issues**: Make sure you're running commands from the correct directories 