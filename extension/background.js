// LockedIn AI - Background Service Worker
// Handles extension icon clicks and keyboard shortcuts

console.log('LockedIn AI: Background service worker loaded');

// Handle extension icon click
chrome.action.onClicked.addListener((tab) => {
  console.log('Extension icon clicked, toggling overlay on tab:', tab.id);

  // Check if tab URL allows content scripts
  if (!canInjectContentScript(tab.url)) {
    console.warn('Cannot inject content script on this page:', tab.url);
    return;
  }

  chrome.tabs.sendMessage(tab.id, { action: 'toggle' }, (response) => {
    if (chrome.runtime.lastError) {
      console.error('❌ Icon click error:', chrome.runtime.lastError.message);
      console.error('Tab ID:', tab.id, 'URL:', tab.url);
      console.error('💡 Try refreshing the page or check if content scripts are blocked');
    } else {
      console.log('✓ Overlay toggled successfully');
    }
  });
});

// Handle keyboard shortcut (Ctrl+Shift+L)
chrome.commands.onCommand.addListener((command) => {
  if (command === 'toggle-overlay') {
    console.log('⌨️ Keyboard shortcut (Ctrl+Shift+L) triggered');

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        const tab = tabs[0];
        console.log('Current tab:', tab.id, tab.url);

        // Check if tab URL allows content scripts
        if (!canInjectContentScript(tab.url)) {
          console.warn('⚠️ Cannot inject content script on this page:', tab.url);
          console.warn('💡 Try this on a regular webpage (not chrome://, edge://, or extension pages)');
          return;
        }

        chrome.tabs.sendMessage(tab.id, { action: 'toggle' }, (response) => {
          if (chrome.runtime.lastError) {
            console.error('❌ Keyboard shortcut error:', chrome.runtime.lastError.message);
            console.error('Tab ID:', tab.id, 'URL:', tab.url);
            console.error('💡 Solution: Refresh the page (F5) and try again');
          } else {
            console.log('✓ Overlay toggled successfully via keyboard');
          }
        });
      } else {
        console.error('❌ No active tab found');
      }
    });
  }
});

// Helper function to check if content scripts can be injected
function canInjectContentScript(url) {
  if (!url) return false;

  // Content scripts cannot run on these URLs
  const blockedPrefixes = [
    'chrome://',
    'chrome-extension://',
    'edge://',
    'about:',
    'view-source:',
    'data:',
  ];

  const blockedDomains = [
    'chrome.google.com/webstore',
  ];

  // Check blocked prefixes
  for (const prefix of blockedPrefixes) {
    if (url.startsWith(prefix)) {
      return false;
    }
  }

  // Check blocked domains
  for (const domain of blockedDomains) {
    if (url.includes(domain)) {
      return false;
    }
  }

  return true;
}

// Handle messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Background received message:', request);

  if (request.action === 'capture-screen') {
    // Handle screen capture request
    chrome.tabs.captureVisibleTab(null, { format: 'png' }, (dataUrl) => {
      if (chrome.runtime.lastError) {
        console.error('Screen capture failed:', chrome.runtime.lastError);
        sendResponse({ success: false, error: chrome.runtime.lastError.message });
      } else {
        sendResponse({ success: true, dataUrl: dataUrl });
      }
    });
    return true; // Keep message channel open for async response
  }

  if (request.action === 'get-tab-id') {
    sendResponse({ tabId: sender.tab?.id });
  }
});

// Log when extension is installed
chrome.runtime.onInstalled.addListener((details) => {
  console.log('LockedIn AI installed:', details.reason);

  if (details.reason === 'install') {
    // Show welcome message or open setup page
    console.log('Welcome to LockedIn AI!');
  }
});
