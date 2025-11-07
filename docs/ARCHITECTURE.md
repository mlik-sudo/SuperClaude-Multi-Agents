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
   - OpenAI Bridge (Phase 3)

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

| Agent | Intent | Rôle | Outils |
|-------|--------|------|--------|
| **doc-hunter** | `doc.search`, `research.doc` | Doc officielle + cache offline | MCP docs + cache |
| **test-architect** | `test.generate`, `test.coverage` | Unit+E2E, property-based, mutation | Coverage API, Stryker/PIT |
| **refactor-master** | `code.refactor`, `code.migrate` | Codemods AST + plans migration | jscodeshift, ts-morph |
| **pr-linter** | `pr.review`, `pr.lint` | Review PR low-cost | reviewdog, danger |
| **writing-studio** | `writing.docs`, `writing.guide` | Rédaction contrôlée | Claude MCP + templates |

**Agents legacy (compatibility):**
- `research_agent` → Intent: `research.general`
- `code_agent` → Intent: `code.generate`, `code.analyze`
- `writing_agent` → Intent: `writing.general`

### 🟠 Équipe OpenAI - Phase 3

| Agent | Intent | Rôle | Outils |
|-------|--------|------|--------|
| **ui-to-code** | `ui.convert`, `vision.ui` | UI/maquettes → composants WCAG | GPT-4o, Storybook, axe |
| **migrator-5000** | `code.migrate.complex` | Migration ciblée + tests non-régression | codemods, compat matrix |
| **creative-studio** | `creative.generate`, `creative.variant` | Variantes créatives multi-canal | DALL-E, GPT-4o |

---

## 📊 Budgets et Quotas

### Configuration par profil

Profils disponibles dans `.ai/config.yaml`:

| Profil | Par tâche | Journalier | Mensuel | Usage |
|--------|-----------|------------|---------|-------|
| **eco** | $0.25 | $3 | $75 | Dev, tests |
| **default** | $0.75 | $10 | $250 | Usage normal |
| **premium** | $2.00 | $30 | $750 | Production, qualité max |
| **ci** | $1.00 | $20 | $500 | CI/CD, automatisation |

### Tracking

Toutes les dépenses sont enregistrées dans `.ai/USAGE.ndjson`:

```json
{
  "timestamp": "2025-11-07T10:00:00Z",
  "task_id": "uuid",
  "team": "adk",
  "agent": "watch_collect",
  "intent": "watch.collect",
  "cost_usd": 0.12,
  "latency_ms": 4180,
  "model": "gemini:1.5-flash@2024-11",
  "status": "ok",
  "tokens": {"input": 1200, "output": 800, "total": 2000}
}
```

---

## 🔒 Policies et Sécurité

### Policies Blocking

Défaillances qui **bloquent** le pipeline:

1. **Secrets détectés** (gitleaks, truffleHog)
   - `.env`, `credentials.json`, clés API
   - Action: Blocage + alerte

2. **Vulnérabilités exploitables** (CVSS ≥ 7.0)
   - Scan: Trivy, Snyk, CodeQL
   - Action: Blocage si score ≥ seuil

3. **Licences interdites** (GPL, AGPL, SSPL)
   - Vérification des dépendances
   - Action: Blocage + rapport

4. **Mutation-survived** > seuil
   - Tests de mutation (Stryker, PIT)
   - Action: Blocage si score < minimum

### Policies Advisory

Défaillances qui génèrent des **warnings**:

1. Style et conventions
2. Micro-performances
3. Wording et documentation
4. Couverture de tests < seuil

---

## 📁 Structure .ai/

```
.ai/
├── INDEX.md              # Index central des artefacts
├── USAGE.ndjson          # Log d'usage et coûts
├── config.yaml           # Configuration globale
├── logs/                 # Logs d'exécution
│   └── <task_id>.ndjson # Log détaillé par tâche
├── reports/              # Rapports d'analyse
│   ├── *.md             # Rapports markdown
│   ├── *.json           # Rapports JSON
│   └── *.sarif          # Rapports SARIF (sécurité)
├── artefacts/            # Artefacts générés
│   ├── watch/           # Données de veille
│   ├── patches/         # Patches de code
│   ├── digests/         # Newsletters
│   ├── tests/           # Tests générés
│   ├── components/      # Composants UI
│   └── proto/           # Prototypes (TTL 24h)
├── cache/                # Cache temporaire
│   ├── embeddings/      # Embeddings RAG
│   └── docs/            # Documentation cachée
└── index/                # Index de recherche
    └── *.index          # Index vectoriels
```

### Politiques de rétention

