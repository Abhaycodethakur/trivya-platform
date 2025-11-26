# Create privacy_policy.md
@"
# Privacy Policy

**Last Updated:** $(Get-Date -Format "yyyy-MM-dd")
**Effective Date:** $(Get-Date -Format "yyyy-MM-dd")

## 1. Introduction

Trivya ("we," "us," "our") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, and protect your information when you use our AI-powered customer support platform.

## 2. Information We Collect

### 2.1 Client Information
- Company name, contact information
- Billing information
- Usage data and analytics

### 2.2 Customer Data (Processed on behalf of clients)
- Customer support inquiries
- Contact information
- Interaction history
- Conversation transcripts

### 2.3 Technical Data
- IP addresses
- Device information
- Usage patterns
- System logs

## 3. How We Use Your Information

### 3.1 To Provide Services
- Process customer support requests
- Generate AI responses
- Maintain service quality

### 3.2 For Platform Improvement
- Analyze usage patterns
- Train AI models
- Develop new features

### 3.3 For Legal Compliance
- Meet regulatory requirements
- Prevent fraud
- Ensure security

## 4. Data Security

- AES-256 encryption for data at rest
- TLS 1.3 for data in transit
- Regular security audits
- Access controls and authentication

## 5. Data Retention

- Customer data retained per client contract
- Automatic deletion after retention period
- Secure data destruction procedures

## 6. Your Rights

Under GDPR and applicable laws:
- Right to access your data
- Right to rectification
- Right to erasure
- Right to data portability
- Right to object to processing

## 7. International Data Transfers

We comply with:
- GDPR Standard Contractual Clauses
- Adequacy decisions where applicable
- Privacy Shield frameworks

## 8. Contact Us

For privacy inquiries:
Email: privacy@trivya.ai
Address: [Your Business Address]

## 9. Changes to This Policy

We will notify you of significant changes via:
- Email notification
- Platform announcement
- Website update
"@ | Out-File -FilePath "legal/policies/privacy_policy.md" -Encoding UTF8