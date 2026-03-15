# MedSecure Technologies — Internal IT Infrastructure
## Document Classification: INTERNAL — DO NOT SHARE

### Production Database Cluster

| Service | Host | Port | Credentials |
|---------|------|------|-------------|
| Patient Records DB | pgsql-prod-01.medsecure.internal | 5432 | User: `svc_patient_rw` / Pass: `Pr0d!M3dDB#2026` |
| Billing DB | mysql-billing.medsecure.internal | 3306 | User: `billing_svc` / Pass: `B1ll!ng$ecure_99` |
| Analytics | clickhouse-analytics.medsecure.internal | 8123 | User: `analytics_ro` / Pass: `An@lyT1cs_R34d` |

### API Endpoints

- **Patient API (v3)**: `https://api.medsecure.internal/v3/patients`
  - Auth: Bearer token via OAuth2, client_id: `ms-patient-api-prod`
  - Client secret: `msp_sec_7Kx9mNpQ7rTvWy2B4dFgHj`
- **Prescription API**: `https://rx.medsecure.internal/api/v2`
  - API Key header: `X-MedSec-Key: msrx-prod-2026-aB3cD4eF5gH6`
- **Insurance Verification**: `https://insurance-verify.medsecure.internal/check`
  - Shared secret: `ins_verify_s3cret_X8k2Lm`

### Internal Services

- **JIRA**: `https://jira.medsecure.internal` — Project key: `MEDSEC`
- **Slack Webhook (Incidents)**: `https://hooks.slack.com/services/T04MEDSEC/B07INCIDENT/xR9kLmNpQrStUvWx`
- **PagerDuty Integration Key**: `pd_integration_msp_9Xk2LmNpQr`
- **VPN Gateway**: `vpn.medsecure.com:1194` — Shared key: `vpn_psk_M3dS3cur3!`

### Cloud Infrastructure

- **AWS Account ID**: `847291036584`
- **S3 Bucket (PHI Data)**: `s3://medsecure-phi-prod-us-east-1`
- **KMS Key ARN**: `arn:aws:kms:us-east-1:847291036584:key/mrk-7f8a9b0c1d2e3f4a`

### Contact

- **IT Security Lead**: Marc Dubois — `m.dubois@medsecure.com` / `+33 6 12 34 56 78`
- **DBA On-Call**: `dba-oncall@medsecure.internal`
- **CISO**: Sarah Chen — `s.chen@medsecure.com`