| Type | Durée | Note |
|------|-------|------|
| Logs | 30 jours | `.ai/logs/*.ndjson` |
| Reports | 90 jours | `.ai/reports/*` |
| Artefacts | Permanent | `.ai/artefacts/*` (sauf proto) |
| Cache | 7 jours | `.ai/cache/*` |
| Prototypes | 24 heures | `.ai/artefacts/proto/*` |

---

## 🚀 Flux d'exécution

### 1. Soumission de tâche

```python
# Via CLI
$ ai run watch.collect --ecosystems github pypi --since 7d

# Via Python
from core.contracts import TaskMessage, TaskConstraints
from core.ai_core import AICore

ai_core = AICore()
task = TaskMessage(
    intent="watch.collect",
    inputs={"ecosystems": ["github", "pypi"], "since": "7d"},
    constraints=TaskConstraints(budget_usd=0.5, latency_s=30)
)
ai_core.submit_task(task, priority=2)
```

### 2. Routage intelligent

L'AI Core sélectionne le meilleur agent selon:

1. **Capacités fonctionnelles** (supporte l'intent?)
2. **Contraintes** (budget, latence respectés?)
3. **SLA** (taux de succès)
4. **Coût** (le moins cher parmi les candidats)

### 3. Exécution

Le bridge approprié est appelé:

```python
# ADK Bridge
result = await super_claude.delegate_to_adk(agent_name, params)

# Anthropic Bridge
result = await super_claude.delegate_to_anthropic(agent_name, params)

# OpenAI Bridge (Phase 3)
result = await super_claude.delegate_to_openai(agent_name, params)
```

### 4. Résultat et métriques

Le résultat est converti en `TaskResult` et enregistré:

- **Budgets** mis à jour
- **Métriques** incrémentées
- **Logs** écrits dans `.ai/USAGE.ndjson`
- **Artefacts** sauvegardés dans `.ai/artefacts/`

---

## 🔍 Observabilité

### Métriques disponibles

```bash
$ ai metrics --format json
{
  "queue_size": 0,
  "budget_spent_today": 2.34,
  "budget_remaining": 7.66,
  "tasks_today": 12,
  "tasks_submitted": 15,
  "tasks_completed": 12,
  "tasks_ok": 10,
  "tasks_advisory": 1,
  "tasks_error": 1,
  "total_cost_usd": 2.34,
  "total_latency_ms": 48250
}
```

### Logs structurés

Chaque tâche génère un log détaillé dans `.ai/logs/<task_id>.ndjson`:

```json
{"timestamp": "2025-11-07T10:00:00Z", "event": "task.started", "task_id": "uuid", "agent": "adk:watch_collect"}
{"timestamp": "2025-11-07T10:00:01Z", "event": "agent.called", "task_id": "uuid", "data": {...}}
{"timestamp": "2025-11-07T10:00:05Z", "event": "task.completed", "task_id": "uuid", "status": "ok", "cost_usd": 0.12}
```

---

## 🧩 Extensibilité

### Ajouter un nouvel agent

1. **Définir les capacités**

```python
# Dans core/ai_core.py -> AgentRegistry._load_default_agents()
new_agent = AgentCapability(
    team="anthropic",
    agent_name="my_new_agent",
    intents=["custom.intent"],
    cost_per_token=0.00003,
    avg_latency_ms=3000,
    sla_success_rate=98.0
)
self.register_agent(new_agent)
```

2. **Implémenter le bridge**

```python
# Dans agents/<team>/bridge.py
def dispatch_my_new_agent(params: dict) -> dict:
    # Logique de l'agent
    return {"status": "success", "result": {...}}
```

3. **Mettre à jour le catalogue**

Documentation dans `docs/AGENTS.md`

---

## 📚 Phase 4: Mémoire et RAG (Planifié)

LangGraph Core avec 3 types de mémoire:

1. **Épisodique**: Runs, artefacts, décisions passées
2. **Sémantique**: Embeddings de docs internes + sorties agents
3. **Intentionnelle**: Historiques d'objectifs, roadmaps

### Grounding strict

Chaque réponse cite `.ai/INDEX.md` + sources URL/commit.

### Politique d'oubli

- TTL sur artefacts éphémères (`proto/*`, caches)
- Compression des logs anciens
- Archivage mensuel

---

## 🔗 Références

- [Contrats A2A](./CONTRACTS.md)
- [Guide CLI](./CLI_GUIDE.md)
- [Catalogue Agents](./AGENTS.md)
- [Configuration](../.ai/config.yaml)
- [INDEX Artefacts](../.ai/INDEX.md)

---

*Généré par SuperClaude Multi-Agents v1.0 - 2025-11-07*
