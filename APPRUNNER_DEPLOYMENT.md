# AWS App Runner Deployment Guide

This guide will help you deploy the Waste Segregation AI to AWS App Runner with both frontend and backend in a single container.

## Prerequisites

- AWS Account with appropriate permissions
- GitHub repository with your code
- AWS credentials configured (already in .env file)

## Step 1: Push Code to GitHub

```powershell
git init
git add .
git commit -m "Ready for App Runner deployment"
git branch -M main
# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/waste-segregation-ai.git
git push -u origin main
```

## Step 2: Deploy to AWS App Runner

### 2.1 Go to AWS App Runner Console
- Navigate to: https://console.aws.amazon.com/apprunner/
- Click "Create service"

### 2.2 Configure Source
- **Source repository**: GitHub
- Click "Connect to GitHub"
- Authorize AWS to access your GitHub
- Select your repository: `waste-segregation-ai`
- Select branch: `main`

### 2.3 Configure Build Settings
- **Build configuration**: Managed runtime
- **Runtime**: Python 3.9
- **Build command**: Leave empty (auto-detected)
- **Start command**: `gunicorn -b 0.0.0.0:5000 app:app`

### 2.4 Configure Service
- **Service name**: `waste-segregation-ai`
- **Port**: 5000

### 2.5 Configure Environment Variables
Click "Add environment variable" and add:
- `AWS_ACCESS_KEY_ID`: Your AWS access key (from .env)
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key (from .env)
- `AWS_REGION`: `ap-south-1`

### 2.6 Review and Deploy
- Review all settings
- Click "Create and deploy"
- Wait for deployment (3-5 minutes)

## Step 3: Access Your Deployed App

Once deployment is complete, App Runner will provide a URL like:
`https://xxxxxxxxxx.us-east-1.apprunner.amazonsaws.com`

Open this URL to test your deployed application.

## Step 4: Update Amplify (Optional)

If you want to keep your Amplify frontend and point it to the new App Runner backend:

1. Go to your Amplify app console
2. Update the fetch URL in index.html to point to your App Runner URL:
   ```javascript
   const response = await fetch('https://your-apprunner-url/upload', {
   ```
3. Redeploy to Amplify

## Troubleshooting

### Deployment fails
- Check that Dockerfile is in the root directory
- Verify requirements.txt includes all dependencies
- Check App Runner logs for specific errors

### App runs but predictions fail
- Verify AWS credentials are correct in environment variables
- Check that AWS Rekognition is enabled in your region
- Verify IAM user has `AmazonRekognitionFullAccess` permission

### Can't access the app
- Check App Runner service status
- Verify the service is in "Running" state
- Check security group settings (should allow port 5000)

## Cost

AWS App Runner free tier:
- First 3 services: Free for 750 hours/month
- Additional services: $0.004 per GB-hour
- AWS Rekognition: 5,000 images/month free (first 12 months)

## Notes

- The app now serves both frontend and backend from a single container
- The frontend uses relative URLs (`/upload`) so it works seamlessly
- AWS credentials are stored as environment variables (never commit .env to GitHub)
