# Deploying to Vercel

This guide will walk you through deploying the FinQuery application to Vercel.

## Prerequisites

1. A GitHub, GitLab, or Bitbucket account
2. A Vercel account (sign up at [vercel.com](https://vercel.com) if you don't have one)
3. Your code pushed to a Git repository

## Deployment Steps

### 1. Prepare Your Repository

Make sure all your files are committed and pushed to your Git repository. The repository should include:

- `hackrx_llm/` - Main application code
- `vercel.json` - Vercel configuration
- `requirements-vercel.txt` - Python dependencies

### 2. Deploy to Vercel

#### Option A: Using Vercel Dashboard

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New..." > "Project"
3. Import your Git repository
4. In the project settings:
   - Set the framework preset to "Other"
   - Set the root directory to "."
   - Set the build command to leave it empty
   - Set the output directory to "public" (Vercel will ignore this for Python)
   - Set the install command to: `pip install -r requirements-vercel.txt`
5. Click "Deploy"

#### Option B: Using Vercel CLI

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Deploy:
   ```bash
   vercel
   ```

### 3. Configure Environment Variables

After deployment, you'll need to set up these environment variables in your Vercel project settings:

1. Go to your project in Vercel Dashboard
2. Navigate to Settings > Environment Variables
3. Add the following variables:
   - `PYTHON_VERSION`: `3.9` (or your preferred Python version)
   - `DOCS_DIR`: `documents` (path to your documents directory)
   - `INDEX_PATH`: `backend_index/store` (path to store the FAISS index)
   - `TOP_K`: `5` (number of results to return)

### 4. Deploying Updates

Vercel will automatically deploy updates when you push to your connected Git repository. For manual deployments:

```bash
git add .
git commit -m "Your commit message"
git push
```

## Troubleshooting

### Common Issues

1. **Build Fails**
   - Check the build logs in the Vercel dashboard
   - Ensure all dependencies are listed in `requirements-vercel.txt`
   - Make sure the Python version is compatible with your dependencies

2. **Static Files Not Loading**
   - Verify the static files are in the correct location (`hackrx_llm/static/`)
   - Check the network tab in browser dev tools for 404 errors

3. **API Endpoints Not Working**
   - Ensure all API routes are properly defined in `webapp.py`
   - Check the Vercel function logs for errors

## Local Development

To test locally before deploying:

```bash
# Install dependencies
pip install -r requirements-vercel.txt

# Run the development server
python -m hackrx_llm.webapp
```

Visit `http://localhost:8000` to test your application locally.

## Additional Resources

- [Vercel Python Runtimes](https://vercel.com/docs/runtimes#official-runtimes/python)
- [Vercel Configuration Reference](https://vercel.com/docs/configuration)
- [Flask on Vercel](https://vercel.com/guides/deploying-flask-with-vercel)
