/**
 * SocialGuard Content Script
 * Detects and blocks ClickFix attacks, fake system prompts, and SEO poisoning
 */

// Suspicious patterns that indicate ClickFix or fake prompts
const SUSPICIOUS_PATTERNS = {
  fakeUpdates: [
    /update.*required/i,
    /security.*warning/i,
    /click.*to.*fix/i,
    /windows.*update/i,
    /chrome.*update/i,
    /flash.*player/i,
    /java.*update/i,
    /download.*fix/i,
    /install.*now/i,
    /critical.*update/i
  ],
  urgentActions: [
    /urgent.*action.*required/i,
    /verify.*account.*now/i,
    /suspended.*account/i,
    /unusual.*activity/i,
    /confirm.*identity/i
  ],
  suspiciousCommands: [
    /powershell/i,
    /cmd\.exe/i,
    /certutil/i,
    /mshta/i,
    /regsvr32/i,
    /rundll32/i
  ]
};

// Known malicious or suspicious TLDs
const SUSPICIOUS_TLDS = [
  '.tk', '.ml', '.ga', '.cf', '.gq', // Free TLDs often used in attacks
  '.xyz', '.top', '.work'
];

// Track detected threats
let detectedThreats = [];

/**
 * Check if domain is recently registered or suspicious
 */
function checkDomain() {
  const hostname = window.location.hostname;

  // Check suspicious TLDs
  for (const tld of SUSPICIOUS_TLDS) {
    if (hostname.endsWith(tld)) {
      return {
        suspicious: true,
        reason: `Suspicious TLD detected: ${tld}`
      };
    }
  }

  // Check for typosquatting of popular domains
  const popularDomains = ['google', 'microsoft', 'apple', 'amazon', 'facebook', 'paypal', 'zoom'];
  for (const domain of popularDomains) {
    if (hostname.includes(domain) && !hostname.endsWith(`${domain}.com`)) {
      return {
        suspicious: true,
        reason: `Possible typosquatting of ${domain}.com`
      };
    }
  }

  return { suspicious: false };
}

/**
 * Scan page content for suspicious patterns
 */
function scanPageContent() {
  const pageText = document.body.innerText.toLowerCase();
  const threats = [];

  // Check for fake update prompts
  for (const pattern of SUSPICIOUS_PATTERNS.fakeUpdates) {
    if (pattern.test(pageText)) {
      threats.push({
        type: 'FAKE_UPDATE',
        pattern: pattern.toString(),
        severity: 'HIGH'
      });
    }
  }

  // Check for urgent action scams
  for (const pattern of SUSPICIOUS_PATTERNS.urgentActions) {
    if (pattern.test(pageText)) {
      threats.push({
        type: 'URGENT_SCAM',
        pattern: pattern.toString(),
        severity: 'MEDIUM'
      });
    }
  }

  // Check for suspicious commands (ClickFix attacks)
  for (const pattern of SUSPICIOUS_PATTERNS.suspiciousCommands) {
    if (pattern.test(pageText)) {
      threats.push({
        type: 'CLICKFIX_COMMAND',
        pattern: pattern.toString(),
        severity: 'CRITICAL'
      });
    }
  }

  return threats;
}

/**
 * Show warning banner
 */
