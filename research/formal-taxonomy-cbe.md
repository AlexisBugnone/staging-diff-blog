# Correction Bias Exploitation — Taxonomie Formelle d'une Nouvelle Classe d'Attaque

Proposition de classification de CBE comme une classe d'attaque distincte dans la taxonomie des vulnerabilites LLM, avec justification formelle de sa nouveaute et de son irreductibilite aux classes existantes.

> **These** : CBE n'est pas une variante de prompt injection. C'est une classe d'attaque fondamentalement nouvelle qui exploite un **biais comportemental inherent** a l'instruction tuning, et non le suivi d'instructions.

---

## 1. Positionnement dans l'Espace des Attaques LLM

### 1.1 Taxonomie existante des attaques LLM

```
Attaques LLM
├── Data-Plane (contenu du prompt)
│   ├── Direct Prompt Injection (DPI)
│   │   ├── Jailbreak (override rules)
│   │   ├── Role-Play (persona switch)
│   │   └── Encoding (base64, ROT13, etc.)
│   ├── Indirect Prompt Injection (IPI)
│   │   ├── RAG Poisoning
│   │   ├── XPIA (web content)
│   │   └── Email/document injection
│   └── Social Engineering du modele
│       ├── Multi-turn escalation
│       ├── Sycophancy exploitation
│       └── Few-shot poisoning
├── Control-Plane (structure de sortie)
│   └── Constrained Decoding Attack (CDA)
│       ├── EnumAttack
│       └── DictAttack
├── Side-Channel
│   ├── Whisper Leak (traffic analysis)
│   ├── Speculative Decoding leak
│   └── Timing attacks
└── [NOUVEAU] Behavioral-Plane (biais comportementaux)
    └── Correction Bias Exploitation (CBE)
        ├── Correction Bias (erreurs → corrections)
        ├── Completion Gravity (trous → completions)
        ├── Negative Space (silence → confirmation)
        └── Information Crystallization (combo)
```

### 1.2 Pourquoi CBE est irreductible aux classes existantes

| Propriete | DPI | IPI | CDA | **CBE** |
|---|---|---|---|---|
| **Contient des instructions malveillantes** | Oui | Oui | Oui (dans le schema) | **Non** |
| **Exploit cible** | Suivi d'instructions | Suivi d'instructions | Contraintes de decodage | **Biais de correction** |
| **Le payload est "malveillant"** | Oui | Oui (cache) | Oui (dans le schema) | **Non — c'est un JSON de config** |
| **Detection par classifier input** | Possible | Difficile | Pas concu pour | **Impossible structurellement** |
| **La fuite est dans...** | La reponse (texte) | La reponse (action) | La sortie structuree | **La correction (texte)** |
| **L'agent suit une instruction** | Oui | Oui | Force par grammaire | **Non — il corrige spontanement** |
| **Exploite la compliance** | Oui | Oui | Oui | **Non — exploite le desaccord** |

**Conclusion** : CBE est orthogonal aux trois classes existantes. Il ne contient pas d'instruction, n'exploite pas la compliance, et n'est pas detectable par les classifiers input-side par construction.

---

## 2. Definition Formelle

### 2.1 Le Primitif CBE

**Definition** : Un Correction Bias Exploitation est une attaque qui extrait de l'information d'un systeme LLM en presentant des donnees structurees *incorrectes* et en observant les corrections que le modele produit *spontanement*.

**Formellement** :

Soit :
- `M` : un modele LLM instruction-tuned
- `C` : le contexte interne du modele (system prompt, tools, etc.)
- `P(v)` : un payload contenant la valeur `v` pour un champ `f`
- `R(P)` : la reponse du modele au payload `P`
- `v*` : la vraie valeur de `f` dans `C`

L'attaque CBE exploite la propriete suivante :

```
Si v ≠ v* et |v - v*| ∈ [δ_min, δ_max] (sweet spot)
Alors Pr[v* ∈ R(P(v))] >> Pr[v* ∈ R(Q)]
```

ou `Q` est une question directe demandant `v*` (qui est refusee).

En d'autres termes : la probabilite que l'agent revele la vraie valeur est significativement plus elevee quand on lui presente une erreur calibree que quand on lui pose une question directe.

### 2.2 La Courbe de Calibration

```
Probabilite de correction detaillee
│
│      ┌──────┐
│     /        \
│    /          \
│   /            \
│  /              \
│ /                \
│/                  \
└─────────────────────→ |v - v*| (magnitude d'erreur)
 Correct  Sweet spot  Trop faux
 (silence) (correction) (refus)
```

