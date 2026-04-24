# LockedIn AI - 5-Minute Quickstart Guide

🎉 **Your complete interview copilot is ready!**

---

## 🚀 Step 1: Start the Backend (2 minutes)

```bash
cd backend

# Activate virtual environment
venv\Scripts\activate

# Start server
python -m src.main
```

**Expected Output:**
```
INFO: Uvicorn running on http://0.0.0.0:8000
Starting LockedIn AI - LockedIn AI Backend v1.0.0
Application startup complete.
```

✅ **Backend is running!**

**API Docs:** http://localhost:8000/docs  
**Health Check:** http://localhost:8000/api/v1/health

---

## 🔌 Step 2: Install Chrome Extension (2 minutes)

1. Open Chrome and go to: `chrome://extensions/`

2. **Enable "Developer mode"** (toggle in top-right corner)

3. Click **"Load unpacked"**

4. Navigate to and select:  
   `D:\All_project\JAI SHREE RAM\lockedin-ai\extension`

5. **Done!** You'll see "LockedIn AI" appear in your extensions

---

## 🎯 Step 3: Test It! (1 minute)

1. **Navigate to any webpage** (e.g., leetcode.com, google.com)

2. **Press `Ctrl+Shift+L`** to toggle the overlay

3. **Try the Manual tab:**
   - Paste: "What is binary search?"
   - Click "Get AI Answer"
   - Watch the magic! ✨

---

## 📋 All Features

### 📝 **Manual Tab**
- Type or paste any interview question
- Get instant AI-powered answers
- Context-aware responses

### 🎙️ **Audio Tab** (Mock Mode)
- Click "Start Recording"
- Speak your question
- Get automatic transcription
- Submit for AI answer

> **Note:** Audio uses mock transcription for testing. To enable real transcription, install faster-whisper separately.

### 📸 **Screen Tab**
- Click "Capture Screen"
- Select the window to capture
- AI extracts the question using GPT-4o Vision
- Automatically analyzes and provides answer

### 👥 **Duo Tab**
- Click "Create Session"
- Share invite code with partner
- Partner clicks "Join Session" and enters code
- Collaborate in real-time!

---

## ⌨️ Keyboard Shortcuts

- **`Ctrl+Shift+L`** - Toggle overlay on/off
- **`Ctrl+Enter`** - Submit question (when input focused)
- **`Esc`** - Close overlay

---

## 🎨 UI Features

- **Draggable**: Click and drag the header to reposition
- **Tabs**: Switch between Manual, Audio, Screen, and Duo modes
- **Context Badge**: Shows how many messages are in your conversation history
- **Beautiful Gradient**: Modern purple theme with smooth animations

---

## 🧪 Quick Tests

### Test 1: Manual Question
```
Question: "Explain the two-sum problem and optimal solution"
Expected: Structured answer with approach, code, complexity
```

### Test 2: Health Check
```bash
curl http://localhost:8000/api/v1/health
Expected: {"status": "degraded", "version": "1.0.0", ...}
```

### Test 3: Duo Mode
```
1. Click Duo tab
2. Click "Create Session"
3. Note the 8-character invite code
4. Open Chrome incognito window
5. Install extension there too
6. Join session with invite code
7. Both windows now connected!
```

---

## 🔧 Configuration

### Backend (.env)
```env
# Already configured - no changes needed!
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_ENDPOINT=https://...
API_KEY=MySecretKey12345!@#$%
```

### Extension (config/config.js)
```javascript
const CONFIG = {
  API_URL: 'http://localhost:8000',
  API_KEY: 'MySecretKey12345!@#$%',  // Matches backend
  DEFAULT_PROMPT_MODE: 'comprehensive',
  AUDIO_ENABLED: true,
  VISION_ENABLED: true,
  DUO_MODE_ENABLED: true,
};
```

---

## ❓ Troubleshooting

### "Backend not responding"
- Check if server is running: `curl http://localhost:8000/api/v1/health`
- Restart: `python -m src.main`

### "Extension doesn't appear"
- Reload extension in `chrome://extensions/`
- Check browser console (F12) for errors
- Refresh the webpage

### "Overlay not showing"
- Press `Ctrl+Shift+L` again
- Check if extension icon is in toolbar
- Try on a different website

### "Audio doesn't work"
- Grant microphone permission when prompted
- Check browser site settings
- Currently in mock mode (shows test transcription)

---

## 📚 Documentation

- **Main README**: `../README.md` - Complete project documentation
- **Test Results**: `../TEST_RESULTS.md` - Detailed test results
- **Extension README**: `../extension/README.md` - Extension-specific docs

---

## 🎓 Usage Tips

1. **Start Simple**: Try Manual tab first before other features
2. **Context Awareness**: Keep using the same session - AI remembers your conversation
3. **Duo Mode**: Great for practice interviews with a friend
4. **Screen Capture**: Perfect for copying questions from coding platforms
5. **Prompt Modes**: Edit `config/prompts.js` to customize AI behavior

---

## 🌟 What's Working

✅ Backend server with all APIs  
✅ Chat completion with GPT-4o  
✅ Vision API for screenshot OCR  
✅ Session management for Duo mode  
✅ Context-aware conversations  
✅ WebSocket for real-time collaboration  
✅ Beautiful Chrome extension UI  
✅ All 4 input methods (Manual, Audio, Screen, Duo)  

---

## 🚧 Known Limitations

⚠️ **Audio**: Using mock transcription (faster-whisper requires ffmpeg on Windows)  
⚠️ **Icons**: Extension uses default icon (custom icons optional)  
⚠️ **Screen Share**: Overlay is visible during screen sharing (by design for practice)  

---

## 🎉 You're Ready!

Your LockedIn AI interview copilot is fully functional. 

**Next steps:**
1. Practice with coding questions
2. Test Duo mode with a friend
3. Customize prompts for your needs
4. Ace your interviews! 💪

**Questions?** Check the main README or TEST_RESULTS.md

---

**Built with ❤️ for interview success**  
Version 1.0.0 | April 2026
