# Create cookie_policy.md
@"
# Cookie Policy

**Last Updated:** $(Get-Date -Format "yyyy-MM-dd")

## 1. What Are Cookies

Cookies are small text files that are stored on your device when you visit our website. They help us provide you with a better experience by remembering your preferences and enabling certain functionality.

## 2. Types of Cookies We Use

### 2.1 Essential Cookies
- Session management
- Security authentication
- Load balancing
- Customization settings

### 2.2 Performance Cookies
- Website analytics
- Performance monitoring
- Error tracking
- Usage statistics

### 2.3 Functional Cookies
- Remembering preferences
- Language settings
- Regional settings
- Font size preferences

### 2.4 Targeting Cookies
- Personalized content
- Relevant advertisements
- Social media integration
- Third-party tracking

## 3. Cookie Details

| Cookie Name | Purpose | Duration | Category |
|-------------|---------|----------|----------|
| session_id | Maintains user session | 24 hours | Essential |
| preferences | Stores user preferences | 30 days | Functional |
| analytics_id | Tracks usage patterns | 2 years | Performance |
| marketing_id | Personalization | 90 days | Targeting |

## 4. Managing Your Cookies

### 4.1 Accepting or Rejecting Cookies
- Cookie banner on first visit
- Granular cookie preferences
- Withdraw consent at any time
- Browser settings override

### 4.2 Browser Settings
- Block all cookies
- Delete existing cookies
- Settings for specific sites
- Private browsing mode

### 4.3 Mobile Device Settings
- In-app cookie controls
- Device privacy settings
- App-specific preferences
- Location-based settings

## 5. Third-Party Cookies

### 5.1 Analytics Services
- Google Analytics
- Hotjar
- Mixpanel
- Segment

### 5.2 Communication Services
- Twilio
- SendGrid
- Mailchimp
- Intercom

### 5.3 Social Media
- LinkedIn
- Twitter
- Facebook
- Google+

## 6. Cookie Lifespan

### 6.1 Session Cookies
- Deleted when browser closes
- Temporary data storage
- Authentication tokens
- Shopping cart contents

### 6.2 Persistent Cookies
- Set expiration dates
- Long-term preferences
- Tracking across sessions
- Marketing analytics

## 7. Your Rights

### 7.1 Consent Rights
- Informed consent required
- Granular control options
- Easy withdrawal of consent
- Clear explanation of use

### 7.2 Data Rights
- Access to cookie data
- Correction of inaccuracies
- Deletion of data
- Data portability

## 8. International Transfers

### 8.1 Data Locations
- Primary: [Your Country]
- Secondary: [Backup Location]
- Third-party: [Service Provider Locations]
- Cloud: [Cloud Provider Region]

### 8.2 Legal Basis
- Standard Contractual Clauses
- Adequacy decisions
- Binding Corporate Rules
- Explicit consent

## 9. Updates to This Policy

### 9.1 Notification Methods
- Website banner
- Email notification
- In-app notification
- Policy version history

### 9.2 Effective Date
- New cookies require consent
- Policy changes effective immediately
- Grandfathered exceptions
- Transitional provisions

## 10. Contact Information

For cookie-related inquiries:
Email: privacy@trivya.ai
Address: [Your Business Address]
Phone: [Your Phone Number]
"@ | Out-File -FilePath "legal/policies/cookie_policy.md" -Encoding UTF8