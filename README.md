# 🚀 LockedIn AI - Real-Time Interview Copilot

> **Your intelligent companion for high-stakes coding interviews**

Lock

edIn AI is a powerful real-time interview assistant that combines AI intelligence with practical features to help you excel in technical interviews. Whether it's algorithms, system design, or behavioral questions, LockedIn AI provides context-aware assistance exactly when you need it.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Key Features

### 🎙️ Real-Time Audio Transcription
- Capture interviewer questions via microphone
- Azure Speech SDK powered transcription
- Technical terminology recognition
- Live transcription display

### 🖼️ Smart Screen Capture & OCR
- Screenshot coding platforms (LeetCode, HackerRank, etc.)
- GPT-5.4-nano Vision API extracts questions and code
- Intelligent parsing of constraints and examples
- One-click question capture

### 👥 LockedIn Duo Mode
- Bring a trusted partner into your session
- Real-time collaboration via WebSocket
- Share context and get live guidance
- Session invite codes for secure access

### 🧠 Context-Aware AI Assistance
- Maintains conversation history
- Provides follow-up question predictions
- Connects answers across interview flow
- Intelligent context summarization

### ⚡ Advanced Capabilities
- Streaming AI responses for real-time feedback
- Multiple input methods (manual, audio, screenshot)
- Draggable overlay interface
- Keyboard shortcuts for efficiency
- Beautiful modern UI with animations

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CHROME EXTENSION                         │
│  ┌──────────┬──────────┬──────────┬──────────────────┐    │
│  │ Overlay  │  Audio   │ Screen   │  WebSocket       │    │
│  │   UI     │ Capture  │ Capture  │  Client          │    │
│  └──────────┴──────────┴──────────┴──────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS + WebSocket
┌────────────────────────┴────────────────────────────────────┐
│                    FASTAPI BACKEND                          │
│  ┌──────────┬──────────┬──────────┬──────────────────┐    │
│  │ REST API │WebSocket │  Speech  │  Vision          │    │
│  │Endpoints │  Server  │  Service │  Service         │    │
│  └──────────┴──────────┴──────────┴──────────────────┘    │
│  ┌──────────┬──────────┬──────────┬──────────────────┐    │
│  │   Azure  │ Session  │ Context  │  AI Response     │    │
│  │  OpenAI  │ Manager  │ Manager  │  Generator       │    │
│  └──────────┴──────────┴──────────┴──────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack

- **Backend**: FastAPI + Python 3.9+
- **AI**: Azure OpenAI GPT-5.4-nano (chat + vision)
- **Speech**: Azure Speech SDK
- **Real-time**: WebSockets
- **Frontend**: Chrome Extension (Manifest V3)
- **Session Storage**: Redis (optional) or in-memory

---

## 📁 Project Structure

```
lockedin-ai/
├── backend/
│   ├── src/
│   │   ├── main.py                    # FastAPI app entry
│   │   ├── api/
│   │   │   ├── routes.py              # REST endpoints
│   │   │   └── websocket.py           # WebSocket handlers
│   │   ├── services/
│   │   │   ├── azure_openai_service.py
│   │   │   ├── audio_service.py       # Speech-to-text
│   │   │   ├── vision_service.py      # OCR/screenshot
│   │   │   ├── session_service.py     # Duo sessions
│   │   │   └── context_service.py     # Conversation context
│   │   ├── models/
│   │   │   └── schemas.py             # Pydantic models
│   │   ├── middleware/
│   │   │   ├── auth.py
│   │   │   └── error_handler.py
│   │   ├── config/
│   │   │   └── settings.py            # Configuration
│   │   └── utils/
│   │       ├── logger.py
│   │       └── exceptions.py
│   ├── .env                           # Environment variables
│   ├── .env.example
│   ├── requirements.txt
│   └── README.md
│
├── extension/
│   ├── manifest.json                  # Manifest V3
│   ├── background.js                  # Service worker
│   ├── content/
│   │   ├── content.js                 # Main content script
│   │   ├── overlay.js                 # UI overlay
│   │   └── audio-capture.js           # Microphone capture
│   ├── popup/
│   │   ├── popup.html
│   │   ├── popup.js
│   │   └── popup.css
│   ├── config/
│   │   ├── config.js                  # API configuration
│   │   └── prompts.js                 # System prompts
│   ├── styles/
│   │   └── overlay.css
│   ├── utils/
│   │   ├── websocket-client.js        # WebSocket handler
│   │   ├── audio-recorder.js          # Audio recording
│   │   └── screen-capture.js          # Screenshot handler
│   └── icons/
│       ├── icon16.png
│       ├── icon48.png
│       └── icon128.png
└── README.md                          # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Chrome/Edge browser
- Azure OpenAI account with GPT-5.4-nano deployment
- Azure Speech Services account
- Node.js (optional, for extension development tools)

### 1. Backend Setup

#### Clone and Navigate
```bash
cd lockedin-ai/backend
```

#### Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment
Copy `.env.example` to `.env` and fill in your credentials:

```env
# Required: Azure OpenAI
AZURE_OPENAI_API_KEY=your-actual-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5.4-nano

