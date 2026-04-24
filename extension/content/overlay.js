// LockedIn AI - Overlay UI Component
// Main UI with multi-tab interface

class LockedInOverlay {
  constructor(config) {
    this.config = config;
    this.overlay = null;
    this.isVisible = false;
    this.currentTab = 'manual';
    this.sessionId = this.generateSessionId();

    // Service managers
    this.audioManager = null;
    this.screenCapture = null;
    this.duoWebSocket = null;

    // UI elements (set in initialize)
    this.elements = {};

    // State
    this.isProcessing = false;
    this.currentMode = config.DEFAULT_PROMPT_MODE;
  }

  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  async initialize() {
    console.log('LockedInOverlay: Initializing');

    // Create overlay HTML
    this.createOverlay();

    // Initialize services
    this.audioManager = new AudioCaptureManager(this.config);
    this.screenCapture = new ScreenCapture({
      onCapture: (dataUrl) => {
        // Handle screen capture inline
        this.elements.screenImage.src = dataUrl;
        this.screenDataUrl = dataUrl;
        document.getElementById('screen-preview').style.display = 'block';
        this.showStatus('Screenshot captured!', 'success');
      },
      onError: (error) => this.showError(error.message),
    });

    // Set up audio callbacks
    this.audioManager.onTranscription((transcription) => {
      this.handleTranscription(transcription);
    });
    this.audioManager.onError((error) => {
      this.showError(`Audio error: ${error.message}`);
    });

    // Attach event listeners
    this.attachEventListeners();

    console.log('LockedInOverlay: Initialized');
  }

