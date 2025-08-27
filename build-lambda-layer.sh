


#!/bin/bash

# Build Lambda Layer with dependencies
# This script creates a Lambda layer with all Python dependencies

set -e

echo "🔧 Building Lambda Layer with dependencies..."

# Create temporary directory
LAYER_DIR="lambda-layer"
rm -rf $LAYER_DIR
mkdir -p $LAYER_DIR/python

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r lambda_requirements.txt -t $LAYER_DIR/python/

# Create zip file
echo "📦 Creating layer zip file..."
cd $LAYER_DIR
zip -r ../lambda-layer.zip .
cd ..

# Cleanup
rm -rf $LAYER_DIR

echo "✅ Lambda layer created: lambda-layer.zip"
echo "   Size: $(du -h lambda-layer.zip | cut -f1)"


