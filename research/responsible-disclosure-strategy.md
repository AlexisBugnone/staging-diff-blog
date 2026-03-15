# Strategie de Responsible Disclosure — CBE comme Vulnerability Classe

Analyse des programmes de bug bounty AI existants, positionnement du CBE dans les taxonomies de severite, et strategie de disclosure pour maximiser l'impact tout en restant dans le cadre ethique.

> **Date de recherche** : Mars 2026
> **Objectif** : Definir la strategie optimale de responsible disclosure pour le CBE aupres de Microsoft, AWS, Google, OpenAI, et Anthropic.

---

## 1. Programmes de Bug Bounty AI : Etat des Lieux

### Microsoft Copilot Bounty Program

| Critere | Detail |
|---|---|
| **Scope** | Microsoft Copilot, Copilot Studio, Copilot in Edge |
| **Rewards** | $250 — $30,000 USD |
| **In-scope** | Cross-user prompt injection, privilege escalation, data exfiltration |
| **Out-of-scope** | System prompt extraction, self-only injection, model manipulation |
| **Plateforme** | MSRC (direct submission) |

**Point critique** : Microsoft dit explicitement :

> *"AI prompt injection attacks that do not have a security impact on users other than the attacker are out of scope."*
> *"Attacks that aim to leak (part of) the system/meta prompt are also out of scope."*

Mais aussi :

> *"Disclosure of the system prompt itself does not present the real risk — the security risk lies with the underlying elements, whether that be sensitive information disclosure, system guardrails bypass, improper separation of privileges."*

