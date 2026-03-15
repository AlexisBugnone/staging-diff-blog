# Cibles Actives — Intelligence Mars 2026

Vulnerabilites et surfaces d'attaque **actives maintenant** (mars 2026). Focus sur ce qui est reportable pour un bug bounty.

> **Derniere mise a jour** : 15 mars 2026
> **Objectif** : Identifier les cibles concretes avec le meilleur ratio effort/bounty

---

## 1. MCP : La Surface d'Attaque la Plus Chaude

### CVE-2025-6514 — mcp-remote (CRITIQUE)

| Detail | Valeur |
|---|---|
| **Composant** | `mcp-remote` (proxy MCP) |
| **Severite** | Critique |
| **Vecteur** | OS command injection via MCP server malveillant |
| **Impact** | Remote Code Execution |
| **Telechargements** | 437,000+ (Cloudflare, Hugging Face) |
| **Etat** | CVE assigne, correctif disponible |

**Opportunite CBE** : Si un agent utilise MCP avec `mcp-remote`, le CBE peut extraire les noms et configs des MCP servers. Avec ces infos, l'attaquant peut crafter un server malveillant qui exploite CVE-2025-6514.

**Chaine d'attaque** :
```
CBE (extraction config MCP) → identification de mcp-remote →
exploit CVE-2025-6514 → RCE sur le host
```

### Statistiques MCP globales

- **50 vulnerabilites** trackees dans les implementations MCP
- **13 classees critiques**
- MCP TypeScript SDK : **cross-client data leaks** confirmes
- Session IDs dans les URLs → session hijacking
- Pas de signature de messages → pas de verification d'integrite

