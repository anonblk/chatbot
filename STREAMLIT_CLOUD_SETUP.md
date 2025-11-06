# Deploy NBA Analytics App to Streamlit Cloud

## Step 1: Go to Streamlit Cloud
Visit: **https://share.streamlit.io/**

## Step 2: Sign In
- Click "Sign in with GitHub"
- Authorize Streamlit Cloud to access your GitHub repos

## Step 3: Deploy New App
1. Click **"New app"** button
2. Fill in the details:
   - **Repository**: `petermartens98/NBA-Analytics-Streamlit-App-with-LangChain-Agent`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
   - **App URL** (optional): Choose a custom name or use auto-generated

## Step 4: Add Your DeepSeek API Key (Optional - for Chat feature)
1. Click **"Advanced settings"**
2. In the **Secrets** section, add:
   ```toml
   DEEPSEEK_API_KEY = "optimalbet_eZUJHiYbKyVWzb95OQlQhnQjQumDbFVv"
   ```
3. Click **"Save"**

## Step 5: Deploy!
- Click **"Deploy!"**
- Wait 2-3 minutes for the app to build and start
- You'll get a URL like: `https://your-app-name.streamlit.app`

## Step 6: Access on Your iPhone 📱
- Open Safari on your iPhone
- Go to your Streamlit Cloud URL
- Bookmark it for easy access!
- The Chat feature will work automatically with your API key

## Benefits ✨
- ✅ Access from anywhere (iPhone, iPad, any device)
- ✅ Always online (no need to keep your computer running)
- ✅ Automatic SSL/HTTPS (secure connection)
- ✅ Free hosting
- ✅ Auto-updates when you push to GitHub

## Alternative: Deploy from Your Forked Repo
If you want to make modifications:
1. Fork `petermartens98/NBA-Analytics-Streamlit-App-with-LangChain-Agent` to your GitHub
2. Make your changes
3. Deploy from your forked repository in Streamlit Cloud
