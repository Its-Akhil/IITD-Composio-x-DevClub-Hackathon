# AI Social Factory - Frontend Guide

## 📁 Frontend Structure

```
frontend/
├── index.html    # Main HTML interface
├── styles.css    # Styling and layout
└── script.js     # API interactions and logic
```

## 🚀 Quick Start

### 1. Start the Backend Server

First, ensure your backend server is running:

```powershell
# From project root directory (recommended)
.\start_dev.ps1

# Or use direct uvicorn command
uvicorn app.main:app --reload --reload-exclude "generated_videos/*" --reload-exclude "logs/*"

# Or simple Python command
python -m app.main
```

The server should start on `http://localhost:8000`

> **Note:** The server is now configured to ignore video files, logs, and database changes to prevent unnecessary restarts during generation.

### 2. Open the Frontend

Simply open `index.html` in your web browser:

- **Windows:** Double-click `index.html` or right-click → Open with → Your Browser
- **macOS/Linux:** Open in browser or use: `open index.html` / `xdg-open index.html`
- **Alternative:** Use VS Code Live Server extension for live reload

### 3. Configure API Key

Before using the frontend, update the API key in `script.js`:

```javascript
const API_KEY = 'your-secret-api-key-here'; // Line 3 in script.js
```

Replace with your actual API key from `.env` file (API_KEY value).

## 📋 Step-by-Step Usage Guide

The frontend presents 9 sequential steps to test and use your AI Social Factory:

### Step 1: Server Health Check ✅
- **Purpose:** Verify backend is running and all services are operational
- **Action:** Click "Check Status" button
- **Expected:** Green success message with service status
- **Troubleshooting:** 
  - Red error? Start backend server with `uvicorn app.main:app --reload`
  - Check if port 8000 is available
  - Verify no firewall blocking localhost connections

### Step 2: Test Gemini AI Integration 🤖
- **Purpose:** Confirm Google Gemini API is properly configured
- **Action:** Click "Test AI" button
- **Expected:** AI-generated response showing API is working
- **Troubleshooting:**
  - Check `GEMINI_API_KEY` in `.env` file
  - Get API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
  - Verify API key has proper permissions

### Step 3: Generate Video Scripts 📝
- **Purpose:** Create multiple script variants for social media videos
- **Action:** 
  1. Click "Generate" button to show form
  2. Enter topic (e.g., "AI and Future of Work")
  3. Select platform (Instagram/YouTube/TikTok/LinkedIn)
  4. Set duration in seconds
  5. Click "Submit"
- **Expected:** 3 unique script variants with different styles
- **Result Location:** Scripts displayed in the interface, also logged in backend

### Step 4: Generate Social Media Caption 📱
- **Purpose:** Create platform-optimized captions with hashtags
- **Action:**
  1. Click "Generate" button to show form
  2. Enter video script or description
  3. Select target platform
  4. Click "Submit"
- **Expected:** Engaging caption with 5-10 relevant hashtags
- **Platform Differences:**
  - Instagram: Visual-focused, 5-10 hashtags
  - LinkedIn: Professional, 2-3 hashtags
  - TikTok: Trendy, short, 3-5 hashtags

### Step 5: Google Sheets Content Calendar 📊
- **Purpose:** Check content calendar integration
- **Action:** Click "Check" button
- **Expected:** List of pending content items from Google Sheets
- **Setup Required:**
  1. Place `credentials.json` in project root
  2. Share sheet with service account email (found in credentials.json)
  3. Set `GOOGLE_SHEET_ID` in `.env` file
- **Troubleshooting:**
  - "Permission denied"? Share sheet with service account
  - "Not found"? Check GOOGLE_SHEET_ID in .env
  - Enable Google Sheets API in Google Cloud Console

### Step 6: Slack Notifications 📢
- **Purpose:** Test Slack webhook integration
- **Action:** Click "Send Test" button
- **Expected:** Success message, check Slack channel for notification
- **Where to Check:** Slack channel configured in `SLACK_WEBHOOK_URL`
- **Setup:**
  1. Create Slack incoming webhook
  2. Add webhook URL to `.env` as `SLACK_WEBHOOK_URL`
  3. Test in Slack channel

### Step 7: AI Video Generation 🎥
- **Purpose:** Generate video from text using AI model
- **Action:**
  1. Click "Generate" button to show form
  2. Enter video description/prompt
  3. Set number of frames (16 recommended)
  4. Click "Generate Video"
- **Expected:** Task ID and processing status
- **Important Notes:**
  - ⏱️ Takes 5-10 minutes on GPU, longer on CPU
  - 📦 First run downloads ~6GB model (10-30 min)
  - 📁 Videos saved to `generated_videos/` folder
  - 👁️ Monitor terminal logs for progress
- **Check Results:** 
  - Video file: `generated_videos/video_{task_id}.mp4`
  - Status: Terminal logs show progress
  - Database: Entry in `video_generations` table

### Step 8: Analytics & Database 📈
- **Purpose:** View system statistics and performance metrics
- **Action:** Click "View Stats" button
- **Expected:** Summary of videos generated, workflows executed
- **Database Info:**
  - File: `ai_social_factory.db` in project root
  - Tables: `video_generations`, `workflow_executions`
  - Tool: Use SQLite browser for detailed queries

### Step 9: Execute Complete Workflow 🔄
- **Purpose:** Run end-to-end automation pipeline
- **Action:**
  1. Click "Run Workflow" button to show form
  2. Enter content topic
  3. Select platform
  4. Click "Execute"