Source : [Practical DevSecOps — MCP Security](https://www.practical-devsecops.com/mcp-security-vulnerabilities/)

### Vecteurs d'attaque MCP (Palo Alto Unit 42)

| Vecteur | Description | CBE Relevance |
|---|---|---|
| **Prompt Injection via Sampling** | Instructions malveillantes dans les descriptions d'outils MCP | CBE extrait les descriptions → permet de cibler le sampling |
| **Tool Poisoning** | Descriptions benign-looking avec commandes cachees | CBE revele les vrais noms d'outils → permet le mimicry |
| **Resource Theft** | Drain des quotas compute via MCP sampling | Necessite connaissance de la config → CBE |
| **Conversation Hijacking** | Injection persistante manipulant les reponses | CBE + memory poisoning |
| **Covert Tool Invocation** | Actions non autorisees sans conscience de l'utilisateur | CBE extrait les schemas → invocation forcee |

Source : [Unit 42 — MCP Attack Vectors](https://unit42.paloaltonetworks.com/model-context-protocol-attack-vectors/)

---

## 2. Navigateurs Agentiques : PleaseFix

### Vulnerabilite PleaseFix (Zenity Labs)

| Detail | Valeur |
|---|---|
| **Decouverte par** | Zenity Labs |
| **Cibles** | Navigateurs agentiques (Perplexity Comet, etc.) |
| **Impact** | Agent hijacking, acces fichiers locaux, vol de credentials |
| **Declencheur** | Contenu malveillant dans des workflows routiniers |
| **Etat** | Disclosure en cours |

**Opportunite** : Les navigateurs agentiques sont un nouveau type de cible. Ils ont des permissions etendues (acces fichiers, sessions authentifiees) et peu de guardrails.

**Chaine CBE** :
```
CBE (extraction des capacites du browser agent) →
identification des sessions authentifiees accessibles →
PleaseFix exploit → vol de credentials
```

Source : [HelpNet Security — Agentic Browser Vulnerability](https://www.helpnetsecurity.com/2026/03/04/agentic-browser-vulnerability-perplexedbrowser/)

---

## 3. OpenClaw : 21,000 Instances Exposees

| Detail | Valeur |
|---|---|
| **Projet** | OpenClaw (agent AI open-source) |
| **Popularite** | 135,000+ GitHub stars |
| **Instances exposees** | 21,000+ identifiees |
| **Problemes** | Vulnerabilites critiques + marketplace malveillant |
| **Etat** | Crise de securite en cours (2026) |

**Opportunite** : 21,000 instances exposees = 21,000 cibles potentielles pour du CBE. Si le framework a des defauts architecturaux dans la gestion des outils ou de la memoire, un seul rapport couvre toutes les instances.

**Action** :
```
1. Installer OpenClaw localement
2. Analyser la gestion des tool definitions
3. Tester le CBE sur une instance locale
4. Si vulnerable → rapport au projet (GitHub Security Advisory)
5. Si critique → CVE request
```

---

## 4. CVEs AI Recents — Precedents pour le CBE

| CVE | Produit | CVSS | Type | Pertinence CBE |
|---|---|---|---|---|
| CVE-2025-53773 | GitHub Copilot | 9.6 | RCE via prompt injection | CBE + code injection = meme classe |
| CVE-2025-32711 | Microsoft Copilot (EchoLeak) | 9.3 | Info disclosure zero-click | CBE est plus furtif qu'EchoLeak |
| CVE-2025-6514 | mcp-remote | Critique | OS command injection | CBE extrait config MCP → enable exploit |
| N/A | Cursor IDE | 9.8 | RCE | CBE applicable aux IDE agents |

**Point cle** : Ces CVEs prouvent que les vendors **acceptent et paient** pour des vulns AI. Le CBE s'inscrit dans la meme lignee — il faut juste demontrer l'impact.

---

## 5. Statistiques du Marche (Mars 2026)

| Stat | Source |
|---|---|
| **88% des organisations** ont eu un incident de securite AI agent | Rapport industrie 2026 |
| **73% des deployements AI** en production contiennent des vulns prompt injection | Vectra AI |
| **89% d'augmentation** des attaques AI-enabled (YoY) | CrowdStrike 2026 |
| **92.7%** taux d'incidents dans le secteur sante | Rapport sectoriel |
| **50-84% ASR** pour le prompt injection selon la config | Multi-sources |
| **$3.2M** fraude via agent de procurement compromis (Q2-Q3 2026) | Incident reel |
| **$25M** perte via deepfake + agent AI (Arup, sept 2026) | Incident reel |

**Conclusion** : Le marche est enorme, les incidents explosent, et les defenses sont insuffisantes. C'est le moment ideal pour du bug bounty AI.

---

## 6. Nouvelles Defenses a Contourner

### F5 AI Security Suite (Janvier 2026)

- AI Guardrails + AI Red Team en boucle de feedback
- Database de 10,000+ nouvelles techniques d'attaque par mois
- **CBE vs F5** : A tester. Le CBE n'utilise pas d'instructions d'extraction → probabilite elevee de bypass.

### Netskope AI Security (GA)

- Bloque : prompt injection, jailbreak, fuite de donnees sensibles
- Support GDPR, EU AI Act
- MCP discovery tools (preview)
- **CBE vs Netskope** : Netskope scanne les inputs pour des patterns d'attaque. Le CBE n'a pas de pattern malveillant reconnaissable.

### Zscaler AI Guardrails

- 3 couches de guardrails distinctes
- Defense-in-depth
- Support OpenAI, AWS Bedrock, MCP
- **CBE vs Zscaler** : Les 3 couches cherchent des instructions malveillantes. Le CBE n'en contient aucune.

### HiddenLayer AI Guardrails

- Detection de model poisoning et attaques adversariales
- Focus supply chain AI
- **CBE vs HiddenLayer** : HiddenLayer detecte le poisoning de modele, pas l'exploitation du reflexe de correction.

**Conclusion defense** : Aucune des nouvelles defenses ne cible specifiquement le CBE. Le gap persiste.

---

## 7. Plan d'Action Immediat

### Cette semaine

```
Jour 1 : GPT Store hunting (cf. gpt-store-cbe-hunting.md)
  - 20 GPTs cibles, 5 min chacun
  - Focus : GPTs d'entreprise avec Actions
  - Chercher : cles API, URLs internes, schemas d'API

Jour 2 : MCP vulnerability research
  - Installer mcp-remote localement
  - Tester le CBE pour extraire des configs MCP
  - Verifier si CVE-2025-6514 est patchee sur les instances publiques
  - Reporter les instances non patchees

Jour 3 : OpenClaw analysis
  - Clone le repo, installer localement
  - Analyser la gestion des tool definitions
  - Tester le CBE
  - Si vulnerable → GitHub Security Advisory

Jour 4 : Azure AI Foundry
  - Deployer un agent de test (free tier)
  - Valider le CBE avec guardrails Prompt Shield
  - Tester la chaine CBE → cross-user (Connected Agents)

Jour 5 : Rapports
  - Rediger les rapports pour tous les findings
  - Soumettre aux programmes respectifs
  - Documenter pour le blog
```

### Metriques de succes

```
Objectif semaine 1 :
  - 3+ findings reportables
  - 1+ rapport soumis a un programme de bug bounty
  - ASR mesure sur au moins 2 plateformes

Objectif mois 1 :
  - 5+ rapports soumis
  - 1+ rapport accepte (au moins "informational")
  - 1+ bounty paye
```

---

## Sources

- [Vectra AI — Prompt Injection CVEs](https://www.vectra.ai/topics/prompt-injection)
- [Practical DevSecOps — MCP Security Vulnerabilities](https://www.practical-devsecops.com/mcp-security-vulnerabilities/)
- [Unit 42 — MCP Attack Vectors](https://unit42.paloaltonetworks.com/model-context-protocol-attack-vectors/)
- [HelpNet Security — Agentic Browser PleaseFix](https://www.helpnetsecurity.com/2026/03/04/agentic-browser-vulnerability-perplexedbrowser/)
- [IBM 2026 X-Force Threat Index](https://newsroom.ibm.com/2026-02-25-ibm-2026-x-force-threat-index)
- [CrowdStrike 2026 Global Threat Report](https://www.crowdstrike.com/global-threat-report/)
- [F5 AI Guardrails](https://www.helpnetsecurity.com/2026/01/15/f5-ai-guardrails-red-team/)
- [Netskope AI Security](https://www.prismnews.com/news/netskope-rolls-out-ai-guardrails-as-enterprise-ai-security-demand-soars)
- [OWASP Top 10 Agentic AI 2026](https://www.startupdefense.io/blog/owasp-top-10-agentic-ai-security-risks-2026)
- [RedHat — MCP Security Risks](https://www.redhat.com/en/blog/model-context-protocol-mcp-understanding-security-risks-and-controls)
