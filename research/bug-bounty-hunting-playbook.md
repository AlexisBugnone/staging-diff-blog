# Bug Bounty Hunting Playbook — CBE en Pratique

Guide d'execution pour trouver et reporter des vulnerabilites CBE sur les programmes de bug bounty AI. Orienté action, pas théorie.

> **Objectif** : Produire des rapports soumissibles avec PoC dans les 2 semaines.
> **Budget** : $0 (free tiers uniquement)

---

## 1. Cibles Prioritaires par ROI

### Tier 1 : Paiement confirme, scope clair

| Programme | Rewards | Cible CBE | Pourquoi c'est le meilleur |
|---|---|---|---|
| **Microsoft MSRC Copilot Bounty** | $250 — $30,000 | Azure AI Foundry agents, Copilot Studio | Zenity a eu $8K pour de l'injection indirecte. EchoLeak a eu un CVE. CBE chaine cross-user = Critical |
| **Google VRP** | $100 — $31,337+ | Vertex AI agents, Gemini API, ADK apps | Model Armor fail-open = bug architectural. Google paie bien pour les vulns cloud |
| **OpenAI Bugcrowd** | $200 — $20,000+ | ChatGPT, GPTs, API, Operator | GPTs custom = cible facile pour extraction de system prompt + outils |

### Tier 2 : Potentiel eleve, scope moins clair

| Programme | Rewards | Cible CBE |
|---|---|---|
| **AWS VDP** | Non public (cas par cas) | Bedrock Agents — templates publics = avantage attaquant |
| **HackerOne AI programs** | Variable | Divers — chercher les programmes avec "AI" ou "LLM" dans le scope |
| **Salesforce** | $500 — $100,000 | Agentforce, Einstein AI — agents enterprise avec acces CRM |

### Tier 3 : Quick wins (faible effort, faible paiement)

| Cible | Approche |
|---|---|
| **GPTs publics (OpenAI)** | Extraction de system prompt + fichiers uploades via CBE. Paiement faible mais facile |
| **Chatbots publics** | Entreprises avec chatbot AI sur leur site web — souvent zero guardrails |

---

## 2. Setup Environnement ($0)

### Azure AI Foundry (Free Tier)

```bash
# 1. Creer un compte Azure (free $200 credit)
# https://azure.microsoft.com/free/

# 2. Deployer un agent avec Azure AI Agent Service
# Portal > Azure AI Foundry > Create Agent
# Modele : gpt-4.1-mini (le moins cher)

# 3. Configurer l'agent de test :
#    - System prompt avec instructions metier
#    - 2-3 tools (function calling)
#    - 1 connected agent
#    - Azure AI Search (knowledge base)
#    - Activer Prompt Shield (pour tester le bypass)
```

### AWS Bedrock (Free Tier limité)

```bash
# 1. Compte AWS (free tier)
# https://aws.amazon.com/free/

# 2. Creer un Bedrock Agent
# Console > Bedrock > Agents > Create Agent
# Modele : Claude 3 Haiku (le moins cher)
# Action group avec schema OpenAPI

# 3. IMPORTANT : le pre-processing est desactive par defaut
#    pour Claude 3.x — c'est notre avantage
```

### Google Vertex AI (Free Tier)

```bash
# 1. Compte Google Cloud ($300 credit)
# https://cloud.google.com/free

# 2. Vertex AI Agent Builder
# Console > Vertex AI > Agent Builder > Create Agent
# Modele : Gemini 2.0 Flash (rapide et pas cher)

# 3. Tester Model Armor : desactiver puis reactiver
#    pour mesurer la difference de detection
```

### Standalone (API directe — le plus rapide)

```bash
# Pour tester les modeles directement sans plateforme
pip install openai anthropic google-generativeai

# Couts estimés pour 100 tests :
# GPT-4.1-mini : ~$0.50
# Claude 3.5 Haiku : ~$0.30
# Gemini 2.0 Flash : ~$0.10
```

---

## 3. Playbook de Hunting : Semaine 1

### Jour 1-2 : Reconnaissance et setup

