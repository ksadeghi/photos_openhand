
#!/bin/bash

# Deploy Photos OpenHand Gallery - Separated Architecture
# This script deploys the backend Lambda and provides instructions for frontend deployment

set -e

echo "🚀 Deploying Photos OpenHand Gallery - Separated Architecture"
echo "=============================================================="

# Check if we're in the right directory
if [ ! -f "backend_lambda.py" ]; then
    echo "❌ Error: backend_lambda.py not found. Please run this script from the project root."
    exit 1
fi

# Check if terraform directory exists
if [ ! -d "terraform" ]; then
    echo "❌ Error: terraform directory not found."
    exit 1
fi

# Navigate to terraform directory
cd terraform

echo "📋 Step 1: Initializing Terraform..."
terraform init

# Check if terraform.tfvars exists, if not create a template
if [ ! -f "terraform.tfvars" ]; then
    echo "📝 Creating terraform.tfvars template..."
    cat > terraform.tfvars << EOF
# AWS Configuration
aws_region = "us-east-1"

# Project Configuration
project_name = "photos-openhand"
environment = "prod"

# S3 Configuration
bucket_name_suffix = "$(date +%s)"

# Lambda Configuration
lambda_timeout = 60
lambda_memory_size = 512

# Iceberg Configuration (optional)
iceberg_warehouse_path = "warehouse/"
EOF
    echo "✅ Created terraform.tfvars - please review and update as needed"
    echo "📝 You may want to customize the aws_region and other settings"
fi

echo "📋 Step 2: Planning Terraform deployment..."
terraform plan

echo "🚀 Step 3: Applying Terraform configuration..."
terraform apply -auto-approve

echo ""
echo "✅ Backend deployment completed!"
echo ""

# Get the backend URL from terraform output
BACKEND_URL=$(terraform output -raw backend_api_url)

echo "📋 Step 4: Frontend Configuration Instructions"
echo "=============================================="
echo ""
echo "Your backend API is deployed at:"
echo "🔗 $BACKEND_URL"
echo ""
echo "To complete the deployment:"
echo ""
echo "1️⃣  Update the frontend configuration:"
echo "   Edit script.js and replace the API_BASE_URL with:"
echo "   const API_BASE_URL = '$BACKEND_URL';"
echo ""
echo "2️⃣  Deploy frontend to AWS Amplify:"
echo "   Option A - Manual Upload:"
echo "   • Go to AWS Amplify Console"
echo "   • Create new app → Deploy without Git"
echo "   • Upload: index.html, style.css, script.js, amplify.yml"
echo ""
echo "   Option B - Git Integration:"
echo "   • Connect your Git repository to Amplify"
echo "   • Amplify will automatically deploy on commits"
echo ""
echo "3️⃣  Test your deployment:"
echo "   • Backend API: curl $BACKEND_URL/api/pictures"
echo "   • Frontend: Open your Amplify app URL"
echo ""

# Create a quick update script for the frontend
cd ..
cat > update-frontend-config.sh << EOF
#!/bin/bash
# Quick script to update frontend configuration

BACKEND_URL="$BACKEND_URL"

echo "Updating script.js with backend URL..."
sed -i.bak "s|const API_BASE_URL = '.*';|const API_BASE_URL = '\$BACKEND_URL';|g" script.js

echo "✅ Updated script.js with backend URL: \$BACKEND_URL"
echo "📝 Original file backed up as script.js.bak"
echo ""
echo "Next steps:"
echo "1. Review the changes in script.js"
echo "2. Deploy to Amplify (upload index.html, style.css, script.js, amplify.yml)"
EOF

chmod +x update-frontend-config.sh

echo "📝 Created update-frontend-config.sh for easy frontend configuration"
echo ""
echo "🎯 Quick Start:"
echo "   ./update-frontend-config.sh    # Update frontend config"
echo "   # Then deploy to Amplify"
echo ""
echo "📚 For detailed instructions, see AMPLIFY_DEPLOYMENT.md"
echo ""
echo "🎉 Deployment completed successfully!"