# Required: Azure Speech
AZURE_SPEECH_API_KEY=your-speech-api-key
AZURE_SPEECH_REGION=eastus

# Required: Authentication
API_KEY=your-secret-key-for-extension
```

**Getting Azure Credentials:**

1. **Azure OpenAI**:
   - Go to [Azure Portal](https://portal.azure.com)
   - Create Azure OpenAI resource
   - Deploy GPT-5.4-nano model
   - Copy key and endpoint from "Keys and Endpoint"

2. **Azure Speech**:
   - Create Azure Speech Services resource
   - Copy key and region from "Keys and Endpoint"

#### Start Backend Server
```bash
python src/main.py
```

Server runs at: `http://localhost:8000`
- Swagger UI: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health

### 2. Chrome Extension Setup

#### Configure Extension
Edit `extension/config/config.js`:

```javascript
const CONFIG = {
  API_URL: 'http://localhost:8000',
  WS_URL: 'ws://localhost:8000',
  API_KEY: 'your-secret-key-here', // Match backend .env API_KEY
  DEFAULT_PROMPT_MODE: 'comprehensive',
  AUDIO_ENABLED: true,
  VISION_ENABLED: true,
  DUO_MODE_ENABLED: true
};
```

#### Install in Chrome
1. Open Chrome → `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select `lockedin-ai/extension/` folder
5. Extension installed! Icon appears in toolbar

---

## 📖 Usage

### Basic Workflow

1. **Start Backend**: Run `python src/main.py`
2. **Open Interview Platform**: Zoom, Meet, LeetCode, etc.
3. **Toggle Assistant**: Press `Ctrl+Shift+L` or click extension icon
4. **Choose Input Method**:
   - **Manual**: Type/paste question
   - **Audio** 🎙️: Click record, speak question
   - **Screen** 📸: Capture screenshot of question
   - **Duo** 👥: Create/join collaborative session
5. **Get AI Answer**: AI provides structured, context-aware response
6. **Continue Conversation**: Context is maintained for follow-ups

### Feature Demos

#### 🎙️ Audio Transcription
```
1. Click "Audio" tab
2. Click "Start Recording"
3. Grant microphone permission (one-time)
4. Speak question: "Explain binary search"
5. See real-time transcription
6. Click "Get AI Answer"
7. Streaming response appears
```

#### 📸 Screen Capture
```
1. Open LeetCode problem in tab
2. Click "Screen" tab
3. Click "Capture Screen"
4. Select window/tab to capture
5. AI extracts question using OCR
6. Review and edit if needed
7. Click "Get AI Answer"
```

#### 👥 Duo Mode
```
Host:
1. Click "Duo" tab
2. Click "Create Session"
3. Share invite code with partner

Partner:
1. Click "Duo" tab
2. Enter invite code
3. Click "Join Session"

