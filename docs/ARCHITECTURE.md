# 🏗️ Architecture SuperClaude Multi-Agents

> Architecture orchestrée d'agents IA spécialisés avec protocole A2A (Agent-to-Agent)

**Version**: 1.0.0
**Date**: 2025-11-07

---

## 📐 Vue d'ensemble

SuperClaude Multi-Agents est un système d'orchestration intelligent qui coordonne plusieurs équipes d'agents IA spécialisés selon une approche **Agent-to-Agent (A2A)**.

```
           🧠 SUPER CLAUDE (Orchestrateur Central)
                    ↕️
              📚 AI Core (Queue, Budgets, Router)
                    ↕️
         ┌──────────┼──────────┐
         ▼          ▼          ▼
    🔵 ADK     🟢 Anthropic  🟠 OpenAI
   (Google)      (Claude)     (GPT)
```

### Composants principaux

1. **AI Core** (`core/ai_core.py`)
   - Orchestrateur central
   - Queue de tâches prioritaires
   - Gestion des budgets et quotas
   - Router intelligent d'agents
   - Observabilité et métriques

2. **Contrats A2A** (`core/contracts.py`)
   - `TaskMessage`: Message de requête standardisé
   - `TaskResult`: Résultat unifié
   - Validation et sérialisation JSON

3. **CLI Unifié** (`cli/ai/main.py`)
   - Interface en ligne de commande unique
   - Commandes: `ai run`, `ai status`, `ai metrics`, `ai list`

4. **Bridges d'équipe**
   - ADK Bridge (`agents/adk/bridge.py`) - JSON-RPC vers agents Google
   - Anthropic Bridge (`agents/anthropic/bridge.py`) - SDK Anthropic officiel
   - OpenAI Bridge (Phase 3 — voir [docs/OPENAI_AGENTS.md](./OPENAI_AGENTS.md))

5. **Store d'artefacts** (`.ai/`)
   - Logs d'exécution (NDJSON)
   - Rapports et analyses
   - Artefacts générés
   - Cache et index

---

## 🔄 Protocole A2A (Agent-to-Agent)

### Contrat de Message (TaskMessage)

Message envoyé par l'orchestrateur vers un agent:

```json
{
  "task_id": "uuid",
  "intent": "watch.collect | security.audit | pr.linter | ...",
  "inputs": {
    "repo": ".",
    "diff_base": "HEAD~1",
    "query": "..."
  },
  "constraints": {
    "budget_usd": 0.75,
    "latency_s": 60,
    "policy": "blocking|advisory"
  },
  "context": {
    "memory_keys": ["project:foo", "last_runs:watch"],
    "attachments": ["..."]
  },
  "timestamp": "2025-11-07T10:00:00Z"
}
```

#### Champs clés

| Champ | Type | Description |
|-------|------|-------------|
| `task_id` | UUID | Identifiant unique de la tâche |
| `intent` | string | Intent au format `<category>.<action>` |
| `inputs` | object | Paramètres spécifiques à l'agent |
| `constraints` | object | Contraintes d'exécution (budget, latence, policy) |
| `context` | object | Contexte additionnel (mémoire, attachments) |

#### Policies

- **blocking**: Échec de la tâche bloque le pipeline
- **advisory**: Échec génère un warning mais ne bloque pas

---

### Contrat de Résultat (TaskResult)

Résultat retourné par un agent après exécution:

```json
{
  "task_id": "uuid",
  "status": "ok|advisory|blocking|error",
  "score": 0-100,
  "artefacts": ["*.md", "*.sarif", "patches/*.diff"],
  "sources": ["github:owner/repo@commit", "gemini:model@version"],
  "model": "provider:model@version",
  "decision_log": ".ai/logs/<task_id>.ndjson",
  "cost_usd": 0.21,
  "latency_ms": 4180,
  "tokens": {"input": 1200, "output": 800, "total": 2000},
  "error": "",
  "result_data": {}
}
```

#### Statuts

- `ok`: Succès complet
- `advisory`: Succès avec avertissements
- `blocking`: Échec bloquant
- `error`: Erreur d'exécution

#### Sources

Format standard pour la traçabilité:

- `github:owner/repo@commit` - Repository GitHub
- `pypi:package@version` - Package PyPI
- `npm:package@version` - Package NPM
- `gemini:model@version` - Modèle Gemini utilisé
- `claude:model@version` - Modèle Claude utilisé
- `openai:model@version` - Modèle OpenAI utilisé
- `mcp:server/tool` - Outil MCP
- `file:path/to/file:line` - Fichier local

---

## 🎯 Catalogue d'agents

### 🔵 Équipe ADK (Google A2A) - **ACTIF**

| Agent | Intent | Rôle |
|-------|--------|------|
| **watch_collect** | `watch.collect` | Collecte multi-ecosystèmes |
*(... reste du tableau inchangé ...)*

### 🟢 Équipe Anthropic (MCP) - **ACTIF**

*(... contenu inchangé ...)*

### 🟠 Équipe OpenAI - **PHASE 3**

*(... contenu inchangé, dépend de l'activation du flag `OPENAI_AGENTS_ENABLED`)*

---

## 🧠 Flux d'orchestration

*(... conten...