# DigitalOcean Deployment Guide for Flask API

This guide provides the necessary commands to deploy the Flask backend on a DigitalOcean droplet using uWSGI and Nginx.

---

### Step 1: Copy Project Files to Server

From your local machine, securely copy the `backend` directory to your server's root directory.

```bash
# Replace your-server-ip with your droplet's IP address
scp -r ./backend root@164.90.145.200:/root/
```

---

### Step 2: Initial Server Setup

Connect to your server and install the required packages.

```bash
# Connect to your server
ssh root@164.90.145.200

# Update system and install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install nginx python3-pip python3-dev python3-venv -y
```

---

### Step 3: Configure Python Environment

Set up the application environment and install dependencies.

```bash
# Navigate to the backend directory
cd /root/backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
pip install uwsgi

# Create a .env file with your production keys
nano .env
```

Your `.env` file should contain:
```
OPENAI_API_KEY=your-openai-api-key
FLASK_ENV=production
PYTHONPATH=/app
PORT=8080
```

Create a `wsgi.py` file for uWSGI to use as an entrypoint:
```bash
# Create wsgi.py
nano wsgi.py
```
Add the following content to `wsgi.py`:
```python
from app import app

if __name__ == "__main__":
    app.run()
```

Deactivate the virtual environment:
```bash
deactivate
```

---

### Step 4: Configure uWSGI Service

Create a uWSGI configuration file.

```bash
# Create directory for uWSGI sites if it doesn't exist
sudo mkdir -p /etc/uwsgi/sites

# Create the configuration file
sudo nano /etc/uwsgi/sites/copywriter-api.ini
```

Paste this into the file:
```ini
[uwsgi]
module = wsgi:app
master = true
processes = 5
socket = /root/backend/copywriter-api.sock
chmod-socket = 660
vacuum = true
die-on-term = true
```

Now, create a `systemd` service to manage uWSGI.

```bash
# Create the systemd service file
sudo nano /etc/systemd/system/copywriter-api.service
```

Paste this configuration:
```ini
[Unit]
Description=uWSGI instance to serve Copywriter Agent API
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/root/backend
EnvironmentFile=/root/backend/.env
ExecStart=/root/backend/venv/bin/uwsgi --ini /etc/uwsgi/sites/copywriter-api.ini

[Install]
WantedBy=multi-user.target
```

Start and enable the service:
```bash
sudo systemctl start copywriter-api
sudo systemctl enable copywriter-api
sudo systemctl status copywriter-api
```

---

### Step 5: Configure Nginx as a Reverse Proxy

Create an Nginx server block to route traffic to uWSGI.

```bash
# Create Nginx config file
sudo nano /etc/nginx/sites-available/copywriter-api
```

Paste the following. It is configured to run on your server's IP address.
```nginx
server {
    listen 80;
    server_name 164.90.145.200; # Use your server's IP

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/root/backend/copywriter-api.sock;
    }
}
```

Enable the site and restart Nginx:
```bash
# Remove default nginx site if it exists
sudo rm /etc/nginx/sites-enabled/default

# Enable your site
sudo ln -s /etc/nginx/sites-available/copywriter-api /etc/nginx/sites-enabled

# Test and restart Nginx
sudo nginx -t
sudo systemctl restart nginx
```

The API is now deployed and accessible at http://164.90.145.200. 