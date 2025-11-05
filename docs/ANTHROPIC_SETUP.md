# 🌉 Guide d'Intégration Anthropic - Super Claude

Guide complet pour configurer et utiliser l'équipe d'agents Anthropic dans Super Claude Multi-Agents.

## 📋 Table des Matières

- [Vue d'ensemble](#vue-densemble)
- [Installation](#installation)
- [Configuration](#configuration)
- [Agents Disponibles](#agents-disponibles)
- [Utilisation](#utilisation)
- [Architecture](#architecture)
- [Tests](#tests)
- [Dépannage](#dépannage)
- [Best Practices](#best-practices)

---

## 🎯 Vue d'ensemble

L'intégration Anthropic dans Super Claude fournit **3 agents spécialisés** accessibles via un bridge JSON-RPC MCP :

| Agent | Rôle | Cas d'usage |
|-------|------|-------------|
| **research_agent** | Recherche & Synthèse | Analyse de questions, veille techno, résumés structurés |
| **code_agent** | Génération de Code | Développement, refactoring, analyse de code |
| **writing_agent** | Rédaction & Édition | Amélioration de contenu, newsletters, documentation |

### ✨ Avantages

- **Spécialisation** : Chaque agent est optimisé pour sa tâche
- **Performance** : Prompts spécialisés = meilleurs résultats
- **Économie** : Filtrage local avant délégation (jusqu'à 98% d'économie de tokens)
- **Isolation** : Architecture bridge sécurisée
- **Traçabilité** : Tracking détaillé des tokens et performances

---

## 📦 Installation

### 1. Dépendances

```bash
# Installer les dépendances
pip install -r requirements.txt

# Vérifier l'installation du SDK Anthropic
python -c "import anthropic; print(anthropic.__version__)"
```

### 2. Clé API

Obtenir une clé API Anthropic :

1. Créer un compte sur [console.anthropic.com](https://console.anthropic.com)
2. Naviguer vers **API Keys**
3. Générer une nouvelle clé (`sk-ant-api03-...`)

---

## ⚙️ Configuration

### 1. Variables d'environnement

Copier et remplir `.env.example` :

```bash
cp .env.example .env
```

Configuration minimale dans `.env` :

```bash
# Obligatoire
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE

# Optionnel
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022  # Défaut
BRIDGE_TIMEOUT=60                            # Timeout en secondes
```

### 2. Modèles disponibles

| Modèle | Description | Coût | Usage recommandé |
|--------|-------------|------|------------------|
| `claude-3-5-sonnet-20241022` | **Recommandé** - Équilibre optimal | $$ | Production générale |
| `claude-3-opus-20240229` | Performances maximales | $$$ | Tâches critiques complexes |
| `claude-3-sonnet-20240229` | Économique | $ | Dev, tests, prototypage |

### 3. Vérification

```bash
# Tester la configuration
python config/settings.py

# Output attendu :
# ✅ Bridge Anthropic: /path/to/agents/anthropic/bridge.py
# ⚙️ Modèle Anthropic: claude-3-5-sonnet-20241022
```

---

## 🤖 Agents Disponibles

### 1. Research Agent 🔍

**Rôle** : Recherche et synthèse d'informations

**Paramètres** :
- `query` (string, obligatoire) : Question ou sujet à analyser
- `depth` (string, optionnel) : Profondeur d'analyse
  - `"quick"` : Résumé rapide (2K tokens max)
  - `"standard"` : Analyse standard (4K tokens) **[défaut]**
  - `"deep"` : Analyse approfondie (8K tokens)

**Format de sortie** :
```json
{
  "summary": "Résumé exécutif en 2-3 phrases",
  "key_points": [
    "Point clé 1",
    "Point clé 2"
  ],
  "insights": [
    "Insight analytique 1"
  ],
  "recommendations": [
    "Recommandation actionnable 1"
  ]
}
```

**Exemple d'usage** :
```python
result = await super_claude.delegate_to_anthropic(
    "research_agent",
    {
        "query": "Quelles sont les tendances Python pour l'IA en 2024?",
        "depth": "standard"
    }
)

print(result["result"]["summary"])
# "Python reste dominant dans l'IA avec PyTorch..."
```

---

### 2. Code Agent 💻

**Rôle** : Génération, analyse et refactoring de code

**Paramètres** :
- `task` (string, obligatoire) : Description de la tâche de code
- `language` (string, optionnel) : Langage cible (défaut : `"python"`)
- `context` (string, optionnel) : Code existant ou contraintes

**Format de sortie** :
```json
{
  "code": "# Code généré avec docstrings...",
  "explanation": "Explication des choix techniques",
  "tests": "# Tests unitaires pytest...",
  "notes": [
    "Complexité : O(n)",
    "Alternative : mémorisation"
  ]
}
```

**Exemple d'usage** :
```python
result = await super_claude.delegate_to_anthropic(
    "code_agent",
    {
        "task": "Implémenter un cache LRU thread-safe",
        "language": "python",
        "context": "Pour une API Flask avec 10K req/s"
    }
)

print(result["result"]["code"])
# from threading import Lock
# from collections import OrderedDict
# ...
```

---

### 3. Writing Agent ✍️

**Rôle** : Rédaction et édition de contenu

**Paramètres** :
- `content` (string, obligatoire) : Contenu à traiter
- `style` (string, optionnel) : Style cible (défaut : `"professional"`)
  - `"professional"` : Formel, précis
  - `"casual"` : Décontracté, accessible
  - `"technical"` : Documentation technique
  - `"marketing"` : Persuasif, engageant
- `task` (string, optionnel) : Type de tâche (défaut : `"improve"`)
  - `"improve"` : Améliorer le contenu
  - `"summarize"` : Résumer
  - `"expand"` : Développer avec détails
  - `"translate"` : Traduire (spécifier langue cible dans content)

**Format de sortie** :
```json
{
  "result": "Contenu traité...",
  "metadata": {
    "word_count": 150,
    "tone": "professional",
    "changes": [
      "Restructuré l'introduction",
      "Ajouté exemples concrets"
    ]
  }
}
```

**Exemple d'usage** :
```python
result = await super_claude.delegate_to_anthropic(
    "writing_agent",
    {
        "content": "Super Claude est un projet multi-agents...",
        "style": "marketing",
        "task": "improve"
    }
)

print(result["result"]["result"])
# "Révolutionnez votre workflow d'IA avec Super Claude..."
```

---

## 🚀 Utilisation

### Usage Basique

```python
import asyncio
from core.super_claude import SuperClaude

async def main():
    sc = SuperClaude()

    # Recherche
    result = await sc.delegate_to_anthropic(
        "research_agent",
        {"query": "Rust vs Go performance", "depth": "quick"}
    )

    print(f"Tokens utilisés: {result['tokens_used']['total']}")
    print(result["result"])

asyncio.run(main())
```

### Orchestration Multi-Agents

```python
from core.super_claude import AgentTask, AgentTeam

tasks = [
    # ADK collecte les données
    AgentTask(
        team=AgentTeam.ADK,
        agent_name="watch_collect",
        method="collect",
        params={"sources": ["github"]},
        priority=1
    ),
    # Anthropic analyse
    AgentTask(
        team=AgentTeam.ANTHROPIC,
        agent_name="research_agent",
        method="research",
        params={"query": "Analyser les tendances", "depth": "standard"},
        priority=2
    ),
    # Anthropic rédige
    AgentTask(
        team=AgentTeam.ANTHROPIC,
        agent_name="writing_agent",
        method="write",
        params={"content": "...", "style": "professional", "task": "improve"},
        priority=3
    )
]

results = await sc.orchestrate(tasks)
```

### Workflow Hybride (Économie de Tokens)

**Pattern recommandé** : Filtrage local → Anthropic analyse

```python
# ❌ MAUVAIS : Envoyer toutes les données brutes (300K tokens)
result = await sc.delegate_to_anthropic(
    "research_agent",
    {"query": f"Analyser ces 1000 repos : {all_repos}"}
)

# ✅ BON : Filtrage local puis analyse ciblée (6K tokens)
# 1. Collecte ADK
repos = await sc.delegate_to_adk("watch_collect", {...})

# 2. Filtrage local
trending = [r for r in repos if r["stars_growth"] > 100][:20]

# 3. Analyse Anthropic
summary = await sc.delegate_to_anthropic(
    "research_agent",
    {"query": f"Synthétiser les tendances de ces 20 repos : {trending}"}
)

# 💰 Économie : 98% de tokens (300K → 6K)
```

---

## 🏗️ Architecture

### Bridge JSON-RPC

```
┌─────────────┐
│ SuperClaude │
└──────┬──────┘
       │ JSON-RPC Request
       ├──────────────────────┐
       │                      │
┌──────▼──────┐      ┌────────▼────────┐
│ ADK Bridge  │      │ Anthropic Bridge│
└──────┬──────┘      └────────┬────────┘
       │                      │
┌──────▼──────┐      ┌────────▼────────┐
│ Google A2A  │      │  Anthropic API  │
│   Agents    │      │   (3 agents)    │
└─────────────┘      └─────────────────┘
```

### Flux de Communication

1. **Requête** : SuperClaude → Bridge (STDIO, JSON-RPC)
2. **Traitement** : Bridge → Anthropic API (SDK)
3. **Réponse** : API → Bridge (JSON) → SuperClaude (MCP format)

### Format JSON-RPC

**Requête** :
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "research_agent",
    "arguments": {
      "query": "Question",
      "depth": "standard"
    }
  }
}
```

**Réponse** :
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\"status\": \"success\", \"result\": {...}, \"tokens_used\": {...}}"
    }]
  }
}
```

---

## 🧪 Tests

### Tests Unitaires

```bash
# Tests de l'intégration Anthropic
pytest tests/unit/test_super_claude_anthropic.py -v

# Avec couverture
pytest tests/unit/test_super_claude_anthropic.py --cov=core --cov=agents/anthropic

# Marker spécifique
pytest -m anthropic
```

### Tests avec Mocks

Les fixtures dans `tests/fixtures/anthropic_responses.py` permettent de tester sans clé API :

```python
from tests.fixtures.anthropic_responses import RESEARCH_AGENT_SUCCESS

def test_with_mock(mocker):
    mock_proc = mocker.patch('asyncio.create_subprocess_exec')
    mock_proc.return_value.communicate.return_value = (
        json.dumps(RESEARCH_AGENT_SUCCESS).encode(),
        b""
    )
    # Test...
```

### Tests d'Intégration

```bash
# Nécessite ANTHROPIC_API_KEY
export ANTHROPIC_API_KEY=sk-ant-...

pytest tests/integration/test_anthropic_integration.py -v
```

---

## 🔧 Dépannage

### Problème : "Bridge Anthropic introuvable"

**Cause** : Chemin du bridge incorrect

**Solution** :
```bash
# Vérifier l'existence du fichier
ls -la agents/anthropic/bridge.py

# Ou définir explicitement
export ANTHROPIC_BRIDGE_PATH=/absolute/path/to/bridge.py
```

---

### Problème : "ANTHROPIC_API_KEY non configurée"

**Cause** : Variable d'environnement manquante

**Solution** :
```bash
# Vérifier
echo $ANTHROPIC_API_KEY

# Définir
export ANTHROPIC_API_KEY=sk-ant-api03-...

# Ou dans .env
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

---

### Problème : "Timeout après 60s"

**Cause** : Requête trop complexe ou API lente

**Solutions** :
1. Augmenter le timeout :
   ```bash
   export BRIDGE_TIMEOUT=120
   ```

2. Réduire la profondeur :
   ```python
   # Passer de "deep" à "standard"
   params={"query": "...", "depth": "standard"}
   ```

3. Simplifier la requête :
   ```python
   # Filtrer localement avant
   filtered_data = data[:100]  # Au lieu de 1000 items
   ```

---

### Problème : "Rate limit exceeded"

**Cause** : Trop de requêtes à l'API Anthropic

**Solutions** :
1. Implémenter un rate limiter :
   ```python
   import asyncio
   from asyncio import Semaphore

   semaphore = Semaphore(5)  # Max 5 concurrent

   async def call_with_limit():
       async with semaphore:
           return await sc.delegate_to_anthropic(...)
   ```

2. Utiliser le batching :
   ```python
   # Grouper les requêtes similaires
   queries = ["Q1", "Q2", "Q3"]
   combined = "\n".join(f"{i}. {q}" for i, q in enumerate(queries))
   result = await sc.delegate_to_anthropic("research_agent", {"query": combined})
   ```

---

### Problème : "Tokens used trop élevé"

**Cause** : Données non filtrées envoyées à l'API

**Solution** - Pattern hybride :
```python
# ❌ AVANT : 50K tokens
result = await sc.delegate_to_anthropic(
    "research_agent",
    {"query": f"Analyser : {huge_dataset}"}
)

# ✅ APRÈS : 5K tokens (90% économie)
# 1. Filtrage local
relevant = filter_locally(huge_dataset)  # Python natif
top_items = relevant[:20]

# 2. Envoi filtré
result = await sc.delegate_to_anthropic(
    "research_agent",
    {"query": f"Synthèse de : {top_items}"}
)
```

---

## 🎯 Best Practices

### 1. Progressive Disclosure

**Concept** : Ne révéler que les données pertinentes à l'agent

```python
# ❌ Envoyer tout le contexte
context = {
    "all_repos": [...],  # 100K lignes
    "all_issues": [...],  # 50K lignes
    "all_commits": [...]  # 200K lignes
}

# ✅ Contexte ciblé
context = {
    "trending_repos": top_20_repos,
    "key_metrics": summary_stats
}
```

### 2. Filtrage Local

**Utiliser Python natif pour les opérations simples** :

```python
# Filtrage, tri, déduplication → Python
filtered = [item for item in data if item["score"] > 80]
sorted_data = sorted(filtered, key=lambda x: x["date"])
unique = list(set(sorted_data))

# Analyse sémantique → Anthropic
analysis = await sc.delegate_to_anthropic(
    "research_agent",
    {"query": f"Identifier les patterns dans : {unique[:50]}"}
)
```

### 3. Prompts Structurés

**Fournir un contexte clair et des contraintes** :

```python
# ❌ Vague
query = "Analyser ce code"

# ✅ Structuré
query = """
Analyser ce code Python selon ces critères :
1. Sécurité (injections, validations)
2. Performance (complexité, optimisations)
3. Maintenabilité (documentation, tests)

Code :
```python
{code}
```

Format attendu : JSON avec {security: [], performance: [], maintainability: []}
"""
```

### 4. Gestion des Erreurs

**Toujours gérer les cas d'erreur** :

```python
result = await sc.delegate_to_anthropic("research_agent", params)

if result["status"] == "error":
    logger.error(f"Erreur Anthropic : {result['output']}")
    # Fallback ou retry
    return fallback_analysis(params)

elif result["status"] == "timeout":
    # Réessayer avec profondeur réduite
    params["depth"] = "quick"
    result = await sc.delegate_to_anthropic("research_agent", params)

else:
    # Succès
    return result["result"]
```

### 5. Monitoring & Logging

**Tracer les tokens et performances** :

```python
import time

start = time.time()
result = await sc.delegate_to_anthropic("code_agent", params)
duration = time.time() - start

logger.info(
    f"code_agent | "
    f"Duration: {duration:.2f}s | "
    f"Tokens: {result.get('tokens_used', {}).get('total', 0)}"
)
```

---

## 📊 Métriques & Optimisation

### Tracking des Coûts

```python
class TokenTracker:
    def __init__(self):
        self.total_tokens = 0
        self.total_cost = 0.0

    def track(self, result, model="claude-3-5-sonnet-20241022"):
        tokens = result.get("tokens_used", {})
        input_tokens = tokens.get("input", 0)
        output_tokens = tokens.get("output", 0)

        # Tarifs Sonnet 3.5 (exemple)
        input_cost = input_tokens * 0.003 / 1000   # $3 / 1M
        output_cost = output_tokens * 0.015 / 1000  # $15 / 1M

        self.total_tokens += tokens.get("total", 0)
        self.total_cost += input_cost + output_cost

tracker = TokenTracker()
result = await sc.delegate_to_anthropic(...)
tracker.track(result)

print(f"💰 Coût total : ${tracker.total_cost:.4f}")
```

---

## 🔗 Ressources

- [Documentation Anthropic](https://docs.anthropic.com)
- [SDK Python Anthropic](https://github.com/anthropics/anthropic-sdk-python)
- [MCP Specification](https://modelcontextprotocol.io)
- [Super Claude Architecture](../README.md)

---

## 📝 Changelog

- **v1.0.0** (2024-11-05) : Intégration initiale Anthropic
  - Bridge JSON-RPC STDIO
  - 3 agents spécialisés (research, code, writing)
  - Tests unitaires et fixtures
  - Documentation complète
