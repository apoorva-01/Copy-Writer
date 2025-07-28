# DigitalOcean Deployment Guide for Flask API

## Prerequisites
- DigitalOcean account
- Docker installed locally (for testing)
- Domain name (optional but recommended)

## Option 1: DigitalOcean App Platform (Recommended)

### Step 1: Prepare Your Repository
1. Push your Flask API code to GitHub/GitLab
2. Make sure your `backend/` directory contains:
   - `app.py` (Flask application)
   - `requirements.txt` (Python dependencies)
   - `Dockerfile` (Docker configuration)
   - `services/` directory (API services)
   - `.env` file template (for reference, don't commit actual secrets)

### Step 2: Create App on DigitalOcean
1. Go to DigitalOcean App Platform
2. Click "Create App"
3. Connect your GitHub/GitLab repository
4. Select the repository containing your Flask API

### Step 3: Configure Build Settings
```yaml
# App Spec (will be auto-generated)
name: copywriter-agent-api
services:
- name: flask-api
  source_dir: /backend  # Important: Set source directory to backend folder
  github:
    repo: your-username/your-repo
    branch: main
  run_command: gunicorn --bind 0.0.0.0:8080 --workers 2 --timeout 120 app:app
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 8080
  routes:
  - path: /
  health_check:
    http_path: /api/health
  envs:
  - key: FLASK_ENV
    value: production
  - key: PYTHONPATH
    value: /app
```

### Step 4: Set Environment Variables
In the DigitalOcean App Platform dashboard:
- Add your OpenAI API key: `OPENAI_API_KEY=your-key-here`
- Add any other required environment variables
- Update CORS origins to include your Vercel domain

### Step 5: Deploy
1. Click "Create Resources"
2. Wait for deployment to complete
3. Note your API URL (something like `https://your-app-name.ondigitalocean.app`)

## Option 2: DigitalOcean Droplet with Docker

### Step 1: Create Droplet
1. Create a new Ubuntu 20.04 droplet
2. Choose appropriate size (2GB RAM minimum recommended)
3. Add your SSH key

### Step 2: Setup Server
```bash
# SSH into your droplet
ssh root@your-droplet-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### Step 3: Deploy Application
```bash
# Clone your repository
git clone https://github.com/your-username/your-repo.git
cd your-repo

# Navigate to backend directory
cd backend

# Create environment file
nano .env
# Add your environment variables:
# OPENAI_API_KEY=your-key-here
# FLASK_ENV=production
# PYTHONPATH=/app
# PORT=8080

# Build and run
docker build -t copywriter-api .
docker run -d --name copywriter-api -p 8080:8080 --env-file .env copywriter-api
```

### Step 4: Setup Nginx (Optional but recommended)
```bash
# Install Nginx
apt install nginx -y

# Create Nginx config
nano /etc/nginx/sites-available/copywriter-api

# Add configuration:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
ln -s /etc/nginx/sites-available/copywriter-api /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Step 5: Setup SSL with Let's Encrypt (Optional)
```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate
certbot --nginx -d your-domain.com

# Auto-renewal
crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Environment Variables Required

Set these in your deployment environment:
```
OPENAI_API_KEY=your-openai-api-key
FLASK_ENV=production
PYTHONPATH=/app
PORT=8080
```

## CORS Configuration

Update your Flask app's CORS configuration in `backend/app.py` to include your Vercel domain:
```python
CORS(app, origins=[
    "http://localhost:3000",  # Next.js development
    "https://your-nextjs-app.vercel.app",  # Your Vercel domain
    "https://*.vercel.app"  # All Vercel preview deployments
])
```

## File Structure for Deployment

Make sure your `backend/` directory has this structure:
```
backend/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── .env.example          # Environment variables template
├── services/             # API services
│   ├── __init__.py
│   ├── image_analyzer.py
│   ├── copy_generator.py
│   ├── brand_data_manager.py
│   └── image_cropper.py
├── static/               # Static files (logo, etc.)
├── uploads/              # Upload directory (will be created)
└── uploads/crops/        # Cropped images directory
```

## Testing Your Deployment

1. Test the health endpoint: `curl https://your-api-domain.com/api/health`
2. Test CORS: Make a request from your frontend
3. Test file uploads with a small image
4. Monitor logs for any errors

## Troubleshooting

### Common Issues
- **Build failures**: Check that `source_dir` is set to `/backend`
- **Import errors**: Ensure all Python files are in the backend directory
- **File upload issues**: Check upload directory permissions
- **CORS errors**: Verify CORS configuration includes your frontend domain

### Debug Commands
- Check logs: `docker logs copywriter-api`
- Restart container: `docker restart copywriter-api`
- Update app: Pull latest code, rebuild, and restart
- Check disk space: `df -h`
- Monitor memory: `free -h`

### App Platform Specific
- Check build logs in DigitalOcean dashboard
- Verify environment variables are set correctly
- Ensure source directory is set to `backend/`
- Check that health check endpoint is accessible 

## Option 3: DigitalOcean Droplet with Gunicorn & Nginx (No Docker)

This method deploys the Python application directly on the server using Gunicorn as the WSGI server and Nginx as a reverse proxy.

### Step 1: Create Droplet
1. Create a new Ubuntu 22.04 droplet.
2. Choose an appropriate size (1GB RAM is sufficient for this setup).
3. Add your SSH key for secure access.

### Step 2: Setup Server Environment
Connect to your droplet via SSH and run the following commands.

```bash
# SSH into your droplet
ssh root@your-droplet-ip

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Nginx, Python, and virtual environment tools
sudo apt install nginx python3-pip python3-dev python3-venv -y
```

### Step 3: Deploy Application Code
```bash
# Clone your repository
git clone https://github.com/your-username/your-repo.git
cd your-repo/backend

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies, including gunicorn
pip install -r requirements.txt
pip install gunicorn

# Create and populate the .env file
nano .env
```
Add your production environment variables to the `.env` file:
```
OPENAI_API_KEY=your-openai-api-key
FLASK_ENV=production
PYTHONPATH=/app
PORT=8080
```
Deactivate the virtual environment for now:
```bash
deactivate
```

### Step 4: Create a Systemd Service File
Create a service file to allow `systemd` to manage the Gunicorn process.

```bash
# Create and open the service file for editing
sudo nano /etc/systemd/system/copywriter-api.service
```

Paste the following content into the file. **Important:** Replace `your-username` with your actual username if you cloned the repo as a different user, and update paths if you cloned into a different directory than `/root`.

```ini
[Unit]
Description=Gunicorn instance for Copywriter Agent API
After=network.target

[Service]
User=root # Consider creating a non-root user for better security
Group=www-data
WorkingDirectory=/root/your-repo/backend
EnvironmentFile=/root/your-repo/backend/.env
ExecStart=/root/your-repo/backend/venv/bin/gunicorn --workers 3 --bind unix:copywriter-api.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```

Now, start and enable the service:
```bash
sudo systemctl start copywriter-api
sudo systemctl enable copywriter-api

# Check the status to ensure it's running correctly
sudo systemctl status copywriter-api
```

### Step 5: Configure Nginx as a Reverse Proxy
Configure Nginx to pass requests to the Gunicorn socket.

```bash
# Create an Nginx configuration file
sudo nano /etc/nginx/sites-available/copywriter-api
```

Add the following server block, replacing `your-domain.com` with your actual domain or droplet IP address.

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/root/your-repo/backend/copywriter-api.sock;
    }
}
```

Enable the configuration and restart Nginx:
```bash
# Link the config file to the sites-enabled directory
sudo ln -s /etc/nginx/sites-available/copywriter-api /etc/nginx/sites-enabled