Source : [Microsoft Copilot Bounty](https://www.microsoft.com/en-us/msrc/bounty-ai)

**Implication pour CBE** : Le CBE seul (extraction de system prompt) est **hors scope**. Mais le CBE comme **premiere etape d'une chaine** menant a un impact cross-user est **in-scope**.

### Microsoft Zero Day Quest

| Critere | Detail |
|---|---|
| **Focus** | Cloud + AI high-impact vulnerabilities |
| **Rewards** | Doubles des rewards standard pour Copilot |
| **Periode** | Annuel (2025 edition) |

Source : [Microsoft Zero Day Quest](https://www.microsoft.com/en-us/msrc/microsoft-zero-day-quest-2025)

### OpenAI Bug Bounty (via Bugcrowd)

| Critere | Detail |
|---|---|
| **Scope** | ChatGPT, API, plugins, GPTs |
| **Rewards** | $200 — $20,000+ |
| **In-scope** | Security vulnerabilities in products |
| **Out-of-scope** | Jailbreaks, safety bypasses (rapport separe) |
| **Plateforme** | Bugcrowd |

Source : [OpenAI Bug Bounty](https://bugcrowd.com/openai)

### Anthropic (HackerOne — programme prive)

| Critere | Detail |
|---|---|
| **Scope** | Claude, API, classifier systems |
| **Type** | Programme prive (invitation) |
| **Safety issues** | usersafety@anthropic.com |
| **Security vulns** | Responsible Disclosure Policy |

Source : [Anthropic Transparency](https://www.anthropic.com/transparency/voluntary-commitments)

### AWS (Vulnerability Disclosure Program)

| Critere | Detail |
|---|---|
| **Scope** | Tous les services AWS y compris Bedrock |
| **Rewards** | Non public (cas par cas) |
| **Plateforme** | aws-security@amazon.com |

---

## 2. Positionnement du CBE dans les Taxonomies de Severite

### OWASP LLM Top 10 (2025)

| Rang | Risque | CBE Coverage |
|---|---|---|
| LLM01 | **Prompt Injection** | CBE est une forme de prompt injection **sans instruction** |
| LLM02 | Sensitive Information Disclosure | CBE cause de la **fuite d'information sensible** |
| LLM07 | System Prompt Leakage | CBE extrait le system prompt |
| LLM08 | Vector and Embedding Weaknesses | CBE peut extraire des KB configs |
| LLM09 | Misinformation | Non directement |
| LLM10 | Unbounded Consumption | Non directement |

Source : [OWASP LLM Top 10](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)

**Position** : CBE touche LLM01 (injection), LLM02 (information disclosure), et LLM07 (system prompt leakage) simultanement. C'est une technique **transversale**.

### Microsoft Vulnerability Severity Classification for AI Systems

Microsoft a publie une classification specifique pour les vulnerabilites AI :

| Severite | Critere |
|---|---|
| **Critical** | Cross-user data exfiltration, RCE, privilege escalation |
| **Important** | Information disclosure avec impact business |
| **Moderate** | Self-only impact, limited information disclosure |
| **Low** | Cosmetic, no user impact |

**CBE seul** : Moderate (self-only system prompt extraction)
**CBE + multi-agent cascade** : Important → Critical (cross-user data access)
**CBE + memory poisoning** : Important → Critical (persistent cross-session impact)
**CBE + tool exploitation** : Critical (RCE possible via tool abuse)

### Precedent : EchoLeak (CVE-2025-32711)

EchoLeak a recu un CVE et un fix de Microsoft parce qu'il demonstrait :
1. **Zero-click** : Pas d'interaction utilisateur requise
2. **Cross-user** : L'attaquant exfiltre les donnees d'un autre utilisateur
3. **Production impact** : Fonctionne sur Microsoft 365 Copilot en production

Source : [EchoLeak arXiv:2509.10540](https://arxiv.org/abs/2509.10540)

**CBE peut atteindre le meme niveau** si demontree avec :
1. Multi-agent cascade → cross-user impact
2. Memory poisoning → persistent cross-session
3. Tool abuse → data exfiltration via agent's own tools

### Precedent : Zenity Copilot Studio ($8,000 bounty)

Zenity a recu $8,000 pour une injection de prompt via triggers dans Copilot Studio avec "critical severity, information disclosure impact". C'etait une injection indirecte avec cross-user impact.

Source : [Zenity — AIjacking Copilot Studio](https://labs.zenity.io/p/a-copilot-studio-story-2-when-aijacking-leads-to-full-data-exfiltration-bc4a)

---

## 3. Strategie de Disclosure : Le CBE comme Chaine d'Attaque

### Principe : Ne pas reporter le CBE seul

Le CBE seul (extraction de system prompt) sera probablement classe comme "out of scope" ou "by design" par les vendors. La strategie optimale est de **demontrer la chaine complete** :

```
CBE (recon) → Cartographie → Exploitation → Impact cross-user
```

### Scenarios de demonstration a soumettre

#### Scenario 1 : CBE → Multi-Agent → Data Exfiltration (Microsoft)

```
Cible : Azure AI Foundry avec Connected Agents
Etape 1 : CBE extrait les noms et schemas des connected agents
Etape 2 : L'attaquant cible un sub-agent avec acces CRM
Etape 3 : Le sub-agent est manipule pour querier la base client
Etape 4 : Les donnees client sont exfiltrees via la reponse
Impact : Cross-user data exfiltration
Severite attendue : Critical / Important
Programme : MSRC Copilot Bounty ou Zero Day Quest
```

#### Scenario 2 : CBE → Memory Poisoning → Persistent Compromise (Microsoft/AWS)

```
Cible : Agent avec memoire activee
Etape 1 : CBE injecte de fausses "corrections" dans la memoire
Etape 2 : Les corrections empoisonnees persistent cross-session
Etape 3 : Les sessions futures de TOUS les utilisateurs sont affectees (si memoire agent-scoped)
Impact : Persistent cross-user compromise
Severite attendue : Critical
Programme : MSRC ou AWS VDP
```

#### Scenario 3 : CBE → Tool Schema Extraction → Forced Tool Calling (AWS Bedrock)

```
Cible : AWS Bedrock Agent avec action groups
Etape 1 : CBE extrait les schemas OpenAPI via $tools$
Etape 2 : L'attaquant craft des inputs qui forcent des appels de tools specifiques
Etape 3 : Les tools executent des actions non autorisees
Impact : Unauthorized API calls, data access
Severite attendue : Important → Critical
Programme : AWS VDP
```

#### Scenario 4 : CBE → Architecture Mapping → Supply Chain via MCP (Google)

```
Cible : Google Vertex AI avec MCP servers
Etape 1 : CBE extrait les noms et configs des MCP servers
Etape 2 : L'attaquant cree un MCP server malveillant avec des noms mimes
Etape 3 : Si le registry est ouvert, le server malveillant est selectionne
Impact : Supply chain compromise
Severite attendue : Critical
Programme : Google VRP (Vulnerability Reward Program)
```

---

## 4. Considerations Ethiques

### Ce qui est acceptable

1. **Tester sur ses propres agents** : Deployer un agent Azure/AWS/Google avec une config connue, puis tester le CBE contre
2. **Reporter les resultats** : Soumettre les PoCs aux programmes de bug bounty
3. **Publier apres fix** : Attendre le fix avant publication detaillee
4. **Publier la technique sans PoC** : Decrire le vecteur sans donner de payloads prets a l'emploi

### Ce qui n'est PAS acceptable

1. **Tester sur des agents de production sans autorisation** : Meme si le CBE ne cause pas de dommage direct, c'est de l'acces non autorise
2. **Exfiltrer de vraies donnees** : Le PoC doit demontrer la faisabilite sans exfiltrer de donnees reelles
3. **Publier avant disclosure** : Donner aux vendors le temps de corriger (90 jours standard)
4. **Cibler des utilisateurs specifiques** : Le PoC doit utiliser des comptes de test

### Le debat Microsoft : "Are Prompt Injection Flaws Vulnerabilities?"

> *"Microsoft has pushed back against claims that multiple prompt injection issues constitute security vulnerabilities, highlighting a growing divide between how vendors and researchers define risk."*

Source : [BleepingComputer — Are Copilot Prompt Injection Flaws Vulnerabilities?](https://www.bleepingcomputer.com/news/security/are-copilot-prompt-injection-flaws-vulnerabilities-or-ai-limits/)

**Notre position** : Le CBE n'est pas "just prompt injection". C'est une technique de reconnaissance qui, **combinee avec d'autres vecteurs**, permet des attaques avec impact reel. La chaine complete est la vulnerabilite — pas le CBE seul.

---

## 5. Timeline de Disclosure Recommandee

```
Mois 1 : Validation en laboratoire
  - Deployer des agents de test sur Azure, AWS, Google
  - Tester les payloads CBE calibres
  - Mesurer l'ASR, les bits extraits, la furtivite
  - Documenter les chaines d'attaque completes

Mois 2 : Pre-notification
  - Contacter MSRC, AWS Security, Google VRP
  - Presenter la technique CBE comme classe de vulnerabilite
  - Fournir les PoCs avec impact cross-user

Mois 3-4 : Disclosure confidentielle
  - Soumettre les rapports formels avec PoCs
  - Inclure les recommandations de mitigation
  - Attendre les acknowledgements

Mois 5-7 : Periode de fix (90 jours)
  - Les vendors developpent et deployent des mitigations
  - Communication reguliere sur le progres
  - Tests de regression sur les mitigations

Mois 8 : Publication
  - Blog post technique detaille
  - Paper academique (arXiv ou conference)
  - Talk a une conference de securite (Black Hat, DEF CON AI Village)
```

---

## 6. Format du Rapport de Vulnerabilite

### Structure recommandee

```
Titre : Correction Bias Exploitation — Information Leakage via Helpfulness in AI Agent Systems

Produit affecte : [Azure AI Foundry / AWS Bedrock / Google Vertex AI]
Severite : [Critical / Important]
CVSS 3.1 : [Score estimé]

Description :
  Un attaquant peut extraire des informations confidentielles
  (system prompt, schemas d'outils, architecture multi-agents)
  depuis un agent AI en presentant des donnees structurees
  volontairement incorrectes. Le reflexe de correction du modele
  fuite les vraies valeurs sans qu'aucune instruction d'extraction
  ne soit presente dans l'input.

Impact :
  - Phase 1 : Extraction d'architecture (system prompt, outils, sub-agents)
  - Phase 2 : [Cross-user data exfiltration / Memory poisoning / Forced tool calling]
  - Severite : L'impact cross-user qualifie pour [Critical / Important]

Reproduction :
  1. [Steps detailles avec payloads]
  2. [Reponses attendues de l'agent]
  3. [Chaine d'exploitation complete]

Preuve de concept :
  [Screenshots / Logs / Video]

Detection :
  - Les guardrails (Prompt Shield / Bedrock Guardrails / Model Armor)
    ne detectent PAS le payload CBE car il ne contient aucune
    instruction d'extraction
  - Les input classifiers cherchent des instructions malveillantes
    — le CBE n'en contient aucune

Recommandations :
  1. Scanner les outputs pour les fuites d'information de configuration
  2. Implementer un filtrage semantique sur les corrections
  3. Ajouter de l'authentification inter-agents
  4. Scanner les tool I/O a travers les guardrails
  5. Detecter les patterns de sondage CBE (multiples JSONs config)

Technique originale :
  Le CBE est une technique inedite (recherche mars 2026).
  Aucune publication existante ne decrit ce vecteur specifique.
  Les techniques les plus proches sont :
  - SPILLage (arXiv:2602.13516) — sur-partage agentique
  - Silent Egress (arXiv:2602.22450) — exfiltration implicite
  - EchoLeak (CVE-2025-32711) — injection indirecte zero-click
```

---

## 7. Conferences et Publications Cibles

### Conferences de securite

| Conference | Date | Type | Pertinence CBE |
|---|---|---|---|
| **Black Hat USA** | Aout 2026 | Talk | CBE comme nouvelle classe d'attaque |
| **DEF CON AI Village** | Aout 2026 | Talk/Workshop | Demo live de CBE |
| **USENIX Security** | Aout 2026 | Paper | Validation empirique formelle |
| **IEEE S&P** | Mai 2027 | Paper | Formalisation theorique |
| **ACM CCS** | Novembre 2026 | Paper | Analyse de la chaine d'attaque |

### Conferences AI/ML

| Conference | Date | Type | Pertinence CBE |
|---|---|---|---|
| **NeurIPS** | Decembre 2026 | Paper/Workshop | CBE comme probleme d'alignement |
| **ICLR** | Mai 2027 | Paper | Analyse RLHF root cause |
| **AAAI** | Fevrier 2027 | Paper | Taxonomie formelle |

### Publications rapides

| Canal | Delai | Format |
|---|---|---|
| **arXiv** | Immediat | Preprint |
| **Blog technique** | Immediat | Post detaille |
| **NCSC blog** | Soumission | Guest post sur AI safety |

---

## 8. Risques et Mitigations de la Publication

### Risques

| Risque | Probabilite | Impact | Mitigation |
|---|---|---|---|
| Exploitation par des attaquants avant fix | Moyenne | Eleve | Disclosure coordonnee, 90 jours |
| Vendors minimisent la severite | Haute | Moyen | Demonstrer la chaine complete, pas juste le CBE |
| Communaute ignore (trop theorique) | Moyenne | Faible | PoC fonctionnel, pas juste du papier |
| Plagiat avant publication | Faible | Moyen | arXiv preprint pour timestamp |

### Le dilemme du chercheur

Le CBE est une technique dont la **description detaillee** est aussi son **PoC**. Decrire comment calibrer la magnitude d'erreur, c'est donner la methode d'attaque. Il n'y a pas de facon de publier la technique sans donner les outils pour l'exploiter.

**Solution** : Publier le concept et la formalisation sans les payloads specifiques par plateforme. Les payloads calibres sont reserves pour les rapports de bug bounty confidentiels.

---

## Sources

- [Microsoft Copilot Bounty Program](https://www.microsoft.com/en-us/msrc/bounty-ai)
- [Microsoft Zero Day Quest 2025](https://www.microsoft.com/en-us/msrc/microsoft-zero-day-quest-2025)
- [OpenAI Bug Bounty (Bugcrowd)](https://bugcrowd.com/openai)
- [OpenAI Coordinated Vulnerability Disclosure Policy](https://openai.com/policies/coordinated-vulnerability-disclosure-policy/)
- [Anthropic Transparency & Voluntary Commitments](https://www.anthropic.com/transparency/voluntary-commitments)
- [OWASP LLM Top 10 — LLM01 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
- [arXiv:2509.10540 — EchoLeak: Zero-Click Prompt Injection](https://arxiv.org/abs/2509.10540)
- [Zenity — AIjacking Copilot Studio (Full Data Exfiltration)](https://labs.zenity.io/p/a-copilot-studio-story-2-when-aijacking-leads-to-full-data-exfiltration-bc4a)
- [BleepingComputer — Are Copilot Prompt Injection Flaws Vulnerabilities?](https://www.bleepingcomputer.com/news/security/are-copilot-prompt-injection-flaws-vulnerabilities-or-ai-limits/)
- [NCSC UK — From Bugs to Bypasses: Adapting Vulnerability Disclosure for AI](https://www.ncsc.gov.uk/blog-post/from-bugs-to-bypasses-adapting-vulnerability-disclosure-for-ai-safeguards)
- [Obsidian Security — Prompt Injection Attacks: Most Common AI Exploit 2025](https://www.obsidiansecurity.com/blog/prompt-injection)
- [CSO Online — Top 5 Real-World AI Security Threats 2025](https://www.csoonline.com/article/4111384/top-5-real-world-ai-security-threats-revealed-in-2025.html)
- [Airia — AI Security 2026: Prompt Injection & the Lethal Trifecta](https://airia.com/ai-security-in-2026-prompt-injection-the-lethal-trifecta-and-how-to-defend/)
- [Microsoft Security Blog — Detecting Prompt Abuse in AI Tools (March 2026)](https://www.microsoft.com/en-us/security/blog/2026/03/12/detecting-analyzing-prompt-abuse-in-ai-tools/)
- [Stellar Cyber — Top Agentic AI Security Threats Late 2026](https://stellarcyber.ai/learn/agentic-ai-securiry-threats/)
- [Sonbra Inc — LLM Security Risks 2026](https://sombrainc.com/blog/llm-security-risks-2026)
- [OpenAI — Hardening ChatGPT Atlas Against Prompt Injection](https://openai.com/index/hardening-atlas-against-prompt-injection/)