- **Process:**
  1. 📝 Generate script variants
  2. 📱 Generate caption with hashtags
  3. 🎥 Generate AI video (optional)
  4. 📤 Post to WordPress
  5. 📢 Send Slack notification
- **Timeline:** 10-15 minutes total
- **Monitor:** Check logs/ folder for real-time progress
- **Results:**
  - Video: `generated_videos/` folder
  - Post: WordPress admin dashboard
  - Notification: Slack channel
  - Database: `workflow_executions` table

## 🎨 Frontend Features

### Visual Indicators
- 🟢 **Green Border:** Step completed successfully
- 🔴 **Red Border:** Step failed or needs configuration
- 🟡 **Yellow Pulse:** Processing in progress
- **Status Dot:** Server online (green) or offline (red)

### Response Types
- ✅ **Success:** Operation completed successfully
- ❌ **Error:** Something went wrong, check troubleshooting
- ℹ️ **Info:** Additional context and guidance
- 📄 **JSON:** Raw API response for debugging

### Interactive Elements
- **Action Buttons:** Trigger API calls for each step
- **Forms:** Input fields slide in when needed
- **Results:** Auto-expand to show responses
- **JSON Viewer:** Formatted API responses for debugging

## 🔧 Configuration

### Required Environment Variables (.env)
```env
# Core API
API_KEY=your-secret-api-key-here

# Gemini AI
GEMINI_API_KEY=your-gemini-api-key

# Google Sheets
GOOGLE_SHEET_ID=your-sheet-id

# Slack
SLACK_WEBHOOK_URL=your-webhook-url

# WordPress
WORDPRESS_URL=your-wordpress-url
WORDPRESS_USERNAME=admin
WORDPRESS_APP_PASSWORD=your-app-password
```

### Update Frontend API Key
Edit `script.js` line 3:
```javascript
const API_KEY = 'your-secret-api-key-here';
```

## 📱 Responsive Design

The frontend is fully responsive and works on:
- 💻 Desktop browsers (Chrome, Firefox, Safari, Edge)
- 📱 Tablets (iPad, Android tablets)
- 📱 Mobile phones (iOS, Android)

## 🐛 Troubleshooting

### Frontend Not Connecting to Backend
1. ✅ Backend server running? Check terminal
2. ✅ Correct port? Default is 8000
3. ✅ CORS enabled? Backend has CORS middleware
4. ✅ Firewall blocking? Check Windows/Mac firewall

### API Key Errors
1. ✅ Updated API_KEY in script.js?
2. ✅ Matches value in .env file?
3. ✅ No quotes or spaces in key?
4. ✅ Backend server restarted after .env change?

### Steps Not Working
1. ✅ Start from Step 1 (Health Check)
2. ✅ Complete steps in order (dependencies)
3. ✅ Check browser console for errors (F12)
4. ✅ Review backend terminal logs
5. ✅ Verify all credentials in .env

### Browser Console Errors
- **CORS Error:** Backend CORS not configured (should be auto-enabled)
- **Network Error:** Backend not running or wrong URL
- **401 Unauthorized:** Incorrect API_KEY
- **500 Server Error:** Check backend logs

## 📊 Testing Workflow

Recommended testing sequence:

1. ✅ **Health Check** → Verify server is running
2. ✅ **Gemini Test** → Confirm AI API works
3. ✅ **Generate Script** → Test structured output
4. ✅ **Generate Caption** → Test caption generation
5. ✅ **Check Sheets** → Verify Google integration
6. ✅ **Test Slack** → Confirm notifications work
7. ⚠️ **Video Generation** → Optional (takes time)
8. ✅ **Analytics** → Check database working
9. 🎉 **Complete Workflow** → Run full automation

## 🎯 Success Criteria

You'll know everything works when:
- ✅ All steps show green checkmarks
- ✅ Server status shows "Online"
- ✅ Scripts generate with 3 variants
- ✅ Captions include hashtags
- ✅ Google Sheets returns data
- ✅ Slack receives notifications
- ✅ Videos appear in generated_videos/
- ✅ Analytics shows data
- ✅ Workflow completes all steps

## 💡 Tips

1. **Start Simple:** Test each step individually before running full workflow
2. **Monitor Logs:** Keep terminal visible to see real-time progress
3. **Save Prompts:** Good video prompts can be reused
4. **Check Results:** After each step, verify output in specified locations
5. **Be Patient:** Video generation takes time, especially first run
6. **Test Incrementally:** Don't jump to workflow without testing individual steps

## 🔗 Useful Links

- [Google AI Studio (Gemini API)](https://aistudio.google.com/app/apikey)
- [Google Cloud Console (Sheets API)](https://console.cloud.google.com/)
- [Slack Webhooks](https://api.slack.com/messaging/webhooks)
- [WordPress REST API](https://developer.wordpress.org/rest-api/)

## 📝 Notes

- **First Video:** Model download takes 10-30 minutes (one-time)
- **Rate Limits:** Gemini API has usage quotas, monitor usage
- **Storage:** Videos are ~50MB each, plan storage accordingly
- **Performance:** GPU recommended for video generation
- **CORS:** Already configured in FastAPI backend

## 🆘 Support

If you encounter issues:

1. Check this README thoroughly
2. Review backend terminal logs
3. Check browser console (F12)
4. Verify all credentials in .env
5. Test individual components before workflow
6. Ensure all required services are running

---

**Ready to start?** Open `index.html` in your browser and begin with Step 1! 🚀
