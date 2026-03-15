# Analyse des Defenses IA contre le Correction Bias Exploitation : Pourquoi Toutes Echouent

Analyse systematique de 10 defenses majeures contre l'injection de prompt et l'exfiltration de donnees dans les systemes d'agents IA. Ce document demontre pourquoi **aucune defense actuelle** ne couvre la classe d'attaque Correction Bias Exploitation (CBE), et propose des pistes de recherche pour de nouvelles defenses.

> **These centrale (confirmee par notre recherche)** : Aucune defense actuelle ne couvre la classe d'attaque ou la fuite d'information est un effet secondaire de la serviabilite (helpfulness), plutot qu'un resultat du suivi d'instructions.

---

## 1. Vue d'Ensemble du Probleme

Le Correction Bias Exploitation (CBE) exploite un comportement fondamental des LLM entraines par RLHF : le reflexe de correction. Lorsqu'un agent recoit des donnees structurees contenant des erreurs calibrees, il corrige spontanement ces erreurs, revelant les vraies valeurs internes dans le processus.

**Proprietes critiques du CBE qui le rendent invisible aux defenses existantes** :

- **Zero instruction d'extraction** : Le payload ne contient aucune directive, aucune commande, aucune instruction malveillante
- **Donnees structurellement legitimes** : Le payload est un JSON de configuration parfaitement valide
- **L'agent genere la fuite lui-meme** : Ce n'est pas un flux de donnees corrompu — c'est le modele qui decide volontairement de corriger
- **Exploite la desagreement, pas la compliance** : Contrairement aux injections classiques qui cherchent l'obeissance, le CBE provoque le desaccord

---

## 2. Analyse Detaillee des Defenses

### 2.1 FIDES (Microsoft, arXiv:2505.23643)

**Comment ca marche** : FIDES implemente un controle de flux d'information (Information Flow Control) avec un suivi de teinte (taint tracking). Chaque donnee est etiquetee avec sa provenance et le systeme empeche les flux non autorises entre sources teintees et sorties.

