# MASTER ALL VIDEO DOWNLOADER
Free, ad-free, no account needed. Download only what you have the right to save.

## 1. Run the server (PC)
    pip install -r backend/requirements.txt
    cd backend && uvicorn app:app --host 0.0.0.0 --port 8000
Install ffmpeg (needed to merge video and audio). Open http://localhost:8000 to test.

## 2. Build the Android app (Android Studio + Node.js)
1. Find your PC's local IP (for example 192.168.1.20). Phone and PC must be on the same Wi-Fi.
2. Edit capacitor.config.json: set server.url to http://YOUR_IP:8000
3. Run:
       npm install
       npx cap add android
       npx cap sync android
       npx cap open android
4. In Android Studio press Run (phone with USB debugging) or Build > Build APK.
For use away from home, host the backend on a server with HTTPS and put that URL in server.url.

## Not built yet
Pause button, accounts/cloud history, native background service, notifications, settings page.
Hosting and bandwidth cost money; funding must come from the owner, not users.
