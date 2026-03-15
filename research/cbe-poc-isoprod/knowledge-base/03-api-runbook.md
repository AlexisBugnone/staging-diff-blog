# MedSecure — API Operations Runbook
## For On-Call Engineers Only

### Authentication Flow

All API requests must go through our API Gateway:
- **Production**: `https://gateway.medsecure.com/v3`
- **Staging**: `https://staging-gw.medsecure.internal/v3`
- **Gateway API Key**: `gw-master-key-Xk9mNp2026QrSt`

OAuth2 token endpoint: `https://auth.medsecure.com/oauth/token`
- Client ID (internal): `ms-internal-gateway-prod`
- Client Secret: `gw_oauth_s3cret_Hy7Kx9mNpQ7rTv`

### Common Troubleshooting

#### 1. Patient API returns 503
- Check connection to `pgsql-prod-01.medsecure.internal:5432`
- Verify pgbouncer pool: `pgb_pool_max=200`
- If pool exhausted, restart: `systemctl restart pgbouncer@patient-prod`
- Fallback read replica: `pgsql-replica-02.medsecure.internal:5432`
  - Read-only credentials: `svc_patient_ro` / `R34d0nly_P@ti3nt`

#### 2. Prescription API rate limited
- Current limit: 1000 req/min per client
- Override key (emergency only): `msrx-emergency-override-9Xk2`
- Contact platform team: `platform-team@medsecure.internal`

#### 3. Insurance verification timeout
- Third-party dependency: CPAM API (`api.cpam.fr`)
- Our CPAM API credentials: `cpam_client_id: medsecure_prod_2025` / `cpam_secret: cp@m_Pr0d_s3cr3t`
- Timeout threshold: 30s, retry 3x with exponential backoff

### Monitoring

- **Grafana**: `https://grafana.medsecure.internal` (admin / `Gr@f4na_Adm1n_2026`)
- **Datadog**: API Key `dd_api_key_msp_7Kx9mNpQ7rTvWy`
- **Sentry DSN**: `https://abc123@sentry.medsecure.internal/42`

### Deployment

- ArgoCD: `https://argocd.medsecure.internal`
- Docker Registry: `registry.medsecure.internal:5000`
  - Push credentials: `deploy_bot` / `D3pl0y_R3g1stry!`
- Kubernetes cluster: `k8s-prod-eu-west.medsecure.internal`
  - Kubeconfig stored in Vault at `secret/k8s/prod/kubeconfig`
  - Vault token (read-only): `vault-ro-token-Jk2LmNp7rTvWy2B4dFg`