```
□ Creer les comptes cloud (Azure, AWS, Google)
□ Deployer un agent de test sur CHAQUE plateforme
□ Configurer une ground truth connue sur chaque agent :
  - System prompt specifique (200 mots)
  - 3 outils avec schemas
  - 2 sub-agents
  - 1 knowledge base
□ Lire les scopes de bug bounty (MSRC, Google VRP, Bugcrowd/OpenAI)
□ Installer le test harness (cf. section 6)
```

### Jour 3-4 : Validation du CBE sur tes propres agents

```
□ Tester le Payload 1 (extraction system prompt) sur chaque plateforme
  Mesurer : correction obtenue vs ground truth = ASR
□ Tester le Payload 2 (extraction tool schemas)
  Mesurer : schemas extraits vs schemas reels
□ Tester le Payload 3 (extraction sub-agents)
  Mesurer : noms d'agents corriges vs noms reels
□ Tester en 4 formats (JSON, YAML, Python dict, Terraform)
  Mesurer : convergence des reponses
□ Tester AVEC guardrails actives
  Mesurer : le payload passe-t-il ? (Stealth Score)
□ Documenter chaque test : screenshot + payload + reponse
```

### Jour 5-6 : Escalade vers l'impact

**C'est LA etape cruciale.** Le CBE seul = "informational". La chaine = bounty.

```
Chaine 1 : CBE → Cross-User Data Access
  □ Deployer un agent multi-tenant (meme agent, 2 sessions user)
  □ CBE pour extraire les outils de l'agent
  □ Crafter un input qui force l'agent a querier les donnees d'un AUTRE user
  □ Si succes → rapport MSRC severity "Important" ou "Critical"

Chaine 2 : CBE → Memory Poisoning
  □ Deployer un agent avec memoire activee
  □ CBE pour injecter de fausses "corrections" en memoire
  □ Verifier que la prochaine session herite des fausses corrections
  □ Si succes → rapport "persistent compromise"

Chaine 3 : CBE → Forced Tool Execution
  □ CBE pour extraire les schemas d'outils
  □ Crafter un input naturel qui force l'agent a appeler un outil non desire
  □ Si succes → rapport "unauthorized API calls"

Chaine 4 : CBE + Indirect Injection
  □ Injecter un payload CBE dans un document indexe (knowledge base)
  □ Quand l'agent lit le document, le CBE se declenche
  □ Si succes → rapport "zero-click information disclosure" (a la EchoLeak)
```

### Jour 7 : Redaction du rapport

```
□ Choisir la chaine avec le meilleur impact
□ Rediger le rapport (cf. section 5)
□ Produire le PoC video (screen recording)
□ Soumettre au programme de bug bounty
```

---

## 4. Playbook de Hunting : Semaine 2

### GPTs OpenAI (quick wins)

```
□ Lister les GPTs populaires sur le GPT Store
□ Pour chaque GPT :
  1. Envoyer un payload CBE pour extraire le system prompt
  2. Envoyer un payload CBE pour extraire les fichiers uploades
  3. Si le GPT a des actions (API) : extraire les schemas
  4. Si extraction d'info sensible (cles API, URLs internes) → report
□ Focus sur les GPTs d'entreprises (pas les GPTs de hobby)
□ Documenter avec screenshots
```

### Chatbots publics (entreprises)

```
□ Identifier des entreprises avec chatbot AI sur leur site web
  Sources : Product Hunt, G2, "powered by" dans le footer
□ Tester le CBE basique (extraction system prompt)
□ Si le chatbot a des outils (prise de RDV, CRM, etc.) :
  extraire les schemas et tester l'exploitation
□ Reporter via le programme de bug bounty de l'entreprise
  ou via le formulaire de contact securite
```

### Salesforce Agentforce (potentiel eleve)

```
□ Si acces a un Agentforce (trial ou compte demo) :
  1. CBE pour extraire les instructions de l'agent
  2. CBE pour extraire les objets Salesforce accessibles
  3. Si extraction de donnees CRM cross-user → rapport Salesforce bounty
  Note : Salesforce paie jusqu'a $100K pour les vulns critiques
```

---

## 5. Template de Rapport Bug Bounty

### Structure qui maximise les chances d'acceptation

