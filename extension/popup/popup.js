// LockedIn AI - Popup Script

const API_URL = 'http://localhost:8000';
const API_KEY = 'MySecretKey12345!@#$%';

// Toggle overlay when button is clicked
document.getElementById('toggle-overlay').addEventListener('click', () => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.tabs.sendMessage(tabs[0].id, { action: 'toggle' });
    window.close();
  });
});

// Check backend status
async function checkBackendStatus() {
  const statusElement = document.getElementById('backend-status');

  try {
    const response = await fetch(`${API_URL}/api/v1/health`, {
      headers: {
        'X-API-Key': API_KEY,
      },
    });

    if (response.ok) {
      statusElement.textContent = 'Online ✓';
      statusElement.className = 'online';
    } else {
      statusElement.textContent = 'Error';
      statusElement.className = 'offline';
    }
  } catch (error) {
    statusElement.textContent = 'Offline ✗';
    statusElement.className = 'offline';
  }
}

// Check status on load
checkBackendStatus();

// Settings link
document.getElementById('settings-link').addEventListener('click', (e) => {
  e.preventDefault();
  alert('Settings panel coming soon!\n\nFor now, edit config/config.js to change settings.');
});