  createOverlay() {
    // Create main overlay container
    this.overlay = document.createElement('div');
    this.overlay.id = 'lockedin-overlay';

    this.overlay.innerHTML = `
      <div class="lockedin-header" id="lockedin-header">
        <div class="lockedin-title">
          🧠 LockedIn AI
        </div>
        <div class="lockedin-header-buttons">
          <button class="lockedin-header-btn" id="lockedin-minimize" title="Minimize">−</button>
          <button class="lockedin-header-btn" id="lockedin-close" title="Close">×</button>
        </div>
      </div>

      <div class="lockedin-body">
        <!-- Tabs -->
        <div class="lockedin-tabs">
          <button class="lockedin-tab active" data-tab="manual">
            📝 Manual
          </button>
          <button class="lockedin-tab" data-tab="audio">
            🎙️ Audio
          </button>
          <button class="lockedin-tab" data-tab="screen">
            📸 Screen
          </button>
          <button class="lockedin-tab" data-tab="duo">
            👥 Duo
          </button>
        </div>

        <!-- Manual Tab -->
        <div class="lockedin-tab-content active" data-content="manual">
          <textarea
            class="lockedin-input"
            id="manual-input"
            placeholder="Paste interview question here..."
          ></textarea>
          <button class="lockedin-btn" id="manual-submit">
            Get AI Answer
          </button>
        </div>

        <!-- Audio Tab -->
        <div class="lockedin-tab-content" data-content="audio">
          <div id="audio-idle">
            <button class="lockedin-btn" id="audio-start">
              🎙️ Start Recording
            </button>
          </div>
          <div id="audio-recording" style="display:none">
            <div class="lockedin-recording">
              <div class="lockedin-recording-icon">⏺</div>
              <div class="lockedin-recording-text">Recording...</div>
              <div class="lockedin-recording-timer" id="recording-timer">00:00</div>
            </div>
            <button class="lockedin-btn" id="audio-stop">
              ⏹️ Stop Recording
            </button>
          </div>
          <div id="audio-transcription" style="display:none">
            <textarea
              class="lockedin-input"
              id="audio-transcription-text"
              placeholder="Transcription will appear here..."
            ></textarea>
            <div style="display:flex; gap:8px;">
              <button class="lockedin-btn" id="audio-get-answer" style="flex:1">
                Get AI Answer
              </button>
              <button class="lockedin-btn lockedin-btn-secondary" id="audio-retry" style="flex:0;">
                🔄
              </button>
            </div>
          </div>
        </div>

        <!-- Screen Tab -->
        <div class="lockedin-tab-content" data-content="screen">
          <button class="lockedin-btn" id="screen-capture">
            📸 Capture Screen
          </button>
          <div id="screen-preview" style="display:none;">
            <img id="screen-image" class="lockedin-screenshot-preview" alt="Screenshot" />
            <button class="lockedin-btn" id="screen-analyze">
              🔍 Analyze & Get Answer
            </button>
          </div>
          <div id="screen-extracted" style="display:none;">
            <textarea
              class="lockedin-input"
              id="screen-extracted-text"
              placeholder="Extracted question..."
            ></textarea>
            <button class="lockedin-btn" id="screen-get-answer">
              Get AI Answer
            </button>
          </div>
        </div>

        <!-- Duo Tab -->
        <div class="lockedin-tab-content" data-content="duo">
          <div id="duo-idle">
            <button class="lockedin-btn" id="duo-create">
              ➕ Create Session
            </button>
            <div style="text-align:center; margin:12px 0; color:#6b7280; font-size:13px;">OR</div>
            <input
              class="lockedin-input"
              id="duo-invite-input"
              placeholder="Enter invite code..."
              style="min-height:auto; padding:12px;"
            />
            <button class="lockedin-btn lockedin-btn-secondary" id="duo-join">
              Join Session
            </button>
          </div>
          <div id="duo-session" style="display:none">
            <div class="lockedin-duo-session">
              <div style="text-align:center; font-weight:600; color:#374151; margin-bottom:8px;">
                Session Active
              </div>
              <div class="lockedin-duo-code" id="duo-code">LOADING</div>
              <div class="lockedin-duo-participants" id="duo-participants"></div>
              <button class="lockedin-btn lockedin-btn-secondary" id="duo-leave" style="margin-top:12px;">
                Leave Session
              </button>
            </div>
            <div id="duo-messages" style="max-height:200px; overflow-y:auto; margin-top:12px; display:none;">
              <!-- Messages appear here -->
            </div>
          </div>
        </div>

        <!-- Context Badge -->
        <div id="context-badge" style="display:none;">
          <span class="lockedin-context-badge">
            <span>💬</span>
            <span id="context-count">0</span> messages in context
          </span>
        </div>

        <!-- Response Area -->
        <div class="lockedin-response" id="response-area"></div>

        <!-- Status Messages -->
        <div id="status-message"></div>
      </div>
    `;

    document.body.appendChild(this.overlay);

    // Cache DOM elements
    this.elements = {
      header: document.getElementById('lockedin-header'),
      closeBtn: document.getElementById('lockedin-close'),
      minimizeBtn: document.getElementById('lockedin-minimize'),

      // Tabs
      tabs: document.querySelectorAll('.lockedin-tab'),
      tabContents: document.querySelectorAll('.lockedin-tab-content'),

      // Manual
      manualInput: document.getElementById('manual-input'),
      manualSubmit: document.getElementById('manual-submit'),

      // Audio
      audioStart: document.getElementById('audio-start'),
      audioStop: document.getElementById('audio-stop'),
      audioRetry: document.getElementById('audio-retry'),
      audioGetAnswer: document.getElementById('audio-get-answer'),
      audioTranscriptionText: document.getElementById('audio-transcription-text'),
      recordingTimer: document.getElementById('recording-timer'),

      // Screen
      screenCapture: document.getElementById('screen-capture'),
      screenAnalyze: document.getElementById('screen-analyze'),
      screenGetAnswer: document.getElementById('screen-get-answer'),
      screenImage: document.getElementById('screen-image'),
      screenExtractedText: document.getElementById('screen-extracted-text'),

      // Duo
      duoCreate: document.getElementById('duo-create'),
      duoJoin: document.getElementById('duo-join'),
      duoLeave: document.getElementById('duo-leave'),
      duoInviteInput: document.getElementById('duo-invite-input'),
      duoCode: document.getElementById('duo-code'),
      duoParticipants: document.getElementById('duo-participants'),

      // Response
      responseArea: document.getElementById('response-area'),
      statusMessage: document.getElementById('status-message'),
      contextBadge: document.getElementById('context-badge'),
      contextCount: document.getElementById('context-count'),
    };
  }

