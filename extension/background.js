/**
 * SocialGuard Background Service Worker
 * Handles threat notifications and logging
 */

// Track threats across tabs
let threatLog = [];

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'threatDetected') {
    handleThreatDetection(message, sender);
  }
});

/**
 * Handle threat detection
 */
function handleThreatDetection(threat, sender) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    url: threat.url,
    tabId: sender.tab.id,
    threats: threat.threats,
    domainIssue: threat.domainIssue
  };

  threatLog.push(logEntry);

  // Keep only last 100 entries
  if (threatLog.length > 100) {
    threatLog.shift();
  }

  // Show notification for critical threats
  const hasCritical = threat.threats.some(t => t.severity === 'CRITICAL');
  if (hasCritical) {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon128.png',
      title: 'SocialGuard: CRITICAL Threat Detected',
      message: `A ClickFix attack was detected on ${new URL(threat.url).hostname}. The page has been flagged.`,
      priority: 2
    });
  }

  // Update badge
  chrome.action.setBadgeText({
    text: threatLog.length.toString(),
    tabId: sender.tab.id
  });

  chrome.action.setBadgeBackgroundColor({
    color: '#dc3545',
    tabId: sender.tab.id
  });

  // Log to console
  console.log('🛡️ Threat detected:', logEntry);

  // Optionally send to backend API for logging
  sendToBackend(logEntry);
}

/**
 * Send threat data to backend API
 */
async function sendToBackend(logEntry) {
  try {
    const response = await fetch('http://localhost:8000/calculate_trust_score', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        event_id: `ext_${Date.now()}`,
        event_type: 'web',
        sender: new URL(logEntry.url).hostname,
        content: JSON.stringify(logEntry.threats),
        lookalike_domain: logEntry.domainIssue?.suspicious || false,
        metadata: logEntry
      })
    });

    if (response.ok) {
      const data = await response.json();
      console.log('📊 Threat logged to backend:', data);
    }
  } catch (error) {
    // Silently fail if backend is not available
    console.log('Backend API not available:', error.message);
  }
}

/**
 * Get threat log (for popup)
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'getThreatLog') {
    sendResponse({ threats: threatLog });
  }
});

console.log('🛡️ SocialGuard background service worker initialized');
