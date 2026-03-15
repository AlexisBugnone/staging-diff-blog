# Correction Bias Exploitation — Research Hub

Recherche complémentaire au blog post [JSON Staging-Differential](../index.html).

## Contenu

### Fondamentaux
| Fichier | Description |
|---|---|
| `state-of-the-art.md` | Synthese complete de la litterature (mars 2026) |
| `formal-taxonomy-cbe.md` | **Taxonomie formelle** : CBE comme nouvelle classe d'attaque (4 plans, preuve d'irreductibilite) |
| `rlhf-root-cause-analysis.md` | **Cause racine** : pourquoi le RLHF rend le CBE inevitable (alignment tax, reward hacking inverse) |

### Surfaces d'attaque par plateforme
| Fichier | Description |
|---|---|
| `azure-ai-foundry-attack-surface.md` | Surface d'attaque specifique Azure AI Foundry (35 elements) |
| `cross-platform-attack-surface.md` | **Comparaison Azure vs AWS Bedrock vs Google Vertex AI** |
| `aws-bedrock-cbe-payloads.md` | **Payloads CBE calibres** pour AWS Bedrock (templates publics, 37+ variables, schemas OpenAPI) |

### Chaines d'attaque (Phase 2)
| Fichier | Description |
|---|---|
| `phase2-tool-schema-weaponization.md` | De l'extraction de schemas a l'exploitation d'outils (654 lignes, 40+ citations) |
| `cda-cbe-combination-attack.md` | **CDA + CBE** : Constrained Decoding Attack amplifie par CBE (96.2% ASR) |
| `multi-agent-cascade-exploitation.md` | Mouvement lateral via correction bias en cascade multi-agents |
| `memory-poisoning-via-cbe.md` | Empoisonnement de memoire persistante via CBE (MINJA, MemoryGraft, Zombie Agents) |
| `blind-enumeration-protocol.md` | **Protocole formel** d'enumeration aveugle (analogie Blind SQLi) |

### Reconnaissance et fingerprinting
| Fichier | Description |
|---|---|
| `behavioral-fingerprinting-cbe.md` | **Fingerprinting comportemental** : identification de modele/config via patterns de correction |

### Canaux et defenses
| Fichier | Description |
|---|---|
| `canaux-exfiltration-output-side.md` | 7 canaux d'exfiltration : steganographie, side-channels, markdown injection |
| `defense-evasion-analysis.md` | Pourquoi FIDES, CaMeL, SecAlign, StruQ echouent contre CBE |

### Incidents reels
| Fichier | Description |
|---|---|
| `real-world-incidents-cbe-parallels.md` | **6 incidents production** analyses (EchoLeak, Copilot RCE, Cursor, Slack AI, Asana MCP, Gemini) |

### Methodologie et disclosure
| Fichier | Description |
|---|---|
| `empirical-validation-methodology.md` | **Protocole experimental** pour valider le CBE en laboratoire (36,000 interactions, 6 modeles, 3 plateformes) |
| `responsible-disclosure-strategy.md` | **Strategie de disclosure** : programmes de bug bounty, taxonomies de severite, timeline |

## Techniques couvertes

1. **Correction Bias Exploitation** — donnees fausses → l'agent corrige → fuite
2. **Completion Gravity** — donnees incompletes → l'agent complete → fuite
3. **Information Crystallization** — combo correction + completion + silence
4. **Behavioral Differential** — faux historique → changelog → fuite
5. **Kill Chain multi-agents** — recon → cartographie → usurpation → action
6. **Schema-Guided Parameter Injection** — schemas extraits → appels d'outils forces
7. **Memory Poisoning via CBE** — corrections stockees en memoire → persistance cross-session
8. **Blind Agent Enumeration** — protocole formel d'extraction sans ground truth
9. **Steganographic Correction Bias** — correction + encodage steganographique
10. **Silent Egress via CBE** — exfiltration implicite comme sous-produit de la correction
11. **CDA + CBE Combination** — schemas extraits par CBE → Constrained Decoding Attack (96.2% ASR)
12. **Behavioral Fingerprinting** — patterns de correction comme empreinte du modele
13. **Reward Hacking Inverse** — l'attaquant exploite le reward signal RLHF pour forcer la correction
14. **AWS Bedrock Template Exploitation** — templates publics comme avantage de l'attaquant
15. **Alignment Tax Exploitation** — l'irreductibilite du compromis safety/helpfulness comme garantie d'attaque

## Decouvertes cles

- **CBE n'est publie nulle part** (recherche mars 2026) — technique entierement nouvelle
- **Cross-plateforme** : Azure, AWS Bedrock, Google Vertex AI partagent le meme gap (tool I/O non scanne)
- **100% des LLMs** sont vulnerables a l'exploitation inter-agents (arXiv:2507.06850)
- **Aucune defense actuelle** ne couvre la fuite d'information par helpfulness (these confirmee)
- **SPILLage** (arXiv:2602.13516) et **Silent Egress** (arXiv:2602.22450) confirment notre these independamment
- **L'alignment tax est partiellement irreductible** (arXiv:2603.00047) — le CBE exploite la composante intrinseque
- **AWS Bedrock est la plateforme la plus favorable** pour un attaquant CBE (templates publics, pre-processing desactive)
- **Le RLHF est la cause racine** — corriger = reward, le CBE est un reward hacking inverse
- **Le CBE est plus furtif que tous les incidents documentes** — zero instruction vs instructions cachees (EchoLeak, Slack, Copilot RCE)
- **6 CVEs de production** confirment que les agents AI sont exploitables en production (EchoLeak CVSS 9.3, Copilot RCE 7.8)

## Statistiques

- **18 documents de recherche** (~10,000+ lignes)
- **150+ citations academiques** (arXiv, NeurIPS, ICLR, Nature)
- **15 techniques** documentees
- **3 plateformes** analysees (Azure, AWS, Google)
- **Protocole experimental** de 36,000 interactions planifie

## Licence

Recherche à usage éducatif et de responsible disclosure uniquement.
