# Deploying Waste Segregation AI to AWS

This guide shows you how to deploy the Waste Segregation AI application to AWS.

## Architecture Overview

The app consists of:
- **Frontend**: Static HTML/CSS/JavaScript files
- **Backend**: Flask Python app with AWS Rekognition integration

## Deployment Options

### Option 1: AWS Amplify (Frontend) + AWS Elastic Beanstalk (Backend) - RECOMMENDED
### Option 2: AWS Amplify (Full Stack with Serverless)
### Option 3: AWS App Runner (Simplest)

---

## Option 1: AWS Amplify (Frontend) + Elastic Beanstalk (Backend)

### Step 1: Deploy Backend to AWS Elastic Beanstalk

**1. Install EB CLI**
```powershell
pip install awsebcli
```

**2. Initialize Elastic Beanstalk**
```powershell
cd C:\Users\Dell\Desktop\waste
eb init
```
- Select region: `ap-south-1` (or your region)
- Select platform: `Python`
- Select Python version: `3.9 or later`
- Application name: `waste-segregation-ai`
- Environment name: `waste-segregation-prod`

**3. Create deployment configuration**
Create `.ebextensions/python.config`:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app.py
  aws:elasticbeanstalk:application:environment:
    AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
    AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
    AWS_REGION: "${AWS_REGION}"
```

**4. Deploy**
```powershell
eb create waste-segregation-prod
```

**5. Get backend URL**
```powershell
eb status
```
Note the `CNAME` - this is your backend URL (e.g., `waste-segregation-prod.ap-south-1.elasticbeanstalk.com`)

---

### Step 2: Update Frontend to Use Backend URL

**1. Open `index.html`**
**2. Find line 518:**
```javascript
const response = await fetch('http://localhost:5000/upload', {
```

**3. Replace with your Elastic Beanstalk URL:**
```javascript
const response = await fetch('https://waste-segregation-prod.ap-south-1.elasticbeanstalk.com/upload', {
```

---

### Step 3: Deploy Frontend to AWS Amplify

**1. Push code to GitHub**
```powershell
git init
git add .
git commit -m "Initial commit"
git branch -M main
# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/waste-segregation-ai.git
git push -u origin main
```

**2. Go to AWS Amplify Console**
- Navigate to https://console.aws.amazon.com/amplify/
- Click "New app" → "Host web app"

**3. Connect GitHub**
- Click "GitHub" → "Connect"
- Authorize AWS to access your GitHub
- Select `waste-segregation-ai` repository
- Select `main` branch

**4. Configure build settings**
- App name: `waste-segregation-ai`
- Environment name: `prod`
- Build settings: Accept defaults (amplify.yml will be used)

**5. Deploy**
- Click "Save and deploy"
- Wait for deployment to complete (~2-3 minutes)

**6. Access your app**
- Amplify will provide a URL like: `https://main.d1234567890.amplifyapp.com`
- Open this URL to test your deployed app

---

## Option 2: AWS Amplify with Serverless Backend (API Gateway + Lambda)

### Step 1: Convert Flask to Serverless

**1. Install Zappa**
```powershell
pip install zappa
```

**2. Initialize Zappa**
```powershell
zappa init
```
- Select region: `ap-south-1`
- App name: `waste-segregation-ai`
- S3 bucket: Create new
- Confirm settings

**3. Deploy to Lambda**
```powershell
zappa deploy production
```

**4. Get API Gateway URL**
Zappa will output a URL like: `https://xyz123.execute-api.ap-south-1.amazonaws.com/production`

**5. Update frontend URL in index.html** (same as Option 1, Step 2)

**6. Deploy frontend to Amplify** (same as Option 1, Step 3)

---

## Option 3: AWS App Runner (Simplest - Full Stack)

### Step 1: Prepare Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
```

Add `gunicorn` to `requirements.txt`:
```
flask>=3.0.0
flask-cors>=4.0.0
boto3>=1.34.0
Pillow>=10.0.0
gunicorn>=21.0.0
```

### Step 2: Push to GitHub
Same as Option 1, Step 3.1

### Step 3: Deploy to App Runner

**1. Go to AWS App Runner Console**
- Navigate to https://console.aws.amazon.com/apprunner/
- Click "Create service"

**2. Configure source**
- Source: GitHub
- Connect your repository
- Select `waste-segregation-ai` repo
- Branch: `main`

**3. Configure build settings**
- Build configuration: Image
- Platform: Linux
- Architecture: x86_64
- Runtime: Python 9

**4. Configure service**
- Service name: `waste-segregation-ai`
- Port: 5000

**5. Deploy**
- Click "Create and deploy"
- Wait for deployment (~3-5 minutes)

**6. Access your app**
- App Runner will provide a URL
- Open this URL to test

---

## Setting Environment Variables

### For Elastic Beanstalk (Option 1):
```powershell
eb setenv AWS_ACCESS_KEY_ID="your-key" AWS_SECRET_ACCESS_KEY="your-secret" AWS_REGION="ap-south-1"
```

### For Amplify (Option 2):
1. Go to Amplify Console
2. Select your app
3. Go to "Environment variables" → "Manage variables"
4. Add:
   - `AWS_ACCESS_KEY_ID`: your-key
   - `AWS_SECRET_ACCESS_KEY`: your-secret
   - `AWS_REGION`: ap-south-1

### For App Runner (Option 3):
1. Go to App Runner Console
2. Select your service
3. Go to "Configuration" → "Environment variables"
4. Add the same variables

---

## Important Notes

### AWS Rekognition IAM Permissions
Ensure your IAM user has:
- `AmazonRekognitionFullAccess`
- Or specific permissions for `rekognition:DetectLabels`

### Free Tier Limits
- AWS Rekognition: 5,000 images/month (free for first 12 months)
- Elastic Beanstalk: 750 hours/month (free tier)
- Amplify: 1,000 build minutes/month (free tier)
- App Runner: Free tier may not be available

### Security
- Never commit AWS credentials to GitHub
- Use environment variables for sensitive data
- Consider using AWS Secrets Manager for production

---

## Troubleshooting

### Backend not responding
- Check Elastic Beanstalk logs
- Verify environment variables are set
- Ensure IAM permissions are correct

### Frontend can't connect to backend
- Check CORS settings in app.py
- Verify backend URL is correct
- Check browser console for errors

### AWS Rekognition errors
- Verify credentials are correct
- Check region matches your Rekognition setup
- Ensure IAM user has proper permissions

---

## Recommended: Option 1 (Elastic Beanstalk + Amplify)

**Why:**
- Separates concerns (frontend vs backend)
- Easier to debug and maintain
- Better for scaling
- More control over backend configuration

**Time to deploy:** ~15-20 minutes
**Cost:** Free tier covers most usage
