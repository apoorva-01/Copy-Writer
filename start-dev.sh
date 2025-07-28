#!/bin/bash

# Development startup script for Copywriter Agent
# This script starts both the Flask API and Next.js frontend

echo "🚀 Starting Copywriter Agent Development Environment"
echo "=================================================="

# Backend Setup
echo "🔧 Setting up Backend (Flask API)..."
cd backend

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating Python virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating backend .env file..."
    cat > .env << EOL
# Flask API Environment Variables
OPENAI_API_KEY=your-openai-api-key-here
FLASK_ENV=development
PYTHONPATH=/app
PORT=8080
EOL
    echo "✅ Created backend/.env - please add your OpenAI API key"
fi

cd ..

# Frontend Setup
echo "🔧 Setting up Frontend (Next.js)..."
cd frontend

# Check if Node.js dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "⚙️ Creating frontend .env.local file..."
    cat > .env.local << EOL
# Next.js Environment Variables (Local Development)
NEXT_PUBLIC_API_URL=http://localhost:8080
EOL
    echo "✅ Created frontend/.env.local"
fi

cd ..

# Function to cleanup background processes
cleanup() {
    echo "🛑 Shutting down servers..."
    kill $FLASK_PID $NEXTJS_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

echo "🔥 Starting Flask API on port 8080..."
cd backend
source venv/bin/activate
python app.py &
FLASK_PID=$!
cd ..

echo "⏳ Waiting for Flask API to start..."
sleep 3

echo "⚡ Starting Next.js frontend on port 3000..."
cd frontend
npm run dev &
NEXTJS_PID=$!
cd ..

echo ""
echo "✅ Development environment started!"
echo "📱 Frontend: http://localhost:3000"
echo "🔌 API: http://localhost:8080"
echo "📊 API Health: http://localhost:8080/api/health"
echo ""
echo "💡 Backend files are in ./backend/"
echo "💡 Frontend files are in ./frontend/"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for background processes
wait 