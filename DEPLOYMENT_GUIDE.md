

# Picture Gallery Lambda Deployment Guide

## Quick Start

### 1. Local Demo (No AWS Required)
```bash
# Run the local demo server
python demo_server.py
```
Visit http://localhost:8000 to see the application in action.

### 2. AWS Deployment

#### Prerequisites
- AWS CLI configured with appropriate permissions
- Node.js and npm installed
- Python 3.9+

#### Step-by-Step Deployment

1. **Install Serverless Framework:**
   ```bash
   npm install -g serverless
   npm install
   ```

2. **Configure AWS credentials:**
   ```bash
   aws configure
   ```

3. **Deploy to AWS:**
   ```bash
   ./deploy.sh dev us-east-1
   ```

4. **Update frontend with backend URL:**
   ```bash
   # Get backend URL from deployment output
   BACKEND_URL=$(aws cloudformation describe-stacks \
       --stack-name picture-gallery-app-dev \
       --query 'Stacks[0].Outputs[?OutputKey==`BackendUrl`].OutputValue' \
       --output text)
   
   # Update frontend code
   sed -i "s|https://your-backend-lambda-url.lambda-url.region.on.aws|$BACKEND_URL|g" frontend_lambda.py
   
   # Redeploy frontend
   serverless deploy function -f frontend --stage dev
   ```

5. **Optional: Setup Iceberg table:**
   ```bash
   python iceberg_setup.py
   ```

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │
│   Lambda        │    │   Lambda        │
│   (HTML/CSS/JS) │    │   (API)         │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┘
                     │
         ┌─────────────────┐    ┌─────────────────┐
         │   S3 Bucket     │    │   Iceberg       │
         │   (Pictures)    │    │   (Metadata)    │
         └─────────────────┘    └─────────────────┘
```

## Features Implemented

✅ **Frontend Lambda Function**
- Serves HTML, CSS, and JavaScript
- Responsive design with modern UI
- File upload interface
- Picture filtering capabilities

✅ **Backend Lambda Function**
- RESTful API endpoints
- Image upload and processing
- S3 integration
- CORS support
- Error handling

✅ **S3 Integration**
- Secure file storage
- Presigned URLs for image access
- Metadata storage

✅ **Iceberg Support**
- Structured data management
- Schema definition
- Query capabilities (ready for implementation)

✅ **Deployment Automation**
- Serverless Framework configuration
- Infrastructure as Code
- Automated deployment scripts

## API Endpoints

### Frontend Lambda
- `GET /` - Main application page
- `GET /style.css` - CSS styles
- `GET /script.js` - JavaScript code

### Backend Lambda
- `GET /pictures` - List all pictures with optional filtering
- `POST /upload` - Upload new pictures
- `GET /picture/{id}` - Get specific picture details

## Configuration

### Environment Variables
- `PICTURES_BUCKET` - S3 bucket for storing images
- `ICEBERG_BUCKET` - S3 bucket for Iceberg data
- `ICEBERG_TABLE_PATH` - Path to Iceberg table
- `AWS_REGION` - AWS deployment region

### Customization Options
- Modify UI in `frontend_lambda.py`
- Add API endpoints in `backend_lambda.py`
- Update Iceberg schema in `iceberg_setup.py`
- Configure deployment in `serverless.yml`

## Security Features

🔒 **S3 Security**
- Private buckets with public access blocked
- Presigned URLs for secure image access
- CORS configuration

🔒 **Lambda Security**
- Minimal IAM permissions
- Input validation
- Error handling without information leakage

🔒 **API Security**
- CORS headers properly configured
- Content-Type validation
- File type restrictions

## Cost Optimization

💰 **Lambda**
- Pay-per-request pricing
- Optimized memory allocation
- Efficient code execution

💰 **S3**
- Standard storage class
- Lifecycle policies (can be added)
- Intelligent tiering (optional)

💰 **Iceberg**
- Efficient data format
- Columnar storage
- Query optimization

## Monitoring & Logging

📊 **CloudWatch Integration**
- Function logs
- Performance metrics
- Error tracking
- Custom dashboards

📊 **X-Ray Tracing** (Optional)
- Request tracing
- Performance analysis
- Bottleneck identification

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check backend CORS headers
   - Verify frontend-backend URL configuration

2. **Upload Failures**
   - Check S3 bucket permissions
   - Verify Lambda memory settings
   - Check file size limits

3. **Image Display Issues**
   - Verify presigned URL generation
   - Check S3 bucket CORS configuration

### Debug Commands

```bash
# View Lambda logs
serverless logs -f frontend --tail
serverless logs -f backend --tail

# Test functions locally
serverless invoke local -f frontend
serverless invoke local -f backend

# Run local tests
python local_test.py
```

## Next Steps

1. **Production Deployment**
   ```bash
   ./deploy.sh prod us-west-2
   ```

2. **Custom Domain Setup**
   - Configure Route 53
   - Add SSL certificate
   - Update serverless.yml

3. **Enhanced Features**
   - Image thumbnails
   - User authentication
   - Advanced filtering
   - Batch operations

4. **Performance Optimization**
   - CloudFront CDN
   - Lambda@Edge
   - Database indexing

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review CloudWatch logs
3. Test with local demo server
4. Verify AWS permissions and configuration


