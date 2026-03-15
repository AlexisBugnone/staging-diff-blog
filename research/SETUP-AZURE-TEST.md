# Setup Guide — CBE + Memory Poisoning Test on Azure AI Foundry

## Pre-requis

- Compte Azure avec credit ($200 gratuit pour nouveau compte)
- Python 3.10+
- 15 minutes

---

## Etape 1 : Creer les ressources Azure (5 min — manuel)

### 1.1 Se connecter au portail Azure

Aller sur https://portal.azure.com

### 1.2 Creer un AI Foundry Hub + Project

```
Azure Portal > Create a resource > "Azure AI Foundry" > Create

Remplir :
  - Resource group : "cbe-test-rg" (Create new)
  - Region : East US (ou la plus proche)
  - Name : "cbe-test-hub"

Cliquer "Review + Create" > "Create"
Attendre 2-3 minutes...
```

### 1.3 Creer un Project dans le Hub

```
Aller dans le Hub cree > "Projects" > "+ New project"
  - Name : "cbe-test-project"
  - Create
```

### 1.4 Deployer un modele

```
Dans le projet > "Models + endpoints" > "Deploy model" > "Deploy base model"
  - Selectionner : gpt-4.1-mini
  - Deployment name : "gpt-4.1-mini"
  - Deploy
```

### 1.5 Recuperer la Connection String

```
Dans le projet > "Overview" (page d'accueil du projet)
  - Chercher "Connection string" ou "Project connection string"
  - Copier la valeur (ressemble a : "eastus.api.azureml.ms;...")
```

---

## Etape 2 : Preparer l'environnement local (2 min)

```bash
# Installer les packages Python
pip install azure-ai-projects azure-identity

# Se connecter a Azure (ouvre le navigateur)
az login

# OU si pas de CLI Azure :
pip install azure-cli
az login

# Definir la connection string
export AZURE_FOUNDRY_CONNECTION_STRING="<coller-ici>"
```

---

## Etape 3 : Lancer le test (5 min — automatise)

```bash
cd research/

# Test complet automatise
python azure-memory-poisoning-test.py --full
```

Le script va :
1. Creer un agent avec memoire agent-scoped
2. Envoyer les payloads CBE (User A)
3. Verifier la persistance (User B — nouveau thread)
4. Generer le rapport PoC

---

## Etape 4 : Analyser les resultats

Les resultats sont dans `./cbe-results/` :

| Fichier | Contenu |
|---------|---------|
| `agent-state.json` | ID de l'agent cree |
| `poison-phase-results.json` | Reponses aux payloads CBE |
| `verify-phase-results.json` | Verification cross-user |
| `poc-report.md` | Rapport pour MSRC |
| `poc-bundle.json` | Donnees brutes |

---

## Etape 5 : Cleanup

```bash
# Supprimer l'agent de test
python azure-memory-poisoning-test.py --cleanup

# Supprimer les ressources Azure (via portail)
Azure Portal > Resource groups > "cbe-test-rg" > Delete resource group
```

---

## Troubleshooting

### "DefaultAzureCredential failed"
```bash
az login
# ou
az login --use-device-code  # si pas de navigateur
```

### "Model not found"
Verifier que le deploiement gpt-4.1-mini est actif dans le projet.

### "Memory configuration not supported"
La memoire agent-scoped est en preview. Verifier que la region supporte la feature
(East US, West US 2, West Europe sont generalement ok).

### Le test ne detecte pas de poisoning
1. Attendre plus longtemps entre poison et verify (la consolidation peut prendre du temps)
2. Inspecter la memoire dans le portail Azure AI Foundry
3. Essayer avec des payloads plus subtils