Both users now see:
- Real-time question sharing
- Synchronized AI responses
- Partner suggestions in sidebar
- Shared context history
```

---

## 🎨 UI Components

### Overlay Tabs

**Manual Tab**
- Text input for questions
- Simple and direct
- Best for copied questions

**Audio Tab** 🎙️
- Microphone recording button
- Live waveform visualization
- Real-time transcription display
- Edit transcribed text before submitting

**Screen Tab** 📸
- Screenshot capture button
- Preview captured image
- Extracted question display
- Edit OCR results

**Duo Tab** 👥
- Create/join session controls
- Invite code display
- Partner presence indicator
- Suggestion sidebar
- Shared context view

### Keyboard Shortcuts

- `Ctrl+Shift+L` - Toggle overlay
- `Ctrl+Enter` - Submit question (from any input)
- `Ctrl+Shift+C` - Clear context
- `Ctrl+Shift+R` - Start/stop recording
- `Esc` - Close overlay

---

## 🔌 API Documentation

### REST Endpoints

#### Health Check
```http
GET /api/v1/health
Response: {"status": "healthy"}
```

#### Chat Completion (Context-Aware)
```http
POST /api/v1/chat/completions
Headers:
  Content-Type: application/json
  X-API-Key: your-api-key

Body:
{
  "messages": [
    {"role": "system", "content": "You are an interview assistant"},
    {"role": "user", "content": "Explain quicksort"}
  ],
  "session_id": "optional-session-id",
  "temperature": 0.7,
  "max_tokens": 2000,
  "stream": false
}
```

#### Vision Analysis (Screenshot OCR)
```http
POST /api/v1/vision/analyze
Headers:
  X-API-Key: your-api-key

Body (multipart/form-data):
  image: <file>
```

#### Audio Transcription
```http
POST /api/v1/audio/transcribe
Headers:
  X-API-Key: your-api-key

Body (multipart/form-data):
  audio: <file>
```

#### Session Management (Duo Mode)
```http
# Create session
POST /api/v1/sessions
Headers:
  X-API-Key: your-api-key

Response:
{
  "session_id": "abc123",
  "invite_code": "XY7Z9K2M",
  "created_at": "2026-04-22T10:30:00Z"
}

# Join session
POST /api/v1/sessions/{session_id}/join
Headers:
  X-API-Key: your-api-key

Body:
{
  "invite_code": "XY7Z9K2M",
  "user_id": "partner-user-id"
}

# Get session info
GET /api/v1/sessions/{session_id}
Headers:
  X-API-Key: your-api-key
```

### WebSocket Endpoints

#### Duo Mode Collaboration
```javascript
WS /ws/duo/{session_id}?user_id={user_id}

Messages:
{
  "type": "question" | "answer" | "suggestion" | "join" | "leave",
  "content": "...",
  "user_id": "...",
  "timestamp": "..."
}
```

#### Audio Streaming
```javascript
WS /ws/audio

Send: Binary audio chunks
Receive: {"transcription": "text", "is_final": true}
```

#### Streaming Chat Responses
```javascript
WS /ws/chat/{session_id}

Send: {"message": "...", "context": [...]}
Receive: {"chunk": "AI response chunk", "done": false}
```

---

## 🧪 Testing

### Test Backend API
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Chat completion
curl -X POST http://localhost:8000/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is a binary search tree?"}
    ],
    "temperature": 0.7,
    "max_tokens": 500
  }'

# Create Duo session
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "X-API-Key: your-key"
```

### Test Extension
1. Load extension in Chrome
2. Open any webpage
3. Press `Ctrl+Shift+L`
4. Test each tab:
   - Manual: Type question → Get answer
   - Audio: Record → Verify transcription → Get answer
   - Screen: Capture → Verify OCR → Get answer
   - Duo: Create session → Join from incognito → Test sync

### Run Unit Tests
```bash
cd backend
pytest tests/ -v --cov=src
```

---

## 🔐 Security & Ethics

### ⚠️ Important Notes

**This tool is for practice and learning:**
- ✅ Interview practice sessions
- ✅ Mock interviews with consent
- ✅ Skill development
- ✅ Personal study

