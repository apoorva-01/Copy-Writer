#!/bin/bash

# DigitalOcean Deployment Script for Copywriting Agent
# Run this script on your DigitalOcean droplet after initial server setup

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
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

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root (use sudo)"
    exit 1
fi

print_status "Starting DigitalOcean deployment setup..."

# Step 1: Update system
print_status "Updating system packages..."
apt update && apt upgrade -y

# Step 2: Install essential packages
print_status "Installing essential packages..."
apt install -y python3 python3-pip python3-venv git nginx ufw curl software-properties-common htop

# Step 3: Install Node.js and PM2
print_status "Installing Node.js and PM2..."
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
apt install -y nodejs
npm install -g pm2

# Step 4: Create application user
print_status "Creating application user 'copywriter'..."
if ! id "copywriter" &>/dev/null; then
    adduser --system --group --home /home/copywriter copywriter
    usermod -aG sudo copywriter
    print_success "User 'copywriter' created successfully"
else
    print_warning "User 'copywriter' already exists"
fi

# Step 5: Set up firewall
print_status "Configuring UFW firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable
print_success "Firewall configured"

# Step 6: Create application directory structure
print_status "Setting up application directory..."
sudo -u copywriter mkdir -p /home/copywriter/copywriting-agent/{logs,uploads,backups}
sudo -u copywriter chmod 755 /home/copywriter/copywriting-agent/uploads

# Step 7: Create Gunicorn configuration
print_status "Creating Gunicorn configuration..."
cat > /home/copywriter/copywriting-agent/gunicorn.conf.py << 'EOF'
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
loglevel = "info"
accesslog = "/home/copywriter/copywriting-agent/logs/access.log"
errorlog = "/home/copywriter/copywriting-agent/logs/error.log"

# Process naming
proc_name = 'copywriting_agent'

# Server mechanics
preload_app = True
daemon = False
pidfile = '/home/copywriter/copywriting-agent/copywriting_agent.pid'
user = 'copywriter'
group = 'copywriter'
tmp_upload_dir = None
EOF

# Step 8: Create PM2 ecosystem file
print_status "Creating PM2 configuration..."
cat > /home/copywriter/copywriting-agent/ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'copywriting-agent',
      cwd: '/home/copywriter/copywriting-agent',
      script: 'venv/bin/gunicorn',
      args: '--config gunicorn.conf.py app:app',
      interpreter: 'none',
      env: {
        NODE_ENV: 'production'
      },
      max_memory_restart: '500M',
      error_file: './logs/pm2-error.log',
      out_file: './logs/pm2-out.log',
      log_file: './logs/pm2-combined.log',
      time: true
    }
  ]
};
EOF

# Step 9: Create backup script
print_status "Creating backup script..."
cat > /home/copywriter/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/copywriter/backups"
APP_DIR="/home/copywriter/copywriting-agent"

mkdir -p $BACKUP_DIR

# Backup uploads and logs
tar -czf $BACKUP_DIR/app_data_$DATE.tar.gz $APP_DIR/uploads $APP_DIR/logs

# Keep only last 7 backups
find $BACKUP_DIR -name "app_data_*.tar.gz" -mtime +7 -delete

echo "Backup completed: app_data_$DATE.tar.gz"
EOF

chmod +x /home/copywriter/backup.sh

# Step 10: Get domain/IP for Nginx configuration
print_status "Configuring Nginx..."
echo ""
print_warning "Do you have a domain name for this application? (y/n)"
read -r HAS_DOMAIN

if [[ $HAS_DOMAIN =~ ^[Yy]$ ]]; then
    echo "Enter your domain name (e.g., yourdomain.com):"
    read -r DOMAIN_NAME
    SERVER_NAME="$DOMAIN_NAME www.$DOMAIN_NAME"
else
    # Get server IP
    SERVER_IP=$(curl -s ifconfig.me)
    SERVER_NAME="$SERVER_IP"
    print_warning "No domain provided. You can access your app at: http://$SERVER_IP"
fi

# Create Nginx configuration
cat > /etc/nginx/sites-available/copywriting-agent << EOF
server {
    listen 80;
    server_name $SERVER_NAME;
    
    client_max_body_size 20M;
    
    # Serve static files directly
    location /static {
        alias /home/copywriter/copywriting-agent/static;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
    
    # Handle file uploads
    location /uploads {
        alias /home/copywriter/copywriting-agent/uploads;
        internal;
    }
    
    # Proxy all other requests to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Handle long-running requests (for AI processing)
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/copywriting-agent /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t
systemctl restart nginx
systemctl enable nginx

# Step 11: Set proper permissions
chown -R copywriter:copywriter /home/copywriter/

print_success "Base deployment setup completed!"

echo ""
print_status "Next steps:"
echo "1. Upload your application files to /home/copywriter/copywriting-agent/"
echo "2. Switch to copywriter user: su - copywriter"
echo "3. Create virtual environment: python3 -m venv venv"
echo "4. Install dependencies: source venv/bin/activate && pip install -r requirements.txt"
echo "5. Create .env file with your API keys"
echo "6. Start with PM2: pm2 start ecosystem.config.js"
echo ""

if [[ $HAS_DOMAIN =~ ^[Yy]$ ]]; then
    print_status "To set up SSL certificate (after uploading your app):"
    echo "1. Install certbot: snap install --classic certbot"
    echo "2. Get certificate: certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME"
    echo ""
fi

print_status "Useful commands:"
echo "- Check PM2 status: su - copywriter -c 'pm2 status'"
echo "- View logs: su - copywriter -c 'pm2 logs copywriting-agent'"
echo "- Restart app: su - copywriter -c 'pm2 restart copywriting-agent'"
echo "- Check Nginx: systemctl status nginx"
echo ""

print_success "Deployment script completed! 🚀" 