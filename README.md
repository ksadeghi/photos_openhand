
# Picture Gallery Lambda Application

A serverless web application built with AWS Lambda functions that stores and displays pictures using S3 and Apache Iceberg for data management.

## Architecture

- **Frontend Lambda**: Serves HTML, CSS, and JavaScript files
- **Backend Lambda**: Handles API requests for picture upload and retrieval
- **S3 Storage**: Stores actual picture files
- **Apache Iceberg**: Manages picture metadata in a structured table format
- **AWS Glue**: Provides catalog services for Iceberg tables

## Features

- 📸 Upload multiple pictures at once
- 🔍 Filter pictures by date and name
- 📱 Responsive web interface
- ⚡ Serverless architecture with Lambda function URLs
- 🗄️ Structured data management with Apache Iceberg
- 🔒 Secure file storage in S3

## Prerequisites

- AWS CLI configured with appropriate permissions
- Node.js and npm (for Serverless Framework)
- Python 3.9+
- Serverless Framework

## Quick Start

1. **Clone and setup the project:**
   ```bash
   git clone <your-repo>
   cd picture-gallery-lambda
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   npm install -g serverless
   serverless plugin install -n serverless-python-requirements
   ```

3. **Deploy the application:**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh dev us-east-1
   ```

4. **Setup Iceberg table (optional):**
   ```bash
   python iceberg_setup.py
   ```

## Configuration

### Environment Variables

The application uses the following environment variables:

- `PICTURES_BUCKET`: S3 bucket for storing picture files
- `ICEBERG_BUCKET`: S3 bucket for Iceberg table data
- `ICEBERG_TABLE_PATH`: Path to the Iceberg table
- `AWS_REGION`: AWS region for deployment

### Customization

1. **Update bucket names** in `serverless.yml`:
   ```yaml
   custom:
     picturesBucket: your-custom-pictures-bucket
     icebergBucket: your-custom-iceberg-bucket
   ```

2. **Modify the frontend** by editing the HTML, CSS, and JavaScript in `frontend_lambda.py`

3. **Extend the backend API** by adding new endpoints in `backend_lambda.py`

## API Endpoints

### Backend Lambda Function URLs

- `GET /pictures` - Retrieve all pictures with optional filtering
  - Query parameters: `date`, `name`
- `POST /upload` - Upload new pictures
- `GET /picture/{id}` - Get specific picture by ID

### Frontend Lambda Function URLs

- `GET /` - Main application page
- `GET /style.css` - CSS styles
- `GET /script.js` - JavaScript code

## File Structure

```
picture-gallery-lambda/
├── frontend_lambda.py      # Frontend Lambda function
├── backend_lambda.py       # Backend Lambda function
├── iceberg_setup.py       # Iceberg table setup
├── serverless.yml         # Serverless Framework configuration
├── requirements.txt       # Python dependencies
├── deploy.sh             # Deployment script
└── README.md             # This file
```

## Development

### Local Testing

You can test the Lambda functions locally using the Serverless Framework:

```bash
# Test frontend function
serverless invoke local -f frontend

# Test backend function
serverless invoke local -f backend --data '{"requestContext":{"http":{"method":"GET"}},"rawPath":"/pictures"}'
```

### Adding New Features

1. **New API endpoints**: Add them to `backend_lambda.py` and update the routing logic
2. **Frontend changes**: Modify the HTML, CSS, or JavaScript in `frontend_lambda.py`
3. **Database schema**: Update the Iceberg schema in `iceberg_setup.py`

## Deployment

### Production Deployment

```bash
./deploy.sh prod us-west-2
```

### Update Frontend with Backend URL

After deployment, update the frontend with the correct backend URL:

```bash
# Get the backend URL from CloudFormation outputs
BACKEND_URL=$(aws cloudformation describe-stacks \
    --stack-name picture-gallery-app-dev \
    --query 'Stacks[0].Outputs[?OutputKey==`BackendUrl`].OutputValue' \
    --output text)

# Update the frontend code
sed -i "s|https://your-backend-lambda-url.lambda-url.region.on.aws|$BACKEND_URL|g" frontend_lambda.py

# Redeploy the frontend function
serverless deploy function -f frontend
```

## Monitoring and Logging

- **CloudWatch Logs**: All Lambda function logs are available in CloudWatch
- **X-Ray Tracing**: Enable X-Ray tracing in `serverless.yml` for detailed performance monitoring
- **CloudWatch Metrics**: Monitor function invocations, duration, and errors

## Security Considerations

- S3 buckets are configured with public access blocked
- CORS is properly configured for cross-origin requests
- Presigned URLs are used for secure image access
- Lambda functions have minimal IAM permissions

## Cost Optimization

- Lambda functions are configured with appropriate memory and timeout settings
- S3 lifecycle policies can be added to manage storage costs
- Consider using S3 Intelligent Tiering for automatic cost optimization

## Troubleshooting

### Common Issues

1. **CORS errors**: Ensure the backend Lambda has proper CORS headers
2. **Image upload failures**: Check S3 bucket permissions and Lambda memory settings
3. **Iceberg table errors**: Verify Glue database and table permissions

### Debugging

1. Check CloudWatch logs for detailed error messages
2. Use `serverless logs -f functionName` to view recent logs
3. Test API endpoints directly using curl or Postman

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

