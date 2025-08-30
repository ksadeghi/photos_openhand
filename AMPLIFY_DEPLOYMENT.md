

# AWS Amplify + Lambda Deployment Guide

This guide explains how to deploy the Photos OpenHand gallery using AWS Amplify for the frontend and AWS Lambda for the backend API.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AWS Amplify   │    │   AWS Lambda     │    │      AWS S3     │
│   (Frontend)    │───▶│   (Backend API)  │───▶│   (Pictures)    │
│                 │    │                  │    │                 │
│ • index.html    │    │ • GET /api/*     │    │ • Image files   │
│ • style.css     │    │ • POST /api/*    │    │ • Metadata      │
│ • script.js     │    │ • DELETE /api/*  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 File Structure

```
/workspace/
├── Frontend (Amplify):
│   ├── index.html          # Main HTML page
│   ├── style.css           # Styling
│   ├── script.js           # Frontend JavaScript
│   └── amplify.yml         # Amplify build configuration
│
├── Backend (Lambda):
│   ├── backend_lambda.py   # Backend API handler
│   └── terraform/          # Infrastructure as Code
│
└── Documentation:
    ├── AMPLIFY_DEPLOYMENT.md
    └── README.md
```

## 🚀 Deployment Steps

### Step 1: Deploy Backend Infrastructure

First, deploy the Lambda function and S3 bucket using Terraform:

```bash
cd terraform/

# Initialize Terraform
terraform init

# Create terraform.tfvars file
cat > terraform.tfvars << EOF
aws_region = "us-east-1"
bucket_name = "photos-openhand-bucket-$(date +%s)"
lambda_function_name = "photos-openhand-backend"
EOF

# Plan and apply
terraform plan
terraform apply
```

**Important**: Note the Lambda Function URL from the Terraform output - you'll need this for the frontend.

### Step 2: Update Frontend Configuration

Update the API endpoint in `script.js`:

```javascript
// Replace this line in script.js:
const API_BASE_URL = 'https://your-lambda-function-url.lambda-url.region.on.aws';

// With your actual Lambda Function URL:
const API_BASE_URL = 'https://abc123def456.lambda-url.us-east-1.on.aws';
```

### Step 3: Deploy Frontend with AWS Amplify

#### Option A: Deploy via AWS Console

1. **Go to AWS Amplify Console**
   - Navigate to https://console.aws.amazon.com/amplify/
   - Click "New app" → "Host web app"

2. **Connect Repository**
   - Choose "Deploy without Git provider" for manual deployment
   - Or connect your GitHub repository

3. **Configure Build Settings**
   - Amplify will automatically detect the `amplify.yml` file
   - The build configuration is already set up

4. **Deploy**
   - Click "Save and deploy"
   - Wait for deployment to complete

#### Option B: Deploy via AWS CLI

```bash
# Install AWS CLI and configure credentials
aws configure

# Create Amplify app
aws amplify create-app --name photos-openhand-gallery

# Create a deployment package
zip -r frontend.zip index.html style.css script.js amplify.yml

# Deploy to Amplify
aws amplify create-deployment --app-id YOUR_APP_ID --branch-name main
```

### Step 4: Configure CORS (if needed)

The Lambda function already includes CORS headers, but if you encounter issues:

1. **Check Lambda Function URL CORS settings**
2. **Verify the API_BASE_URL in script.js matches exactly**
3. **Ensure all API endpoints return proper CORS headers**

## 🔧 Configuration Details

### Frontend Configuration (`script.js`)

Key configuration at the top of `script.js`:

```javascript
// Configuration - Update this with your Lambda function URL
const API_BASE_URL = 'https://your-lambda-function-url.lambda-url.region.on.aws';
```

### Backend Configuration (`backend_lambda.py`)

Key configuration in the Lambda function:

```python
# Configuration
PICTURES_BUCKET = 'photos-openhand-bucket'  # Update with your bucket name
```

### Amplify Build Configuration (`amplify.yml`)

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - echo "No build process needed for static files"
    build:
      commands:
        - echo "Building static frontend..."
        - echo "Frontend files are ready to serve"
  artifacts:
    baseDirectory: /
    files:
      - index.html
      - style.css
      - script.js
  cache:
    paths: []
```

## 🌐 API Endpoints

The backend Lambda provides these API endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/pictures` | Get all pictures |
| POST | `/api/pictures` | Upload a picture |
| DELETE | `/api/pictures` | Delete pictures |
| POST | `/api/pictures/rate` | Rate a picture |
| POST | `/api/pictures/comment` | Add comment |
| POST | `/api/pictures/download` | Download pictures as ZIP |
| GET | `/api/stats` | Get gallery statistics |

## 🔒 Security Considerations

### CORS Configuration
- Lambda function includes proper CORS headers
- Allows all origins (`*`) for development
- Consider restricting origins in production

### S3 Bucket Security
- Bucket is private by default
- Lambda uses presigned URLs for image access
- Images are not publicly accessible

### Lambda Function Security
- Function has minimal IAM permissions
- Only accesses the designated S3 bucket
- No external dependencies beyond AWS SDK

## 🧪 Testing the Deployment

### 1. Test Backend API

```bash
# Test the Lambda function directly
curl https://your-lambda-function-url.lambda-url.region.on.aws/api/pictures

# Should return JSON array of pictures
```

### 2. Test Frontend

1. Open the Amplify app URL in your browser
2. Try uploading a picture
3. Test rating and commenting features
4. Test bulk download functionality

### 3. Verify S3 Integration

```bash
# List objects in your S3 bucket
aws s3 ls s3://your-bucket-name/pictures/

# Should show uploaded pictures
```

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Verify API_BASE_URL in script.js is correct
   - Check Lambda function CORS headers
   - Ensure Lambda Function URL allows CORS

2. **Pictures Not Loading**
   - Check S3 bucket permissions
   - Verify Lambda has S3 read permissions
   - Check presigned URL generation

3. **Upload Failures**
   - Verify Lambda has S3 write permissions
   - Check file size limits (Lambda has 6MB limit for synchronous invocations)
   - Verify base64 encoding in frontend

4. **Download Not Working**
   - Check Lambda timeout settings (increase for large downloads)
   - Verify ZIP file creation in Lambda logs
   - Check browser download settings

### Debug Steps

1. **Check Lambda Logs**
   ```bash
   aws logs tail /aws/lambda/photos-openhand-backend --follow
   ```

2. **Check Amplify Build Logs**
   - Go to Amplify Console → Your App → Build History
   - Check build logs for errors

3. **Test API Endpoints**
   ```bash
   # Test each endpoint individually
   curl -X GET https://your-lambda-url/api/pictures
   curl -X GET https://your-lambda-url/api/stats
   ```

## 📊 Monitoring and Maintenance

### CloudWatch Monitoring
- Lambda function metrics available in CloudWatch
- Set up alarms for errors and duration
- Monitor S3 bucket usage

### Cost Optimization
- Amplify hosting: Pay per GB served
- Lambda: Pay per request and execution time
- S3: Pay for storage and requests

### Updates and Maintenance
- Frontend updates: Push to Amplify (automatic deployment if connected to Git)
- Backend updates: Update Lambda function code via Terraform or AWS Console
- Infrastructure changes: Update Terraform configuration

## 🎯 Production Considerations

### Performance
- Consider CloudFront CDN for global distribution
- Optimize image sizes and formats
- Implement caching strategies

### Security
- Restrict CORS origins to your domain
- Implement authentication (Cognito)
- Add input validation and sanitization

### Scalability
- Lambda automatically scales
- Consider S3 Transfer Acceleration for large uploads
- Monitor and adjust Lambda timeout and memory settings

## 📝 Next Steps

1. **Custom Domain**: Configure a custom domain for your Amplify app
2. **Authentication**: Add user authentication with AWS Cognito
3. **CDN**: Set up CloudFront for better performance
4. **Monitoring**: Implement comprehensive monitoring and alerting
5. **Backup**: Set up S3 cross-region replication for backups

---

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review AWS CloudWatch logs
3. Verify all configuration settings
4. Test each component individually

The separated architecture provides better scalability, maintainability, and follows AWS best practices for modern web applications.


