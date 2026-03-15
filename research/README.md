# Correction Bias Exploitation — Research Hub

Recherche complémentaire au blog post [JSON Staging-Differential](../index.html).

## Contenu

### Fondamentaux
| Fichier | Description |
|---|---|
| `state-of-the-art.md` | Synthese complete de la litterature (mars 2026) |
| `azure-ai-foundry-attack-surface.md` | Surface d'attaque specifique Azure AI Foundry (35 elements) |
| `cross-platform-attack-surface.md` | **Comparaison Azure vs AWS Bedrock vs Google Vertex AI** |

### Chaines d'attaque (Phase 2)
| Fichier | Description |
|---|---|
| `phase2-tool-schema-weaponization.md` | De l'extraction de schemas a l'exploitation d'outils (654 lignes, 40+ citations) |
| `multi-agent-cascade-exploitation.md` | Mouvement lateral via correction bias en cascade multi-agents |
| `memory-poisoning-via-cbe.md` | Empoisonnement de memoire persistante via CBE (MINJA, MemoryGraft, Zombie Agents) |
| `blind-enumeration-protocol.md` | **Protocole formel** d'enumeration aveugle (analogie Blind SQLi) |

### Canaux et defenses
| Fichier | Description |
|---|---|
| `canaux-exfiltration-output-side.md` | 7 canaux d'exfiltration : steganographie, side-channels, markdown injection |
| `defense-evasion-analysis.md` | Pourquoi FIDES, CaMeL, SecAlign, StruQ echouent contre CBE |

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

## Decouvertes cles

- **CBE n'est publie nulle part** (recherche mars 2026) — technique entierement nouvelle
- **Cross-plateforme** : Azure, AWS Bedrock, Google Vertex AI partagent le meme gap (tool I/O non scanne)
- **100% des LLMs** sont vulnerables a l'exploitation inter-agents (arXiv:2507.06850)
- **Aucune defense actuelle** ne couvre la fuite d'information par helpfulness (these confirmee)
- **SPILLage** (arXiv:2602.13516) et **Silent Egress** (arXiv:2602.22450) confirment notre these independamment

## Licence

Recherche à usage éducatif et de responsible disclosure uniquement.