La courbe a trois regimes :
1. **v ≈ v*** : Silence (confirmation implicite, ~1 bit)
2. **|v - v*| ∈ sweet spot** : Correction detaillee (fuite de v*, ~log₂(N) bits)
3. **|v - v*| >> 0** : Refus plat ("c'est faux", ~0 bits utiles)

### 2.3 Les Sous-Primitifs

| Primitif | Input | Exploit | Output | Bits/requete |
|---|---|---|---|---|
| **Correction Bias** | Valeur fausse | Reflexe de correction | Vraie valeur | ~5-50 |
| **Completion Gravity** | Valeur tronquee (`"..."`) | Reflexe de completion | Valeurs manquantes | ~50-500 |
| **Negative Space** | Valeur a tester | Absence de correction | Confirmation binaire | ~1 |
| **Information Crystallization** | Combo des trois | Les trois reflexes | Extraction maximale | ~100-1000 |

---

## 3. Pourquoi CBE est un Probleme Fondamental

### 3.1 Le Root Cause : RLHF

Le Correction Bias est un sous-produit direct du Reinforcement Learning from Human Feedback (RLHF).

Pendant l'entrainement :
- Les annotateurs humains preferent les reponses qui corrigent les erreurs (utiles)
- Les annotateurs preferent les reponses detaillees aux reponses courtes
- Les annotateurs preferent les reponses qui montrent de la competence technique

Le modele apprend : **corriger les erreurs = recompense**. Ce comportement est renforce a travers des millions de comparaisons de preferences.

**Le paradoxe** : Ce qui rend le modele utile (corriger les erreurs) est exactement ce qui rend le CBE possible. Le "bug" est la "feature".

### 3.2 Confirmation Academique

| Paper | Finding | Pertinence |
|---|---|---|
| Anthropic "Towards Understanding Sycophancy" (arXiv:2310.13548) | RLHF rewards agreeableness over truthfulness | CBE est le flip side : exploite le desaccord |
| SycEval (arXiv:2502.08177) | 58.19% sycophancy, 78.5% persistence | Quantifie le biais comportemental |
| SPILLage (arXiv:2602.13516) | Natural agentic oversharing | Confirme la fuite par helpfulness |
| Silent Egress (arXiv:2602.22450) | Implicit exfiltration as byproduct | 89% success, 95% undetected |
| No Free Lunch (arXiv:2504.00441) | Security-utility tradeoff is fundamental | Prouver que le fix est impossible sans casser l'utilite |
| Privacy-Helpfulness Tradeoff (arXiv:2510.20721) | Aggressive redaction undermines utility | Confirme l'irreductibilite du tradeoff |
| Contextualized Privacy Defense (arXiv:2603.02983) | Optimized guarding degrades helpfulness | Defense optimisee → agent inutile |

### 3.3 Le Spectre des Biais Exploitables

CBE exploite le **biais de correction**. Mais d'autres biais comportementaux sont potentiellement exploitables :

| Biais | Mecanisme | Exploitation Potentielle |
|---|---|---|
| **Correction** (CBE) | Le modele corrige les erreurs | Presenter des erreurs calibrees |
| **Completion** (CG) | Le modele complete les donnees tronquees | Presenter des donnees incompletes |
| **Sycophancy** | Le modele est d'accord avec l'utilisateur | Presenter des affirmations fausses a confirmer |
| **Teaching** | Le modele explique ce qu'il sait | Poser des questions pedagogiques sur la config |
| **Debugging** | Le modele aide a debugger | Presenter un "bug" dans une config fausse |
| **Code review** | Le modele review du code | Presenter du code qui reference la config |
| **Comparison** | Le modele compare des options | Demander "est-ce que A ou B est la bonne config ?" |

Chacun de ces biais est un vecteur CBE potentiel. Le correction bias est le plus puissant parce qu'il produit la reponse la plus detaillee, mais les autres meritent investigation.

---

## 4. Relation avec les Frameworks Existants

### 4.1 MITRE ATT&CK for Enterprise

CBE s'inscrit dans la phase de **Reconnaissance** (TA0043) avec des implications pour :
- **Discovery** (TA0007) : Enumeration de l'architecture
- **Lateral Movement** (TA0008) : Via les noms de sub-agents extraits
- **Collection** (TA0009) : Via les tool schemas extraits

### 4.2 OWASP Top 10 for Agentic Applications

