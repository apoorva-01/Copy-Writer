# 🚀 DigitalOcean Deployment Guide - Copywriting Agent

Complete step-by-step guide to deploy your Flask copywriting agent on DigitalOcean.

## 📋 Prerequisites

- DigitalOcean account
- Domain name (optional but recommended)
- OpenAI API key
- Google Sheets credentials (if using real brand data)
- Local terminal with SSH access

## 🎯 Deployment Overview

We'll set up:
- Ubuntu 22.04 Droplet
- Python 3.11+ environment
- Gunicorn WSGI server
- Nginx reverse proxy
- PM2 for process management
- SSL certificate with Let's Encrypt
- Firewall configuration

---

## Step 1: Create DigitalOcean Droplet

1. **Log into DigitalOcean Dashboard**
   - Go to [DigitalOcean](https://www.digitalocean.com/)
   - Click "Create" → "Droplets"

2. **Choose Configuration**
   ```
   Image: Ubuntu 22.04 (LTS) x64
   Plan: Basic
   CPU: Regular Intel - $12/month (2GB RAM, 1 vCPU, 50GB SSD)
   Region: Choose closest to your users
   Authentication: SSH Key (recommended) or Password
   ```

3. **Add SSH Key (Recommended)**
   - Generate SSH key locally if you don't have one:
   ```bash
   ssh-keygen -t rsa -b 4096 -c "your_email@example.com"
   ```
   - Copy public key:
   ```bash
   cat ~/.ssh/id_rsa.pub
   ```
   - Paste in DigitalOcean SSH key field

4. **Create Droplet**
   - Name your droplet (e.g., "copywriting-agent")
   - Click "Create Droplet"
   - Note the IP address once created

---

## Step 2: Initial Server Setup

1. **Connect to Your Droplet**
   ```bash
   ssh root@your_droplet_ip
   ```

2. **Update System Packages**
   ```bash
   apt update && apt upgrade -y
   ```

3. **Install Essential Packages**
   ```bash
   apt install -y python3 python3-pip python3-venv git nginx ufw curl software-properties-common
   ```

4. **Install Node.js and PM2**
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
   apt install -y nodejs
   npm install -g pm2
   ```

5. **Create Application User**
   ```bash
   adduser --system --group --home /home/copywriter copywriter
   usermod -aG sudo copywriter
   ```

---

## Step 3: Deploy Your Application

1. **Switch to Application User**
   ```bash
   su - copywriter
   cd /home/copywriter
   ```

2. **Clone Your Repository**
   
   **Option A: If using Git repository:**
   ```bash
   git clone https://github.com/yourusername/your-repo.git copywriting-agent
   cd copywriting-agent
   ```
   
   **Option B: Upload files manually:**
   ```bash
   mkdir copywriting-agent
   cd copywriting-agent
   # Then upload your files using scp from local machine:
   # scp -r /path/to/your/project/* copywriter@your_droplet_ip:/home/copywriter/copywriting-agent/
   ```

3. **Create Python Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Python Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Create Upload Directory**
   ```bash
   mkdir -p uploads
   chmod 755 uploads
   ```

---

## Step 4: Environment Configuration

1. **Create Production Environment File**
   ```bash
   nano .env
   ```

2. **Add Your Environment Variables**
   ```env
   # Flask Configuration
   FLASK_ENV=production
   SECRET_KEY=your-super-secret-production-key-here-change-this
   
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Google Sheets Configuration (Optional)
   GOOGLE_SHEETS_ID=your_google_sheets_id
   GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"..."}
   # OR
   # GOOGLE_SERVICE_ACCOUNT_PATH=/home/copywriter/copywriting-agent/credentials.json
   ```

3. **Secure the Environment File**
   ```bash
   chmod 600 .env
   ```

4. **Test the Application**
   ```bash
   source venv/bin/activate
   python3 app.py
   ```
   - Press `Ctrl+C` to stop after confirming it starts without errors

---

## Step 5: Configure Gunicorn

1. **Create Gunicorn Configuration**
   ```bash
   nano gunicorn.conf.py
   ```

2. **Add Gunicorn Settings**
   ```python
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
   ```

3. **Create Logs Directory**
   ```bash
   mkdir logs
   ```

4. **Test Gunicorn**
   ```bash
   source venv/bin/activate
   gunicorn --config gunicorn.conf.py app:app
   ```
   - Press `Ctrl+C` to stop after confirming it works

---

## Step 6: Configure PM2 for Process Management

1. **Create PM2 Configuration**
   ```bash
   nano ecosystem.config.js
   ```

2. **Add PM2 Configuration**
   ```javascript
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
   ```

3. **Start Application with PM2**
   ```bash
   pm2 start ecosystem.config.js
   pm2 save
   pm2 startup
   ```
   - Copy and run the command PM2 provides for auto-startup

4. **Verify Application is Running**
   ```bash
   pm2 status
   pm2 logs copywriting-agent
   ```

---

## Step 7: Configure Nginx Reverse Proxy

1. **Exit from copywriter user back to root**
   ```bash
   exit
   ```

2. **Create Nginx Configuration**
   ```bash
   nano /etc/nginx/sites-available/copywriting-agent
   ```

3. **Add Nginx Configuration**
   ```nginx
   server {
       listen 80;
       server_name your_domain.com www.your_domain.com;  # Replace with your domain
       
       client_max_body_size 20M;  # Allow large file uploads
       
       # Serve static files directly
       location /static {
           alias /home/copywriter/copywriting-agent/static;
           expires 30d;
           add_header Cache-Control "public, no-transform";
       }
       
       # Handle file uploads
       location /uploads {
           alias /home/copywriter/copywriting-agent/uploads;
           internal;  # Only allow internal access
       }
       
       # Proxy all other requests to Gunicorn
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           
           # Handle long-running requests (for AI processing)
           proxy_read_timeout 300s;
           proxy_connect_timeout 75s;
           
           # WebSocket support (if needed in future)
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }
   }
   ```

4. **Enable the Site**
   ```bash
   ln -s /etc/nginx/sites-available/copywriting-agent /etc/nginx/sites-enabled/
   rm /etc/nginx/sites-enabled/default  # Remove default site
   ```

5. **Test and Restart Nginx**
   ```bash
   nginx -t
   systemctl restart nginx
   systemctl enable nginx
   ```

---

## Step 8: Configure Firewall

1. **Set Up UFW Firewall**
   ```bash
   ufw default deny incoming
   ufw default allow outgoing
   ufw allow ssh
   ufw allow 'Nginx Full'
   ufw --force enable
   ```

2. **Check Firewall Status**
   ```bash
   ufw status
   ```

---

## Step 9: Domain and SSL Setup

### If you have a domain:

1. **Point Domain to Droplet**
   - In your domain registrar's DNS settings:
   ```
   A record: @ → your_droplet_ip
   A record: www → your_droplet_ip
   ```

2. **Install Certbot for SSL**
   ```bash
   apt install snapd
   snap install core; snap refresh core
   snap install --classic certbot
   ln -s /snap/bin/certbot /usr/bin/certbot
   ```

3. **Get SSL Certificate**
   ```bash
   certbot --nginx -d your_domain.com -d www.your_domain.com
   ```

4. **Set Up Auto-Renewal**
   ```bash
   certbot renew --dry-run
   ```

### If you don't have a domain:

You can access your app directly via IP: `http://your_droplet_ip`

