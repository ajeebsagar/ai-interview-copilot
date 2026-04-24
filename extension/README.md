# LockedIn AI - Chrome Extension

Real-time interview copilot with audio transcription, screen OCR, and Duo mode collaboration.

## Installation

1. Start the backend server:
```bash
cd ../backend
python src/main.py
```

2. Load the extension in Chrome:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" (top right)
   - Click "Load unpacked"
   - Select the `extension/` folder

3. The extension is now installed!

## Usage

### Quick Start

1. **Toggle Overlay**: Press `Ctrl+Shift+L` or click the extension icon
2. **Choose Input Method**:
   - **Manual** 📝: Type/paste question
   - **Audio** 🎙️: Record your question
   - **Screen** 📸: Capture screenshot
   - **Duo** 👥: Collaborate with a partner

### Features

**Manual Tab**
- Paste interview questions
- Get instant AI answers
- Context-aware responses

**Audio Tab**
- Click "Start Recording"
- Speak your question
- Get automatic transcription
- Review and submit for AI answer

**Screen Tab**
- Click "Capture Screen"
- Select the window/tab
- AI extracts the question using OCR
- Get answer with extracted context

**Duo Mode**
- Create session → Get invite code
- Share code with partner
- Real-time collaboration
- Both see questions and answers

## Configuration

Edit `config/config.js` to customize:

```javascript
const CONFIG = {
  API_URL: 'http://localhost:8000',      // Backend URL
  API_KEY: 'MySecretKey12345!@#$%',      // Match backend .env
  DEFAULT_PROMPT_MODE: 'comprehensive',   // or 'concise'
  AUDIO_ENABLED: true,
  VISION_ENABLED: true,
  DUO_MODE_ENABLED: true,
};
```

## Keyboard Shortcuts

- **Ctrl+Shift+L**: Toggle overlay
- **Ctrl+Enter**: Submit question (when input is focused)
- **Esc**: Close overlay

## Troubleshooting

### Extension doesn't load
- Reload extension in `chrome://extensions/`
- Check browser console for errors (F12)
- Refresh the webpage

### Backend connection fails
- Ensure backend is running: `curl http://localhost:8000/api/v1/health`
- Check API_KEY matches between extension and backend
- Verify CORS settings in backend

### Audio recording fails
- Grant microphone permission
- Check browser site settings
- Try refreshing the page

### Screen capture fails
- Grant necessary permissions
- Try capturing specific tab vs entire screen

## File Structure

```
extension/
├── manifest.json              # Extension configuration
├── background.js              # Service worker
├── config/
│   ├── config.js             # Settings
│   └── prompts.js            # AI prompts
├── content/
│   ├── content.js            # Main script
│   ├── overlay.js            # UI component
│   └── audio-capture.js      # Audio integration
├── popup/
│   ├── popup.html            # Popup UI
│   ├── popup.css             # Popup styles
│   └── popup.js              # Popup logic
├── styles/
│   └── overlay.css           # Overlay styles
└── utils/
    ├── websocket-client.js   # WebSocket manager
    ├── audio-recorder.js     # Audio recording
    └── screen-capture.js     # Screenshot capture
```

## Support

For issues or questions:
- Check backend logs: `tail -f backend/logs/app.log`
- Check browser console: F12 → Console
- Review network requests: F12 → Network

## License

MIT License
