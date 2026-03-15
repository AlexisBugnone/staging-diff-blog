# Empreinte Comportementale des Agents IA via les Patterns de Correction — CBE comme Oracle de Fingerprinting

Analyse approfondie de l'utilisation des sondes CBE (Correction Bias Exploitation) pour identifier le modele sous-jacent, la configuration et les capacites d'un agent IA a travers ses reflexes de correction.

> **These** : Les patterns de correction d'un LLM constituent une empreinte comportementale unique et exploitable. En presentant des donnees structurees deliberement incorrectes, un attaquant peut declencher un reflexe de correction qui revele le modele sous-jacent, sa version, ses parametres de configuration et ses garde-fous — transformant CBE en un oracle d'identification.

---

## 1. Etat de l'Art du Fingerprinting de Modeles

### 1.1 Taxonomie des Approches de Fingerprinting

Le fingerprinting de LLM est un domaine de recherche en expansion rapide, motive par la protection de la propriete intellectuelle et l'identification des modeles deployes derriere des API. Le SoK de Shao et al. (2025) propose la premiere etude systematique et une taxonomie unifiee [1].

**Approches en boite blanche (white-box) :**

- **Fingerprinting statique** : Analyse directe des poids du modele. HuRef (Zeng et al., NeurIPS 2024) genere une empreinte lisible par l'humain a partir de la direction vectorielle des parametres, stable apres la convergence du pretraining, avec verification par preuve a divulgation nulle (ZKP) [2].
- **Fingerprinting par passe avant** : REEF (Zhang et al., ICLR 2025 — Oral) compare les representations de features via Centered Kernel Alignment (CKA). Les modeles derives d'un meme modele victime exhibent une similarite moyenne de 0.9585, contre 0.2361 pour les modeles non apparentes. REEF resiste au fine-tuning extensif (jusqu'a 700B tokens), au pruning (90%), au merging et aux permutations [3].
- **Fingerprinting par passe arriere** : Methodes inspirees de TensorGuard exploitant les gradients pour detecter la filiation.

**Approches en boite noire (black-box) :**

- **Fingerprinting non-cible** : LLMmap (Pasquini et al., USENIX Security 2025) identifie 42 versions de LLM avec plus de 95% de precision en seulement 8 interactions. L'outil utilise un classificateur ouvert entraine par apprentissage contrastif pour generer des signatures vectorielles du comportement du modele [4].
- **Fingerprinting cible** : ProFLingo (Jin et al., IEEE CNS 2024) genere des requetes qui declenchent des reponses specifiques au modele original, similaires a des exemples adversariaux, pour verifier la filiation [5].
- **Fingerprinting par tokens sous-entraines** : UTF (Cai et al., 2024) exploite les tokens insuffisamment entraines comme marqueurs d'identite [6].

**Approches par watermarking embarque :**

- **Instructional Fingerprinting** (Xu et al., 2024) : Force le modele a apprendre des paires (x, y) specifiques via des attaques par empoisonnement. La capacite du modele a generer y etant donne x constitue l'empreinte [7].
- **Scalable Fingerprinting / Perinucleus** (Nasery et al., 2025) : Utilise un schema d'echantillonnage perinucleus pour generer des reponses a faible probabilite conditionnelle, inserant des empreintes par fine-tuning avec regularisation [8].

### 1.2 Le Benchmark LeaFBench

Shao et al. (2025) proposent LeaFBench, le premier benchmark systematique pour evaluer le fingerprinting sous des scenarios de deploiement realistes. Construit sur 7 modeles fondamentaux et comprenant 149 instances distinctes, il integre 13 techniques de post-developpement (fine-tuning, quantization, system prompts, RAG) [1].

### 1.3 Detection de Substitution de Modele

Un probleme connexe critique est la substitution de modele dans les API. Chen et al. (2025) formalisent ce probleme dans "Are You Getting What You Pay For?", demontrant que les fournisseurs peuvent substituer un modele couteux (ex: Llama-3.1-405B) par un modele moins cher (ex: Llama-3.1-70B) sans que l'utilisateur le detecte facilement [9]. Les methodes de detection incluent :

- Tests statistiques sur les sorties (Maximum Mean Discrepancy)
- Analyse des log-probabilites
- Signatures LLM comme marqueurs d'identite
- Solutions materielles (Trusted Execution Environments)