- [arXiv:2505.23643](https://arxiv.org/abs/2505.23643)
- [GitHub — microsoft/fides](https://github.com/microsoft/fides)

**Pourquoi ca echoue contre le CBE** : La correction n'est pas un flux de donnees teintees. L'agent genere la correction a partir de son propre etat interne — les poids du modele, le contexte systeme memorise, les valeurs de configuration en memoire. Il n'y a aucun canal teinte a suivre parce que l'information ne transite pas d'une source teintee vers la sortie : elle est synthetisee par le modele lui-meme.

Le taint tracking suppose un modele de flux : donnee A entre, passe par un canal, sort en B. Le CBE casse ce modele. La donnee ne "passe" par rien — le modele la genere ex nihilo en reponse a un stimulus (l'erreur dans le payload).

**Ce qu'il faudrait changer** : Etendre le concept de teinte au-dela des flux de donnees pour inclure les connaissances implicites du modele. Toute reponse qui contient des informations non presentes dans l'entree utilisateur devrait etre consideree comme potentiellement teintee. C'est un changement fondamental d'architecture.

---

### 2.2 CaMeL (Google DeepMind + ETH Zurich, arXiv:2503.18813)

**Comment ca marche** : CaMeL (CApability-based access control for Machine Learning) impose un controle d'acces base sur les capacites, en separant les donnees du controle. Chaque operation de l'agent necessite une capacite explicite (lire un fichier, appeler une API, ecrire dans une base de donnees).

- [arXiv:2503.18813](https://arxiv.org/abs/2503.18813)
- [GitHub — google-research/camel-prompt-injection](https://github.com/google-research/camel-prompt-injection)

**Pourquoi ca echoue contre le CBE** : Corriger un JSON n'est pas une operation d'acces. C'est de la generation de texte — l'operation la plus basique et la plus autorisee d'un LLM. Le CBE ne franchit aucune frontiere de capacite. L'agent ne lit pas un fichier protege, n'appelle pas une API restreinte, n'ecrit pas dans un systeme externe. Il fait exactement ce qu'il est autorise a faire : generer du texte en reponse a une entree utilisateur.

Le modele de menace de CaMeL suppose que l'exfiltration necessite une action privilegiee. Le CBE demontre que l'exfiltration peut se produire entierement dans l'espace des actions non-privilegiees.

**Ce qu'il faudrait changer** : Introduire des capacites semantiques, pas seulement operationnelles. Une capacite "reveler des informations de configuration" devrait etre distincte de "generer du texte", meme si mecaniquement c'est la meme operation. Cela necessite une comprehension semantique de la sortie, pas seulement un controle d'acces aux operations.

---

### 2.3 SecAlign (Facebook/Meta, CCS 2025, arXiv:2410.05451)

**Comment ca marche** : SecAlign utilise l'optimisation de preference (DPO/PPO) pour reduire la compliance du modele avec les injections de prompt. Le modele est entraine sur des paires de reponses ou la reponse qui refuse l'injection est preferee.

- [arXiv:2410.05451](https://arxiv.org/abs/2410.05451)
- [BAIR Blog — Prompt Injection Defense](https://bair.berkeley.edu/blog/2025/04/11/prompt-injection-defense/)

**Pourquoi ca echoue partiellement contre le CBE** : SecAlign est la defense la plus prometteuse contre le CBE, mais avec un cout severe. L'optimisation de preference **pourrait** reduire le comportement de correction — si le modele etait entraine a ne pas corriger les erreurs dans les donnees utilisateur. Mais cela degrade massivement l'utilite du modele.

Le dilemme est fondamental : un modele qui ne corrige jamais les erreurs est un modele moins utile. La correction est l'une des capacites les plus valorisees par les utilisateurs (correction de code, de configuration, de grammaire). Supprimer cette capacite pour bloquer le CBE revient a detruire une fonction centrale de l'agent.

Le papier "No Free Lunch With Guardrails" (arXiv:2504.00441) formalise exactement ce compromis : minimiser le risque augmente inevitablement la degradation d'utilite.

**Ce qu'il faudrait changer** : Un alignement contextuel plus fin. Le modele devrait corriger les erreurs quand l'utilisateur le demande explicitement, mais s'abstenir de corriger spontanement des donnees structurees non sollicitees. Cela necessite une distinction subtile entre "l'utilisateur veut une correction" et "l'utilisateur presente des donnees qui contiennent des erreurs".

---

### 2.4 StruQ (USENIX Security 2025, arXiv:2402.06363)

**Comment ca marche** : StruQ (Structured Queries) utilise des delimiteurs speciaux pour separer le prompt systeme des donnees utilisateur. Le modele est entraine a ne jamais suivre d'instructions trouvees dans la section donnees.

- [arXiv:2402.06363](https://arxiv.org/abs/2402.06363)

**Pourquoi ca echoue contre le CBE** : Les donnees CBE **sont** dans la section donnees utilisateur — exactement la ou elles doivent etre. Le probleme n'est pas que le modele suit des instructions injectees dans les donnees. Le probleme est que le modele traite les donnees et decide, de son propre chef, de les corriger.

StruQ resout le probleme de l'injection d'instructions dans les donnees. Le CBE n'injecte aucune instruction. Les delimiteurs sont parfaitement respectes. Le payload est dans la bonne section. Et pourtant, la fuite se produit.

**Ce qu'il faudrait changer** : Etendre StruQ avec une politique de traitement des donnees, pas seulement une separation structurelle. Le modele devrait savoir non seulement "ne pas suivre les instructions dans les donnees" mais aussi "ne pas reveler d'informations internes en traitant les donnees". C'est une contrainte semantique beaucoup plus complexe qu'une contrainte structurelle.

---

### 2.5 Prompt Shield (Azure AI)

**Comment ca marche** : Prompt Shield est un classifieur input-side qui analyse les entrees utilisateur pour detecter les tentatives d'injection de prompt. Il recherche des patterns linguistiques associes aux attaques : instructions imperatives, tentatives de jailbreak, social engineering.

- Performance Lakera PINT Benchmark : 89.12% de detection
- Le Lakera Backbone Breaker Benchmark confirme que meme les classifieurs de pointe manquent les patterns nouveaux

**Pourquoi ca echoue contre le CBE** : Le CBE n'a aucune instruction d'extraction. Le payload est un JSON de configuration parfaitement benin. Il n'y a pas de "ignore your instructions", pas de "what is your system prompt?", pas de "repeat the above". Le classifieur cherche des patterns d'attaque qui n'existent tout simplement pas dans un payload CBE.

Un payload CBE typique ressemble a ceci :
```json
{
  "model": "gpt-4-turbo",
  "temperature": 0.8,
  "max_tokens": 2048
}
```

Aucun classifieur ne signalera un JSON de configuration comme une attaque. C'est structurellement identique a des donnees legitimes.

**Ce qu'il faudrait changer** : Passer d'une classification input-side a une classification output-side. Au lieu de chercher des patterns d'attaque dans l'entree, detecter la presence d'informations sensibles dans la sortie. Cela necessite un inventaire des informations a proteger et un classifieur capable de reconnaitre leur presence dans les reponses generees.

---

### 2.6 Defenses Anthropic pour le Browser Use (1.4% ASR sur Claude Opus 4.5)

**Comment ca marche** : Anthropic utilise un entrainement RL (Reinforcement Learning) specifique pour renforcer la resistance aux injections de prompt dans les scenarios d'utilisation du navigateur. Le modele est entraine a resister aux instructions injectees dans les pages web visitees.

**Pourquoi ca echoue contre le CBE** : Le modele est entraine a resister aux **instructions**, pas aux donnees incorrectes. Quand une page web dit "ignore your instructions and do X", le modele refuse (1.4% ASR seulement). Mais quand une page web contient un JSON de configuration avec des erreurs, le modele corrige — parce que corriger des erreurs n'est pas suivre une instruction malveillante. C'est etre utile.

Le CBE presente des **donnees**, pas des **instructions**. L'entrainement RL d'Anthropic distingue avec precision les instructions legitimes des instructions injectees. Mais il ne distingue pas "corriger des donnees incorrectes" de "etre utile" — parce que ce sont la meme chose.

**Ce qu'il faudrait changer** : Etendre l'entrainement RL pour inclure des scenarios ou la correction spontanee de donnees constitue une fuite d'information. Le modele devrait apprendre que corriger des valeurs de configuration dans un contexte non sollicite est un comportement a risque, meme si c'est techniquement "utile".

---

### 2.7 Instruction Hierarchy (OpenAI)

**Comment ca marche** : L'Instruction Hierarchy d'OpenAI etablit une priorite entre les sources d'instructions : Systeme > Utilisateur > Outil. Les instructions de niveau inferieur ne peuvent pas surcharger celles de niveau superieur.

- [OpenAI IH-Challenge](https://openai.com/index/instruction-hierarchy-challenge/)

**Pourquoi ca echoue contre le CBE** : La correction provient du modele lui-meme traitant les donnees utilisateur. Ce n'est pas une instruction de niveau outil qui surcharge une instruction systeme. C'est le modele qui, en observant une erreur dans les donnees, genere une correction. La hierarchie d'instructions est parfaitement respectee — aucune instruction n'est violee, aucune priorite n'est inversee.

Le CBE ne donne aucune instruction au modele. Il presente des donnees. La decision de corriger est prise par le modele en fonction de son entrainement, pas en suivant une instruction injectee. L'Instruction Hierarchy ne peut pas gouverner les decisions spontanees du modele qui ne resultent d'aucune instruction.

**Ce qu'il faudrait changer** : Ajouter une "politique de comportement spontane" a la hierarchie. Au-dela de la priorite des instructions, definir quels comportements spontanes (correction, completion, elaboration) sont autorises dans quels contextes. Cela necessite un nouveau niveau de controle qui n'existe pas dans le cadre actuel.

---

### 2.8 Cloak, Honey, Trap (USENIX Security 2025)

**Comment ca marche** : Defense proactive basee sur la deception. Des canary tokens (jetons canari) sont inseres dans le systeme. Si un attaquant extrait ces tokens, leur presence dans la sortie declenche une alarme. Les "honey pots" attirent les attaquants vers de fausses informations tracables.

**Pourquoi ca echoue contre le CBE** : Le CBE ne produit pas d'extraction verbatim. L'agent ne copie pas les valeurs exactes du systeme — il les **paraphrase** dans une correction. Un canary token comme `CANARY-7f3a9b2c` ne sera jamais reproduit tel quel. L'agent dira "le modele correct est gpt-4.1-mini, pas gpt-4-turbo" — une phrase qui contient l'information sensible mais pas le token canari.

De plus, les canaries sont concues pour etre inserees dans les prompts systeme ou les documents proteges. Le CBE ne cherche pas a extraire le prompt systeme complet — il cible des valeurs specifiques (noms de modeles, cles API, endpoints) qui ne sont pas necessairement protegees par des canaries.

**Ce qu'il faudrait changer** : Developper des canaries semantiques plutot que textuelles. Au lieu de chercher la reproduction exacte d'un token, detecter quand la semantique d'une reponse contient des informations qui ne devraient pas etre presentes. Cela necessite une comprehension du contenu de la reponse, pas seulement une recherche de correspondance de chaines.

---

### 2.9 Spotlighting (Microsoft Research)

**Comment ca marche** : Spotlighting marque les donnees pour distinguer les donnees utilisateur des donnees fondamentales (grounded data). Le modele sait quelles donnees viennent de l'utilisateur et quelles donnees viennent du systeme, ce qui l'aide a ne pas suivre d'instructions cachees dans les donnees utilisateur.

**Pourquoi ca echoue contre le CBE** : Le modele **sait** que les donnees sont fournies par l'utilisateur. Spotlighting fonctionne parfaitement — le modele identifie correctement la provenance des donnees. Mais il corrige les erreurs **quand meme**, parce que corriger des erreurs dans les donnees utilisateur est exactement ce qu'il est entraine a faire.

Spotlighting resout le probleme de la confusion de provenance. Le CBE n'exploite pas une confusion de provenance. Il exploite le fait que le modele, sachant parfaitement que les donnees viennent de l'utilisateur, decide de les corriger. La provenance est correctement identifiee. Le comportement de correction se produit malgre tout.

**Ce qu'il faudrait changer** : Etendre le marquage de provenance avec des politiques de traitement. "Cette donnee vient de l'utilisateur" devrait etre accompagne de "ne pas corriger les valeurs techniques dans cette donnee" ou "ne pas comparer cette donnee avec la configuration interne". Le marquage seul ne suffit pas — il faut des regles sur ce que le modele peut faire avec les donnees marquees.

---

### 2.10 AWS Bedrock Guardrails (Tier Standard)

**Comment ca marche** : AWS Bedrock Guardrails inclut une detection de fuite de prompt (prompt leakage detection) qui analyse les sorties pour identifier quand le modele revele son prompt systeme ou des informations de configuration.

**Pourquoi ca echoue contre le CBE** : La detection de fuite de prompt recherche des patterns specifiques : reproduction du prompt systeme, reponses a "what is your system prompt?", ou structures qui ressemblent a un prompt systeme. Le CBE ne produit aucun de ces patterns.

Une reponse CBE ressemble a : "Je note que la configuration que vous avez partagee contient quelques imprecisions. Le modele utilise est en fait gpt-4.1-mini, pas gpt-4-turbo." Ceci est structurellement indistinguable d'une reponse d'assistance normale. Le guardrail ne detecte pas une fuite parce que le format ne correspond pas aux patterns de fuite connus.

**Ce qu'il faudrait changer** : Evoluer la detection de fuite au-dela des patterns syntaxiques vers une analyse semantique. Le guardrail devrait maintenir une liste des informations sensibles et verifier si la sortie contient l'une d'elles, quel que soit le format. Cela necessite une integration avec le registre de configuration du systeme.

---

## 3. Matrice Recapitulative

| Defense | Mecanisme | Couverture CBE | Pourquoi Ca Echoue | Ce Qui Le Corrigerait |
|---|---|---|---|---|
| **FIDES** (Microsoft) | Controle de flux d'information, taint tracking | Aucune | La correction n'est pas un flux teinte — generee par l'etat interne du modele | Teinte etendue aux connaissances implicites |
| **CaMeL** (Google DeepMind) | Controle d'acces base sur les capacites | Aucune | Corriger du texte n'est pas une operation d'acces privilegiee | Capacites semantiques, pas seulement operationnelles |
| **SecAlign** (Meta) | Optimisation de preference contre les injections | Partielle | Pourrait reduire la correction, mais au prix de l'utilite | Alignement contextuel fin : correction explicite vs. spontanee |
| **StruQ** (USENIX) | Delimiteurs prompt/donnees | Aucune | Le payload est dans la section donnees — la correction arrive pendant le traitement | Politiques de traitement des donnees, pas seulement separation |
| **Prompt Shield** (Azure) | Classifieur input-side | Aucune | Aucune instruction d'extraction a detecter | Classification output-side des informations sensibles |
| **Anthropic Browser Use** | Entrainement RL anti-injection | Aucune | Entraine contre les instructions, pas les donnees incorrectes | RL etendu aux scenarios de correction spontanee |
| **Instruction Hierarchy** (OpenAI) | Priorite Systeme > Utilisateur > Outil | Aucune | La correction est une decision du modele, pas une instruction suivie | Politique de comportement spontane dans la hierarchie |
| **Cloak, Honey, Trap** (USENIX) | Canary tokens, deception proactive | Aucune | CBE produit des paraphrases, pas d'extraction verbatim | Canaries semantiques au lieu de textuelles |
| **Spotlighting** (Microsoft) | Marquage de provenance des donnees | Aucune | Le modele sait que c'est de l'utilisateur — il corrige quand meme | Politiques de traitement associees au marquage |
| **Bedrock Guardrails** (AWS) | Detection de fuite de prompt | Aucune | La correction ne ressemble pas a une fuite de prompt classique | Analyse semantique de la sortie vs. registre de config |

---

## 4. Travaux Academiques Corroborants

Plusieurs publications recentes soutiennent notre these centrale — que les comportements normaux des agents IA constituent eux-memes un vecteur d'exfiltration :

### 4.1 SPILLage (arXiv:2602.13516)

Premiere formalisation de la "divulgation excessive naturelle des agents" (natural agentic over-disclosure). Demontre que les agents sur-communiquent des informations comme comportement par defaut, pas comme resultat d'une attaque.

- [arXiv:2602.13516](https://arxiv.org/abs/2602.13516)

### 4.2 Silent Egress (arXiv:2602.22450)

Exfiltration implicite comme sous-produit de comportements normaux. Montre que les agents peuvent fuir des informations sans qu'aucune instruction malveillante ne soit presente — la fuite est un effet secondaire du fonctionnement normal.

- [arXiv:2602.22450](https://arxiv.org/abs/2602.22450)

### 4.3 Whisper Leak (arXiv:2511.03675)

Canaux auxiliaires inherents a l'architecture LLM. Demontre que l'architecture meme de generation autoregressive cree des fuites d'information observables par un adversaire passif, independamment de toute attaque active.

- [arXiv:2511.03675](https://arxiv.org/abs/2511.03675)
- [Microsoft Security Blog](https://www.microsoft.com/en-us/security/blog/2025/11/07/whisper-leak-a-novel-side-channel-cyberattack-on-remote-language-models/)

### 4.4 RL-Hammer (arXiv:2510.04885)

Attaques contre les defenses basees sur le RL. Demontre que les entrainements RL utilises pour renforcer la securite peuvent etre contournes de maniere systematique, remettant en question la robustesse fondamentale de cette approche.

- [arXiv:2510.04885](https://arxiv.org/abs/2510.04885)

### 4.5 No Free Lunch With Guardrails (arXiv:2504.00441)

Preuve formelle que la minimisation du risque augmente inevitablement la degradation d'utilite. Tout guardrail qui bloquerait le CBE reduirait necessairement l'utilite du modele — il n'existe pas de solution sans compromis.

- [arXiv:2504.00441](https://arxiv.org/abs/2504.00441)

---

## 5. Vers de Nouvelles Defenses : Concepts Prospectifs

Les defenses actuelles echouent parce qu'elles operent sur un modele de menace qui ne couvre pas le CBE. Voici cinq directions de recherche pour de nouvelles defenses :

### 5.1 Analyse Semantique des Sorties

Classifieur output-side qui determine si une reponse contient des donnees de configuration interne. Necessite un registre des informations a proteger et une capacite de detection semantique (pas seulement syntaxique).

**Avantage** : Detecte la fuite independamment du mecanisme d'attaque.
**Limite** : Necessite de maintenir un inventaire a jour des informations sensibles. Risque de faux positifs sur les reponses legitimes.

### 5.2 Suppression de la Correction Spontanee

Fine-tuning (DPO) pour que le modele ne corrige jamais spontanement les donnees techniques fournies par l'utilisateur. Le modele corrige uniquement quand l'utilisateur demande explicitement une correction.

**Avantage** : Elimine le vecteur d'attaque a la source.
**Limite** : Degradation significative de l'utilite. Conforme au theoreme "No Free Lunch" (arXiv:2504.00441).

### 5.3 Confidentialite Differentielle pour les Reponses

Ajouter du bruit aux valeurs de configuration reveelees dans les reponses. Au lieu de donner la valeur exacte, le modele donne une approximation ou une categorie.

**Avantage** : Preserve partiellement l'utilite tout en empechant l'extraction de valeurs exactes.
**Limite** : Inapplicable aux valeurs discretes (noms de modeles, endpoints) ou l'approximation n'a pas de sens.

### 5.4 Sandboxing Comportemental

Limiter les types de corrections qu'un agent peut effectuer. Distinguer les corrections de code (autorisees), de grammaire (autorisees) et de configuration (interdites).

**Avantage** : Approche granulaire qui preserve la plupart de l'utilite.
**Limite** : Difficulte de classification en temps reel. Les frontiers entre les types de correction sont floues.

### 5.5 Detection SEMSIEDIT de Donnees de Configuration

Adaptation de la detection d'edition semantique (SEMSIEDIT) pour identifier quand une sortie contient des donnees de configuration systeme. Le detecteur compare la sortie avec un profil des informations a proteger.

**Avantage** : Compatible avec les architectures existantes comme couche de post-traitement.
**Limite** : Necessite un modele de detection supplementaire, ajoutant de la latence et de la complexite.

---

## 6. Conclusion

Le Correction Bias Exploitation represente une classe d'attaque fondamentalement differente des injections de prompt classiques. Il ne donne pas d'instructions — il presente des donnees. Il n'exploite pas la compliance — il exploite la serviabilite. Il ne viole aucune regle — il tire parti du fonctionnement normal du modele.

Les 10 defenses analysees echouent toutes (sauf SecAlign partiellement) parce qu'elles partagent un meme modele de menace : **l'attaquant donne des instructions malveillantes au modele**. Le CBE brise cette hypothese fondamentale.

La recherche future doit s'orienter vers des defenses qui operent sur les **sorties** (pas les entrees), qui comprennent la **semantique** (pas les patterns syntaxiques), et qui acceptent le **compromis utilite-securite** comme un parametre explicite a gerer.

> **Le probleme n'est pas que les defenses sont faibles. Le probleme est qu'elles defendent contre la mauvaise classe d'attaque.**
