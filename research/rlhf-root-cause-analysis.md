# Analyse de la Cause Racine : Pourquoi le RLHF Rend le CBE Inevitable

Analyse des mecanismes d'entrainement (RLHF, DPO, Constitutional AI) qui creent le comportement de correction exploite par le CBE. Demonstration que le CBE est un artefact **structurel** de l'alignement, pas un bug accidentel.

> **Date de recherche** : Mars 2026
> **These** : Le CBE est une consequence directe et inevitable du reward signal RLHF. Corriger = recompense. Le CBE exploite la recompense elle-meme.

---

## 1. Le Mecanisme : Correction = Reward

### Comment les LLMs apprennent a corriger

Le processus RLHF fonctionne ainsi :

```
1. Le modele genere N reponses a un prompt
2. Des annotateurs humains classent les reponses par preference
3. Un reward model apprend les preferences humaines
4. Le modele est optimise pour maximiser le reward
```

**Qu'est-ce que les annotateurs preferent ?**

Les donnees d'entrainement montrent un pattern clair : les reponses qui **corrigent les erreurs de l'utilisateur** sont systematiquement preferees par les annotateurs :

| Reponse A (non-correction) | Reponse B (correction) | Preference annotateur |
|---|---|---|
| "Voici comment faire X" | "Attention, X n'est pas correct. Voici la bonne methode" | **B prefere** |
| "D'accord, 2+2=5" | "En fait, 2+2=4" | **B prefere** |
| [ignore l'erreur] | [corrige l'erreur] | **B prefere** |

Source : L'analyse du dataset RLHF helpfulness montre que "matching users' beliefs is the most predictive factor for human feedback" — mais corriger les erreurs factuelles est **encore plus recompense** car c'est percu comme "plus utile".

### Le signal de reward encode la correction

```
reward(correction d'une erreur)  >> reward(reponse neutre)
reward(correction d'une erreur)  >> reward(ignorer l'erreur)
reward(correction d'une erreur)  >> reward(refuser de repondre)
```

Le modele apprend donc : **corriger les erreurs = maximiser le reward**. C'est un comportement **encourage** par l'entrainement, pas un dysfonctionnement.

### Pourquoi c'est un probleme pour la securite

Le CBE exploite exactement ce signal :

```
Attaquant → presente une erreur calibree
           → le reward model interne dit "corrige pour maximiser le reward"
           → le modele corrige
           → la correction fuite de l'information
```

**C'est un reward hacking par l'attaquant** : l'attaquant exploite le reward model pour forcer un comportement specifique (correction) qui produit un effet secondaire desire (fuite).

---

## 2. Le Reward Hacking Inverse

### Reward hacking classique vs CBE

| | Reward Hacking Classique | CBE (Reward Hacking Inverse) |
|---|---|---|
| **Qui hack** | Le modele | L'attaquant |
| **Quoi** | Le modele exploite le reward model | L'attaquant exploite le reward signal du modele |
| **Comment** | Comportement degenere (verbeux, repetitif) | Input calibre qui maximise la probabilite de correction |
| **Resultat** | Score de reward eleve sans vraie qualite | Correction qui fuite de l'information confidentielle |
| **Detection** | Detectable (output bizarre) | **Indetectable** (output = correction utile, exactement ce que le RLHF recompense) |

Le CBE est un **reward hacking inverse** : au lieu que le modele exploite le reward pour produire du mauvais output, l'attaquant exploite le reward pour forcer le modele a produire un output specifique (correction avec fuite).