  attachEventListeners() {
    // Close/Minimize
    this.elements.closeBtn.onclick = () => this.hide();
    this.elements.minimizeBtn.onclick = () => this.hide();

    // Make draggable
    this.makeDraggable();

    // Tab switching
    this.elements.tabs.forEach(tab => {
      tab.onclick = () => this.switchTab(tab.dataset.tab);
    });

    // Manual tab
    this.elements.manualSubmit.onclick = () => this.handleManualSubmit();
    this.elements.manualInput.onkeydown = (e) => {
      if (e.ctrlKey && e.key === 'Enter') {
        this.handleManualSubmit();
      }
    };

    // Audio tab
    this.elements.audioStart.onclick = () => this.startAudioRecording();
    this.elements.audioStop.onclick = () => this.stopAudioRecording();
    this.elements.audioRetry.onclick = () => this.resetAudioTab();
    this.elements.audioGetAnswer.onclick = () => this.handleAudioSubmit();

    // Screen tab
    this.elements.screenCapture.onclick = () => this.captureScreen();
    this.elements.screenAnalyze.onclick = () => this.analyzeScreen();
    this.elements.screenGetAnswer.onclick = () => this.handleScreenSubmit();

    // Duo tab
    this.elements.duoCreate.onclick = () => this.createDuoSession();
    this.elements.duoJoin.onclick = () => this.joinDuoSession();
    this.elements.duoLeave.onclick = () => this.leaveDuoSession();
  }

  makeDraggable() {
    let isDragging = false;
    let currentX, currentY, initialX, initialY;

    this.elements.header.addEventListener('mousedown', (e) => {
      isDragging = true;
      initialX = e.clientX - this.overlay.offsetLeft;
      initialY = e.clientY - this.overlay.offsetTop;
    });

    document.addEventListener('mousemove', (e) => {
      if (isDragging) {
        e.preventDefault();
        currentX = e.clientX - initialX;
        currentY = e.clientY - initialY;

        this.overlay.style.left = currentX + 'px';
        this.overlay.style.top = currentY + 'px';
        this.overlay.style.right = 'auto';
      }
    });

    document.addEventListener('mouseup', () => {
      isDragging = false;
    });
  }

  switchTab(tabName) {
    this.currentTab = tabName;

    // Update tabs
    this.elements.tabs.forEach(tab => {
      tab.classList.toggle('active', tab.dataset.tab === tabName);
    });

    // Update content
    this.elements.tabContents.forEach(content => {
      content.classList.toggle('active', content.dataset.content === tabName);
    });

    console.log('Switched to tab:', tabName);
  }

  async handleManualSubmit() {
    const question = this.elements.manualInput.value.trim();
    if (!question) {
      this.showError('Please enter a question');
      return;
    }

    await this.getAIAnswer(question);
  }

  async startAudioRecording() {
    document.getElementById('audio-idle').style.display = 'none';
    document.getElementById('audio-recording').style.display = 'block';

    const success = await this.audioManager.startRecording();
    if (success) {
      this.startRecordingTimer();
    } else {
      this.resetAudioTab();
    }
  }

  stopAudioRecording() {
    this.audioManager.stopRecording();
    this.stopRecordingTimer();

    document.getElementById('audio-recording').style.display = 'none';
    this.showStatus('Processing audio...', 'info');
  }