---

## Step 10: Final Configuration and Testing

1. **Set Proper File Permissions**
   ```bash
   chown -R copywriter:copywriter /home/copywriter/copywriting-agent
   chmod -R 755 /home/copywriter/copywriting-agent
   chmod 600 /home/copywriter/copywriting-agent/.env
   ```

2. **Restart All Services**
   ```bash
   su - copywriter -c "cd /home/copywriter/copywriting-agent && pm2 restart all"
   systemctl restart nginx
   ```

3. **Test Your Application**
   ```bash
   curl -I http://your_domain.com  # or http://your_droplet_ip
   ```

4. **Monitor Application**
   ```bash
   # Check PM2 status
   su - copywriter -c "pm2 status"
   
   # Check logs
   su - copywriter -c "pm2 logs copywriting-agent"
   
   # Check Nginx logs
   tail -f /var/log/nginx/access.log
   tail -f /var/log/nginx/error.log
   ```

---

## 🔧 Post-Deployment Maintenance

### Regular Updates

1. **Update Application**
   ```bash
   su - copywriter
   cd /home/copywriter/copywriting-agent
   git pull  # if using git
   source venv/bin/activate
   pip install -r requirements.txt
   pm2 restart copywriting-agent
   ```

2. **Update System**
   ```bash
   apt update && apt upgrade -y
   pm2 update  # Update PM2 if needed
   ```

