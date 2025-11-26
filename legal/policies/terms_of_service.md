# Create terms_of_service.md
@"
# Terms of Service

**Last Updated:** $(Get-Date -Format "yyyy-MM-dd")
**Effective Date:** $(Get-Date -Format "yyyy-MM-dd")

## 1. Acceptance of Terms

By accessing and using Trivya ("Service"), you accept and agree to be bound by these Terms.

## 2. Description of Service

Trivya provides AI-powered customer support automation platform including:
- Mini Trivya (Basic support automation)
- Trivya (Advanced support automation)
- Trivya High (Enterprise support automation)

## 3. User Responsibilities

### 3.1 Data Accuracy
- Ensure customer data is accurate
- Maintain up-to-date knowledge base
- Monitor AI interactions

### 3.2 Compliance
- Comply with applicable laws
- Obtain necessary consents
- Respect customer privacy

### 3.3 Prohibited Uses
- Misleading or harmful content
- Illegal activities
- Reverse engineering

## 4. Payment Terms

### 4.1 Subscription Model
- Monthly billing based on usage
- Custom pricing for enterprise
- 30-day payment terms

### 4.2 Overage Charges
- Soft cap: +20% no charge
- Hard cap: Additional fees apply
- Notification before charges

## 5. Service Availability

### 5.1 Uptime Guarantee
- 99.9% uptime SLA
- Scheduled maintenance windows
- Emergency procedures

### 5.2 Support Levels
- Standard: Email support
- Premium: Priority support
- Enterprise: Dedicated support

## 6. Data Ownership

- You own your customer data
- We process data per instructions
- Data deletion on request
- Backup and recovery procedures

## 7. Limitation of Liability

- Service provided "as is"
- Limitation of indirect damages
- Maximum liability equals subscription fee
- Force majeure exceptions

## 8. Termination

### 8.1 By You
- 30-day notice period
- Data export options
- Final settlement

### 8.2 By Us
- Material breach of terms
- Non-payment
- Illegal usage

## 9. Dispute Resolution

- Good faith negotiation
- Arbitration clause
- Governing law: [Your Jurisdiction]

## 10. Changes to Terms

- 30-day notice for material changes
- Immediate effect for legal requirements
- Continued use constitutes acceptance
"@ | Out-File -FilePath "legal/policies/terms_of_service.md" -Encoding UTF8