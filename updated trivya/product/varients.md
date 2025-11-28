Of course. Keeping all our documentation aligned is crucial. Here is the complete, updated 
`variants.pdf` documentation (v2.0), incorporating all the strategic decisions and new features 
we've defined. --- 
### **File 1: Trivya AI Workforce - Product Variants Documentation (v2.0)** 
**# Trivya: AI Workforce for Customer Support** 
## **Mini Trivya – The AI Freshy Support Agent** 
### **Overview** 
Mini Trivya is the AI equivalent of a fresher (trainee) customer support agent—but with 
enhanced consistency, speed, and multi-channel capabilities. It eliminates 100% of workload 
normally assigned to fresh support hires, while ensuring safety, escalation, and compliance. 
Mini Trivya is designed as the first variant in the Trivya suite, providing companies with an AI 
employee that handles repetitive support tasks, FAQs, and basic customer interactions across 
multiple platforms. 
### **Role Definition: "The Freshy"** 
In human support teams, freshers usually: - Answer FAQs with templated responses - Create and categorize tickets - Check order/shipping status - Prepare refund/cancellation requests (but don't approve) - Escalate complex cases to seniors - Do bulk updates and follow-up 
Mini Trivya replaces all of these tasks—and goes one step further by safely handling basic 
customer interactions 24/7 across voice and digital channels. 
### **Core Functionalities** 
1.  **Multi-Channel Coverage** -   **Email**: Reads, classifies, and responds to support emails -   **Live Chat/Web Widget**: Answers FAQs and order queries in real time -   **Social Media (FB, Insta, X, WhatsApp)**: Handles DMs and comments for routine 
questions 
    -   **SMS**: Sends updates (order shipped, delivery ETA, reminders) 
    -   **Phone Calls (Up to 2 concurrent)**: 
        -   Greets customers professionally 
        -   Provides FAQs + order/tracking info 
        -   Collects refund/cancellation requests 
        -   Escalates complex/edge cases to higher-level AI or human agents 
 
2.  **Ticket Management** 
    -   Auto-create tickets from all channels 
    -   Tag and categorize tickets by intent (refund, product issue, shipping) 
    -   Prioritize based on urgency (e.g., angry customer detected) 
    -   Merge/split duplicate tickets 
    -   Close/resolve bulk tickets 
 
3.  **Customer Query Handling** 
    -   **FAQs**: Instantly resolves routine questions (returns, pricing, shipping, login) 
    -   **Order Tracking**: Fetches real-time updates from Shopify/ERP 
    -   **Refund Intake & Verification**: Collects details, performs initial policy checks, verifies 
customer information, and flags for human review. **[Core Principle]** AI will **NEVER** 
execute a refund. 
    -   **Escalations**: Detects when queries exceed its scope → passes to Trivya/Trivya High or 
human 
 
4.  **Voice AI with Guardrails** 
    -   Handles basic voice conversations with customers 
    -   Provides only eligible, public-facing information 
    -   Deflects or escalates when asked about internal/private company data 
    -   Scripted safe boundaries: 
        -   "I can help you with orders, returns, and general queries" 
        -   "For sensitive account-specific questions, I'll connect you to a senior agent" 
 
5.  **Internal Safeguards** 
    -   **Role-based knowledge access**: Only sees public KB + order data 
    -   **Escalation triggers**: 
        -   Customer tone = angry/urgent 
        -   VIP or high-value customer detected 
        -   Legal/compliance queries 
        -   Refund requests beyond basic verification 
    -   **Audit trail**: Every action logged for compliance 
 
### **[UPDATED] Dynamic Pricing & Scaling** 
 
Mini Trivya pricing scales automatically based on actual workload: -   **Base Platform Fee**: **$1,000/month** (covers infrastructure) 
-   **Per-Ticket Fee**: $0.10 per ticket resolution over 200/day -   **Per-Call Slot**: $75 per concurrent call line (up to 2 included) -   **Minimum Agents**: Can deploy 1-5 Mini agents based on volume 
### **[UPDATED] Value Proposition** -   Replaces a 24/7 team of 3 trainees for **over 90% cost savings**. -   Provides multi-channel coverage, including calls. -   Ensures faster resolutions with zero repetitive workload for humans. -   Serves as the foundation for scaling up to Trivya (Junior) and Trivya High. -   **Self-Service Ready**: SMBs can onboard without human interaction via automated 
workload assessment. --- 
## **Trivya – The AI Junior Customer Support Agent** 
### **Overview** 
Trivya is the AI equivalent of a junior customer care agent. It builds on Mini Trivya by handling 
not just basic tasks but also autonomous resolution of day-to-day issues such as 
troubleshooting and multi-channel coordination. 
Unlike Mini, Trivya is trusted to resolve 70-80% of customer issues end-to-end, only escalating 
high-value or complex cases. With its self-learning and monitoring layer, Trivya improves 
continuously over time and ensures reliability with self-healing and proactive monitoring. 
### **Role Definition: "The Junior Agent"** 
In a human team, junior agents: - Answer FAQs and repetitive questions - Manage chats, emails, and social messages - Handle simple refunds under a threshold - Guide customers through troubleshooting - Suggest knowledge base updates - Escalate unusual or sensitive cases to seniors 
Trivya mirrors this role—but never gets tired, can handle multiple calls at once, and improves by 
learning from every interaction. 
### **Core Functionalities** 
1.  **Inherited from Mini Trivya (Freshy)** -   Multi-channel coverage: email, chat, socials, SMS, and up to 3 simultaneous calls -   Ticket creation, tagging, categorization, and prioritization 
    -   FAQ answers from KB 
    -   Order/shipping lookups (via integrations like Shopify/ERP) 
    -   Refund/cancellation intake with verification 
    -   Escalation triggers (VIPs, legal, fraud, unusual patterns) 
 
2.  **Enhanced Junior-Level Autonomy** 
    -   **Refund Verification & Recommendation**: Performs deep verification, analyzes customer 
history against return policies, detects potential fraud, provides clear recommendations 
(APPROVE/REVIEW/DENY) to human agents. **[Core Principle]** AI will **NEVER** execute a 
refund. 
    -   **Knowledge Base Auto-Update**: Detects recurring issues and drafts or updates FAQs 
automatically. 
    -   **Case Summarization**: Generates clear summaries of ticket history + customer tone 
before escalation. 
    -   **Troubleshooting Guidance**: Guides customers step-by-step for common 
technical/product issues. 
    -   **Expanded Call Handling**: Can handle 3 calls simultaneously while maintaining quality. 
 
3.  **Self-Learning Features** 
    -   **Pattern Detection**: Spots recurring issues from tickets. 
    -   **Automation Suggestions**: Proposes new KB entries or workflows (requires admin 
approval). 
    -   **Continuous Adaptation**: Learns from human resolutions → reduces future escalations. 
    -   **Performance Monitoring**: Tracks accuracy and CSAT → auto-generates improvement 
reports. 
 
4.  **Monitoring & Self-Healing Layer** 
    -   **Self-Monitoring**: Continuously checks its own workflows. 
    -   **Self-Healing**: Fixes small issues automatically (e.g., retrying failed API calls, refreshing 
data). 
    -   **Error Escalation**: If an issue cannot be fixed → alerts admins/team instantly. 
    -   **Transparency**: Keeps full logs of errors and how they were resolved. 
 
### **[UPDATED] Dynamic Pricing & Scaling** 
 
Trivya pricing includes: -   **Base Agent Fee**: **$2,500/month** per Trivya agent -   **Call Capacity**: 3 concurrent calls included, +$75 per additional call slot -   **Volume Threshold**: Handles up to 300 tickets/day per agent -   **Smart Bundling**: System automatically recommends agent combinations based on 
assessment 
 
### **[UPDATED] Value Proposition** -   Replaces a 24/7 team of 3 junior agents for **over 85% cost savings**. 
-   Eliminates 100% of junior agent workload. -   Resolves 70-80% of customer issues without human input. -   Improves over time with self-learning and KB updates. -   Ensures reliability with self-healing and monitoring. -   Handles 3 simultaneous calls plus all text channels. -   **Fully Automated Scaling**: Pricing and agent count adjust without human involvement. --- 
## **Trivya High – The AI Senior Customer Support Agent** 
### **Overview** 
Trivya High is the senior-level AI Customer Support Agent—an enhanced version of Trivya with 
advanced decision-making capabilities, broader authority, and strategic intelligence. It 
represents the AI equivalent of a Senior Customer Support Agent who can handle complex 
cases, make informed decisions within safe limits, and provide strategic insights. 
Trivya High eliminates 80-85% of human support workload while maintaining appropriate human 
oversight for high-risk decisions, ensuring both efficiency and safety. 
### **Role Definition: "The Senior Support Agent"** 
In traditional teams, senior support agents: - Handle complex escalations and VIP customers - Make refund/cancellation decisions within company limits - Coordinate with internal teams when needed - Mentor junior staff and optimize processes - Analyze trends and suggest improvements - Handle sensitive customer situations 
Trivya High performs these roles with enhanced capabilities but maintains smart boundaries and 
escalation protocols. 
### **Complete Functionality Breakdown** 
#### **1. Inherited & Enhanced from Trivya (Junior)** 
| Feature | Trivya Capability | Trivya High Enhancement | 
|---------|-------------------|-------------------------| 
| Multi-Channel Support | 3 simultaneous calls | 5 simultaneous calls + video support | 
| Refund Authority | Verification & recommendation | Advanced fraud detection + strategic 
recommendation | 
| KB Management | Basic article updates | Advanced KB optimization + multilingual support | 
| Call Handling | Basic conversations | Complex troubleshooting + screen sharing | 
| Learning Speed | Standard pattern recognition | Advanced pattern recognition + strategic 
insights | 
#### **2. Advanced Senior-Level Capabilities** 
**A. Enhanced Multi-Channel Ecosystem** 
| Channel | Advanced Capabilities | Concurrent Handling | Senior-Level Features | 
|---------|----------------------|---------------------|-----------------------| 
| Voice Calls | Complex troubleshooting, emotional de-escalation | 5 calls | Advanced 
conversation management | 
| Video Support | Screen sharing, visual product demos | 3-5 sessions | Technical problem 
solving | 
| Email | Complex inquiry resolution, multi-thread management | Unlimited | Advanced context 
understanding | 
| Social Media | Crisis management, brand reputation protection | 100+ interactions | 
PR-sensitive responses | 
| Live Chat | Complex product consultations, sales support | Unlimited | Advanced product 
knowledge | 
**B. Advanced Decision Making (With Smart Limits)** 
| Decision Type | Authority Level | Human Escalation Triggers | 
|---------------|-----------------|---------------------------| 
| Standard Refunds | Advanced verification with fraud detection | All refunds requiring human 
approval | 
| Account Changes | Basic profile updates only | Payment methods, billing info, 
security-sensitive data | 
| Product Issues | Replacement recommendations up to $50 | Higher value items, warranty 
disputes | 
| Service Credits | Recommendations up to $50 | Larger amounts, repeated requests | 
| VIP Requests | Information gathering only | All VIP financial requests escalated | 
**C. Internal Coordination & Intelligence** 
| Department | Coordination Level | Intelligence Provided | 
|------------|-------------------|-----------------------| 
| Logistics | Auto-creates shipping tickets, tracks complex delivery issues | Shipping trend 
analysis, carrier performance insights | 
| Finance | Processes refund verifications, flags payment issues | Refund pattern analysis, 
revenue impact reports | 
| Engineering | Creates detailed bug reports with customer impact analysis | Product issue 
trending, customer satisfaction correlation | 
| Sales | Identifies upsell opportunities, manages account transitions | Customer lifetime value 
insights, expansion opportunities | 
| Management | Provides performance metrics and trend analysis | Strategic recommendations, 
efficiency insights | 
#### **3. [NEW] The "Brand Ambassador" Knowledge Base** -   **Client Knowledge Ingestion**: During onboarding, clients upload their own documentation 
(product manuals, company policies, mission statements, FAQs). -   **RAG-Powered Expertise**: The AI ingests this information, allowing it to speak with the 
client's unique brand voice and act as a true expert on their products and policies. -   **Contextual Responses**: When a customer asks a question, the AI provides answers that 
are not just correct, but are also perfectly aligned with the client's brand identity and values. 
#### **4. Advanced Intelligence & Learning Systems** 
**A. Predictive Customer Intelligence** -   **Churn Risk Prediction**: Identifies customers likely to cancel and triggers retention 
workflows. -   **Satisfaction Forecasting**: Predicts CSAT scores and proactively addresses potential 
issues. -   **Usage Pattern Analysis**: Identifies optimization opportunities for customer success. -   **Escalation Prevention**: Detects issues before they require human intervention. 
**B. Business Intelligence & Analytics** -   **Cost Impact Analysis**: Tracks savings vs traditional support models. -   **Efficiency Optimization**: Identifies workflow improvements and automation opportunities. -   **Customer Insights**: Provides strategic recommendations for product and service 
improvements. -   **Trend Forecasting**: Predicts support volume and resource needs. 
**C. Advanced Self-Learning** -   **Resolution Optimization**: Learns from every successful case resolution. -   **Error Prevention**: Identifies and prevents recurring mistakes. -   **Policy Adaptation**: Adapts to new policies and business changes automatically. -   **Performance Monitoring**: Continuously monitors all systems and self-corrects minor 
issues. 
#### **5. Enhanced Proactive Support** 
| Proactive Initiative | Description | Business Impact | 
|----------------------|-------------|------------------| 
| Issue Prevention | Identifies potential problems before customers contact support | 30% 
reduction in inbound tickets | 
| Customer Health Monitoring | Tracks usage patterns and proactively reaches out for 
optimization | 25% improvement in customer retention | 
| Product Guidance | Provides personalized tips and best practices based on usage | 40% 
increase in feature adoption | 
| Renewal Management | Manages subscription renewals with personalized offers | 20% 
improvement in renewal rates | 
#### **6. Enterprise-Grade Safety & Controls** 
**A. Smart Escalation System** -   **Risk Assessment**: Every decision evaluated for business risk. -   **Confidence Scoring**: Only acts when confidence exceeds threshold. -   **Pattern Recognition**: Escalates unusual situations automatically. -   **VIP Protection**: Special handling for high-value customers. 
**B. Human Oversight Integration** -   **Approval Workflows**: Configurable approval for high-value decisions. -   **Real-time Monitoring**: Human supervisors can monitor and intervene. -   **Rollback Controls**: Any action can be reversed instantly. -   **Audit Trails**: Complete logs of all decisions and actions. 
**C. Security & Compliance** -   **Data Protection**: Enterprise-grade encryption and privacy controls. -   **Regulatory Compliance**: GDPR, CCPA, and industry-specific compliance. -   **Access Controls**: Role-based permissions and security monitoring. -   **Incident Response**: Automated security incident detection and response. 
### **[UPDATED] Dynamic Pricing & Scaling** 
Trivya High pricing: -   **Base Agent Fee**: **$4,000/month** per Trivya High agent -   **Call Capacity**: 5 concurrent calls included, +$100 per additional slot -   **Volume Threshold**: Handles up to 500 tickets/day per agent -   **Video Support**: +$200/month for video session capability -   **Enterprise Floor**: Minimum 2 agents for companies >500 employees 
### **Workload Elimination Analysis** 
**Trivya (Junior) vs Trivya High Comparison:** 
| Support Function | Trivya Automation | Trivya High Automation | Human Role | 
|------------------|-------------------|------------------------|------------| 
| FAQs & Basic Support | 100% | 100% | None | 
| Order Tracking & Management | 100% | 100% | None | 
| Simple Refunds (<$50) | Verification | Enhanced verification | Approval | 
| Medium Refunds ($50+) | Escalated | Enhanced fraud detection + escalation | All medium/high 
refunds | 
| Complex Technical Issues | 30% | 70% | Specialized expertise | 
| VIP Customer Support | 20% | 60% | Relationship management | 
| Internal Coordination | 50% | 85% | Strategic oversight | 
| Crisis Management | 0% | 40% | Executive decisions | 
| Business Analytics | Basic reporting | Advanced insights | Strategic planning | 
**Overall Workload Elimination:** -   **Trivya (Junior Agent)**: Eliminates 70% of total support workload. -   **Trivya High (Senior Agent)**: Eliminates 78-82% of total support workload. 
### **[UPDATED] Value Proposition** -   Replaces a 24/7 team of 3 senior agents for **over 80% cost savings**. -   Eliminates 80-85% of human support workload. -   Handles most complex cases independently (except financial approvals). -   Provides strategic business intelligence beyond cost savings. -   Scales senior expertise across all customer interactions. -   **[NEW] Acts as a "Brand Ambassador": Becomes a true expert on the client's company, 
products, and voice, enhancing brand loyalty and trust. -   **Automated Enterprise Pricing**: Absorbs usage variance with smart caps while protecting 
margins. 