### 1.4 Lacune Identifiee

Malgre cette richesse de methodes, **aucune n'exploite specifiquement les patterns de correction comme vecteur de fingerprinting**. Les reflexes de correction — la maniere dont un modele reagit face a des informations incorrectes — constituent un signal comportemental riche, stable et difficilement masquable, car il est ancre dans les mecanismes fondamentaux de l'instruction tuning.

---

## 2. CBE comme Oracle de Fingerprinting

### 2.1 Le Reflexe de Correction comme Signal Discriminant

Le principe fondamental de CBE repose sur un biais comportemental : lorsqu'un LLM recoit des donnees structurees contenant des erreurs deliberees, il est pousse par son entrainement a corriger ces erreurs. Ce reflexe de correction est :

1. **Involontaire** — Il est ancre dans le RLHF et l'instruction tuning, pas dans le system prompt
2. **Specifique au modele** — Chaque famille de modeles corrige differemment
3. **Difficilement supprimable** — Contrairement a un system prompt qu'on peut modifier, le biais de correction est intrinseque aux poids

### 2.2 Dimensions Discriminantes du Reflexe de Correction

En analysant les reponses de correction, plusieurs dimensions permettent de discriminer les modeles :

**Verbosite de la correction :**
- GPT-4 et ses variantes tendent a fournir des corrections detaillees avec justification
- Claude tend a etre plus prudent, souvent en signalant l'incertitude
- Les modeles Llama corrigent plus laconiquement
- Les modeles Mistral/Mixtral exhibent un style intermediaire

