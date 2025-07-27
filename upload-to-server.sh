#!/bin/bash

# Upload Script for Copywriting Agent to DigitalOcean
# Run this script from your local project directory

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "app.py" ] || [ ! -f "requirements.txt" ]; then
    print_error "Please run this script from your copywriting agent project directory"
    print_error "The directory should contain app.py and requirements.txt"
    exit 1
fi

# Get server details
echo "Enter your DigitalOcean droplet IP address:"
read -r SERVER_IP

echo "Enter the SSH username (usually 'root' for initial setup):"
read -r SSH_USER

# Validate inputs
if [ -z "$SERVER_IP" ] || [ -z "$SSH_USER" ]; then
    print_error "Server IP and SSH username are required"
    exit 1
fi

print_status "Uploading files to $SSH_USER@$SERVER_IP..."

# Create temporary directory for clean upload
TEMP_DIR=$(mktemp -d)
print_status "Creating clean copy of project files..."

# Copy essential files and directories
cp -r app.py config.py demo.py requirements.txt services/ static/ templates/ "$TEMP_DIR/"

# Create uploads directory if it doesn't exist
mkdir -p "$TEMP_DIR/uploads"

# Create README for server
cat > "$TEMP_DIR/SERVER_README.md" << 'EOF'
# Server Setup Instructions

This directory contains your copywriting agent application files.

## Next Steps:

1. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Create .env file:
   ```bash
   nano .env
   ```
   
   Add your environment variables:
   ```
   FLASK_ENV=production
   SECRET_KEY=your-super-secret-production-key-here
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_SHEETS_ID=your_google_sheets_id
   GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
   ```

4. Test the application:
   ```bash
   python3 app.py
   ```
   Press Ctrl+C to stop after confirming it works.

5. Start with PM2:
   ```bash
   pm2 start ecosystem.config.js
   pm2 save
   pm2 startup
   ```

6. Check status:
   ```bash
   pm2 status
   pm2 logs copywriting-agent
   ```

Your app should now be accessible via your domain or server IP!
EOF

print_status "Uploading application files via SCP..."

# Upload files to server
scp -r "$TEMP_DIR"/* "$SSH_USER@$SERVER_IP:/home/copywriter/copywriting-agent/"

# Clean up temporary directory
rm -rf "$TEMP_DIR"

print_success "Files uploaded successfully!"

print_status "Connecting to server to set up the application..."

# SSH into server and run setup commands
ssh "$SSH_USER@$SERVER_IP" << 'ENDSSH'
    # Switch to copywriter user and set up the application
    echo "Setting up application as copywriter user..."
    
    # Ensure proper ownership
    chown -R copywriter:copywriter /home/copywriter/copywriting-agent
    
    # Switch to copywriter user for remaining setup
    sudo -u copywriter bash << 'ENDSU'
        cd /home/copywriter/copywriting-agent
        
        # Create virtual environment
        echo "Creating Python virtual environment..."
        python3 -m venv venv
        
        # Activate virtual environment and install dependencies
        echo "Installing Python dependencies..."
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        
        echo "Setup completed! Please create your .env file and start the application."
        echo "See SERVER_README.md for detailed instructions."
ENDSU
ENDSSH

echo ""
print_success "Application uploaded and set up successfully! 🚀"
echo ""
print_status "Next steps on your server:"
echo "1. SSH into your server: ssh $SSH_USER@$SERVER_IP"
echo "2. Switch to copywriter user: su - copywriter"
echo "3. Go to app directory: cd /home/copywriter/copywriting-agent"
echo "4. Create .env file with your API keys: nano .env"
echo "5. Start the application: pm2 start ecosystem.config.js"
echo ""
print_status "Example .env file content:"
echo "FLASK_ENV=production"
echo "SECRET_KEY=your-super-secret-production-key"
echo "OPENAI_API_KEY=your_openai_api_key_here"
echo "GOOGLE_SHEETS_ID=your_google_sheets_id_if_using"
echo "GOOGLE_CREDENTIALS_JSON={\"type\":\"service_account\",...}"
echo ""
print_status "After setting up .env, your app will be accessible at:"
print_status "http://$SERVER_IP (or your domain if configured)" 