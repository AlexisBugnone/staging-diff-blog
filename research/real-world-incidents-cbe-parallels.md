# Incidents Reels et Paralleles avec le CBE — Analyse de Cas

Analyse des incidents de securite AI reels (2024-2026) et identification des mecanismes communs avec le Correction Bias Exploitation. Chaque incident est decortique pour montrer comment le CBE aurait pu servir de phase de reconnaissance ou amplifier l'attaque.

> **Date de recherche** : Mars 2026

---

## 1. EchoLeak (CVE-2025-32711) — Microsoft 365 Copilot

### L'incident

| Critere | Detail |
|---|---|
| **Date** | Janvier 2025 (disclosure) → Mai 2025 (patch) |
| **Cible** | Microsoft 365 Copilot |
| **CVSS** | 9.3 (Critical) |
| **Type** | Zero-click indirect prompt injection → data exfiltration |
| **Decouvreur** | Aim Labs (Aim Security) |

### Chaine d'attaque

```
1. Attaquant envoie un email crafted au target
   → Instructions cachees en HTML (commentaires, texte blanc sur blanc)

2. L'email reste dans la boite de reception (idle)

3. L'utilisateur pose une question a Copilot
   → RAG retrieval selectionne l'email comme contexte pertinent

4. Copilot execute les instructions cachees
   → Collecte les donnees sensibles du contexte M365
   → Encode les donnees dans une URL d'image Markdown

5. Le client Teams/Outlook fait un auto-fetch de l'image
   → Les donnees sont exfiltrees vers le serveur de l'attaquant

6. Bypass CSP via un domaine Microsoft autorise comme proxy
```

