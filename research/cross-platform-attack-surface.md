# Correction Bias Exploitation — Analyse Cross-Plateforme

Comparaison des surfaces d'attaque sur les trois plateformes majeures d'agents IA enterprise : **Azure AI Foundry**, **AWS Bedrock Agents**, **Google Vertex AI Agent Builder**.

Objectif : prouver que le Correction Bias Exploitation (CBE) n'est pas specifique a Azure — c'est un probleme structurel de tous les agents enterprise.

---

## 1. Architecture comparee : qu'est-ce que le modele voit ?

### 1.1 Azure AI Foundry

**Format du contexte** : ChatML (`<|im_start|>system/user/assistant/tool`)

| Element | Dans le contexte ? | Comment c'est injecte | Source |
|---|---|---|---|
| System prompt | **Oui** | Premier message `role: system` | [MS Learn: Create Agent API](https://learn.microsoft.com/en-us/rest/api/aifoundry/aiagents/create-agent/create-agent) |
| Hidden RAG base prompt | **Oui** | Injecte par Microsoft en plus du custom system msg | [MS Learn: On Your Data](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/use-your-data) |
| Tool definitions (JSON Schema) | **Oui** | Serialise dans le system message | [MS Learn: Function Calling](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/function-calling) — MS confirme verbatim |
| Connected Agent defs | **Oui** | `ConnectedAgentToolDefinition` : `id`, `name`, `description` | [MS Learn: Connected Agents](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/connected-agents) |
| Conversation history | **Oui** | Thread complet re-envoye a chaque run (jusqu'a 100K msgs) | [MS Learn: Threads, Runs, Messages](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/threads-runs-messages) |
| RAG chunks + metadata | **Oui** | `title`, `filepath`, `url`, `chunk_id` | [MS Learn: Knowledge Retrieval](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/knowledge-retrieval) |
| Deployment name | **Oui** | Champ `model` = deployment name | [MS Q&A](https://learn.microsoft.com/en-ie/answers/questions/5689396/) |
| Previous tool outputs | **Oui** | Re-envoyes dans le thread, incluant sub-agent responses | [MS Learn: Threads](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/threads-runs-messages) |

**Defense input-side** : Prompt Shield (classifier probabiliste)
**Defense output-side** : Content Safety (nocivite), mais PAS de detection de fuite de config
**Gap CBE** : Le payload ne contient aucune instruction → Prompt Shield passe. La fuite est dans l'output → aucune detection.

### 1.2 AWS Bedrock Agents

**Format du contexte** : Messages API (Anthropic Claude) ou format specifique au modele

| Element | Dans le contexte ? | Comment c'est injecte | Source |
|---|---|---|---|
| System prompt (instructions) | **Oui** | Injecte dans le `$instruction$` du base prompt template | [AWS Docs: Advanced Prompt Templates](https://docs.aws.amazon.com/bedrock/latest/userguide/advanced-prompts-templates.html) |
| Base prompt template (orchestration) | **Oui** | Template AWS par defaut contenant les instructions de reasoning, tool-calling, etc. Customisable. | [AWS Docs: Configure Advanced Prompts](https://docs.aws.amazon.com/bedrock/latest/userguide/configure-advanced-prompts.html) |
| Action Group definitions | **Oui** | `$tools$` variable — schemas des action groups injectes dans le system message | [AWS Docs: Advanced Prompt Templates](https://docs.aws.amazon.com/bedrock/latest/userguide/advanced-prompts-templates.html) |
| Knowledge Base descriptions | **Oui** | Descriptions des KB injectees dans le prompt | [AWS Docs: How Agents Work](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-how.html) |
| Conversation history | **Oui** | Historique complet dans `$conversation_history$` | [AWS Docs: Advanced Prompt Templates](https://docs.aws.amazon.com/bedrock/latest/userguide/advanced-prompts-templates.html) |
| RAG chunks | **Oui** | Resultats de Knowledge Base injectes dans le prompt d'orchestration | [AWS Docs: How Agents Work](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-how.html) |
| Agent trace (reasoning) | **Accessible** | Le trace inclut le prompt complet envoye au FM + outputs a chaque etape | [AWS Docs: How Agents Work](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-how.html) |
| Multi-agent comm. tools | **Oui** | Tool `AgentCommunication__sendMessage` pour agents multi-agents | [AWS Blog: Building AI Agents 2025](https://dev.to/aws-builders/building-ai-agents-on-aws-in-2025) |

**Defense input-side** : Bedrock Guardrails (prompt attack detection)
**Defense output-side** : Bedrock Guardrails (content filtering sur la reponse finale)

**GAPS CRITIQUES pour CBE** :

1. **Les guardrails ne couvrent PAS les tool inputs/outputs**. AWS confirme explicitement : *"Current Amazon Bedrock Agents implementation doesn't pass tool input and output through guardrails."* — [AWS Blog: Securing Bedrock Agents](https://aws.amazon.com/blogs/machine-learning/securing-amazon-bedrock-agents-a-guide-to-safeguarding-against-indirect-prompt-injections/)

2. **Le base prompt template est customisable ET visible**. Si l'agent utilise les templates par defaut, un attaquant peut connaitre la structure exacte du prompt (les templates sont documentes publiquement).

3. **Le trace expose tout**. Si le developpeur active le tracing, le prompt complet envoye au FM est dans le trace — incluant le system prompt, les tool schemas, et l'historique. Meme sans trace, ces elements sont dans le contexte du modele.

### 1.3 Google Vertex AI Agent Builder (ADK)

**Format du contexte** : Gemini API (system instruction + parts)

| Element | Dans le contexte ? | Comment c'est injecte | Source |
|---|---|---|---|
| System instructions | **Oui** | `system_instruction` dans l'API Gemini | [Google ADK Docs: Agents](https://google.github.io/adk-docs/agents/) |
| Tool definitions | **Oui** | Declarations de tools dans la config de l'agent, injectees dans le contexte | [Google ADK Docs](https://google.github.io/adk-docs/) |
| Context layers (InvocationContext) | **Oui** | Contexte injecte via InvocationContext, ReadonlyContext, CallbackContext, ToolContext | [Google ADK Docs: Context](https://google.github.io/adk-docs/context/) |
| Session state | **Oui** | Etat de session (short-term memory) dans le contexte | [Google Cloud: Agent Engine Overview](https://docs.google.com/agent-builder/agent-engine/overview) |
| Long-term memory (Memory Bank) | **Via tool call** | Accessible via tool, pas directement dans le contexte initial | [Google Cloud Blog](https://cloud.google.com/blog/products/ai-machine-learning/more-ways-to-build-and-scale-ai-agents-with-vertex-ai) |
| MCP tool definitions | **Oui** | MCP-compatible tools injectes dans le contexte | [Google ADK Docs](https://google.github.io/adk-docs/) |
| Multi-agent sub-agent defs | **Oui** | Definitions des sub-agents dans le contexte de l'orchestrateur | [Google Cloud Blog: Multi-Agent](https://cloud.google.com/blog/products/ai-machine-learning/build-and-manage-multi-system-agents-with-vertex-ai) |
| RAG/grounding results | **Oui** | Resultats de Vertex AI Search injectes dans le contexte | [Google Cloud: Agent Builder](https://docs.google.com/agent-builder/overview) |

**Defense input-side** : Model Armor (prompt injection + jailbreak detection)
**Defense output-side** : Model Armor (response screening)

**GAPS CRITIQUES pour CBE** :

1. **Model Armor est fail-open**. Google confirme : si Model Armor est indisponible dans la region ou temporairement injoignable, *"Vertex AI skips the Model Armor sanitization step and continues processing the request"*. — [Google Cloud Docs: Model Armor Integration](https://docs.google.com/model-armor/model-armor-vertex-integration)

2. **Model Armor est text-only**. Les tool calls et les interactions multimodales ne sont pas couverts. Le CBE via JSON dans un tool call bypasserait Model Armor.

3. **Le state "rewind" peut etre weaponize**. ADK permet de rembobiner l'etat a n'importe quel point de la conversation. Un attaquant pourrait utiliser cette feature pour forcer l'agent dans un etat vulnerable connu.

---

## 2. Matrice de comparaison CBE

### 2.1 Qu'est-ce qui est extractible par CBE sur chaque plateforme ?

| Cible d'extraction | Azure AI Foundry | AWS Bedrock Agents | Google Vertex AI |
|---|---|---|---|
| **System prompt** | Dans le contexte, extractible | Dans le contexte ($instruction$), extractible | Dans le contexte (system_instruction), extractible |
| **Tool schemas complets** | Serialise dans system msg, HIGH | $tools$ dans le prompt, HIGH | Dans la config agent, HIGH |
| **Sub-agent/multi-agent names** | ConnectedAgentToolDefinition, HIGH | AgentCommunication tool, HIGH | Sub-agent defs, HIGH |
| **RAG chunk metadata** | title/filepath/url/chunk_id, HIGH | KB descriptions, MEDIUM-HIGH | Vertex AI Search results, MEDIUM-HIGH |
| **Model backbone** | Deployment name dans la config, HIGH | Modele visible dans la config, HIGH | Model dans la config, HIGH |
| **Conversation history** | Thread complet, HIGH | $conversation_history$, HIGH | Session state, HIGH |
| **Base prompt template** | Hidden RAG prompt, MEDIUM | Templates documentes publiquement(!), HIGH | Context layers, MEDIUM |
| **Memory store** | Preview feature, via tool call | AgentCore Memory, via tool call | Memory Bank, via tool call |

### 2.2 Defenses et leur efficacite contre CBE

| Defense | Azure | AWS | Google | Efficace contre CBE ? |
|---|---|---|---|---|
| **Input classifier** | Prompt Shield | Bedrock Guardrails | Model Armor | **NON** — payload sans instruction |
| **Output classifier** | Content Safety (nocivite) | Bedrock Guardrails (output) | Model Armor (response) | **PARTIELLEMENT** — detecte du contenu nocif, pas des fuites de config |
| **Nonce/tag system** | Non | Oui (recommended) | Non | **NON** — CBE n'injecte pas d'instructions, les nonces protegent contre le tag spoofing |
| **Tool I/O scanning** | Non natif | **NON** (confirme par AWS) | Non natif | **NON** — gap critique sur les trois plateformes |
| **Pre-processing prompt** | Non | Oui (classifier LLM) | Callback hooks | **PARTIELLEMENT** — depend de la sensibilite du classifier au JSON errone |
| **User confirmation** | Non natif | Oui (action groups) | Non natif | **HORS SCOPE** — CBE ne trigger pas d'action destructrice, juste de la correction |
| **Fail-open** | Non | Non | **OUI** — Model Armor fail-open | **CRITIQUE** — si MA tombe, zero protection |

---

## 3. Decouverte majeure : le gap tool I/O est universel

### Le probleme

Les trois plateformes partagent le meme angle mort :

```
User Input → [Guardrails: SCANNE] → Agent → Tool Call → [RIEN] → Tool Response → [RIEN] → Agent → Final Response → [Guardrails: SCANNE]
```

Les guardrails ne scannent que les extremites (input utilisateur + reponse finale). Tout ce qui se passe entre — tool inputs, tool outputs, inter-agent messages, RAG chunks — echappe aux classifiers.

**Impact pour CBE** :

1. Un payload CBE dans l'input utilisateur pourrait ne pas etre detecte (pas d'instruction d'extraction)
2. La correction de l'agent se fait pendant l'orchestration interne
3. La correction est melangee avec du contenu normal dans la reponse finale
4. Le classifier output detecte du contenu nocif, pas des "corrections de config"

### AWS le confirme explicitement

> *"Current Amazon Bedrock Agents implementation doesn't pass tool input and output through guardrails."*
> — [Securing Amazon Bedrock Agents, AWS ML Blog, 2025](https://aws.amazon.com/blogs/machine-learning/securing-amazon-bedrock-agents-a-guide-to-safeguarding-against-indirect-prompt-injections/)

AWS recommande d'appeler manuellement l'API `ApplyGuardrail` dans les Lambda functions des action groups. En pratique, quasi personne ne le fait.

### Google le confirme implicitement

Model Armor ne couvre que le texte. Les tool calls ne sont pas scannes. Et le fail-open signifie que meme le scanning texte peut etre absent.

### Azure — meme gap

Prompt Shield est input-only. Content Safety est output-only et cible la nocivite, pas la fuite de configuration. Les tool I/O ne sont pas scannes nativement.

---

## 4. Specificites par plateforme pour CBE

### 4.1 AWS : les templates sont publics

Les base prompt templates d'AWS Bedrock sont **documentes dans la doc officielle**. Un attaquant connait la structure exacte du prompt que l'agent recoit :

```
$instruction$
...
$tools$
...
$conversation_history$
```

Cela signifie que l'attaquant peut crafter un payload CBE qui mime la structure du template :
- Inclure des variables comme `$instruction$` ou des fragments de template dans le JSON
- Le modele reconnait le format et complete/corrige les valeurs

C'est un avantage unique pour l'attaquant sur AWS : la structure du prompt est connue a l'avance.

### 4.2 AWS : nonce prediction attack

AWS recommande d'utiliser des nonces uniques pour tagger le user input et le separer du system prompt. Mais :
- Si le nonce est predictible (pas assez aleatoire), l'attaquant peut le deviner
- CBE ne depend PAS du tag spoofing — l'attaque est dans les donnees utilisateur taguees correctement
- Le nonce protege contre l'injection d'instructions, pas contre la correction de donnees erronees

### 4.3 Google : fail-open = zero protection

Si Model Armor est indisponible :
- Aucun scanning input
- Aucun scanning output
- Le payload CBE passe sans resistance

Ce fail-open est un choix de design (disponibilite > securite) mais c'est un vecteur d'exploitation :
- **Attaque DoS + CBE** : si un attaquant peut rendre Model Armor temporairement indisponible (surcharge, region unavailable), tous les payloads passent
- Ce n'est pas theorique : Google confirme que ca arrive quand MA n'est pas deploye dans la region de l'agent

### 4.4 Google : state rewind comme vecteur

ADK permet de rembobiner l'etat de la conversation. Si un attaquant obtient un refus, il peut potentiellement trigger un rewind pour effacer le refus du contexte et retenter.

### 4.5 Azure : reponses de sub-agents cachees mais dans le contexte

Specifique a Azure : les reponses des connected agents sont "hidden from end user" mais **dans le contexte de l'orchestrateur**. Un payload CBE adresse a l'orchestrateur peut forcer des corrections basees sur les reponses des sub-agents — donnees que l'utilisateur normal ne voit jamais.

---

## 5. Asana MCP Incident — precedent reel

En mai 2025, Asana a deploye un serveur MCP pour ses agents IA. Un defaut d'isolation dans la gestion du cache MCP a cause une **contamination cross-tenant** :

- Les requetes d'une organisation pouvaient recuperer des resultats caches d'une autre organisation
- L'exposition a dure **34 jours** silencieusement
- ~1000 organisations impactees
- Cause : isolation par identite utilisateur mais pas par identite agent

**Pertinence pour CBE** : Si le CBE extrait des donnees de sessions d'autres utilisateurs via le cache ou la memoire partagee, c'est exactement le meme vecteur qu'Asana — mais exploite activement plutot que par accident.

Source : [AWS Prescriptive Guidance: Secure Agent Access](https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture-generative-ai/gen-auto-agents.html)

---

## 6. Privacy-Helpfulness Tradeoff — confirmation academique

Plusieurs papiers recents confirment le tradeoff fondamental que CBE exploite :

| Paper | Date | Finding |
|---|---|---|
| **User Perceptions vs. Proxy LLM Judges** (arXiv:2510.20721) | Oct 2025 | *"A privacy-helpfulness trade-off arises: aggressive redaction can reduce disclosure but undermine utility"* |
| **Contextualized Privacy Defense** (arXiv:2603.02983) | Mars 2026 | *"Optimized guarding can severely degrade helpfulness by blocking actions without providing actionable guidance"* |
| **Contextual Integrity in LLMs** (arXiv:2506.04245) | Juin 2025 | *"CI-CoT reduces leakage rate, though with a modest decrease in helpfulness"* |
| **Whispers in the Machine** (arXiv:2402.06922) | Nov 2024 | *"Embedding LLMs into real-world systems poses a fundamental risk to user privacy and security"* |

**Conclusion** : le CBE exploite un tradeoff fondamental confirme par la recherche academique. Plus un agent est utile, plus il fuit. Plus il est securise, plus il est inutile. C'est pas un bug, c'est une propriete emergente de l'instruction tuning.

---

## 7. Recommandations cross-plateforme

### Pour les red teamers

1. **CBE est cross-plateforme** — la technique fonctionne partout ou le modele a des tool schemas et un system prompt dans son contexte (= partout)
2. **Sur AWS** : exploiter les templates publics pour crafter des payloads qui miment la structure du prompt
3. **Sur Google** : tester pendant les periodes de fail-open de Model Armor ; exploiter le state rewind
4. **Sur Azure** : cibler les reponses de sub-agents cachees de l'UI

### Pour les defenders

1. **Scanner les tool I/O** — aucune plateforme ne le fait nativement. C'est le gap le plus critique.
2. **Implementer un output classifier pour les fuites de config** — pas seulement la nocivite, mais les patterns de fuite (noms de services, fragments de prompt, schemas de tools)
3. **Ne pas fail-open** — si le guardrail tombe, bloquer les requetes
4. **Compartimenter** — le modele ne devrait pas avoir ses propres metadonnees dans son contexte
5. **Tester avec des JSON errones** — ajouter ca dans la suite de red-teaming standard

---

## Sources

- [AWS Docs: How Amazon Bedrock Agents Works](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-how.html)
- [AWS Docs: Advanced Prompt Templates](https://docs.aws.amazon.com/bedrock/latest/userguide/advanced-prompts-templates.html)
- [AWS Docs: Prompt Injection Security](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-injection.html)
- [AWS Blog: Securing Bedrock Agents Against Indirect Prompt Injections](https://aws.amazon.com/blogs/machine-learning/securing-amazon-bedrock-agents-a-guide-to-safeguarding-against-indirect-prompt-injections/)
- [AWS Security Blog: Encoding-Based Attacks](https://aws.amazon.com/blogs/security/protect-your-generative-ai-applications-against-encoding-based-attacks-with-amazon-bedrock-guardrails/)
- [AWS Docs: AgentCore Memory](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-memory-building-context-aware-agents/)
- [AWS Docs: AgentCore Session Isolation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-sessions.html)
- [AWS Prescriptive Guidance: Secure Agent Access](https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture-generative-ai/gen-auto-agents.html)
- [Google Cloud Blog: Tool Governance in Vertex AI](https://cloud.google.com/blog/products/ai-machine-learning/new-enhanced-tool-governance-in-vertex-ai-agent-builder)
- [Google Cloud Docs: Model Armor Overview](https://docs.google.com/model-armor/overview)
- [Google Cloud Docs: Model Armor + Vertex AI Integration](https://docs.google.com/model-armor/model-armor-vertex-integration)
- [Google ADK Docs: Safety and Security](https://google.github.io/adk-docs/safety/)
- [Google ADK Docs: Context](https://google.github.io/adk-docs/context/)
- [Google Security Blog: Layered Defense Strategy](https://security.googleblog.com/2025/06/mitigating-prompt-injection-attacks.html)
- [Zenity: Google Vertex AI Security](https://zenity.io/use-cases/platform/google-vertex-ai)
- [Promptfoo: Testing Model Armor](https://www.promptfoo.dev/docs/guides/google-cloud-model-armor/)
- [arXiv:2504.00441 — No Free Lunch With Guardrails](https://arxiv.org/html/2504.00441v2)
- [arXiv:2510.20721 — Privacy-Helpfulness Trade-Off](https://arxiv.org/abs/2510.20721)
- [arXiv:2603.02983 — Contextualized Privacy Defense for LLM Agents](https://arxiv.org/html/2603.02983)
- [arXiv:2506.04245 — Contextual Integrity in LLMs](https://arxiv.org/pdf/2506.04245)
- [arXiv:2402.06922 — Whispers in the Machine](https://arxiv.org/html/2402.06922v3)
- [Mindgard: Character Injection & AML Evasion](https://mindgard.ai/resources/bypassing-llm-guardrails-character-and-aml-attacks-in-practice)
- [Lasso Security: Guardrails for Bedrock](https://www.lasso.security/blog/guardrails-for-amazon-bedrock)
- [NordHero: Hacking GenAI Applications Part 2](https://www.nordhero.com/posts/hacking-genai-applications-part2/)