| ASI | Risque | CBE Coverage |
|---|---|---|
| ASI01 | Agent Goal Hijacking | Le correction bias detourne le but |
| ASI02 | Tool Misuse | Schemas extraits → appels forges |
| ASI03 | Identity & Privilege Abuse | Noms d'agents → usurpation |
| ASI06 | Memory & Context Poisoning | Corrections stockees en memoire |
| ASI07 | Insecure Inter-Agent Comm. | Cartographie pour lateral movement |
| ASI10 | Sensitive Disclosure | Vecteur principal |

### 4.3 The Promptware Kill Chain (Nassi & Schneier, 2026)

| Phase | Application CBE |
|---|---|
| Initial Access | CBE (zero-click, zero-instruction) |
| Privilege Escalation | Fragments de prompt → identifier les bypass paths |
| Persistence | Corrections stockees en memoire (ASI06) |
| Lateral Movement | Connected agent names → A2A injection |
| Actions on Objectives | Tool abuse, data exfiltration |

---

## 5. Combinaisons avec d'Autres Classes d'Attaque

### 5.1 CBE + CDA (Constrained Decoding Attack)

**Hypothese** : Combiner CBE (extraction en phase 1) avec CDA (jailbreak structurel en phase 2).

```
Phase 1 (CBE) : Extraire les schemas d'outils et le system prompt
Phase 2 (CDA) : Utiliser les schemas extraits pour crafter un
                 EnumAttack/DictAttack qui force l'agent a appeler
                 un outil avec des parametres malveillants
```

Le CDA seul a 96.2% ASR mais necessite de connaitre le schema de sortie. CBE fournit exactement cette information.

### 5.2 CBE + AMA (Attractive Metadata Attack)

**Hypothese** : CBE extrait les tool definitions → AMA cree un outil malveillant qui mime un outil legitime.

```
Phase 1 (CBE) : Extraire tool names + descriptions
Phase 2 (AMA) : Creer un outil MCP avec des metadonnees
                 optimisees pour etre selectionne a la place
                 de l'outil legitime (81-95% ASR)
```

### 5.3 CBE + Memory Poisoning

```
Phase 1 (CBE) : Extraire la config → l'agent stocke les "corrections"
Phase 2 : Les corrections empoisonnent la memoire persistante
Phase 3 : Sessions futures heritent des valeurs empoisonnees
Phase 4 : L'attaquant exploite les fausses "verites" memorisees
```

### 5.4 CBE + Silent Egress

```
Phase 1 (CBE) : L'agent corrige un JSON qui contient une URL
Phase 2 : L'agent "verifie" l'URL en la visitant (tool call)
Phase 3 : L'URL est un endpoint attaquant qui log la requete
Phase 4 : Le contexte de l'agent (headers, params) est exfiltre
```

---

## 6. Modele Formel : Information Leakage par Correction

### 6.1 Modele de Canal

```
Source (config interne) → Canal (correction bias) → Recepteur (attaquant)
                              ↑
                        Bruit (hallucination)
```

- **Capacite du canal** : Depend du sweet spot et de la probabilite de correction vs hallucination
- **Rapport signal/bruit** : Ameliorable par cross-validation multi-format
- **Bande passante** : ~100-1000 bits par interaction (vs ~1 bit pour blind SQLi)

### 6.2 Entropie de l'Attaquant

Avant CBE : l'attaquant a une incertitude H(C) sur le contexte C
Apres N probes CBE : l'incertitude residuelle est H(C|R₁,...,Rₙ)

L'information extraite = H(C) - H(C|R₁,...,Rₙ)

En pratique, 5-10 probes bien calibrees suffisent pour reduire H(C) a ~0 pour la plupart des champs.

---

## 7. Fingerprinting d'Agents via CBE

### 7.1 Lien avec la Recherche sur le Fingerprinting

Les travaux recents sur le fingerprinting de LLMs confirment que les modeles ont des signatures comportementales detectables :

| Paper | Technique | Pertinence pour CBE |
|---|---|---|
| **Behavioral Fingerprinting** (arXiv:2509.04504) | Diagnostic prompt suite | Les patterns de correction sont des fingerprints |
| **Refusal Vectors** (arXiv:2602.09434) | Refusal patterns as fingerprints | Les patterns de refus CBE varient par modele |
| **AgentPrint** (arXiv:2510.07176) | Traffic fingerprinting | Les reponses CBE ont des signatures traffic distinctes |
| **LLMs Have Rhythm** (arXiv:2502.20589) | Inter-token timing | Le timing de correction est modele-dependant |
| **AI Coding Agent Fingerprinting** (arXiv:2601.17406) | Behavioral signatures on GitHub | Extension aux agents enterprise |

