"""
SocialGuard ML Classifier
BERT-based phishing detection model (stub implementation)
"""

from typing import Dict, List
import re
from datetime import datetime


class PhishingClassifier:
    """
    BERT-based phishing classifier stub
    In production, this would use a trained transformer model
    """

    def __init__(self):
        self.urgency_keywords = [
            'urgent', 'immediate', 'asap', 'quickly', 'hurry', 'rush',
            'emergency', 'critical', 'important', 'warning', 'alert',
            'suspended', 'locked', 'expired', 'verify now', 'act now',
            'limited time', 'expires', 'deadline'
        ]

        self.credential_keywords = [
            'password', 'username', 'login', 'credential', 'pin', 'otp',
            'verification code', 'mfa', '2fa', 'security code', 'token',
            'authenticate', 'confirm identity', 'social security'
        ]

        self.payment_keywords = [
            'payment', 'invoice', 'wire transfer', 'bank account', 'routing number',
            'credit card', 'cvv', 'billing', 'transaction', 'refund',
            'paypal', 'venmo', 'zelle', 'gift card', 'bitcoin', 'cryptocurrency'
        ]

        self.impersonation_keywords = [
            'ceo', 'cfo', 'president', 'executive', 'manager', 'director',
            'hr', 'human resources', 'it support', 'help desk', 'security team',
            'microsoft', 'google', 'apple', 'amazon', 'paypal', 'irs', 'fbi'
        ]

    def classify_email(self, text: str, sender: str = '', subject: str = '') -> Dict:
        """
        Classify email as phishing or benign
        Returns classification with confidence score and detected features
        """
        text_lower = text.lower()
        subject_lower = subject.lower()
        sender_lower = sender.lower()

        features = self._extract_features(text_lower, subject_lower, sender_lower)
        confidence = self._calculate_confidence(features)

        classification = 'phishing' if confidence > 0.5 else 'benign'

        return {
            'classification': classification,
            'confidence': confidence,
            'features': features,
            'timestamp': datetime.utcnow().isoformat()
        }

    def _extract_features(self, text: str, subject: str, sender: str) -> Dict:
        """Extract features for classification"""
        features = {
            'urgency_score': 0,
            'credential_request': False,
            'payment_request': False,
            'impersonation_detected': False,
            'suspicious_links': 0,
            'suspicious_sender': False,
            'typos_detected': False
        }

        # Urgency detection
        urgency_count = sum(1 for keyword in self.urgency_keywords if keyword in text or keyword in subject)
        features['urgency_score'] = min(1.0, urgency_count / 3)  # Normalize to 0-1

        # Credential request detection
        features['credential_request'] = any(keyword in text for keyword in self.credential_keywords)

        # Payment request detection
        features['payment_request'] = any(keyword in text for keyword in self.payment_keywords)

        # Impersonation detection
        features['impersonation_detected'] = any(keyword in text or keyword in sender for keyword in self.impersonation_keywords)

        # Suspicious link detection
        features['suspicious_links'] = self._count_suspicious_links(text)

        # Suspicious sender detection
        features['suspicious_sender'] = self._check_suspicious_sender(sender)

        return features

    def _count_suspicious_links(self, text: str) -> int:
        """Count suspicious links in text"""
        # Find all URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)

        suspicious_count = 0
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top']

        for url in urls:
            # Check for suspicious TLDs
            if any(tld in url for tld in suspicious_tlds):
                suspicious_count += 1
            # Check for IP addresses instead of domains
            if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url):
                suspicious_count += 1
            # Check for URL shorteners
            if any(shortener in url for shortener in ['bit.ly', 'tinyurl', 't.co']):
                suspicious_count += 1

        return suspicious_count

    def _check_suspicious_sender(self, sender: str) -> bool:
        """Check if sender looks suspicious"""
        if not sender:
            return False

        # Check for mismatched display name and email
        # Check for free email providers pretending to be companies
        free_providers = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'aol.com']
        corporate_keywords = ['invoice', 'billing', 'noreply', 'support', 'admin', 'security']

        sender_lower = sender.lower()

        # If sender has corporate keyword but uses free email provider
        if any(provider in sender_lower for provider in free_providers):
            if any(keyword in sender_lower for keyword in corporate_keywords):
                return True

        return False

    def _calculate_confidence(self, features: Dict) -> float:
        """Calculate phishing confidence score"""
        score = 0.0

        # Weight different features
        if features['urgency_score'] > 0.5:
            score += 0.25

        if features['credential_request']:
            score += 0.30

        if features['payment_request']:
            score += 0.25

        if features['impersonation_detected']:
            score += 0.20

        if features['suspicious_links'] > 0:
            score += min(0.30, features['suspicious_links'] * 0.15)

        if features['suspicious_sender']:
            score += 0.20

        return min(1.0, score)


