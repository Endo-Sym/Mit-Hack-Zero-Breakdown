# AWS Amplify Deployment Guide

## Prerequisites

- AWS Account with Amplify access
- GitHub repository connected to AWS Amplify
- AWS Bedrock access configured

## Environment Variables (Required)

Set these in AWS Amplify Console → App Settings → Environment Variables:

```
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
VITE_API_URL=https://your-backend-api-url.com
```

## Build Settings

### Frontend
- Framework: React (Vite)
- Node Version: 20.x
- Build Command: `npm run build`
- Build Output Directory: `zero-breakdown-app/dist`

### Backend (Optional - for static export only)
- Python Version: 3.11
- Package Manager: pip
- Requirements: `backend/requirements.txt`

## Deployment Steps

### 1. Connect Repository
```bash
# Push to GitHub
git add .
git commit -m "Deploy to AWS Amplify"
git push origin main
```

### 2. Configure Amplify Console
1. Go to AWS Amplify Console
2. Connect your GitHub repository
3. Select branch: `main`
4. Amplify will auto-detect `amplify.yml`

### 3. Set Environment Variables
In Amplify Console:
- Navigate to: App Settings → Environment Variables
- Add all required variables listed above

### 4. Deploy Backend API Separately

**Option A: AWS Lambda + API Gateway**
```bash
# Use AWS SAM or Serverless Framework
cd backend
serverless deploy
```

**Option B: AWS EC2 / Elastic Beanstalk**
```bash
# Deploy FastAPI to EC2
cd backend
eb init
eb create zero-breakdown-api
eb deploy
```

**Option C: AWS App Runner**
```bash
# Use Docker to deploy
docker build -t zero-breakdown-backend ./backend
aws ecr create-repository --repository-name zero-breakdown-backend
docker tag zero-breakdown-backend:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/zero-breakdown-backend:latest
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/zero-breakdown-backend:latest
```

### 5. Update Frontend API URL
After backend deployment, update `VITE_API_URL` in Amplify environment variables with your backend URL.

## Build Output Structure

```
zero-breakdown-app/dist/
├── index.html
├── assets/
│   ├── index-[hash].js
│   ├── index-[hash].css
│   └── ...
└── ...
```

## Troubleshooting

### Build Fails
1. Check Node/Python versions in build logs
2. Verify all dependencies in package.json/requirements.txt
3. Check environment variables are set correctly

### Backend Connection Issues
1. Verify CORS settings in FastAPI
2. Check API Gateway/Lambda permissions
3. Ensure VITE_API_URL is correct

### PyMuPDF Installation Issues
If PyMuPDF fails to install, add to requirements.txt:
```
pymupdf-fonts==1.0.5
```

## Post-Deployment

1. Test frontend: `https://main.xxxxxxxxxx.amplifyapp.com`
2. Test backend API endpoints
3. Verify AWS Bedrock integration works
4. Check CSV upload functionality
5. Test PDF embedding generation

## Monitoring

- CloudWatch Logs for backend
- Amplify Console for frontend build logs
- AWS X-Ray for tracing (optional)

## Cost Optimization

- Use Amplify free tier (1000 build minutes/month)
- Consider Lambda for backend (pay per request)
- Use S3 for static file storage
- Enable CloudFront caching

## CI/CD Pipeline

Every push to `main` branch will trigger:
1. Automatic build via amplify.yml
2. Frontend deployment to Amplify
3. Backend artifacts prepared (manual deployment required)

## Support

For issues, check:
- AWS Amplify Documentation
- FastAPI Documentation
- AWS Bedrock Documentation