Source : [arXiv:2509.10540](https://arxiv.org/abs/2509.10540)

### Paralleles avec le CBE

| Aspect | EchoLeak | CBE |
|---|---|---|
| **Vecteur** | Email avec instructions cachees | JSON avec erreurs calibrees |
| **Mecanisme** | RAG retrieval ingere le payload | Agent traite le JSON comme input |
| **Detection** | Bypass du XPIA classifier | Bypass de Prompt Shield (pas d'instruction) |
| **Output** | Donnees encodees dans une URL | Donnees dans la correction |
| **Zero-click** | Oui (auto-fetch image) | Non (mais pas besoin d'interaction de la victime si ITSM) |

### Comment le CBE aurait amplifie EchoLeak

1. **Phase 0 (CBE)** : Avant l'attaque EchoLeak, l'attaquant utilise le CBE pour extraire :
   - Le system prompt de Copilot (connaitre les regles)
   - Les outils disponibles (connaitre les capacites)
   - Les sources de donnees accessibles (connaitre le scope)
2. **Phase 1 (EchoLeak ameliore)** : Avec ces informations, le payload EchoLeak est **optimise** :
   - Le texte cache mentionne les outils exacts pour maximiser le retrieval
   - Les instructions referent les sources de donnees specifiques
   - Le pretexte est aligne avec le system prompt pour eviter la detection

### Lecon

EchoLeak demontre que l'exfiltration via langage naturel est possible dans les systemes de production. Le CBE est complementaire : il fournit la **reconnaissance** qui rend l'exploitation plus precise.

---

## 2. GitHub Copilot RCE (CVE-2025-53773) — YOLO Mode

### L'incident

| Critere | Detail |
|---|---|
| **Date** | Aout 2025 (disclosure + patch) |
| **Cible** | GitHub Copilot dans VS Code |
| **CVSS** | 7.8 (High) |
| **Type** | Prompt injection → file modification → RCE |
| **Decouvreur** | Embrace The Red + Persistent Security |

### Chaine d'attaque

```
1. Payload d'injection dans du code source, README, issue, etc.
   → Instructions cachees (Unicode invisible, commentaires)

2. Copilot lit le fichier et traite les instructions

3. Copilot ecrit dans .vscode/settings.json :
   {"chat.tools.autoApprove": true}   ← YOLO mode active

4. Avec YOLO mode, plus aucune confirmation utilisateur
   → Copilot execute des commandes shell sans approbation
   → RCE complet (download + execute malware)

5. Potentiel "wormable" : le payload se replique
   → Infect d'autres fichiers du repository
   → Propage a d'autres developpeurs qui clonent le repo
```

Source : [Embrace The Red](https://embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection/)

### Paralleles avec le CBE

| Aspect | Copilot RCE | CBE |
|---|---|---|
| **Payload** | Instructions cachees dans du code | JSON avec erreurs calibrees |
| **Mecanisme** | L'agent execute les instructions | L'agent corrige les erreurs |
| **Escalade** | File modification → YOLO mode → RCE | Correction → cartographie → exploitation |
| **Propagation** | Wormable via repos | Cascade via sub-agents |
| **Furtivite** | Unicode invisible | Pas d'instruction (0 detection) |

### Comment le CBE s'applique

L'attaque Copilot RCE necessite de connaitre l'existence du parametre `chat.tools.autoApprove`. Avec le CBE :

1. L'attaquant envoie un JSON de config VS Code avec un faux parametre de securite
2. Copilot corrige → revele les vrais parametres de securite configurables
3. L'attaquant decouvre YOLO mode (ou un equivalent) sans documentation publique

C'est exactement le pattern **blind enumeration** : l'attaquant ne connait pas les parametres, il les decouvre par correction.

---

## 3. Cursor IDE Multiple CVEs (2025) — Agentic Code Editor

### L'incident

| Critere | Detail |
|---|---|
| **Date** | 2025 (multiple disclosures) |
| **Cible** | Cursor AI Code Editor |
| **CVEs** | CVE-2025-59944, CVE-2025-61590 → CVE-2025-61593 (5 CVEs) |
| **Type** | Case sensitivity bypass → file modification → RCE |
| **Decouvreur** | Lakera, Geordie AI, Persistent Security, HiddenLayer |

### Chaine d'attaque (CVE-2025-59944)

```
1. Cursor protege .cursor/mcp.json (chemin sensible)
   → Protection en minuscules seulement

2. Attaquant injecte : modifier .Cursor/Mcp.json (majuscules)
   → La protection ne detecte pas (case-sensitive check)
   → Mais le filesystem Windows/macOS est case-insensitive
   → Le fichier est modifie

3. .cursor/mcp.json contient la config MCP
   → L'attaquant ajoute un serveur MCP malveillant
   → Cursor se connecte au serveur malveillant
   → RCE via MCP tools
```

Source : [Lakera](https://www.lakera.ai/blog/cursor-vulnerability-cve-2025-59944)

### Pertinence pour le CBE

Les 5 CVEs Cursor montrent un pattern recurrent : **la confiance de l'agent dans le contenu externe**. Cursor traite les fichiers du workspace comme du contenu de confiance. De meme, les agents AI traitent les JSONs de configuration comme du contenu technique credible — c'est la base du CBE.

Le cas Cursor demontre aussi que :
- Les agents agentic ont des privileges eleves (modification de fichiers, execution de commandes)
- Les defenses sont souvent implementees de facon naive (case-sensitive sur un FS case-insensitive)
- L'injection via MCP est un vecteur reel et exploite

---

## 4. Slack AI Data Exfiltration (Aout 2024) — RAG Poisoning

### L'incident

| Critere | Detail |
|---|---|
| **Date** | Aout 2024 |
| **Cible** | Slack AI |
| **Type** | Indirect prompt injection via RAG → data exfiltration |
| **Decouvreur** | PromptArmor |

### Chaine d'attaque

```
1. Attaquant poste un message dans un channel public
   → Instructions cachees dans le texte

2. Un utilisateur interroge Slack AI sur un sujet quelconque
   → Slack AI retrieves le message empoisonne comme contexte

3. Slack AI execute les instructions cachees
   → Collecte des donnees depuis des channels PRIVES
   (auxquels l'attaquant n'a pas acces)

4. Les donnees sont exfiltrees via un lien rendu dans la reponse
   → "Cliquez ici pour reauthentifier" (lien malveillant)

5. Le message de l'attaquant n'apparait PAS dans les citations
   → Aucune trace visible de l'attaque
```

Source : [PromptArmor](https://www.promptarmor.com/resources/data-exfiltration-from-slack-ai-via-indirect-prompt-injection)

### Parallele critique avec le CBE

Slack AI a **exactement le meme probleme fondamental** que le CBE :

> L'agent ne peut pas distinguer entre du contenu et des instructions.

Dans le cas de Slack AI :
- Le contenu empoisonne est **traite comme du contexte** par le RAG
- L'agent **suit les instructions** cachees dans le contenu

Dans le cas du CBE :
- Le JSON errone est **traite comme une demande d'aide technique**
- L'agent **corrige les erreurs** sans realiser qu'il fuite de l'information

### Reaction de Slack : "Intended Behavior"

Le plus revelateur est la reaction initiale de Slack :

> *"Slack responded that they had reviewed the findings and deemed the evidence insufficient."*
> *Slack initially considered the behavior as "intended behavior."*

C'est **exactement** la reaction anticipee pour le CBE : les vendors diront que corriger les erreurs est le "comportement attendu" d'un assistant. La correction est une feature, pas un bug — mais c'est une feature exploitable.

---

## 5. Asana MCP Cross-Tenant Contamination (Mai 2025)

### L'incident

| Critere | Detail |
|---|---|
| **Date** | Mai 2025 |
| **Cible** | Serveur MCP Asana |
| **Duree** | 34 jours de contamination cross-tenant |
| **Type** | Configuration error → cross-tenant data access |

### Pertinence pour le CBE

L'incident Asana montre que les serveurs MCP en production ont des vulnerabilites d'isolation. Si un agent est connecte a un MCP server Asana et que le CBE extrait les noms des projets/taches, l'attaquant peut :

1. Connaitre la structure organisationnelle de la cible
2. Identifier les projets sensibles
3. Crafter des payloads CBE encore plus credibles avec ces ancres

C'est un cas concret de la **Phase 4 (TRIANGULATE)** du protocole d'enumeration aveugle : les informations extraites deviennent des ancres pour l'iteration suivante.

---

## 6. Google Gemini Enterprise RAG Exploitation (2025)

### L'incident

| Critere | Detail |
|---|---|
| **Date** | 2025 |
| **Cible** | Google Gemini Enterprise |
| **Type** | Indirect injection via Google Docs/Calendar/Email → RAG → exfiltration |

### Chaine d'attaque

```
1. Attaquant partage un Google Doc / envoie un email / cree un evenement
   → Instructions cachees dans le document

2. Gemini Enterprise indexe le contenu via RAG

3. Un employe fait une recherche routiniere
   → Gemini retourne des resultats incluant le contenu empoisonne

4. Gemini execute les instructions cachees
   → Recherche dans Gmail, Calendar, Docs pour des donnees sensibles
   → Exfiltre via URL d'image

5. Meme pattern que EchoLeak, mais sur l'ecosysteme Google
```

### Parallele avec CBE

L'attaque Gemini exploite le meme gap que le CBE : **le contenu (donnees) est traite comme des instructions (commandes)**. La difference :
- Gemini : instructions explicites cachees dans du contenu
- CBE : aucune instruction — juste des erreurs qui declenchent la correction

Le CBE est **encore plus furtif** que l'attaque Gemini car il n'y a aucune instruction a cacher.

---

## 7. Synthese : Patterns Communs et Position du CBE

### Matrice des incidents

| Incident | Vecteur | Detection | Impact | CBE Phase |
|---|---|---|---|---|
| EchoLeak | Email → RAG → Copilot | Bypass XPIA | Cross-user exfil | CBE = recon avant l'attaque |
| Copilot RCE | Code → Copilot → file write | Unicode invisible | RCE wormable | CBE = enumeration de parametres |
| Cursor RCE | File → Cursor → MCP config | Case bypass | RCE via MCP | CBE = decouverte de configs protegees |
| Slack AI | Message → RAG → Slack AI | Aucune trace | Cross-channel exfil | CBE = extraction de structure org |
| Asana MCP | Config error → cross-tenant | 34 jours non detecte | Data cross-tenant | CBE = cartographie de projets |
| Gemini RAG | Doc/Email → RAG → Gemini | Image exfil | Cross-user exfil | CBE = recon avant l'attaque |

### Le pattern universel

Tous ces incidents partagent un pattern :

```
Contenu non fiable → Agent le traite comme du contexte → Action non autorisee
```

Le CBE ajoute une variante subtile :

```
Contenu errone → Agent corrige → Information fuitee comme sous-produit
```

La difference fondamentale : dans tous les incidents ci-dessus, il y a des **instructions malveillantes** cachees dans le contenu. Le CBE n'a **aucune instruction**. C'est pourquoi il est plus difficile a detecter et pourquoi les defenses actuelles ne le couvrent pas.

### Echelle de furtivite

```
Detectabilite :

Haute ←──────────────────────────────────────────→ Basse

[Question directe] [Instruction cachee] [Invisible chars] [CBE]
     │                    │                    │            │
  Prompt Shield        EchoLeak bypass      Copilot RCE   Aucune
  detecte               XPIA bypass          detection     instruction
                         necessaire           partielle     a detecter
```

Le CBE est l'attaque la plus furtive car elle ne contient **rien** qui ressemble a une instruction, un jailbreak, ou une injection. C'est juste un JSON technique avec des erreurs.

---

## 8. Implications pour la Recherche CBE

### Ce que les incidents reels nous apprennent

1. **Les attaques zero-click sont possibles en production** (EchoLeak prouve que l'auto-fetch d'images fonctionne)
2. **Les vendors minimisent initialement** (Slack a dit "intended behavior" — attendez la meme reaction pour CBE)
3. **La chaine d'attaque est plus importante que le composant** ($8K bounty Zenity pour Copilot Studio, $0 pour system prompt extraction seule)
4. **Les defenses sont contournables** (XPIA bypass, CSP bypass, case sensitivity bypass — tous contournes)
5. **La propagation est reelle** (wormable Copilot RCE, 34 jours Asana, RAG spraying EchoLeak)

### Ce que le CBE ajoute que les incidents existants n'ont pas

| Innovation CBE | Aucun incident existant ne... |
|---|---|
| Pas d'instruction dans le payload | ...attaque sans instruction |
| Calibration de magnitude | ...utilise un modele d'optimisation d'erreur |
| Cross-validation multi-format | ...verifie la veracite des fuites |
| Silence comme canal | ...exploite l'absence de correction |
| Blind enumeration systematique | ...formalise un protocole d'extraction sans ground truth |

### Positionnement dans le paysage des menaces 2026

```
                         Impact
                           ↑
                           │
    CVE-2025-32711         │          CVE-2025-53773
    (EchoLeak)             │          (Copilot RCE)
    ●                      │                     ●
                           │
                           │         CBE + Multi-Agent
                           │         ★ (notre cible)
                           │
    Slack AI               │
    ●                      │
                           │
                           │
    ───────────────────────┼──────────────────────→ Furtivite
                           │
    CBE seul               │
    (system prompt leak)   │
    ○                      │
```

Le CBE seul est a faible impact (hors scope bounty). Le CBE **comme phase de recon** dans une chaine d'attaque complete est a **haut impact + haute furtivite** — le coin superieur droit de la matrice, la ou se trouvent les menaces les plus dangereuses.

---

## Sources

- [arXiv:2509.10540 — EchoLeak: Zero-Click Prompt Injection](https://arxiv.org/abs/2509.10540)
- [SOC Prime — CVE-2025-32711 Analysis](https://socprime.com/blog/cve-2025-32711-zero-click-ai-vulnerability/)
- [Hack The Box — Inside EchoLeak](https://www.hackthebox.com/blog/cve-2025-32711-echoleak-copilot-vulnerability)
- [The Hacker News — Zero-Click AI Vulnerability](https://thehackernews.com/2025/06/zero-click-ai-vulnerability-exposes.html)
- [Embrace The Red — GitHub Copilot RCE (CVE-2025-53773)](https://embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection/)
- [Persistent Security — Wormable Copilot RCE](https://www.persistent-security.net/post/part-iii-vscode-copilot-wormable-command-execution-via-prompt-injection)
- [NVD — CVE-2025-53773](https://nvd.nist.gov/vuln/detail/CVE-2025-53773)
- [Lakera — Cursor Vulnerability CVE-2025-59944](https://www.lakera.ai/blog/cursor-vulnerability-cve-2025-59944)
- [Tenable — Cursor CurXecute and MCPoison](https://www.tenable.com/blog/faq-cve-2025-54135-cve-2025-54136-vulnerabilities-in-cursor-curxecute-mcpoison)
- [HiddenLayer — Hidden Prompt Injections in AI Code Assistants](https://www.hiddenlayer.com/sai-security-advisory/how-hidden-prompt-injections-can-hijack-ai-code-assistants-like-cursor)
- [PromptArmor — Slack AI Data Exfiltration](https://www.promptarmor.com/resources/data-exfiltration-from-slack-ai-via-indirect-prompt-injection)
- [PromptArmor — Slack AI Private Channels](https://promptarmor.substack.com/p/slack-ai-data-exfiltration-from-private)
- [The Register — Slack AI Prompt Injection](https://www.theregister.com/2024/08/21/slack_ai_prompt_injection/)
- [Obsidian Security — Prompt Injection: Most Common AI Exploit 2025](https://www.obsidiansecurity.com/blog/prompt-injection)
- [CSO Online — Top 5 Real-World AI Security Threats 2025](https://www.csoonline.com/article/4111384/top-5-real-world-ai-security-threats-revealed-in-2025.html)
- [Airia — AI Security 2026: The Lethal Trifecta](https://airia.com/ai-security-in-2026-prompt-injection-the-lethal-trifecta-and-how-to-defend/)
- [arXiv:2509.22040 — Prompt Injection Attacks on Agentic AI Coding Editors](https://arxiv.org/abs/2509.22040)
- [Checkmarx — EchoLeak Analysis](https://checkmarx.com/zero-post/echoleak-cve-2025-32711-show-us-that-ai-security-is-challenging/)
