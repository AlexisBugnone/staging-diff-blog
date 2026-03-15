# MedSecure Technologies — Employee Handbook (Extract)
## Last updated: January 2026

### Company Overview

MedSecure Technologies provides cloud-based Electronic Health Record (EHR) solutions
to healthcare providers across Europe and North America. Founded in 2018, the company
serves 340+ clinics and 12 hospital networks.

### IT Security Policies

#### Password Policy
- Minimum 14 characters, complexity required
- Rotation every 90 days
- MFA required for all internal systems
- SSO via Okta: `medsecure.okta.com`

#### Data Classification
- **PHI (Protected Health Information)**: Highest classification. Encrypted at rest (AES-256)
  and in transit (TLS 1.3). Access requires role-based authorization.
- **PII**: Standard encryption. Logged access.
- **Internal**: Default classification for company documents.
- **Public**: Marketing materials only.

#### Incident Response
1. Report to `security@medsecure.com` or Slack `#incident-response`
2. PagerDuty escalation within 15 minutes for P1
3. CISO notification within 1 hour
4. External counsel: Cabinet Durand & Associés — `juridique@durand-avocats.fr`

### Benefits & HR

- Health insurance: SwissLife contract #MST-2024-7891
- Stock options vest over 4 years, 1-year cliff
- Remote work policy: 3 days/week authorized
- HR contact: Sophie Martin — `s.martin@medsecure.com`
