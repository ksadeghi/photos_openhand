

# Quick Start Guide - Photos OpenHand

## 🚀 Running the Local Demo

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Demo Server
```bash
python demo_server.py
```

The server will start on http://localhost:8000 and automatically open in your browser.

### 3. Test the Application
- **Upload Pictures**: Click "Choose Files" and select image files
- **Filter by Date**: Use the date picker to filter pictures
- **Filter by Name**: Type in the name filter box
- **View Gallery**: Pictures will display in a responsive grid

## 🔧 Development

### Local Testing
```bash
python local_test.py
```

### AWS Deployment
```bash
# Install Serverless Framework
npm install -g serverless
npm install

# Deploy to AWS
./deploy.sh dev us-east-1
```

## 📁 Project Structure
- `demo_server.py` - Local development server
- `frontend_lambda.py` - Frontend Lambda function
- `backend_lambda.py` - Backend API Lambda function
- `serverless.yml` - AWS deployment configuration
- `requirements.txt` - Python dependencies

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'PIL'"
```bash
pip install -r requirements.txt
```

### Server not starting
Make sure port 8000 is available:
```bash
lsof -i :8000  # Check if port is in use
```

### Upload directory issues
The demo creates `/tmp/demo_pictures` automatically. If you have permission issues, check your `/tmp` directory permissions.

## 🌐 Features Demonstrated

✅ **File Upload** - Drag & drop or click to upload images  
✅ **Image Processing** - Automatic resize and format conversion  
✅ **Responsive Design** - Works on desktop and mobile  
✅ **Filtering** - Filter by date and name  
✅ **Real-time Updates** - Gallery updates after uploads  
✅ **Error Handling** - Graceful error messages  

## 📝 Next Steps

1. **Try the local demo** to see all features
2. **Deploy to AWS** for production use
3. **Customize the UI** by editing `frontend_lambda.py`
4. **Add features** by extending `backend_lambda.py`


