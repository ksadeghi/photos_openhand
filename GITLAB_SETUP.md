

# GitLab Setup Instructions for photos_openhand

## Step 1: Create GitLab Project

1. Go to [GitLab.com](https://gitlab.com)
2. Click "New project" or the "+" button
3. Choose "Create blank project"
4. Fill in the details:
   - **Project name**: `photos_openhand`
   - **Project description**: `Serverless Picture Gallery Application with AWS Lambda Functions, S3 storage, and Apache Iceberg data management`
   - **Visibility**: Choose your preferred visibility (Private/Internal/Public)
   - **Initialize repository with a README**: Leave unchecked (we already have one)

## Step 2: Push Your Code

After creating the project, GitLab will show you the repository URL. Use these commands:

```bash
# Add GitLab as remote origin (replace YOUR_USERNAME with your GitLab username)
git remote add origin https://gitlab.com/YOUR_USERNAME/photos_openhand.git

# Push to GitLab
git push -u origin master
```

## Alternative: If you have a GitLab token

If you have a GitLab personal access token, you can use:

```bash
# Replace YOUR_TOKEN and YOUR_USERNAME
git remote add origin https://oauth2:YOUR_TOKEN@gitlab.com/YOUR_USERNAME/photos_openhand.git
git push -u origin master
```

## Step 3: Verify Upload

After pushing, you should see all these files in your GitLab repository:

- `README.md` - Main project documentation
- `DEPLOYMENT_GUIDE.md` - Detailed deployment instructions
- `frontend_lambda.py` - Frontend Lambda function
- `backend_lambda.py` - Backend Lambda function
- `serverless.yml` - Serverless Framework configuration
- `requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies
- `deploy.sh` - Deployment script
- `demo_server.py` - Local demo server
- `local_test.py` - Local testing script
- `iceberg_setup.py` - Iceberg table setup
- `.env.example` - Environment variables template
- `.gitignore` - Git ignore rules

## Next Steps

1. **Set up CI/CD** (optional):
   - Configure GitLab CI/CD pipeline
   - Add AWS credentials as GitLab variables
   - Automate deployment on push

2. **Configure project settings**:
   - Add project description and tags
   - Set up issue templates
   - Configure merge request settings

3. **Invite collaborators** (if needed):
   - Add team members with appropriate permissions
   - Set up branch protection rules

## Repository Structure

Your repository is now ready with:
✅ Complete serverless picture gallery application
✅ AWS Lambda functions for frontend and backend
✅ S3 and Iceberg integration
✅ Deployment automation
✅ Local development and testing tools
✅ Comprehensive documentation