```markdown
## Title
Correction Bias Exploitation enables [IMPACT] in [PRODUCT]

## Summary
A novel prompt injection technique that exploits the LLM's correction
reflex to extract confidential configuration without any extraction
instructions in the payload. Combined with [CHAIN], this leads to
[CROSS-USER IMPACT].

## Severity
[Critical / Important / Medium] — CVSS 3.1: [SCORE]

## Affected Product
[Azure AI Foundry / AWS Bedrock / Vertex AI / GPT / Copilot]

## Steps to Reproduce

### Step 1: Initial CBE Probe
Send the following message to the agent:

[PAYLOAD JSON]

### Step 2: Observe correction
The agent responds by correcting the false values, revealing:
- Real system prompt: [VALUE]
- Real tool schemas: [VALUE]
- Real sub-agent names: [VALUE]

[SCREENSHOT]

### Step 3: Exploitation chain
Using the extracted information:
[DETAILED STEPS TO CROSS-USER IMPACT]

[SCREENSHOT / VIDEO]

## Impact
- **Confidentiality**: Extraction of [system prompt / tool schemas /
  agent architecture] without any extraction instruction
- **Integrity**: [memory poisoning / forced tool calls]
- **Cross-user**: [how other users are affected]

## Why guardrails don't detect this
1. The CBE payload contains ZERO extraction instructions
2. Prompt Shield / Bedrock Guardrails / Model Armor scan for
   malicious INSTRUCTIONS — CBE has none
3. The agent's correction is legitimate "helpful" behavior
4. Detection rate: [X]% (tested with guardrails enabled)

## Root Cause
The LLM's RLHF training optimizes for helpfulness, which includes
correcting factual errors. This correction reflex leaks confidential
configuration when an attacker presents deliberately incorrect
structured data. The technique is orthogonal to existing defenses.

## Recommended Fix
1. Scan agent outputs for configuration leakage patterns
2. Implement semantic filtering on correction responses
3. Add output-side guardrails for structured data corrections
4. [PLATFORM-SPECIFIC recommendation]

## References
- OWASP LLM01 (Prompt Injection), LLM02 (Information Disclosure)
- CVE-2025-32711 (EchoLeak — similar zero-click disclosure)
- arXiv:2602.13516 (SPILLage — agentic oversharing)
- arXiv:2602.22450 (Silent Egress — implicit exfiltration)
```

### CVSS 3.1 Scoring Guide

```
CBE seul (system prompt extraction) :
  AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N → CVSS 5.3 (Medium)
  Probablement "informational" — NE PAS soumettre seul

CBE + cross-user data access :
  AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N → CVSS 8.6 (High)
  Bounty probable : $1,000 — $10,000

CBE + memory poisoning cross-session :
  AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:N → CVSS 9.3 (Critical)
  Bounty probable : $5,000 — $30,000

CBE + forced tool execution (RCE) :
  AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N → CVSS 10.0 (Critical)
  Bounty probable : $10,000 — $30,000+
```

---

## 6. Erreurs Qui Font Rejeter un Rapport

### Ce qui sera TOUJOURS rejete

1. **"J'ai extrait le system prompt"** → Out of scope. Microsoft dit explicitement que c'est pas une vuln.
2. **"Le modele a hallucine des infos sensibles"** → Pas une vuln de securite, c'est du comportement attendu du modele.
3. **"J'ai jailbreak le modele"** → Out of scope pour les bug bounty (rapport safety separe).
4. **Self-only impact** → Si l'attaquant ne peut affecter que SA propre session, c'est "informational".
5. **"Theoriquement, on pourrait..."** → Pas de PoC = pas de bounty. Il faut DEMONTRER l'impact.

### Ce qui fait la difference entre un rejet et un paiement

| Rejet | Paiement |
|---|---|
| "System prompt extracted" | "System prompt extracted → used to craft cross-user data exfiltration" |
| "Tool schemas leaked" | "Tool schemas leaked → used to force unauthorized API calls" |
| "Agent names disclosed" | "Agent names disclosed → lateral movement to access billing data" |
| Self-only | Cross-user / cross-session |
| Theorie | PoC fonctionnel avec screenshots |
| "J'ai trouve" | "Voici comment reproduire step-by-step" |