class VoiceVerification:
    """
    Voice biometrics and synthetic voice detection stub
    In production, this would use CNN/RNN models on audio spectrograms
    """

    def __init__(self):
        self.voice_profiles = {}

    def analyze_call(self, audio_features: Dict) -> Dict:
        """
        Analyze voice call for authenticity
        audio_features should contain: sample_rate, duration, pitch_variance, etc.
        """
        synthetic_score = self._detect_synthetic_voice(audio_features)
        authenticity_score = 1.0 - synthetic_score

        return {
            'authenticity_score': authenticity_score,
            'synthetic_likelihood': synthetic_score,
            'recommendation': self._get_verification_action(synthetic_score),
            'timestamp': datetime.utcnow().isoformat()
        }

    def _detect_synthetic_voice(self, audio_features: Dict) -> float:
        """
        Detect if voice is AI-generated
        Returns score 0-1 (higher = more likely synthetic)
        """
        score = 0.0

        # Check for unnatural characteristics
        # In real implementation, would analyze spectrograms, pitch patterns, etc.

        # Placeholder logic based on audio features
        if audio_features.get('pitch_variance', 1.0) < 0.3:
            score += 0.3  # Too consistent pitch suggests TTS

        if audio_features.get('background_noise', 0) < 0.1:
            score += 0.2  # Too clean audio suggests synthetic

        if audio_features.get('speech_rate_variance', 1.0) < 0.2:
            score += 0.25  # Too consistent rate suggests TTS

        return min(1.0, score)

    def _get_verification_action(self, synthetic_score: float) -> str:
        """Get recommended action based on synthetic score"""
        if synthetic_score > 0.7:
            return "BLOCK_AND_VERIFY"
        elif synthetic_score > 0.4:
            return "REQUIRE_CALLBACK"
        else:
            return "ALLOW_WITH_MONITORING"


# Example usage
if __name__ == "__main__":
    # Test phishing classifier
    classifier = PhishingClassifier()

    test_email = """
    URGENT: Your account has been suspended!

    We detected unusual activity on your account. Please verify your identity
    immediately by providing your password and security code.

    Click here: http://paypa1-secure.tk/verify

    This link expires in 24 hours!

    PayPal Security Team
    """

    result = classifier.classify_email(
        text=test_email,
        sender="security@gmail.com",
        subject="URGENT: Account Suspended - Verify Now"
    )

    print("Phishing Classification Result:")
    print(f"Classification: {result['classification']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Features: {result['features']}")
    print()

    # Test voice verification
    voice_verifier = VoiceVerification()

    test_audio = {
        'sample_rate': 44100,
        'duration': 30.5,
        'pitch_variance': 0.2,  # Low variance
        'background_noise': 0.05,  # Very clean
        'speech_rate_variance': 0.15  # Low variance
    }

    voice_result = voice_verifier.analyze_call(test_audio)

    print("Voice Verification Result:")
    print(f"Authenticity Score: {voice_result['authenticity_score']:.2%}")
    print(f"Synthetic Likelihood: {voice_result['synthetic_likelihood']:.2%}")
    print(f"Recommendation: {voice_result['recommendation']}")