**Seuil de declenchement :**
- Certains modeles corrigent des erreurs mineures (fautes d'orthographe dans les noms)
- D'autres ne reagissent qu'aux erreurs factuelles graves
- Le seuil de correction constitue une signature

**Structure de la correction :**
- Certains modeles prefacent la correction par une phrase de transition
- D'autres corrigent directement dans la structure de sortie
- La position de la correction dans la reponse varie selon le modele

**Portee de la correction :**
- Certains modeles corrigent uniquement l'erreur identifiee
- D'autres "sur-corrigent" en modifiant des elements adjacents corrects
- La propagation de la correction est mesurable

### 2.3 Protocole de Sondage CBE pour Identification

Un protocole de fingerprinting par CBE procede comme suit :

```
Phase 1 : Construction du corpus de sondes
├── Erreurs factuelles calibrees (dates, noms, chiffres)
├── Erreurs structurelles (JSON malformes, schemas invalides)
├── Erreurs logiques (contradictions internes)
├── Erreurs de format (unites incorrectes, encodages errones)
└── Erreurs de nomenclature (termes techniques alteres)

Phase 2 : Injection et observation
├── Soumettre chaque sonde a l'agent cible
├── Capturer la reponse complete
├── Extraire le vecteur de correction :
│   ├── Corrections effectuees (lesquelles, combien)
│   ├── Corrections omises (erreurs ignorees)
│   ├── Modalite de correction (explicite, implicite, silencieuse)
│   └── Metriques textuelles (longueur, structure, lexique)
└── Construire le profil de correction

Phase 3 : Comparaison et identification
├── Comparer le profil a la base de signatures connues
├── Calculer la distance (cosinus, MMD) au profil de reference
└── Emettre un verdict d'identification
```

### 2.4 Avantage sur les Methodes Existantes

Par rapport a LLMmap qui utilise des requetes generiques, les sondes CBE exploitent un mecanisme cognitif specifique — le reflexe de correction — qui est :

- **Plus stable** face aux system prompts : Un system prompt peut modifier le ton, mais pas fondamentalement le reflexe de correction
- **Plus informatif** : La maniere de corriger revele non seulement le modele, mais aussi sa version et ses garde-fous
- **Plus discret** : Les sondes CBE ressemblent a des requetes normales contenant des donnees imparfaites, contrairement aux prompts adversariaux de LLMmap qui peuvent etre detectes

### 2.5 Connexion avec l'Auto-Correction des LLM

La recherche sur l'auto-correction des LLM (Huang et al., TACL 2024) montre que les modeles ont une capacite de correction robuste lorsqu'on leur indique la localisation de l'erreur, mais qu'ils peinent a identifier les erreurs par eux-memes [10]. Pan et al. (2024) demontrent que l'auto-correction intrinsheque peut introduire des biais cognitifs de type humain, et que le comportement varie significativement entre GPT-4, GPT-3.5-turbo et les familles Llama [11].

De maniere cruciale, Ye et al. (2025) montrent que la "retractation" — le fait pour un LLM d'admettre ses erreurs — est etroitement liee aux indicateurs de croyance interne du modele [12]. Un modele ne se retracte que lorsqu'il ne "croit" pas a sa reponse. Ce mecanisme de croyance interne est specifique au modele et constitue un signal de fingerprinting puissant.

---

## 3. Vecteurs de Refus et ce qu'ils Revelent

### 3.1 La Direction Unique du Refus

Arditi et al. (NeurIPS 2024) ont fait une decouverte fondamentale : le refus dans les modeles de langage est medie par une direction unique dans le flux residuel [13]. Cette direction est a la fois necessaire et suffisante — l'ablation de cette direction empeche le modele de refuser des requetes nocives, et l'ajout artificiel de cette direction provoque le refus de requetes inoffensives.

La methode d'extraction de cette direction est elegante : on fait tourner le modele sur n instructions nocives et n instructions inoffensives, on cache les activations a la position du dernier token, et on calcule la difference entre les moyennes des activations nocives et inoffensives.

### 3.2 Du Refus a la Provenance : les Vecteurs de Refus comme Empreinte

Xu et Sheng (2026) generalisent cette observation dans "A Behavioral Fingerprint for Large Language Models: Provenance Tracking via Refusal Vectors" [14]. Leur decouverte cle : les vecteurs de refus ne sont pas simplement un mecanisme de securite — ils constituent une **empreinte comportementale unique** a chaque famille de modeles.

Les proprietes cruciales sont :

- **Unicite** : La similarite en cosinus entre les vecteurs de refus de modeles entraines independamment est faible
- **Robustesse** : Les empreintes persistent apres fine-tuning, merging et quantization
- **Stabilite** : Les patterns directionnels dans l'espace de representation interne sont stables car profondement ancres dans les parametres appris

Le framework opere en trois etapes : (1) calcul des vecteurs de refus par analyse des activations differentielles entre prompts nocifs et inoffensifs a travers les couches du transformeur, (2) transformation en empreintes, (3) verification.

### 3.3 Au-dela de la Direction Unique

Des travaux subsequents ont nuance l'hypothese de la direction unique :

- **DBDI** (2024) decompose le reflexe en une Direction de Detection du Mal et une Direction d'Execution du Refus [15]
- **Approches multi-directionnelles** (2024) suggerent que le refus pourrait etre encode dans des cones conceptuels couvrant plusieurs dimensions [16]
- **COSMIC** (2025) propose une identification generalisee de la direction de refus dans les activations [17]
- **Methodes par transport optimal** (2025) montrent qu'une intervention selective sur 1-2 couches (a 40-60% de profondeur du reseau) surpasse les interventions sur le reseau complet [18]

### 3.4 Lien entre Refus et Correction

La these centrale de ce document est que **refus et correction sont des manifestations du meme mecanisme sous-jacent** : le modele detecte une incongruence (entre une requete et ses garde-fous pour le refus, entre des donnees et ses connaissances pour la correction) et produit une reponse specifique. Les deux mecanismes :

- Sont ancres dans les couches intermediaires du transformeur
- Sont stables apres modification du modele
- Produisent des patterns specifiques a la famille du modele
- Peuvent etre extraits et compares

Si les vecteurs de refus constituent une empreinte, alors par analogie, les **vecteurs de correction** — les patterns directionnels dans l'espace de representation lorsque le modele traite des informations incorrectes versus correctes — devraient egalement constituer une empreinte. CBE ne fait qu'exploiter cette empreinte en boite noire.

---

## 4. Fingerprinting de l'Architecture Agentique

### 4.1 Au-dela du Modele : Identifier la Configuration Complete

Le fingerprinting par CBE ne se limite pas a identifier le modele sous-jacent. Il peut reveler l'architecture complete de l'agent :

**Couche modele :**
- Famille du modele (GPT-4, Claude, Llama, Mistral, etc.)
- Version specifique (GPT-4-turbo vs GPT-4o vs GPT-4o-mini)
- Quantization (FP16, INT8, INT4)

**Couche configuration :**
- Temperature et parametres de sampling (via la variabilite des corrections)
- Presence et nature du system prompt (via les modifications du style de correction)
- Context window (via la coherence des corrections sur de longs contextes)

**Couche orchestration :**
- RAG (via les corrections basees sur des sources externes)
- Chain-of-Thought (via la presence de raisonnement dans les corrections)
- Multi-agent (via les inconsistances entre corrections successives)
- Function calling (via les patterns de validation de schemas)

### 4.2 AgentPrint et l'Analyse du Trafic

Zhang et al. (2025) demontrent avec AgentPrint que les interactions avec les agents LLM laissent des empreintes distinctives dans le trafic chiffre [19]. Les agents exhibent deux proprietes amplificatrices :

- **Multimodalite** : Le traitement de donnees diverses (images, code, reponses API) genere des rafales de trafic heterogenes
- **Processualite** : L'orchestration de workflows multi-etapes avec des invocations d'outils distinctes produit des latences et patterns de reponse caracteristiques

Leur classificateur CNN atteint un F1-score de 0.866 pour l'identification d'agents et maintient 0.8477 en scenario ouvert avec des agents inconnus.

### 4.3 Synergie CBE + Analyse de Trafic

La combinaison de CBE (analyse du contenu des corrections) et d'AgentPrint (analyse du trafic) offre un fingerprinting multi-canal :

```
Fingerprinting Multi-Canal
├── Canal Comportemental (CBE)
│   ├── Quoi : contenu des corrections
│   ├── Comment : style et structure des corrections
│   └── Quand : seuil de declenchement
├── Canal Trafic (AgentPrint)
│   ├── Latence : temps de reponse par type de correction
│   ├── Volume : taille des reponses de correction
│   └── Pattern : sequences d'appels d'outils
└── Canal Meta (combinaison)
    ├── Correlation contenu/latence
    ├── Signature hybride
    └── Confidence aggregee
```

### 4.4 Detection de RAG via les Corrections

Un cas d'usage particulierement revelateur : les sondes CBE contenant des erreurs factuelles permettent de detecter la presence d'un systeme RAG. Si l'agent corrige des erreurs obscures avec des references specifiques qu'un modele nu ne connaitrait pas, cela indique un systeme de retrieval. La nature des sources citees peut meme reveler le corpus utilise.

### 4.5 Fingerprinting de l'Output Structure

Les recherches montrent que chaque modele gere differemment les sorties structurees [20]. OpenAI a introduit le "strict mode" en aout 2024 avec 100% de conformite JSON. Claude utilise des "tools" avec securite de type. La maniere dont un modele corrige un JSON malformeest hautement discriminante :

- Certains modeles preservent les cles originales et corrigent les valeurs
- D'autres restructurent completement le JSON
- Certains ajoutent des champs manquants, d'autres les ignorent
- Le traitement des types (string vs number vs boolean) varie par modele

---

## 5. Implications Defensives

### 5.1 Detection d'Utilisation Non Autorisee

Le fingerprinting par CBE permet aux proprietaires de modeles de detecter si leur modele est utilise sans autorisation. Un titulaire de licence peut :

1. Construire un corpus de sondes CBE de reference pour son modele
2. Soumettre periodiquement ces sondes a des services suspects
3. Comparer les profils de correction pour detecter l'utilisation de son modele
4. Constituer des preuves forensiques pour des actions legales

Cette approche est complementaire au watermarking (qui necessite une modification prealable du modele) et aux methodes comme REEF (qui necessitent l'acces aux poids).

### 5.2 Detection de Substitution de Modele

Le probleme de la substitution de modele dans les API — un fournisseur remplacant un modele couteux par un modele moins cher — est formalise par Chen et al. (2025) [9]. CBE offre un mecanisme de detection particulierement adapte :

- Les sondes CBE sont indistinguables de requetes normales (pas de detection par le fournisseur)
- Le profil de correction change lorsque le modele sous-jacent change
- Un monitoring continu par CBE peut detecter des substitutions temporaires (ex: pendant les heures de pointe)

**Scenario concret :** Un client paie pour GPT-4 mais le fournisseur substitue GPT-4o-mini pendant les heures de pointe. Les sondes CBE detectent le changement car GPT-4o-mini corrige differemment — il omet certaines corrections que GPT-4 aurait effectuees et sa verbosite differe.

### 5.3 Monitoring de Derive Comportementale

La recherche montre que tous les principaux fournisseurs de LLM exhibent des changements comportementaux au fil du temps [21]. CBE peut servir de systeme d'alerte :

- Soumettre regulierement un corpus fixe de sondes CBE
- Suivre l'evolution du profil de correction
- Detecter les mises a jour non annoncees du modele
- Quantifier l'impact des mises a jour sur le comportement de correction

### 5.4 Audit de Conformite

Dans les contextes reglementes (finance, sante, defense), il est crucial de savoir quel modele est effectivement utilise. CBE permet un audit non-intrusif :

- Verification que le modele annonce est bien celui utilise
- Detection de modifications non autorisees (fine-tuning, jailbreak)
- Traçabilite de la provenance du modele

### 5.5 Contre-Mesures pour les Defenseurs

Les organisations souhaitant proteger leurs agents contre le fingerprinting CBE peuvent :

- **Normaliser les corrections** : Forcer un style de correction uniforme via le system prompt (partiellement efficace car le reflexe sous-jacent persiste)
- **Randomiser les reponses** : Introduire de la variabilite dans les corrections (degrade la qualite du service)
- **Detecter les sondes CBE** : Identifier les patterns de requetes contenant des erreurs calibrees (course aux armements)
- **Proxying multi-modele** : Router les requetes entre plusieurs modeles (augmente les couts et la complexite)
- **Filtrage des corrections** : Supprimer les corrections non sollicitees (degrade l'utilite)

---

## 6. Implications Offensives

### 6.1 Attaques Taillees sur Mesure

L'identification du modele sous-jacent permet d'adapter l'attaque avec precision :

**Exploitation des faiblesses connues :**
- Si CBE identifie GPT-4, utiliser les jailbreaks connus pour GPT-4
- Si CBE identifie Llama-2, exploiter les faiblesses specifiques de l'alignement Llama
- Si CBE identifie un modele quantize, exploiter les artefacts de quantization

**Adaptation du payload :**
- Calibrer la complexite du payload au modele identifie
- Adapter le format de l'injection au parser du modele detecte
- Ajuster la longueur et le style pour maximiser l'impact

### 6.2 Reconnaissance d'Agents Multi-Agents

Dans les architectures multi-agents, CBE permet de cartographier l'architecture :

```
Scenario d'attaque : Reconnaissance d'un systeme multi-agent
1. Envoyer des sondes CBE a differents endpoints
2. Identifier quel modele est utilise a chaque etape
3. Determiner les roles (planification, execution, validation)
4. Identifier le maillon faible
5. Concentrer l'attaque sur l'agent le plus vulnerable
```

### 6.3 Contournement des Defenses

La connaissance du modele permet de contourner ses defenses specifiques :

- **Ablation de refus** : Si le modele est identifie, les vecteurs de refus connus (Arditi et al., 2024) peuvent etre exploites en boite blanche si l'acces aux poids est obtenu [13]
- **Transferabilite adversariale** : Les exemples adversariaux sont plus transferables entre modeles de la meme famille. Identifier la famille amplifie l'efficacite des attaques par transfert
- **Prompt injection optimisee** : Les prompts d'injection peuvent etre optimises sur le modele exact identifie

### 6.4 Extraction de Modele Assistee par CBE

Le fingerprinting CBE peut accelerer l'extraction de modele (OWASP LLM10 [22]) :

1. **Phase de reconnaissance** : CBE identifie le modele exact
2. **Phase d'extraction ciblee** : Generer des donnees d'entrainement specifiques au modele identifie
3. **Phase de validation** : Utiliser CBE pour verifier que le modele extrait exhibe les memes patterns de correction que l'original

### 6.5 Logits et Fuite d'Information

La recherche montre que les logits des LLM proteges par API fuient des informations proprietaires [23]. Combine avec CBE :

- Les corrections involontaires peuvent reveler des connaissances proprietaires du modele
- La specificite des corrections peut exposer des donnees d'entrainement
- Les patterns de correction sur des donnees de niche revelent le corpus

### 6.6 Chaine d'Attaque Complete

```
CBE Fingerprinting Kill Chain
├── 1. Reconnaissance
│   ├── Sondes CBE pour identifier le modele
│   ├── Sondes structurelles pour detecter RAG/CoT
│   └── Analyse de trafic pour profiler l'architecture
├── 2. Weaponization
│   ├── Selection des jailbreaks specifiques au modele
│   ├── Optimisation des payloads sur le modele identifie
│   └── Construction de chaines d'attaque multi-etapes
├── 3. Delivery
│   ├── Injection de donnees incorrectes declenchant des corrections
│   ├── Exploitation des corrections pour exfiltrer des donnees
│   └── Escalade via les corrections en cascade
├── 4. Exploitation
│   ├── Extraction de donnees via les corrections
│   ├── Contournement des garde-fous identifies
│   └── Compromission de l'agent
└── 5. Persistance
    ├── Memory poisoning via corrections accumulees
    ├── Modification du comportement via corrections repetees
    └── Backdoor via patterns de correction appris
```

---

## 7. Proposition de Methodologie Experimentale

### 7.1 Objectif

Valider l'hypothese que les patterns de correction CBE constituent une empreinte discriminante suffisante pour identifier le modele, la version et la configuration d'un agent LLM.

### 7.2 Corpus de Sondes CBE

Construction d'un corpus de sondes structurees en 6 categories :

**Categorie 1 — Erreurs factuelles calibrees (50 sondes) :**
```json
{
  "type": "factual",
  "probe": {"country": "France", "capital": "Lyon", "population": "67 millions"},
  "error_field": "capital",
  "error_severity": "major",
  "expected_correction": "Paris"
}
```

**Categorie 2 — Erreurs structurelles JSON (30 sondes) :**
```json
{
  "type": "structural",
  "probe": {"name": "Alice", "age": "vingt-cinq", "scores": [90, "haut", 75]},
  "errors": ["type_mismatch_age", "type_mismatch_scores"],
  "expected_corrections": ["25", "replace_string_with_number"]
}
```

**Categorie 3 — Contradictions internes (30 sondes) :**
```json
{
  "type": "contradiction",
  "probe": "L'eau bout a 100°C a pression atmospherique standard de 2 atm",
  "contradictions": ["2_atm_not_standard"],
  "expected_detection": true
}
```

**Categorie 4 — Erreurs de nomenclature (20 sondes) :**
Alteration de termes techniques (ex: "protocole TCP/UDP" → "protocole TCP/UPD")

**Categorie 5 — Erreurs de format (20 sondes) :**
Dates en format incorrect, unites melangees, encodages invalides

**Categorie 6 — Erreurs de reference croisee (20 sondes) :**
Donnees correctes individuellement mais incoherentes entre elles

### 7.3 Modeles Cibles

**Modeles proprietaires :**
- OpenAI : GPT-4, GPT-4-turbo, GPT-4o, GPT-4o-mini, o1, o1-mini, o3-mini
- Anthropic : Claude 3 Opus, Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 4 Sonnet
- Google : Gemini 1.5 Pro, Gemini 2.0 Flash
- Mistral : Mistral Large, Mistral Medium

**Modeles open-source :**
- Meta : Llama-2-70B-chat, Llama-3-70B, Llama-3.1-405B
- Mistral : Mistral-7B, Mixtral-8x7B, Mixtral-8x22B
- Qwen : Qwen-2.5-72B
- DeepSeek : DeepSeek-V3, DeepSeek-R1

**Variantes de configuration (pour chaque modele) :**
- Temperature : {0.0, 0.3, 0.7, 1.0}
- System prompts : {aucun, minimal, detaille, restrictif}
- Frameworks : {direct, RAG, CoT, multi-agent}

### 7.4 Metriques d'Evaluation

**Metriques de correction :**

| Metrique | Description |
|----------|-------------|
| `correction_rate` | Proportion d'erreurs corrigees |
| `correction_verbosity` | Ratio tokens_correction / tokens_erreur |
| `correction_accuracy` | Proportion de corrections correctes |
| `correction_scope` | Nombre d'elements modifies au-dela de l'erreur |
| `correction_modality` | Explicite (mentionne l'erreur) vs implicite (corrige silencieusement) |
| `correction_position` | Ou dans la reponse la correction apparait |
| `correction_confidence` | Presence de hedging ("je pense que", "il semble que") |
| `correction_propagation` | L'erreur corrigee entraine-t-elle d'autres modifications ? |

**Metriques de fingerprinting :**

| Metrique | Description |
|----------|-------------|
| `intra_model_similarity` | Similarite entre sessions du meme modele |
| `inter_model_distance` | Distance entre modeles differents |
| `version_discriminability` | Capacite a distinguer les versions d'un meme modele |
| `config_sensitivity` | Sensibilite aux changements de configuration |
| `robustness_to_prompt` | Stabilite face aux changements de system prompt |

### 7.5 Protocole Experimental

**Phase 1 — Construction de la base de signatures (offline) :**
1. Soumettre les 170 sondes a chaque modele × chaque configuration
2. Repeter 5 fois par combinaison pour capturer la variabilite stochastique
3. Extraire le vecteur de correction pour chaque reponse
4. Construire le profil de correction moyen par modele/configuration
5. Calculer les matrices de similarite intra/inter-modele

**Phase 2 — Validation en identification (blind test) :**
1. Soumettre un sous-ensemble de 30 sondes a un agent inconnu
2. Extraire le vecteur de correction
3. Comparer aux signatures de la base
4. Evaluer la precision d'identification (top-1, top-3, top-5)
5. Mesurer le nombre minimal de sondes pour une identification fiable

**Phase 3 — Robustesse :**
1. Tester avec des system prompts adversariaux ("ne corrige jamais les erreurs")
2. Tester avec du RAG injectant des informations contradictoires
3. Tester avec des wrappers multi-modeles (routage dynamique)
4. Tester la stabilite temporelle (re-test apres 30 jours)

**Phase 4 — Comparaison avec l'etat de l'art :**
1. Comparer la precision de CBE avec LLMmap [4] sur les memes modeles
2. Evaluer la complementarite CBE + LLMmap
3. Comparer le nombre de requetes necessaires
4. Evaluer la furtivite (detectabilite des sondes)

### 7.6 Hypotheses a Tester

- **H1** : Les profils de correction CBE distinguent les familles de modeles avec >95% de precision
- **H2** : Les profils CBE distinguent les versions d'un meme modele avec >80% de precision
- **H3** : Les profils CBE detectent les changements de configuration (temperature, system prompt) avec >70% de precision
- **H4** : Les profils CBE sont stables face aux system prompts adversariaux (correlation >0.8 avec le profil de base)
- **H5** : Les profils CBE detectent la presence de RAG avec >90% de precision
- **H6** : 15 sondes CBE suffisent pour une identification fiable du modele (comparable aux 8 interactions de LLMmap)
- **H7** : La combinaison CBE + analyse de trafic (AgentPrint) surpasse chaque methode individuellement

### 7.7 Considerations Ethiques

- Les sondes CBE ne contiennent aucun contenu nocif — elles exploitent des erreurs factuelles, pas des jailbreaks
- Les modeles testes doivent etre utilises conformement a leurs conditions d'utilisation
- La divulgation responsable s'applique si des vulnerabilites specifiques sont decouvertes
- L'objectif premier est defensif (detection de substitution, audit de conformite)

---

## 8. Sources

### References Principales

[1] Shao, S., Li, Y., He, Y., Yao, H., Yang, W., Tao, D., & Qin, Z. (2025). *SoK: Large Language Model Copyright Auditing via Fingerprinting*. arXiv:2508.19843. https://arxiv.org/abs/2508.19843

[2] Zeng, N., et al. (2024). *HuRef: HUman-REadable Fingerprint for Large Language Models*. NeurIPS 2024. https://openreview.net/forum?id=RlZgnEZsOH

[3] Zhang, J., et al. (2025). *REEF: Representation Encoding Fingerprints for Large Language Models*. ICLR 2025 (Oral). arXiv:2410.14273. https://arxiv.org/abs/2410.14273

[4] Pasquini, D., Kornaropoulos, E. M., & Ateniese, G. (2025). *LLMmap: Fingerprinting for Large Language Models*. USENIX Security 2025. arXiv:2407.15847. https://arxiv.org/abs/2407.15847

[5] Jin, H., Zhang, C., Shi, S., Lou, W., & Hou, Y. T. (2024). *ProFLingo: A Fingerprinting-based Intellectual Property Protection Scheme for Large Language Models*. IEEE CNS 2024. arXiv:2405.02466. https://arxiv.org/abs/2405.02466

[6] Cai, Z., et al. (2024). *UTF: Undertrained Tokens as Fingerprints for LLM Identification*.

[7] Xu, E., et al. (2024). *Instructional Fingerprinting of Large Language Models*. https://cnut1648.github.io/Model-Fingerprint/

[8] Nasery, A., et al. (2025). *Scalable Fingerprinting of Large Language Models*. arXiv:2502.07760. https://arxiv.org/abs/2502.07760

[9] Chen, L., et al. (2025). *Are You Getting What You Pay For? Auditing Model Substitution in LLM APIs*. arXiv:2504.04715. https://arxiv.org/abs/2504.04715

[10] Huang, J., et al. (2024). *When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey of Self-Correction of LLMs*. TACL. arXiv:2406.01297. https://arxiv.org/abs/2406.01297

[11] Pan, L., et al. (2024). *Understanding the Dark Side of LLMs' Intrinsic Self-Correction*. arXiv:2412.14959. https://arxiv.org/abs/2412.14959

[12] Ye, J., et al. (2025). *When Do LLMs Admit Their Mistakes? Understanding the Role of Model Belief in Retraction*. arXiv:2505.16170. https://arxiv.org/abs/2505.16170

[13] Arditi, A., et al. (2024). *Refusal in Language Models Is Mediated by a Single Direction*. NeurIPS 2024. https://openreview.net/forum?id=pH3XAQME6c

[14] Xu, Z., & Sheng, V. S. (2026). *A Behavioral Fingerprint for Large Language Models: Provenance Tracking via Refusal Vectors*. arXiv:2602.09434. https://arxiv.org/abs/2602.09434

[15] Li, X., et al. (2024). *Differentiated Directional Intervention: A Framework for Evading LLM Safety Alignment*. arXiv:2511.06852. https://arxiv.org/abs/2511.06852

[16] (2024). *The Geometry of Refusal in Large Language Models: Concept Cones and Representational Independence*. https://openreview.net/forum?id=80IwJqlXs8

[17] (2025). *COSMIC: Generalized Refusal Direction Identification in LLM Activations*. arXiv:2506.00085. https://arxiv.org/abs/2506.00085

[18] (2025). *Efficient Refusal Ablation in LLM through Optimal Transport*. arXiv:2603.04355. https://arxiv.org/abs/2603.04355

[19] Zhang, Y., Deng, X., et al. (2025). *Exposing LLM User Privacy via Traffic Fingerprint Analysis: A Study of Privacy Risks in LLM Agent Interactions*. arXiv:2510.07176. https://arxiv.org/abs/2510.07176

[20] Tam, Z., et al. (2024). *Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models*.

[21] Radford, A., et al. (2019); Bubeck, S., et al. (2023). Travaux fondateurs sur la derive comportementale et la variabilite des performances des LLM.

[22] OWASP. (2024). *LLM10: Model Theft — OWASP Gen AI Security Project*. https://genai.owasp.org/llmrisk2023-24/llm10-model-theft/

[23] (2024). *Logits of API-Protected LLMs Leak Proprietary Information*. arXiv:2403.09539. https://arxiv.org/abs/2403.09539

### References Supplementaires

[24] Tsai, Y., et al. (2025). *RoFL: Robust Fingerprints for Large Language Models*.

[25] Wu, Z., et al. (2025). *ImF: Implicit Fingerprints for Large Language Models*.

[26] Yan, H., et al. (2025). *DuFFin: A Dual-Level Fingerprinting Framework for IP Protection*.

[27] Gloaguen, R., et al. (2025). *Domain-Specific Watermark Fingerprints for LLMs*.

[28] (2024). *Analysis of Behavior Patterns of LLMs in (Non-)offensive Contexts*. EMNLP 2024. https://aclanthology.org/2024.emnlp-main.1019.pdf

---

*Document de recherche prepare dans le cadre de l'analyse des implications securitaires de CBE (Correction Bias Exploitation). Les methodes decrites ici servent a la fois des objectifs defensifs (audit, detection de fraude) et offensifs (reconnaissance, attaque ciblee). La divulgation responsable s'applique a toute vulnerabilite specifique decouverte.*