  startRecordingTimer() {
    let seconds = 0;
    this.recordingInterval = setInterval(() => {
      seconds++;
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      this.elements.recordingTimer.textContent =
        `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }, 1000);
  }

  stopRecordingTimer() {
    if (this.recordingInterval) {
      clearInterval(this.recordingInterval);
      this.recordingInterval = null;
    }
  }

  handleTranscription(transcription) {
    document.getElementById('audio-transcription').style.display = 'block';
    this.elements.audioTranscriptionText.value = transcription;
    this.showStatus('Transcription complete!', 'success');
  }

  resetAudioTab() {
    document.getElementById('audio-idle').style.display = 'block';
    document.getElementById('audio-recording').style.display = 'none';
    document.getElementById('audio-transcription').style.display = 'none';
    this.elements.audioTranscriptionText.value = '';
    this.elements.recordingTimer.textContent = '00:00';
    this.stopRecordingTimer();
  }

  async handleAudioSubmit() {
    const question = this.elements.audioTranscriptionText.value.trim();
    if (!question) {
      this.showError('No transcription available');
      return;
    }

    await this.getAIAnswer(question);
  }

  async captureScreen() {
    try {
      this.showStatus('Capturing screen...', 'info');
      const dataUrl = await this.screenCapture.captureActiveTab();

      this.elements.screenImage.src = dataUrl;
      this.screenDataUrl = dataUrl;

      document.getElementById('screen-preview').style.display = 'block';
      this.showStatus('Screenshot captured!', 'success');
    } catch (error) {
      this.showError('Screen capture failed: ' + error.message);
    }
  }

  async analyzeScreen() {
    if (!this.screenDataUrl) {
      this.showError('No screenshot available');
      return;
    }

    try {
      this.showStatus('Analyzing screenshot with AI...', 'info');

      // Convert dataURL to Blob
      const blob = ScreenCapture.dataUrlToBlob(this.screenDataUrl);
      const file = new File([blob], 'screenshot.png', { type: 'image/png' });

      // Create FormData
      const formData = new FormData();
      formData.append('image', file);
      formData.append('include_code', 'true');

      // Send to backend
      const response = await fetch(
        `${this.config.API_URL}/api/v1/vision/analyze`,
        {
          method: 'POST',
          headers: {
            'X-API-Key': this.config.API_KEY,
          },
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('Vision analysis result:', result);

      // Display extracted question
      let extractedText = result.question;
      if (result.code_snippet) {
        extractedText += '\n\nCode:\n```\n' + result.code_snippet + '\n```';
      }
      if (result.constraints && result.constraints.length > 0) {
        extractedText += '\n\nConstraints:\n' + result.constraints.map(c => `- ${c}`).join('\n');
      }

      this.elements.screenExtractedText.value = extractedText;
      document.getElementById('screen-extracted').style.display = 'block';

      this.showStatus('Question extracted successfully!', 'success');

    } catch (error) {
      this.showError('Analysis failed: ' + error.message);
    }
  }

  async handleScreenSubmit() {
    const question = this.elements.screenExtractedText.value.trim();
    if (!question) {
      this.showError('No extracted text available');
      return;
    }

    await this.getAIAnswer(question);
  }

  async getAIAnswer(question) {
    if (this.isProcessing) {
      return;
    }

    this.isProcessing = true;
    this.showStatus('Getting AI answer...', 'info');
    this.elements.responseArea.textContent = 'Thinking...';

    try {
      // Prepare request
      const systemPrompt = window.getSystemPrompt(this.currentMode);
      const requestBody = {
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: question },
        ],
        session_id: this.sessionId,
        temperature: this.config.DEFAULT_TEMPERATURE,
        max_tokens: this.config.DEFAULT_MAX_TOKENS,
      };

      // Send to backend
      const response = await fetch(
        `${this.config.API_URL}/api/v1/chat/completions`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': this.config.API_KEY,
          },
          body: JSON.stringify(requestBody),
        }
      );

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('AI response:', result);

      // Display response
      this.displayResponse(result.content);

      // Update context badge
      if (result.context_used > 0) {
        this.elements.contextBadge.style.display = 'block';
        this.elements.contextCount.textContent = result.context_used;
      }

      this.showStatus('Answer received!', 'success');

    } catch (error) {
      console.error('AI answer failed:', error);
      this.showError('Failed to get answer: ' + error.message);
      this.elements.responseArea.textContent = '';
    } finally {
      this.isProcessing = false;
    }
  }

  displayResponse(content) {
    // Format response with better rendering
    let formatted = content
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n/g, '<br>');

    this.elements.responseArea.innerHTML = formatted;
  }

  async createDuoSession() {
    try {
      this.showStatus('Creating session...', 'info');

      const response = await fetch(
        `${this.config.API_URL}/api/v1/sessions`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': this.config.API_KEY,
          },
          body: JSON.stringify({
            user_id: this.sessionId,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to create session: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('Duo session created:', result);

      this.duoSessionId = result.session_id;
      this.duoInviteCode = result.invite_code;

      // Show session UI
      document.getElementById('duo-idle').style.display = 'none';
      document.getElementById('duo-session').style.display = 'block';
      this.elements.duoCode.textContent = result.invite_code;

      // Connect WebSocket
      await this.connectDuoWebSocket();

      this.showStatus('Session created! Share the code with your partner.', 'success');

    } catch (error) {
      this.showError('Failed to create session: ' + error.message);
    }
  }

  async joinDuoSession() {
    const inviteCode = this.elements.duoInviteInput.value.trim();
    if (!inviteCode) {
      this.showError('Please enter invite code');
      return;
    }

    try {
      this.showStatus('Joining session...', 'info');

      // Find session by invite code (simplified - would need backend endpoint)
      // For MVP, assume format: sessionId is derived from invite
      this.duoSessionId = 'session_' + inviteCode;
      this.duoInviteCode = inviteCode;

      // Show session UI
      document.getElementById('duo-idle').style.display = 'none';
      document.getElementById('duo-session').style.display = 'block';
      this.elements.duoCode.textContent = inviteCode;

      // Connect WebSocket
      await this.connectDuoWebSocket();

      this.showStatus('Joined session successfully!', 'success');

    } catch (error) {
      this.showError('Failed to join session: ' + error.message);
    }
  }

  async connectDuoWebSocket() {
    const wsUrl = `${this.config.WS_URL}/ws/duo/${this.duoSessionId}?user_id=${this.sessionId}`;

    this.duoWebSocket = new WebSocketClient(wsUrl, {
      autoReconnect: true,
      maxReconnectAttempts: this.config.MAX_RECONNECT_ATTEMPTS,
      reconnectDelay: this.config.RECONNECT_DELAY_MS,
    });

    this.duoWebSocket.onMessage((data) => {
      console.log('Duo message:', data);
      // Handle Duo messages (questions, suggestions, etc.)
    });

    this.duoWebSocket.onConnection((status) => {
      console.log('Duo connection status:', status);
    });

    await this.duoWebSocket.connect();
  }

  leaveDuoSession() {
    if (this.duoWebSocket) {
      this.duoWebSocket.disconnect();
      this.duoWebSocket = null;
    }

    document.getElementById('duo-idle').style.display = 'block';
    document.getElementById('duo-session').style.display = 'none';
    this.elements.duoInviteInput.value = '';

    this.duoSessionId = null;
    this.duoInviteCode = null;

    this.showStatus('Left session', 'info');
  }

  showStatus(message, type = 'info') {
    const statusDiv = this.elements.statusMessage;
    statusDiv.innerHTML = `
      <div class="lockedin-status lockedin-status-${type}">
        ${type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ'}
        ${message}
      </div>
    `;

    setTimeout(() => {
      statusDiv.innerHTML = '';
    }, 5000);
  }

  showError(message) {
    this.showStatus(message, 'error');
  }

  toggle() {
    this.isVisible ? this.hide() : this.show();
  }

  show() {
    this.overlay.style.display = 'flex';
    this.isVisible = true;

    // Focus input based on current tab
    if (this.currentTab === 'manual') {
      this.elements.manualInput.focus();
    }
  }

  hide() {
    this.overlay.style.display = 'none';
    this.isVisible = false;
  }

  isVisible() {
    return this.isVisible;
  }
}

// Make LockedInOverlay globally available
if (typeof window !== 'undefined') {
  window.LockedInOverlay = LockedInOverlay;
}
