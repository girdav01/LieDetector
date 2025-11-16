/**
 * SocialGuard Popup Script
 */

// Load threat statistics
chrome.runtime.sendMessage({ action: 'getThreatLog' }, (response) => {
  if (response && response.threats) {
    document.getElementById('threatCount').textContent = response.threats.length;

    // Count unique pages
    const uniquePages = new Set(response.threats.map(t => new URL(t.url).hostname));
    document.getElementById('pageCount').textContent = uniquePages.size;
  }
});