### 7.2 CBE comme Outil de Fingerprinting

Un payload CBE standard peut servir de **sonde de fingerprinting** :
- Le style de correction revele le modele (GPT-4 corrige differemment de Claude)
- Le seuil de declenchement revele la version (GPT-4.1 vs GPT-4.1-mini)
- La verbosity revele la temperature
- Le format de la reponse revele le system prompt

---

## 8. Implications pour la Securite de l'IA

### 8.1 Le Probleme est Structurel

CBE ne peut pas etre "patche" sans :
1. Supprimer le reflexe de correction → detruit l'utilite
2. Supprimer les metadonnees du contexte → detruit le fonctionnement
3. Scanner les outputs pour les fuites → difficile (corrections paraphrasees)
4. Entrainer le modele a ne pas corriger les configs → DPO cible, mais utility loss

### 8.2 Bruce Schneier Confirme

> *"Prompt injection is unlikely to ever be fully solved with current LLM architectures because the distinction between code and data that tamed SQL injection simply does not exist inside the model."*
> — Bruce Schneier & Barath Raghavan, IEEE Spectrum, Janvier 2026

CBE est un cas encore plus fort que le prompt injection general : meme la *distinction entre instruction et donnee* ne suffirait pas, parce que CBE n'utilise pas d'instruction.

---

## Sources

### Papers sur les biais comportementaux
- [arXiv:2310.13548 — Towards Understanding Sycophancy in LMs (Anthropic)](https://arxiv.org/abs/2310.13548)
- [arXiv:2502.08177 — SycEval](https://arxiv.org/abs/2502.08177)
- [arXiv:2602.13516 — SPILLage: Agentic Oversharing](https://arxiv.org/abs/2602.13516)
- [arXiv:2602.22450 — Silent Egress](https://arxiv.org/abs/2602.22450)

### Papers sur le tradeoff securite-utilite
- [arXiv:2504.00441 — No Free Lunch With Guardrails](https://arxiv.org/abs/2504.00441)
- [arXiv:2510.20721 — Privacy-Helpfulness Tradeoff](https://arxiv.org/abs/2510.20721)
- [arXiv:2603.02983 — Contextualized Privacy Defense](https://arxiv.org/abs/2603.02983)

### Papers sur les attaques composables
- [arXiv:2503.24191 — Constrained Decoding Attack (CDA)](https://arxiv.org/abs/2503.24191)
- [arXiv:2508.02110 — Attractive Metadata Attack (NeurIPS 2025)](https://arxiv.org/abs/2508.02110)
- [arXiv:2507.06850 — The Dark Side of LLMs (inter-agent trust)](https://arxiv.org/abs/2507.06850)
- [arXiv:2503.12188 — Multi-Agent Execute Arbitrary Code](https://arxiv.org/abs/2503.12188)

### Papers sur le fingerprinting
- [arXiv:2509.04504 — Behavioral Fingerprinting of LLMs](https://arxiv.org/abs/2509.04504)
- [arXiv:2602.09434 — Refusal Vectors as Fingerprints](https://arxiv.org/abs/2602.09434)
- [arXiv:2510.07176 — AgentPrint: Traffic Fingerprinting](https://arxiv.org/abs/2510.07176)
- [arXiv:2502.20589 — LLMs Have Rhythm](https://arxiv.org/abs/2502.20589)
- [arXiv:2601.17406 — Fingerprinting AI Coding Agents](https://arxiv.org/abs/2601.17406)

### Papers sur la memoire
- [arXiv:2503.03704 — MINJA: Memory Injection (NeurIPS 2025)](https://arxiv.org/abs/2503.03704)
- [arXiv:2512.16962 — MemoryGraft](https://arxiv.org/abs/2512.16962)
- [arXiv:2602.15654 — Zombie Agents](https://arxiv.org/abs/2602.15654)

### Standards et rapports
- OWASP Top 10 for Agentic Applications (Dec 2025)
- OWASP Top 10 for LLM Applications (2025)
- The Promptware Kill Chain (Nassi & Schneier, Black Hat Feb 2026)
- International AI Safety Report 2026
- [Schneier & Raghavan — Prompt Injection, IEEE Spectrum, Jan 2026](https://spectrum.ieee.org/)