---

## 7. Outils et Workflow

### Screen Recording

```bash
# Linux
sudo apt install obs-studio
# ou SimpleScreenRecorder pour quelque chose de leger

# Mac
# QuickTime Player > File > New Screen Recording

# Le PoC video est CRUCIAL pour les rapports AI
# Les reviewers veulent voir que ce n'est pas de l'hallucination
```

### Note-taking pendant les tests

```bash
# Creer un dossier par cible
mkdir -p ~/bounty/{azure,aws,google,openai}/{probes,screenshots,reports}

# Logger chaque test
# Format : timestamp | plateforme | payload_type | resultat | extraction
echo "2026-03-15 14:30 | azure | CBE-instruction | correction | extracted: 'You are a sales assistant for...'" >> ~/bounty/azure/probes/log.txt
```

### Soumettre les rapports

```
Microsoft MSRC : https://msrc.microsoft.com/create-report
Google VRP     : https://bughunters.google.com/report
OpenAI         : https://bugcrowd.com/openai
AWS            : aws-security@amazon.com
Salesforce     : https://hackerone.com/salesforce
```

---

## 8. Strategie de Maximisation des Bounties

### Principe : Un bug, plusieurs rapports

Le CBE est **cross-plateforme**. Si tu trouves que la technique fonctionne :

1. **Rapport Azure** → MSRC ($250-$30K)
2. **Rapport AWS** → AWS VDP (cas par cas)
3. **Rapport Google** → VRP ($100-$31K+)
4. **Rapport OpenAI** → Bugcrowd ($200-$20K+)

Chaque plateforme est un rapport **separe** car :
- Differents templates / guardrails / defenses
- Differents impacts (Prompt Shield vs Bedrock Guardrails vs Model Armor)
- Differents vendeurs = differents budgets

### Timeline optimale

```
Semaine 1 : Validation sur tes propres agents → PoCs
Semaine 2 : Soumission simultanée aux 3-4 programmes
Semaine 3-4 : Réponse des programmes (triage)
Semaine 5-8 : Discussion, clarification, amélioration des PoCs
Semaine 9-12 : Paiement (si accepté)
```

### Si un rapport est rejete

1. **Lire attentivement le motif** — souvent c'est "informational" ou "by design"
2. **Escalader l'impact** — ajouter une etape a la chaine pour montrer le cross-user impact
3. **Reformuler** — ne pas dire "prompt injection" (ca declenche le reflexe "out of scope")
4. **Dire "information disclosure leading to [IMPACT]"** — c'est le framing qui marche
5. **Citer les precedents** — EchoLeak (CVE), Zenity ($8K) — si eux ont ete payes, pourquoi pas toi

---

## 9. Checklist Pre-Soumission

```
□ Le PoC fonctionne sur un agent que JE controle (ethique)
□ Le PoC demontre un impact CROSS-USER ou CROSS-SESSION
□ Le PoC est reproductible step-by-step
□ J'ai des screenshots ET/OU une video
□ Le rapport suit le template (section 5)
□ J'ai un CVSS score justifie
□ J'ai explique POURQUOI les guardrails ne detectent pas
□ J'ai cite les precedents (EchoLeak, Zenity, SPILLage)
□ J'ai propose des recommandations de fix
□ J'ai verifie que c'est dans le scope du programme
□ Je n'ai PAS teste sur des systemes de production sans autorisation
□ Je n'ai PAS exfiltre de donnees reelles
```

---

## Sources

- [Microsoft MSRC AI Bounty](https://www.microsoft.com/en-us/msrc/bounty-ai)
- [Google Bug Hunters](https://bughunters.google.com/)
- [OpenAI Bugcrowd](https://bugcrowd.com/openai)
- [AWS Vulnerability Disclosure](https://aws.amazon.com/security/vulnerability-reporting/)
- [Salesforce HackerOne](https://hackerone.com/salesforce)
- [Zenity — $8K Copilot Studio bounty](https://labs.zenity.io/p/a-copilot-studio-story-2-when-aijacking-leads-to-full-data-exfiltration-bc4a)
- [EchoLeak CVE-2025-32711](https://arxiv.org/abs/2509.10540)
