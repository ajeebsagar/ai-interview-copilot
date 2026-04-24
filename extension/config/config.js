// LockedIn AI - Configuration
const CONFIG = {
  // Backend API Configuration
  API_URL: 'https://lockedin-ai-backend.onrender.com',
  WS_URL: 'wss://lockedin-ai-backend.onrender.com',
  API_KEY: 'MySecretKey12345!@#$%', // Match backend .env API_KEY

  // Feature Flags
  AUDIO_ENABLED: true,
  VISION_ENABLED: true,
  DUO_MODE_ENABLED: true,

  // AI Settings
  DEFAULT_PROMPT_MODE: 'comprehensive', // 'concise' or 'comprehensive'
  DEFAULT_TEMPERATURE: 0.7,
  DEFAULT_MAX_TOKENS: 2500,

  // Context Settings
  MAX_CONTEXT_MESSAGES: 10,
  AUTO_SAVE_CONTEXT: true,

  // Audio Settings
  AUDIO_SAMPLE_RATE: 16000,
  AUDIO_CHUNK_DURATION_MS: 1000,
  AUTO_TRANSCRIBE: true,

  // UI Settings
  OVERLAY_DEFAULT_WIDTH: 500,
  OVERLAY_DEFAULT_HEIGHT: 600,
  ANIMATION_DURATION: 300,

  // Session Settings
  SESSION_TIMEOUT_MINUTES: 60,
  AUTO_RECONNECT_WS: true,
  MAX_RECONNECT_ATTEMPTS: 5,
  RECONNECT_DELAY_MS: 3000,

  // Debug
  DEBUG_MODE: false,
  LOG_LEVEL: 'info', // 'debug', 'info', 'warn', 'error'
};

// Make config globally available
if (typeof window !== 'undefined') {
  window.LOCKEDIN_CONFIG = CONFIG;
}