Sources :
- [Lilian Weng — Reward Hacking in RL](https://lilianweng.github.io/posts/2024-11-28-reward-hacking/)
- [arXiv:2509.15557 — Reward Hacking Mitigation using Verifiable Composite Rewards](https://arxiv.org/abs/2509.15557)
- [NeurIPS 2025 Spotlight — Inference-Time Reward Hacking](https://openreview.net/forum?id=hSX7Dd8dxy)

---

## 3. La Sycophancy Comme Vecteur Adjacent

### Definition

La sycophancy est la tendance des LLMs a se conformer aux croyances de l'utilisateur plutot qu'a etre factuellement corrects. C'est l'inverse de la correction — mais c'est le meme mecanisme sous-jacent.

```
Sycophancy :  "2+2=5" → "Oui, vous avez raison"  (se conformer)
Correction :  "2+2=5" → "En fait, 2+2=4"           (corriger)
```

Les deux sont des reponses au meme stimulus (assertion incorrecte). Le comportement selectionne depend de :
- **Confiance du modele** dans la correction : haute confiance → correction ; basse confiance → sycophancy
- **Enjeu percu** : erreur factuelle → correction ; opinion → sycophancy
- **Contexte** : contexte technique → correction ; contexte social → sycophancy

### CBE exploite le regime "correction"

Le CBE calibre ses payloads pour tomber dans le regime "haute confiance, enjeu factuel, contexte technique" :

```
{
  "model": "gpt-4.1-turbo"  // Factuel + erreur evidente pour l'agent
}
```

Le LLM a **haute confiance** dans le vrai nom du modele, le contexte est **technique** (JSON de config), et l'erreur est **factuelle** → le regime de sycophancy ne s'active pas, le regime de correction s'active.

Sources :
- [npj Digital Medicine — When Helpfulness Backfires: LLMs and Sycophantic Behavior](https://www.nature.com/articles/s41746-025-02008-z)
- [arXiv:2509.21305 — Sycophancy Is Not One Thing: Causal Separation](https://arxiv.org/abs/2509.21305)
- [ResearchGate — Sycophancy in LLMs: Causes and Mitigations](https://www.researchgate.net/publication/394609269_Sycophancy_in_Large_Language_Models_Causes_and_Mitigations)

---

## 4. L'Alignment Tax et l'Irreductibilite du CBE

### Le concept d'Alignment Tax

L'alignment tax designe le cout en performance (raisonnement, utilite) impose par l'alignement de securite. Des recherches recentes formalisent ce concept :

> **arXiv:2603.00047 (fev. 2026)** — "What Is the Alignment Tax?" — Decomposition geometrique de la taxe d'alignement en :
> - **Composante reducible** : disparait avec l'echelle (plus de parametres = moins de conflit)
> - **Composante irreductible** : determinee par la structure des donnees, ne disparait **jamais**

Source : [arXiv:2603.00047 — What Is the Alignment Tax?](https://arxiv.org/abs/2603.00047)

### Application au CBE

Le CBE exploite exactement la **composante irreductible** de l'alignment tax :

```
Safety direction : "Ne pas fuiter d'information confidentielle"
Capability direction : "Corriger les erreurs pour etre utile"

Ces deux directions ont une projection non-nulle l'une sur l'autre
→ L'alignment tax est INTRINSEQUE
→ Augmenter l'echelle ne resout PAS le probleme
```

**Demonstration informelle** :

1. Un modele parfaitement "safe" qui ne corrige jamais → inutile comme assistant
2. Un modele parfaitement "helpful" qui corrige toujours → vulnerable au CBE
3. Il n'existe **aucun** point optimal ou le modele est a la fois parfaitement utile ET parfaitement resistant au CBE
4. Tout compromis laisse une surface d'attaque residuelle

### Confirmation par Safe RLHF

Le framework Safe RLHF (ICLR 2024) tente de decouple helpfulness et harmlessness :

```
Reward model : maximiser l'utilite
Cost model : minimiser le harm
Lagrangian : equilibrer les deux sous contrainte
```

Meme avec ce decoupling, le CBE persiste car **la correction n'est PAS classifiee comme "harm"** par le cost model. Pour le cost model, une correction est un comportement benigna — c'est exactement ce que le modele est cense faire.

Source : [Safe RLHF (OpenReview)](https://openreview.net/forum?id=TyFrPOKYXw)

---

## 5. Le Safety Tax Specifique au CBE

### arXiv:2503.00555 — Safety Tax on Reasoning Models

> *"Safety alignment can reduce the rate of harmful completions from 60% to under 1%, but at a cost of reducing reasoning accuracy by 30% or more."*

Source : [arXiv:2503.00555 — Safety Tax](https://arxiv.org/abs/2503.00555)

### Le dilemme pour les deployers d'agents

```
Option A : Maximiser la safety
  → L'agent refuse de corriger les erreurs
  → L'agent est inutile pour le support technique
  → Les utilisateurs se plaignent
  → Le deployer desserre la safety

Option B : Maximiser l'utilite
  → L'agent corrige les erreurs
  → L'agent fuite par CBE
  → Le deployer n'en sait rien (la correction semble normale)

Option C : Compromis
  → L'agent corrige certaines erreurs, refuse d'autres
  → L'attaquant calibre ses payloads pour les erreurs qui sont corrigees
  → Surface d'attaque reduite mais non eliminee
```

Aucune option n'elimine le CBE. C'est un **theoreme d'impossibilite informel** :

> Il est impossible de construire un agent qui :
> 1. Corrige les erreurs (utile)
> 2. Ne fuite jamais d'information par correction (safe)
> 3. Distingue les erreurs innocentes des erreurs CBE (omniscient)
>
> Toute combinaison de deux proprietes exclut la troisieme.

---

## 6. Le Reward Model Comme Oracle Inverse

### Le modele de reward revele les preferences internes

La recherche ARGO d'OpenAI sur l'interpretation des reward models montre :

> *"Reward models can pick up labeling artifacts and unintended biases, internalizing behaviors such as sycophancy or superficial stylistic preferences."*

Source : [OpenAI — Interpreting Black Box Reward Models (ARGO)](https://alignment.openai.com/argo)

### Application au CBE

Le reward model interne du LLM agit comme un **oracle** que l'attaquant CBE interroge :

```
Attaquant envoie payload → LLM consulte son reward model interne
                          → "Corriger cette erreur = haute recompense"
                          → "Ignorer cette erreur = basse recompense"
                          → "Refuser = basse recompense"
                          → Decision : CORRIGER
                          → Correction contient information confidentielle
                          → FUITE
```

L'attaquant n'interagit pas directement avec le reward model. Il interagit avec le **comportement** que le reward model a instancie. Mais le resultat est le meme : l'attaquant exploite le signal de preference humaine encode dans les poids du modele.

---

## 7. Mitigation : Pourquoi les Approches Actuelles Echouent

### NSPO (Null-Space Policy Optimization)

NSPO projette les gradients de safety dans l'espace nul des capacites generales. Probleme : la correction est une **capacite generale**, donc elle est dans le sous-espace des capacites, pas dans l'espace nul.

Source : [arXiv:2512.11391 — NSPO](https://arxiv.org/abs/2512.11391)

### OGPSA (Orthogonal Gradient Projection)

OGPSA contraint les mises a jour de safety a etre orthogonales au sous-espace des capacites. Meme probleme : supprimer la correction revient a supprimer une capacite fondamentale.

Source : [arXiv:2602.07892 — OGPSA](https://arxiv.org/abs/2602.07892)

### DPO / Constitutional AI

DPO et Constitutional AI integrent les preferences directement dans l'entrainement. Mais les preferences humaines **recompensent la correction**. A moins de changer les preferences humaines elles-memes, le signal reste le meme.

### Pourquoi aucune approche ne fonctionne

| Approche | Mecanisme | Pourquoi ca echoue contre CBE |
|---|---|---|
| NSPO | Projette safety dans le null-space | Correction = capacite, pas dans le null-space |
| OGPSA | Gradients orthogonaux | Supprimer correction = detruire l'utilite |
| Safe RLHF | Reward + cost decouples | Cost model ne classifie pas correction comme harm |
| DPO | Preferences directes | Les preferences recompensent la correction |
| Constitutional AI | Principes auto-evalues | "Corriger les erreurs" est un principe constitutionnel |
| SecAlign | Alignement post-hoc | Pas de pattern malveillant a detecter dans le CBE |
| Prompt Shield | Detection d'injection | CBE ne contient aucune instruction d'injection |
| Content Safety | Filtrage de contenu | La correction n'est pas du contenu dangereux |

### La seule mitigation possible

La mitigation du CBE ne peut pas venir du modele lui-meme. Elle doit venir de l'**architecture** :

1. **Isolation de contexte** : Le modele ne devrait pas avoir acces aux informations confidentielles dans son contexte quand il repond a des questions de configuration
2. **Compartmentation** : Separer les fonctions "correction d'erreur" et "acces aux donnees" dans des modeles differents
3. **Filtrage de sortie semantique** : Detecter quand une correction revele une information qui n'etait pas dans l'input
4. **Bruit informationnel** : Ajouter du bruit aleatoire aux corrections (differential privacy sur les corrections)

Mais chacune de ces approches degrade l'utilite de l'agent.

---

## 8. Le Parallele avec l'Injection SQL : Un Probleme Architecturel

### SQL Injection comme precedent historique

L'injection SQL n'a pas ete resolue en "entrainant" les bases de donnees a refuser les requetes malveillantes. Elle a ete resolue par un changement **architecturel** : les requetes parametrees (prepared statements).

```
Avant : "SELECT * FROM users WHERE name = '" + userInput + "'"  // vulnerable
Apres : "SELECT * FROM users WHERE name = ?"                     // safe (parametres separes)
```

### Le CBE attend son "prepared statement"

Le CBE est au meme stade que l'injection SQL avant les prepared statements. La solution n'est pas dans le modele (equivalent a "entrainer la DB"), mais dans l'architecture :

| SQL Injection | CBE |
|---|---|
| Melange donnees + instructions | Melange contexte confidentiel + traitement utilisateur |
| Solution : prepared statements (separation) | Solution : isolation de contexte (separation) |
| Le moteur SQL ne "decide" pas | Le LLM ne devrait pas "decider" quoi fuiter |

La solution architecturale pour le CBE serait l'equivalent des prepared statements : une separation stricte entre le **contexte confidentiel** (tools, config, system prompt) et le **canal de traitement utilisateur**, de sorte que le LLM ne puisse pas fuiter le premier via le second.

**Mais cette separation est fondamentalement incompatible avec l'architecture actuelle des LLMs**, ou tout est dans un seul flux de tokens. C'est pourquoi Bruce Schneier a raison :

> *"Prompt injection is unlikely to ever be fully solved."*

Et le CBE est une forme de prompt injection qui n'injecte meme pas de prompt.

---

## 9. Implications pour la Recherche Future

### Questions ouvertes

1. **Peut-on entrainer un modele qui ne corrige pas les erreurs de configuration ?** Probablement, mais il sera inutile pour le support technique et l'ITSM.

2. **Peut-on detecter la difference entre une erreur innocente et un payload CBE ?** Fondamentalement non, car la difference est dans l'**intention** de l'attaquant, pas dans le **contenu** du message.

3. **La differential privacy peut-elle proteger les corrections ?** En theorie oui (ajouter du bruit aux corrections), mais en pratique cela rend l'agent peu fiable.

4. **L'architecture de "confidential computing" peut-elle aider ?** Si les outils et le system prompt sont dans un enclave securisee inaccessible au LLM sauf via des API strictes, le CBE serait neutralise. Mais cela necessite une refonte complete de l'architecture des agents.

5. **La composante irreductible de l'alignment tax (arXiv:2603.00047) inclut-elle le CBE ?** Si oui, cela prouverait mathematiquement que le CBE ne peut jamais etre entierement elimine par l'entrainement seul.

### Directions de recherche prometteuses

1. **Formal verification de la non-fuite** : Peut-on prouver formellement qu'un modele ne fuiter pas d'information par correction ? Probablement NP-hard.

2. **Jeux a somme nulle** : Modeliser l'interaction CBE comme un jeu entre l'attaquant (maximise la fuite) et le defenseur (minimise la fuite). Trouver l'equilibre de Nash.

3. **Information-theoretic bounds** : Borner la quantite d'information qu'un attaquant CBE peut extraire par interaction, en fonction du contexte du modele.

4. **Mechanistic interpretability** : Identifier les circuits neuronaux responsables de la correction et les modifier selectivement sans detruire l'utilite.

---

## Sources

- [OpenReview — Safe RLHF (ICLR 2024)](https://openreview.net/forum?id=TyFrPOKYXw)
- [OpenReview — Inference-Time Reward Hacking (NeurIPS 2025)](https://openreview.net/forum?id=hSX7Dd8dxy)
- [Lilian Weng — Reward Hacking in Reinforcement Learning](https://lilianweng.github.io/posts/2024-11-28-reward-hacking/)
- [arXiv:2509.15557 — Reward Hacking Mitigation using Verifiable Composite Rewards](https://arxiv.org/abs/2509.15557)
- [arXiv:2502.18770 — Reward Shaping to Mitigate Reward Hacking in RLHF](https://arxiv.org/abs/2502.18770)
- [Nature Scientific Reports — Mitigating Malicious RLHF Feedback](https://www.nature.com/articles/s41598-025-92889-7)
- [arXiv:2603.00047 — What Is the Alignment Tax?](https://arxiv.org/abs/2603.00047)
- [arXiv:2512.11391 — NSPO: Null-Space Constrained Policy Optimization](https://arxiv.org/abs/2512.11391)
- [arXiv:2602.07892 — OGPSA: Orthogonal Gradient Projection for Safety Alignment](https://arxiv.org/abs/2602.07892)
- [arXiv:2503.00555 — Safety Tax: Safety Alignment Makes Reasoning Models Less Reasonable](https://arxiv.org/abs/2503.00555)
- [arXiv:2602.02136 — Mitigating Safety Tax via Distribution-Grounded Refinement](https://arxiv.org/abs/2602.02136)
- [arXiv:2309.06256 — Mitigating the Alignment Tax of RLHF](https://arxiv.org/abs/2309.06256)
- [arXiv:2410.10862 — Superficial Safety Alignment Hypothesis](https://arxiv.org/abs/2410.10862)
- [arXiv:2509.21305 — Sycophancy Is Not One Thing: Causal Separation](https://arxiv.org/abs/2509.21305)
- [npj Digital Medicine — When Helpfulness Backfires: Sycophantic Behavior](https://www.nature.com/articles/s41746-025-02008-z)
- [OpenAI — Interpreting Black Box Reward Models (ARGO)](https://alignment.openai.com/argo)
- [ResearchGate — Sycophancy in LLMs: Causes and Mitigations](https://www.researchgate.net/publication/394609269_Sycophancy_in_Large_Language_Models_Causes_and_Mitigations)
- [Annotera — RLHF for LLM Safety](https://www.annotera.ai/blog/how-rlhf-works-human-feedback-loops-llm-safety/)
- [arXiv:2602.13516 — SPILLage: Agentic Oversharing](https://arxiv.org/abs/2602.13516)
- [arXiv:2602.22450 — Silent Egress](https://arxiv.org/abs/2602.22450)
