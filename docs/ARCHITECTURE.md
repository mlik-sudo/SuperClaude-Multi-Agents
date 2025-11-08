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

## 🎯 Catalogue d'Agents

### 🔵 Équipe ADK (Google A2A) - Phase 1

| Agent | Intent | Rôle | Artefacts |
|-------|--------|------|-----------|
| **watch-collect** | `watch.collect` | Scraping GitHub/PyPI/NPM normalisé | `watch.ndjson`, `sources.json` |
| **watch-analyze** | `watch.analyze` | Détection tendances/patterns (Gemini) | `watch.analysis.json`, `insights.md` |
| **curate-digest** | `curate.digest` | Curation newsletter/blog/social | `DIGEST.md`, `digest.html` |
| **label-github-issue** | `github.label` | Multi-label + confiance + actions | `triage.report.json` |

**Mapping des anciens noms:**
- `watch_collect` → `watch-collect`
- `analyse_watch_report` → `watch-analyze`
- `curate_digest` → `curate-digest`
- `label_github_issue` → `label-github-issue`

### 🟢 Équipe Anthropic (MCP) - Phase 2

| Agent | Intent | Rôle |
|-------|--------|------|
| **doc-hunter** | `doc.search` | Recherche documentaire + cache |
| **test-architect** | `test.generate` | Génération de tests multi-niveaux |
| **refactor-master** | `code.refactor` | Codemods AST, plans de migration |
| **pr-linter** | `pr.review` | Revue PR automatique |
| **writing-studio** | `writing.docs` | Rédaction assistée |
| **research_agent / code_agent / writing_agent** | Legacy (compatibilité) |

### 🟠 Équipe OpenAI - Phase 3 (Planifiée)

Agents prévus : `ui-to-code`, `migrator-5000`, `creative-studio`. Voir [docs/OPENAI_AGENTS.md](./OPENAI_AGENTS.md) pour la roadmap détaillée.

---

## 🧠 Flux d'orchestration

1. `ai run <intent>` crée un `TaskMessage` avec contraintes.
2. `AI Core` route vers l'agent le plus adapté (SLA/coût/latence) et push dans la queue.
3. `SuperClaude` sélectionne l'équipe et invoque le bridge correspondant.
4. Le résultat est converti en `TaskResult`, budgets/métriques/logs sont mis à jour.

*(Diagrammes et exemples restent identiques)*

---

## 🔍 Observabilité

*(Sections Metrics, Logs, Export identiques)*

---

## 🧩 Extensibilité

*(Procédure d'ajout d'agent identique)*

---

## 📚 Phase 4: Mémoire et RAG (Planifié)

*(Contenu identique)*

---

## 🔐 Sécurité opérationnelle

- **Menaces couvertes** : subprocess non fiables (bridges ADK/OpenAI), compromission de clés API, fuite d'artefacts.
- **Check-list rapide** :
  1. Résoudre les chemins via `config/settings.py` (pas de chemins absolus utilisateurs).
  2. Activer `BRIDGE_TIMEOUT` / `AGENT_TIMEOUT` et surveiller `.ai/logs/`.
  3. Scanner les secrets avant chaque push (`gitleaks protect --staged`).
- Référez-vous à [docs/SECURITY.md](./SECURITY.md) pour le détail et à [docs/OPENAI_AGENTS.md](./OPENAI_AGENTS.md) avant d'activer la Phase 3.

---

## 🔗 Références

- [Contrats A2A](./CONTRACTS.md)
- [Guide CLI](./CLI_GUIDE.md)
- [Catalogue Agents](./AGENTS.md)
- [Configuration](../.ai/config.yaml)
- [INDEX Artefacts](../.ai/INDEX.md)
- [Sécurité](./SECURITY.md)
- [Agents OpenAI](./OPENAI_AGENTS.md)

---

*Généré par SuperClaude Multi-Agents v1.0 - 2025-11-07*
