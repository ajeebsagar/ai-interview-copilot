// LockedIn AI - Main Content Script
// Initializes the extension and handles overlay toggle

(function() {
  'use strict';

  // Prevent multiple injections
  if (window.lockedInAILoaded) {
    console.log('LockedIn AI: Already loaded');
    return;
  }
  window.lockedInAILoaded = true;

  console.log('LockedIn AI: Loading...');

  // Wait for all dependencies to load
  function waitForDependencies() {
    return new Promise((resolve) => {
      const check = () => {
        if (window.LOCKEDIN_CONFIG &&
            window.LOCKEDIN_PROMPTS &&
            window.WebSocketClient &&
            window.AudioRecorder &&
            window.ScreenCapture &&
            window.AudioCaptureManager &&
            window.LockedInOverlay) {
          resolve();
        } else {
          setTimeout(check, 100);
        }
      };
      check();
    });
  }

  // Initialize the extension
  async function initialize() {
    try {
      await waitForDependencies();

      console.log('LockedIn AI: All dependencies loaded');

      // Create overlay instance
      const overlay = new window.LockedInOverlay(window.LOCKEDIN_CONFIG);

      // Initialize overlay
      await overlay.initialize();

      // Listen for toggle messages from background script
      chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.action === 'toggle') {
          console.log('✓ LockedIn AI: Received toggle message');
          overlay.toggle();
          sendResponse({ success: true });
          return true;
        }
      });

      // Global keyboard shortcut (Esc to close)
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && overlay.isVisible()) {
          overlay.hide();
        }
      });

      console.log('✓ LockedIn AI: Successfully loaded!');
      console.log('  Press Ctrl+Shift+L to toggle overlay');

    } catch (error) {
      console.error('LockedIn AI: Initialization failed', error);
    }
  }

  // Start initialization
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }

})();
