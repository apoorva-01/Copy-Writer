# Vercel Deployment Guide for Next.js Frontend

## Prerequisites
- Vercel account (free tier available)
- GitHub/GitLab repository with your Next.js code
- Your Flask API deployed and accessible

## Step 1: Prepare Your Repository

Make sure your repository has a `frontend/` directory containing:
- `package.json` with Next.js dependencies
- `next.config.js` with proper configuration
- `vercel.json` (optional but recommended)
- `app/` directory with your Next.js App Router code
- `public/` directory with static assets

## Step 2: Deploy to Vercel

### Option A: Vercel Dashboard (Recommended)

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your GitHub/GitLab repository
4. Vercel will automatically detect it's a Next.js project
5. **Important**: Configure the Root Directory:
   - In the project setup, set **Root Directory** to `frontend`
   - This tells Vercel to look for your Next.js app in the frontend folder
6. Configure the following settings:

**Build and Output Settings:**
- Framework Preset: `Next.js`
- Root Directory: `frontend` (Important!)
- Build Command: `npm run build` (auto-detected)
- Output Directory: `.next` (auto-detected)
- Install Command: `npm install` (auto-detected)

**Environment Variables:**
Add these in the Environment Variables section:
```
NEXT_PUBLIC_API_URL=https://your-flask-api.digitalocean.com
```

7. Click "Deploy"

### Option B: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to your frontend directory
cd frontend

# Login to Vercel
vercel login

# Deploy from your frontend directory
vercel

# Follow the prompts:
# - Set up and deploy? Y
# - Which scope? (select your account)
# - Link to existing project? N
# - What's your project's name? copywriter-agent-frontend
# - In which directory is your code located? ./

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL
# Enter: https://your-flask-api.digitalocean.com

# Deploy to production
vercel --prod
```

### Option C: Deploy from Repository Root

If you want to deploy from the repository root instead of just the frontend folder:

1. In Vercel dashboard, set **Root Directory** to `frontend`
2. All build commands will automatically run from the frontend directory
3. This allows you to keep both frontend and backend in the same repository

## Step 3: Configure Environment Variables

In your Vercel dashboard:

1. Go to your project settings
2. Click "Environment Variables"
3. Add the following variables:

| Name | Value | Environment |
|------|-------|-------------|
| `NEXT_PUBLIC_API_URL` | `https://your-flask-api.digitalocean.com` | Production, Preview, Development |

## Step 4: Update Your Flask API CORS

After deployment, update your Flask API's CORS configuration in `backend/app.py` to include your Vercel domain:

```python
# In your backend/app.py
CORS(app, origins=[
    "http://localhost:3000",  # Next.js development
    "https://your-app-name.vercel.app",  # Your production domain
    "https://*.vercel.app"  # All Vercel preview deployments
])
```

## Step 5: Custom Domain (Optional)

1. In your Vercel project dashboard, go to "Settings" > "Domains"
2. Add your custom domain
3. Follow the DNS configuration instructions
4. Update your Flask API CORS to include the custom domain

## Step 6: Automatic Deployments

Vercel automatically deploys when you push to your main branch. You can:

1. **Preview Deployments**: Every pull request gets a preview URL
2. **Production Deployments**: Pushes to main branch deploy to production
3. **Branch Deployments**: Configure specific branches for staging

## Vercel Configuration Files

### frontend/vercel.json (Optional)
```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "functions": {
    "app/api/**/*.js": {
      "maxDuration": 30
    }
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

### frontend/next.config.js
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}/api/:path*`,
      },
    ]
  },
  images: {
    domains: ['localhost'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
}

module.exports = nextConfig
```

## Project Structure for Deployment

Your repository should look like this:
```
your-repo/
├── frontend/              # Next.js application (Vercel deploys this)
│   ├── app/              # Next.js App Router
│   ├── public/           # Static assets
│   ├── package.json      # Dependencies
│   ├── next.config.js    # Next.js config
│   ├── vercel.json       # Vercel config (optional)
│   └── .env.local        # Local environment variables
├── backend/              # Flask API (deployed separately)
│   └── ...
└── README.md
```

## Testing Your Deployment

1. **Test the deployment URL**: Visit your Vercel app URL
2. **Test API connectivity**: Try uploading an image and generating copy
3. **Test responsive design**: Check on mobile and desktop
4. **Test CORS**: Ensure API calls work from your domain
5. **Test environment variables**: Verify API URL is correct

## Troubleshooting

### Common Issues:

1. **Build failures**: Check that Root Directory is set to `frontend`
2. **API calls failing**: Check NEXT_PUBLIC_API_URL environment variable
3. **CORS errors**: Update Flask API CORS configuration
4. **Images not loading**: Verify image paths and Next.js Image component usage
5. **404 errors**: Ensure all required files are in the frontend directory

### Debug Steps:

1. **Check build logs**: Vercel dashboard > Deployments > Click on deployment
2. **Verify Root Directory**: Project Settings > General > Root Directory should be `frontend`
3. **Check environment variables**: Project Settings > Environment Variables
4. **Test locally**: Run `cd frontend && npm run build && npm start` locally
5. **Check file structure**: Ensure all Next.js files are in frontend directory

### Performance Optimization:

1. **Enable Image Optimization**: Next.js handles this automatically
2. **Static Generation**: Most pages can be statically generated
3. **Bundle Analysis**: Run `npm run build` to see bundle sizes
4. **Caching**: Vercel automatically handles caching

## Environment-Specific URLs

- **Development**: `http://localhost:3000` (run from `frontend/` directory)
- **Preview**: `https://your-app-git-branch-username.vercel.app`
- **Production**: `https://your-app.vercel.app`

## Monitoring and Analytics

1. **Vercel Analytics**: Enable in project settings
2. **Web Vitals**: Monitor Core Web Vitals
3. **Function Logs**: Monitor API route performance (if using Next.js API routes)
4. **Speed Insights**: Track page load performance

## Development Workflow

1. **Local Development**: Run `cd frontend && npm run dev`
2. **Test Build**: Run `cd frontend && npm run build`
3. **Push Changes**: Commit and push to trigger automatic deployment
4. **Monitor**: Check Vercel dashboard for deployment status

Your Next.js frontend should now be deployed on Vercel and communicating with your Flask API on DigitalOcean! 