# Deployment Guide 🚀

## Step 1: Create a GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Name it (e.g., `finance-summary-app`)
5. Choose **Public** or **Private** (your choice)
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

## Step 2: Push Your Code to GitHub

After creating the repository, GitHub will show you commands. Use these commands in your terminal:

```bash
# Navigate to your project directory
cd c:\Users\Michael\coding\finance_app

# Add the remote repository (replace YOUR_USERNAME and YOUR_REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push your code
git push -u origin main
```

**Note**: Replace `YOUR_USERNAME` with your GitHub username and `YOUR_REPO_NAME` with your repository name.

## Step 3: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "Sign in" and authorize with your GitHub account
3. Click "New app" button
4. Fill in the form:
   - **Repository**: Select your repository from the dropdown
   - **Branch**: Select `main`
   - **Main file path**: Enter `app.py`
   - **App URL**: Choose a custom URL (optional)
5. Click "Deploy"

## Step 4: Wait for Deployment

- Streamlit Cloud will install dependencies from `requirements.txt`
- The app will build and deploy automatically
- You'll see a live URL once deployment is complete (e.g., `https://finance-summary-app.streamlit.app`)

## Troubleshooting

### If deployment fails:
1. Check that `requirements.txt` has all dependencies
2. Ensure `app.py` is in the root directory
3. Verify the main file path is correct (`app.py`)

### If you need to update the app:
1. Make changes locally
2. Commit and push:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push
   ```
3. Streamlit Cloud will automatically redeploy

## Security Notes

- ✅ CSV files are excluded from git (via `.gitignore`)
- ✅ Users upload files through the web interface (not stored in repo)
- ✅ No sensitive data is committed to the repository

