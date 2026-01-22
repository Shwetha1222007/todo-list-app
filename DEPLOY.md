# Deployment Guide for TaskMaster Pro

Since your app is built with **Streamlit**, the easiest and fastest way to deploy it for free is using **Streamlit Community Cloud**.

## Prerequisites
1. Ensure your code is on GitHub (which we just did!).
   - Repository: `https://github.com/Shwetha1222007/todo-list-app`
2. You need a free account at [share.streamlit.io](https://share.streamlit.io/).

## Steps to Deploy

1. **Log in** to [Streamlit Community Cloud](https://share.streamlit.io/).
2. Click the **"New app"** button.
3. Choose **"Use existing repo"**.
4. Select your repository: `Shwetha1222007/todo-list-app`.
5. Configuration:
   - **Branch**: `main`
   - **Main file path**: `app.py`
6. Click **"Deploy!"**.

## Important Limitations
- **Data Persistence**: On the free Community Cloud, the local `tasks.json` file is **ephemeral**. This means if the app restarts (which happens occasionally), your tasks might be reset. 
- **Audio Autoplay**: Modern browsers often block audio from playing automatically unless the user has interacted with the page first. The "Activate" button in the sidebar handles this.
- **Background Run**: The "Autonomous Alarm" works while the tab is open. If you close the browser tab, the Python script stops running, and alarms will not trigger until you visit the URL again.

## Need Permanent Data?
To save tasks permanently (even after app restarts), you would need to connect a database (like Google Sheets, Firestore, or Supabase).