### Monitoring Commands

```bash
# Check application status
pm2 status

# View real-time logs
pm2 logs copywriting-agent --lines 100

# Monitor system resources
htop

# Check disk space
df -h

# Check memory usage
free -h
```

### Backup Strategy

1. **Backup Application Data**
   ```bash
   # Create backup script
   nano /home/copywriter/backup.sh
   ```

   ```bash
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   BACKUP_DIR="/home/copywriter/backups"
   APP_DIR="/home/copywriter/copywriting-agent"
   
   mkdir -p $BACKUP_DIR
   
   # Backup uploads and logs
   tar -czf $BACKUP_DIR/app_data_$DATE.tar.gz $APP_DIR/uploads $APP_DIR/logs
   
   # Keep only last 7 backups
   find $BACKUP_DIR -name "app_data_*.tar.gz" -mtime +7 -delete
   ```

   ```bash
   chmod +x /home/copywriter/backup.sh
   ```

2. **Set Up Automated Backups**
   ```bash
   crontab -e -u copywriter
   # Add: 0 2 * * * /home/copywriter/backup.sh
   ```

---

## 🚨 Troubleshooting

### Common Issues

1. **Application Won't Start**
   ```bash
   # Check PM2 logs
   pm2 logs copywriting-agent
   
   # Check if all dependencies are installed
   su - copywriter -c "cd /home/copywriter/copywriting-agent && source venv/bin/activate && pip list"
   ```

2. **502 Bad Gateway Error**
   ```bash
   # Check if Gunicorn is running
   pm2 status
   
   # Check Nginx configuration
   nginx -t
   
   # Check Nginx logs
   tail -f /var/log/nginx/error.log
   ```

3. **File Upload Issues**
   ```bash
   # Check permissions
   ls -la /home/copywriter/copywriting-agent/uploads
   
   # Fix permissions if needed
   chown -R copywriter:copywriter /home/copywriter/copywriting-agent/uploads
   chmod 755 /home/copywriter/copywriting-agent/uploads
   ```

4. **Out of Memory**
   ```bash
   # Check memory usage
   free -h
   
   # Restart application
   pm2 restart copywriting-agent
   
   # Consider upgrading droplet size
   ```

### Performance Optimization

1. **Enable Gzip Compression**
   ```bash
   nano /etc/nginx/nginx.conf
   ```
   
   Uncomment and configure gzip settings:
   ```nginx
   gzip on;
   gzip_vary on;
   gzip_min_length 1024;
   gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
   ```

2. **Optimize Gunicorn Workers**
   - Monitor CPU usage and adjust workers in `gunicorn.conf.py`
   - Formula: `(2 x CPU cores) + 1`

---

## 🎉 Success!

Your copywriting agent is now deployed and running on DigitalOcean! 

**Access your application:**
- With domain: `https://your_domain.com`
- Without domain: `http://your_droplet_ip`

**Key URLs:**
- Main app: `/`
- Health check: Add a health endpoint if needed

**Next Steps:**
- Set up monitoring with services like UptimeRobot
- Consider adding a CDN for better performance
- Set up automated backups to DigitalOcean Spaces
- Monitor costs and optimize droplet size as needed

---

## 📞 Need Help?

If you encounter issues:
1. Check the logs: `pm2 logs copywriting-agent`
2. Verify all services are running: `pm2 status && systemctl status nginx`
3. Test connectivity: `curl -I http://localhost:8000`
4. Check this guide's troubleshooting section

Your copywriting agent is now live and ready to generate brand-perfect copy! 🚀 