# Test Nginx configuration for syntax errors
sudo nginx -t

# Restart Nginx to apply changes
sudo systemctl restart nginx
```

### Step 6: Setup SSL with Let's Encrypt (Recommended)
If you have a domain, secure your site with a free SSL certificate from Let's Encrypt.

```bash
# Install Certbot for Nginx
sudo apt install certbot python3-certbot-nginx -y

# Obtain and install the SSL certificate
sudo certbot --nginx -d your-domain.com

# Test the auto-renewal process
sudo certbot renew --dry-run
```
Your API should now be running securely on your domain. 

## Option 4: DigitalOcean Droplet with uWSGI & Nginx (No Docker)

This option uses uWSGI as the application server, which is a powerful alternative to Gunicorn, and pairs it with Nginx as a reverse proxy.

### Step 1: Create Droplet & Setup Server
Follow the same initial steps as in the Gunicorn setup:
1.  Create an Ubuntu 22.04 droplet.
2.  SSH into the server.
3.  Update packages: `sudo apt update && sudo apt upgrade -y`
4.  Install prerequisites: `sudo apt install nginx python3-pip python3-dev python3-venv -y`

### Step 2: Deploy Application Code & Install uWSGI
```bash
# Clone the repository
git clone https://github.com/your-username/your-repo.git
cd your-repo/backend

# Set up Python environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies, including uwsgi
pip install -r requirements.txt
pip install uwsgi

# Create the .env file
nano .env
```
Add your production environment variables to the `.env` file:
```
OPENAI_API_KEY=your-openai-api-key
FLASK_ENV=production
PYTHONPATH=/app
PORT=8080
```
You can now `deactivate` the virtual environment.

### Step 3: Configure uWSGI
Create a uWSGI configuration file to define how the application should run.

```bash
# Create a uWSGI configuration file
sudo nano /etc/uwsgi/sites/copywriter-api.ini
```

Paste the following configuration, replacing paths and usernames as needed:

```ini
[uwsgi]
module = wsgi:app

master = true
processes = 5

socket = /root/your-repo/backend/copywriter-api.sock
chmod-socket = 660
vacuum = true

die-on-term = true
```
You will also need to create a `wsgi.py` file in `your-repo/backend` to serve as the entry point for uWSGI:
```python
# wsgi.py
from app import app

if __name__ == "__main__":
    app.run()
```

### Step 4: Create a Systemd Service for uWSGI
Let `systemd` manage the uWSGI process for you.

```bash
# Create a systemd service file
sudo nano /etc/systemd/system/copywriter-api.service
```

Add the following service definition, updating the user and paths:

```ini
[Unit]
Description=uWSGI instance to serve Copywriter Agent API
After=network.target

[Service]
User=root # Consider a non-root user
Group=www-data
WorkingDirectory=/root/your-repo/backend
EnvironmentFile=/root/your-repo/backend/.env
ExecStart=/root/your-repo/backend/venv/bin/uwsgi --ini /etc/uwsgi/sites/copywriter-api.ini

[Install]
WantedBy=multi-user.target
```

Start and enable the service:
```bash
sudo systemctl start copywriter-api
sudo systemctl enable copywriter-api
sudo systemctl status copywriter-api
```

### Step 5: Configure Nginx Reverse Proxy
The Nginx configuration is nearly identical to the Gunicorn setup.

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/copywriter-api
```
Add the server block:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/root/your-repo/backend/copywriter-api.sock;
    }
}
```

Enable the site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/copywriter-api /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```
At this point, your deployment should be live. You can proceed with setting up SSL with Certbot as described in the Gunicorn guide. 