**DO NOT use for:**
- ❌ Real job interviews without disclosure
- ❌ Academic exams or assessments  
- ❌ Deceptive purposes

### Screen Sharing Visibility
The overlay **IS visible** during screen sharing. For legitimate practice:
- Use second device (phone/tablet) for assistance
- Use dual monitor setup (share only one screen)
- Practice offline with the tool

### Security Features
- API key authentication for all endpoints
- Session invite codes for Duo mode (8-character random)
- CORS restrictions to extension origin
- Rate limiting on API endpoints
- Input validation on all services
- Secure WebSocket connections

---

## 🛠️ Troubleshooting

### Extension Not Loading
```
❌ Overlay doesn't appear when pressing Ctrl+Shift+L
```
**Solutions:**
- Reload extension in `chrome://extensions/`
- Check browser console (F12) for errors
- Verify content script injection in DevTools > Sources
- Refresh webpage

### Backend Connection Failed
```
❌ Error: Failed to fetch / API Error 401
```
**Solutions:**
- Verify backend is running: `curl http://localhost:8000/api/v1/health`
- Check API_KEY in extension config matches backend .env
- Verify CORS settings in backend
- Check network tab in DevTools

### Audio Not Recording
```
❌ Microphone permission denied
```
**Solutions:**
- Grant microphone permission in browser
- Check site settings in Chrome
- Verify HTTPS (required for production)
- Test microphone in another app

### Screen Capture Fails
```
❌ Cannot capture screen
```
**Solutions:**
- Grant desktopCapture permission
- Try capturing specific tab vs entire screen
- Check Chrome permissions settings
- Reload extension

### Duo Mode Connection Issues
```
❌ WebSocket connection failed
```
**Solutions:**
- Verify backend WebSocket server is running
- Check firewall settings
- Ensure correct WS URL in config
- Test with same user in incognito mode first

---

## 🚀 Deployment

### Backend Deployment

**Azure App Service:**
```bash
# Create App Service
az webapp create --resource-group myResourceGroup \
  --plan myAppServicePlan --name lockedin-ai-backend \
  --runtime "PYTHON:3.9"

# Configure environment variables
az webapp config appsettings set --resource-group myResourceGroup \
  --name lockedin-ai-backend \
  --settings @env-vars.json

# Deploy
az webapp up --runtime PYTHON:3.9 --sku B1
```

**Docker:**
```bash
# Build image
docker build -t lockedin-ai-backend backend/

# Run container
docker run -p 8000:8000 --env-file backend/.env lockedin-ai-backend
```

### Extension Distribution

**Chrome Web Store:**
1. Zip extension folder
2. Create developer account
3. Submit to Chrome Web Store
4. Wait for review (~3-5 days)

**Private Distribution:**
- Share unpacked extension folder
- Users load via "Load unpacked" in developer mode

---

## 📊 Performance

- Audio transcription latency: <2 seconds
- Vision OCR processing: <3 seconds
- AI response time: 2-5 seconds (streaming)
- WebSocket message latency: <100ms
- Context retrieval: <50ms

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

- **Azure OpenAI** for GPT-5.4-nano API
- **Azure Speech** for transcription services
- **FastAPI** for the amazing web framework
- **Chrome Extensions** for platform support

---

## 📧 Support

For issues or questions:
- Open an issue on GitHub
- Check troubleshooting section above
- Review API documentation

---

**Built with ❤️ for interview success**

⭐ Star this repo if it helps you!

---

## 📈 Roadmap

### Upcoming Features
- [ ] Multi-language support
- [ ] Custom prompt templates
- [ ] Export conversation history
- [ ] Mobile companion app
- [ ] IDE plugins (VS Code, JetBrains)
- [ ] Practice mode with mock interviews
- [ ] Analytics dashboard
- [ ] Voice synthesis for answers
- [ ] Code execution sandbox

### Future Integrations
- [ ] Multiple AI providers (Claude, Gemini)
- [ ] Integration with calendars
- [ ] Slack notifications for Duo sessions
- [ ] Recording playback for review
