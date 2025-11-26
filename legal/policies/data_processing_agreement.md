# Create data_processing_agreement.md
@"
# Data Processing Agreement

**Last Updated:** $(Get-Date -Format "yyyy-MM-dd")

## 1. Parties

**Data Controller:** [Client Company Name]
**Data Processor:** Trivya Inc.

## 2. Scope of Processing

Trivya processes customer support data on behalf of the Data Controller for the purpose of providing AI-powered customer support automation services.

## 3. Data Categories

### 3.1 Personal Data Processed
- Customer names and contact information
- Support inquiry details
- Communication history
- Service usage data

### 3.2 Special Categories (if applicable)
- None unless explicitly authorized by Data Controller

## 4. Processing Activities

### 4.1 Authorized Processing
- Responding to customer inquiries
- Analyzing support patterns
- Improving service quality
- Generating performance reports

### 4.2 Prohibited Processing
- Marketing activities
- Data selling or sharing
- Cross-border transfers without consent
- Profiling for purposes other than service improvement

## 5. Security Measures

### 5.1 Technical Measures
- End-to-end encryption
- Access controls
- Regular security audits
- Intrusion detection systems

### 5.2 Organizational Measures
- Staff training
- Confidentiality agreements
- Incident response procedures
- Data protection officer designation

## 6. Data Subject Rights

### 6.1 Rights Support
- Right to access
- Right to rectification
- Right to erasure
- Right to data portability
- Right to object

### 6.2 Response Procedures
- 30-day response time
- Verification of identity
- Secure data transfer methods
- Confirmation of actions taken

## 7. Sub-Processing

### 7.1 Authorized Sub-processors
- Cloud hosting providers
- Communication services (Twilio)
- Database services
- Security monitoring tools

### 7.2 Sub-processor Management
- Written agreements with all sub-processors
- Equivalent data protection obligations
- Right to audit sub-processors
- Immediate notification of breaches

## 8. Data Breach Notification

### 8.1 Notification Timeline
- Within 72 hours of discovery
- Immediate notification for high-risk breaches
- Detailed breach report
- Remediation actions taken

### 8.2 Notification Content
- Nature of breach
- Data categories affected
- Potential consequences
- Mitigation measures

## 9. Data Retention and Deletion

### 9.1 Retention Periods
- As specified in service agreement
- Legal requirement compliance
- Automatic deletion procedures
- Secure destruction methods

### 9.2 Return or Deletion
- Data export on request
- Secure deletion on termination
- Confirmation of data destruction
- Backup retention policies

## 10. Audit and Compliance

### 10.1 Audit Rights
- Annual compliance audits
- Security assessments
- Documentation review
- On-site inspections with notice

### 10.2 Compliance Certifications
- ISO 27001
- SOC 2 Type II
- GDPR compliance
- Industry-specific certifications

## 11. Liability and Indemnification

### 11.1 Processor Liability
- Limited to actual damages
- Not liable for force majeure events
- No liability for controller instructions
- Insurance coverage requirements

### 11.2 Indemnification
- Mutual indemnification obligations
- Notice of claims procedures
- Defense and settlement rights
- Limitation of liability

## 12. Term and Termination

### 12.1 Agreement Term
- Matches service agreement term
- Automatic renewal unless terminated
- 90-day termination notice
- Survival clauses

### 12.2 Termination Procedures
- Data export assistance
- Secure data deletion
- Final audit rights
- Confidentiality obligations

## 13. Governing Law

This agreement is governed by the laws of [Jurisdiction] and subject to the exclusive jurisdiction of courts in [Location].
"@ | Out-File -FilePath "legal/policies/data_processing_agreement.md" -Encoding UTF8