function showWarningBanner(threats, domainCheck) {
  // Remove existing banner if present
  const existingBanner = document.getElementById('socialguard-warning');
  if (existingBanner) {
    existingBanner.remove();
  }

  // Create warning banner
  const banner = document.createElement('div');
  banner.id = 'socialguard-warning';
  banner.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
    color: white;
    padding: 16px 20px;
    z-index: 999999;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    animation: slideDown 0.3s ease;
  `;

  const highestSeverity = threats.reduce((max, t) =>
    t.severity === 'CRITICAL' ? 'CRITICAL' : (max === 'CRITICAL' || t.severity === 'HIGH') ? max : t.severity
  , 'MEDIUM');

  banner.innerHTML = `
    <div style="max-width: 1200px; margin: 0 auto;">
      <div style="display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 16px;">
          <div style="font-size: 32px;">🛡️</div>
          <div>
            <div style="font-weight: 700; font-size: 18px; margin-bottom: 4px;">
              ⚠️ SocialGuard: ${highestSeverity} RISK DETECTED
            </div>
            <div style="font-size: 14px; opacity: 0.95;">
              This page shows signs of a social engineering attack. Do not follow instructions or download files.
            </div>
            ${domainCheck.suspicious ? `
              <div style="font-size: 13px; margin-top: 6px; padding: 8px; background: rgba(255,255,255,0.2); border-radius: 4px;">
                🔍 ${domainCheck.reason}
              </div>
            ` : ''}
          </div>
        </div>
        <button id="socialguard-details" style="
          background: white;
          color: #dc3545;
          border: none;
          padding: 10px 20px;
          border-radius: 6px;
          font-weight: 600;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.2s;
        ">
          View Details
        </button>
      </div>
      <div id="socialguard-threat-details" style="display: none; margin-top: 16px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.3);">
        <div style="font-weight: 600; margin-bottom: 8px;">Detected Threats:</div>
        <ul style="margin: 0; padding-left: 20px; font-size: 13px;">
          ${threats.map(t => `
            <li style="margin: 4px 0;">
              <strong>${t.type}</strong> (${t.severity}) - Common in ${getThreatDescription(t.type)} attacks
            </li>
          `).join('')}
        </ul>
        <div style="margin-top: 12px; padding: 12px; background: rgba(255,255,255,0.15); border-radius: 4px; font-size: 13px;">
          <strong>Recommended Actions:</strong>
          <ul style="margin: 8px 0 0 0; padding-left: 20px;">
            <li>Do not click any links or download files from this page</li>
            <li>Do not copy/paste any commands into your terminal</li>
            <li>Close this tab and navigate away</li>
            <li>Report this site if you reached it from a search engine</li>
          </ul>
        </div>
      </div>
    </div>
  `;

  document.body.insertBefore(banner, document.body.firstChild);

  // Add click handler for details button
  const detailsBtn = document.getElementById('socialguard-details');
  const detailsDiv = document.getElementById('socialguard-threat-details');

  detailsBtn.addEventListener('click', () => {
    if (detailsDiv.style.display === 'none') {
      detailsDiv.style.display = 'block';
      detailsBtn.textContent = 'Hide Details';
    } else {
      detailsDiv.style.display = 'none';
      detailsBtn.textContent = 'View Details';
    }
  });

  // Notify background script
  chrome.runtime.sendMessage({
    action: 'threatDetected',
    url: window.location.href,
    threats: threats,
    domainIssue: domainCheck
  });
}

/**
 * Get human-readable threat description
 */
function getThreatDescription(type) {
  const descriptions = {
    'FAKE_UPDATE': 'fake software update/ClickFix',
    'URGENT_SCAM': 'phishing/urgency manipulation',
    'CLICKFIX_COMMAND': 'ClickFix command injection'
  };
  return descriptions[type] || 'social engineering';
}

/**
 * Monitor for dynamically added content
 */
const observer = new MutationObserver((mutations) => {
  // Debounce rapid changes
  clearTimeout(window.socialGuardScanTimeout);
  window.socialGuardScanTimeout = setTimeout(() => {
    performScan();
  }, 500);
});

/**
 * Perform security scan
 */
function performScan() {
  const domainCheck = checkDomain();
  const contentThreats = scanPageContent();

  if (domainCheck.suspicious || contentThreats.length > 0) {
    detectedThreats = contentThreats;
    showWarningBanner(contentThreats, domainCheck);
  }
}

// Initial scan when page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', performScan);
} else {
  performScan();
}

// Monitor for dynamic content changes
observer.observe(document.body, {
  childList: true,
  subtree: true,
  characterData: true
});

// Add animation keyframes
const style = document.createElement('style');
style.textContent = `
  @keyframes slideDown {
    from {
      transform: translateY(-100%);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }
`;
document.head.appendChild(style);

console.log('🛡️ SocialGuard extension activated');
