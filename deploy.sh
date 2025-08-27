#!/bin/bash

# Deployment script for Picture Gallery Lambda Application

set -e

echo "🚀 Starting deployment of Picture Gallery Lambda Application..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

# Check if Serverless Framework is installed
if ! command -v serverless &> /dev/null; then
    echo "📦 Installing Serverless Framework..."
    npm install -g serverless
fi

# Check if serverless-python-requirements plugin is installed
if ! serverless plugin list | grep -q "serverless-python-requirements"; then
    echo "📦 Installing serverless-python-requirements plugin..."
    serverless plugin install -n serverless-python-requirements
fi

# Set deployment stage (default to dev)
STAGE=${1:-dev}
REGION=${2:-us-east-1}

echo "📍 Deploying to stage: $STAGE in region: $REGION"

# Deploy the application
echo "🔧 Deploying Lambda functions and infrastructure..."
serverless deploy --stage $STAGE --region $REGION

# Get the function URLs
echo "🔗 Getting function URLs..."
FRONTEND_URL=$(aws cloudformation describe-stacks \
    --stack-name picture-gallery-app-$STAGE \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`FrontendUrl`].OutputValue' \
    --output text)

BACKEND_URL=$(aws cloudformation describe-stacks \
    --stack-name picture-gallery-app-$STAGE \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`BackendUrl`].OutputValue' \
    --output text)

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "📱 Application URLs:"
echo "   Frontend: $FRONTEND_URL"
echo "   Backend:  $BACKEND_URL"
echo ""
echo "🔧 Next steps:"
echo "1. Update the API_BASE_URL in the frontend JavaScript code with your backend URL"
echo "2. Visit the frontend URL to access your picture gallery"
echo "3. Configure your Iceberg table in the backend if needed"
echo ""
echo "📝 To update the frontend with the correct backend URL, run:"
echo "   sed -i \"s|https://your-backend-lambda-url.lambda-url.region.on.aws|$BACKEND_URL|g\" frontend_lambda.py"
echo "   serverless deploy function -f frontend --stage $STAGE --region $REGION"

