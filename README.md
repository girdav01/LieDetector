# SocialGuard - AI-Powered Social Engineering Defense Platform

![SocialGuard](https://img.shields.io/badge/Security-SocialGuard-blue)
![Version](https://img.shields.io/badge/version-1.0.0-green)
![License](https://img.shields.io/badge/license-MIT-blue)

**Real-time protection against social engineering attacks combining AI-powered trust scoring with just-in-time behavioral nudges.**

## 🎯 Overview

SocialGuard is a comprehensive fraud detection and social engineering defense platform based on the [Unit 42 2025 Global Incident Response Report](https://unit42.paloaltonetworks.com/2025-unit-42-global-incident-response-report-social-engineering-edition/). It addresses the growing threat landscape where 36% of incidents start with social engineering.

### Key Threats Addressed

- **ClickFix Attacks** - Fake system prompts and SEO poisoning
- **Help Desk Manipulation** - MFA bypass and account takeover
- **Voice Cloning** - AI-generated voice impersonation
- **Executive Impersonation** - CEO fraud and BEC attacks
- **Credential Phishing** - Sophisticated phishing campaigns

## 🏗️ Architecture

### Core Components

1. **Trust Scoring Engine** (FastAPI Backend)
   - Real-time risk assessment (0-100 score)
   - Multi-signal analysis (identity, content, behavior, context)
   - Redis caching for low-latency scoring

2. **Just-In-Time Nudges** (React Frontend)
   - Color-coded trust banners (Green/Amber/Red)
   - Contextual warnings at decision points
   - User feedback loop for continuous learning

3. **ClickFix Defense** (Chrome Extension)
   - Detects fake update prompts
   - Identifies SEO poisoning
   - Blocks command injection attempts
   - Typosquatting detection

4. **ML Classifier** (Python)
   - Phishing detection
   - Voice synthetic analysis
   - Feature extraction and scoring

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- Redis (optional, fallback to in-memory cache)
- Chrome/Edge browser (for extension)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the API server
python main.py

# Server runs on http://localhost:8000
# API docs available at http://localhost:8000/docs
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Chrome Extension Setup

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `extension` directory
5. Extension is now active and protecting your browsing

## 📊 API Usage

### Calculate Trust Score

```bash
POST http://localhost:8000/calculate_trust_score
Content-Type: application/json

{
  "event_id": "evt_123",
  "event_type": "email",
  "sender": "ceo@company-corp.com",
  "domain_age_days": 7,
  "lookalike_domain": true,
  "urgency_language": true,
  "payment_request": true,
  "after_hours": true
}
```

**Response:**
```json
{
  "event_id": "evt_123",
  "score": 25,
  "risk_level": "HIGH",
  "factors": [
    "New domain (registered 7 days ago)",
    "Lookalike domain detected",
    "Urgency/emotional manipulation detected",
    "Payment or financial information requested",
    "After-hours sensitive request"
  ],
  "timestamp": "2025-11-14T20:00:00Z"
}
```

### Deliver Nudge

```bash
POST http://localhost:8000/deliver_nudge
Content-Type: application/json

{
  "event_id": "evt_123",
  "event_type": "email",
  "sender": "ceo@company-corp.com",
  "lookalike_domain": true,
  "urgency_language": true
}
```

**Response:**
```json
{
  "event_id": "evt_123",
  "banner_color": "RED",
  "message": "⚠️ HIGH RISK: This interaction shows multiple suspicious indicators...",
  "action_required": "BLOCK",
  "verification_method": "dual_approval_callback"
}
```

## 🎨 Trust Banner Component

```jsx
import TrustBanner from './components/TrustBanner';

function EmailViewer() {
  return (
    <TrustBanner
      score={45}
      message="This request shows suspicious patterns. Verify before proceeding."
      factors={[
        "New domain (registered 12 days ago)",
        "Urgency language detected"
      ]}
      eventId="evt_456"
    />
  );
}
```

## 🔒 Trust Scoring Algorithm

The trust scoring engine analyzes multiple signal categories:

### Identity Signals (-70 points max)
- Domain age < 30 days: -25
- Lookalike domain: -30
- SPF/DKIM/DMARC failures: -15 each

### Content Analysis (-50 points max)
- Urgency language: -15
- Credential requests: -20
- Payment requests: -20
- QR codes (ClickFix): -10

### Behavioral Patterns (-35 points max)
- Not in org graph: -15
- Device change: -10
- Location change: -10

### Contextual Factors (-30 points max)
- After-hours + sensitive request: -15
- Voice synthetic score > 0.6: -25

### Risk Levels
- **0-39**: HIGH RISK (Red) → Block + Dual Verification
- **40-69**: MEDIUM RISK (Amber) → Verify via Callback
- **70-100**: LOW RISK (Green) → Allow with Monitoring

## 🛡️ Chrome Extension Features

### Real-Time Protection

- **Fake Update Detection**: Identifies ClickFix prompts
- **SEO Poisoning**: Detects malicious search results
- **Typosquatting**: Catches lookalike domains
- **Command Injection**: Blocks PowerShell/cmd attempts
- **Urgency Scams**: Flags emotional manipulation

### Visual Warnings

- Persistent red banner on suspicious pages
- Detailed threat breakdown
- Recommended actions
- Browser notifications for critical threats

## 📈 Metrics & Analytics

Access system metrics:

```bash
GET http://localhost:8000/metrics
```

Returns:
- Total events processed
- Risk level distribution
- Feedback counts
- System health

## 🔄 Feedback Loop

Users can provide feedback to improve detection:

```bash
POST http://localhost:8000/user_feedback

{
  "event_id": "evt_123",
  "action": "reported_suspicious",
  "user_comment": "Known phishing campaign"
}
```

Actions:
- `reported_suspicious` - User marked as threat
- `confirmed_legit` - False positive
- `ignored` - User ignored warning

## 🎯 Use Cases

### 1. Email Security
Monitor incoming emails for phishing, BEC, and impersonation attacks.

### 2. Help Desk Protection
Verify caller identity before MFA resets or password changes.

### 3. Web Browsing Safety
Block ClickFix, fake updates, and SEO poisoning in real-time.

### 4. Voice Call Verification
Detect AI-generated voice cloning in executive impersonation.

### 5. Financial Transaction Review
Add verification steps for suspicious payment requests.

## 🔧 Configuration

### Backend Configuration

Edit `backend/main.py`:

```python
# Redis connection
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# CORS origins
allow_origins=["*"]  # Restrict in production

# Cache TTL
r.setex(key, 3600, value)  # 1 hour
```

### Extension Configuration

Edit `extension/content.js`:

```javascript
// Adjust detection sensitivity
const SUSPICIOUS_PATTERNS = {
  fakeUpdates: [...],  // Add patterns
  urgentActions: [...],
  suspiciousCommands: [...]
};

// Backend API endpoint
const API_ENDPOINT = 'http://localhost:8000';
```

## 📚 ML Model Training

The current implementation uses rule-based classification. For production:

1. Collect labeled dataset of phishing vs. benign emails
2. Fine-tune BERT model:

```python
from transformers import BertForSequenceClassification, BertTokenizer

# Load pre-trained BERT
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Train on your dataset
# See ml_models/phishing_classifier.py for stub implementation
```

3. Replace rule-based logic with trained model
4. Add voice biometrics using CNN/RNN on spectrograms

## 🌐 Deployment

### Docker Deployment

```bash
# Build backend
docker build -t socialguard-api ./backend

# Run with Redis
docker-compose up -d

# Backend: http://localhost:8000
# Redis: localhost:6379
```

### Production Considerations

- Use environment variables for configuration
- Enable HTTPS/TLS for all endpoints
- Implement rate limiting
- Add authentication/authorization
- Set up monitoring and alerting
- Configure Redis persistence
- Deploy behind reverse proxy (nginx)

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Train production BERT model on phishing dataset
- [ ] Add voice biometrics implementation
- [ ] Slack/Teams integration
- [ ] Mobile SDK for iOS/Android
- [ ] Advanced analytics dashboard
- [ ] SIEM integration (Splunk, ELK)
- [ ] Multi-language support

## 📄 License

MIT License - See LICENSE file for details

## 🔗 References

- [Unit 42 2025 Social Engineering Report](https://unit42.paloaltonetworks.com/2025-unit-42-global-incident-response-report-social-engineering-edition/)
- [NIST Phishing Detection Guidelines](https://www.nist.gov/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## 📧 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Review documentation at /docs
- Check API docs at http://localhost:8000/docs

---

**Built with ❤️ to protect against social engineering attacks**

🛡️ **Stay Safe. Stay Vigilant. Stay Protected.**
