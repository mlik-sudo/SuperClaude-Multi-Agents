# 🚀 Guide CLI SuperClaude

> Interface en ligne de commande unifiée pour orchestrer les agents SuperClaude

**Version**: 1.0.0

---

## Installation

```bash
# Cloner le repository
git clone https://github.com/mlik-sudo/SuperClaude-Multi-Agents.git
cd SuperClaude-Multi-Agents

# Installer les dépendances
pip install -r requirements.txt

# Rendre le CLI exécutable
chmod +x ai

# Ajouter au PATH (optionnel)
export PATH="$PATH:$(pwd)"
```

---

## Commandes

### `ai run` - Exécuter une tâche

Exécute une tâche via un intent:

```bash
ai run <intent> [options]
```

#### Options communes

| Option | Type | Défaut | Description |
|--------|------|--------|-------------|
| `--budget` | float | 0.75 | Budget max en USD |
| `--latency` | int | 60 | Latence max en secondes |
| `--blocking` | flag | false | Mode blocking (échec = arrêt) |
| `--priority` | int | 1 | Priorité de la tâche |
| `--format` | string | text | Format de sortie (json, md, text) |
| `--dry-run` | flag | false | Simulation sans exécution |

#### Exemples

##### Veille technologique

```bash
# Collecter les nouveautés GitHub/PyPI/NPM des 7 derniers jours
ai run watch.collect --ecosystems github pypi npm --since 7d

# Analyser un rapport de veille
ai run watch.analyze --input .ai/artefacts/watch/watch.ndjson

# Générer un digest newsletter
ai run curate.digest --input .ai/reports/watch.analysis.json --format md
```

##### Review de Pull Request

```bash
# Linter une PR (mode advisory)
ai run pr.lint --pr 128 --format md

# Review approfondie (mode blocking)
ai run pr.review --pr 128 --blocking --budget 1.5
```

##### Sécurité

```bash
# Audit de sécurité sur un diff (mode blocking)
ai run security.audit --diff HEAD~1 --blocking --budget 0.5

# Scan de secrets
ai run security.secrets --path . --format sarif
```

##### Tests

```bash
# Générer des tests unitaires
ai run test.generate --path src/components/Button.tsx

# Vérifier la couverture
ai run test.coverage --path src --min 70
```

##### Code

```bash
# Générer du code
ai run code.generate --query "React component for user profile card"

# Refactoring
ai run code.refactor --path src/legacy --target es2022

# Migration
ai run code.migrate --from vue2 --to vue3 --path src/
```

##### Documentation

```bash
# Recherche dans la documentation
ai run doc.search --query "Claude API rate limits"

# Génération de guide
ai run writing.guide --topic "Getting started with SuperClaude" --style technical
```

##### Créativité (OpenAI - Phase 3)

```bash
# Convertir UI → Code
ai run ui.convert --image mockup.png --framework react

# Génération créative
ai run creative.generate --prompt "Logo for AI startup" --variants 5
```

---

### `ai status` - Statut du système

Affiche l'état actuel de SuperClaude:

```bash
ai status
```

**Sortie:**

```
📊 SuperClaude Status
==================================================

📋 Queue:
   Tâches en attente: 3

💰 Budget:
   Dépensé aujourd'hui: $2.34
   Restant: $7.66
   Tâches aujourd'hui: 12

📈 Métriques:
   tasks_submitted: 15
   tasks_completed: 12
   tasks_ok: 10
   tasks_advisory: 1
   tasks_error: 1
   total_cost_usd: 2.34
   total_latency_ms: 48250
```

---

### `ai metrics` - Métriques détaillées

Affiche les métriques de performance:

```bash
ai metrics [--format json|text]
```

**Format JSON:**

```bash
ai metrics --format json
```

```json
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

---

### `ai list` - Lister les agents

Liste les agents disponibles et leurs intents:

```bash
ai list
```

**Sortie:**

```
📋 Agents disponibles
==================================================

🔹 Équipe ADK
   - watch_collect
   - analyse_watch_report
   - curate_digest
   - label_github_issue

🔹 Équipe ANTHROPIC
   - doc_hunter
   - test_architect
   - refactor_master
   - pr_linter
   - writing_studio

🔹 Équipe OPENAI
   - ui_to_code
   - migrator_5000
   - creative_studio


🎯 Intents supportés
==================================================

watch.collect:
   → adk/watch_collect

pr.review:
   → anthropic/pr_linter

code.generate:
   → anthropic/code_agent

[...]
```

---

## Profils de configuration

Les profils sont définis dans `.ai/config.yaml`.

### Utilisation

```bash
# Profil par défaut
ai run watch.collect --since 7d

# Profil économique
ai run watch.collect --since 7d --profile eco

# Profil premium (haute qualité)
ai run code.generate --query "..." --profile premium

# Profil CI/CD
ai run security.audit --diff HEAD~1 --profile ci
```

### Profils disponibles

| Profil | Budget/tâche | Budget/jour | Usage |
|--------|--------------|-------------|-------|
| **eco** | $0.25 | $3 | Dev, tests locaux |
| **default** | $0.75 | $10 | Usage quotidien |
| **premium** | $2.00 | $30 | Production, qualité max |
| **ci** | $1.00 | $20 | CI/CD, automatisation |

---

## Formats de sortie

### Text (défaut)

Sortie formatée pour le terminal:

```bash
ai run watch.collect --since 7d
```

```
🎯 Exécution de la tâche: watch.collect
   Budget: $0.75 | Latency: 60s | Policy: advisory
✓ Agent sélectionné: adk/watch_collect

✅ Tâche complétée: ok
   Score: 95/100
   Coût: $0.1200
   Latency: 4180ms

📦 Artefacts générés:
   - artefacts/watch/watch.ndjson
   - artefacts/watch/sources.json
```

### JSON

Sortie JSON pour scripts/CI:

```bash
ai run watch.collect --since 7d --format json
```

```json
{
  "task_id": "abc-123",
  "status": "ok",
  "score": 95,
  "artefacts": ["artefacts/watch/watch.ndjson", "artefacts/watch/sources.json"],
  "sources": ["github:trending", "pypi:new-releases"],
  "model": "adk:watch_collect",
  "cost_usd": 0.12,
  "latency_ms": 4180,
  "tokens": {"input": 1200, "output": 800, "total": 2000}
}
```

### Markdown

Sortie Markdown pour documentation:

```bash
ai run pr.review --pr 128 --format md
```

```markdown
# Résultat de tâche: abc-123

## Statut: OK

**Score**: 95/100
**Modèle**: anthropic:pr_linter
**Coût**: $0.2500
**Latence**: 3200ms

## Artefacts

- `.ai/reports/pr-review-128.md`

## Sources

- github:owner/repo#128
```

---

## Dry-run (simulation)

Simule l'exécution sans appeler les agents:

```bash
ai run watch.collect --since 7d --dry-run
```

**Sortie:**

```
🎯 Exécution de la tâche: watch.collect
   Budget: $0.75 | Latency: 60s | Policy: advisory
✓ Agent sélectionné: adk/watch_collect

🔍 Mode DRY-RUN - Tâche non exécutée

TaskMessage:
{
  "task_id": "abc-123",
  "intent": "watch.collect",
  "inputs": {
    "since": "7d"
  },
  ...
}
```

---

## Pipelines

Combiner plusieurs tâches:

```bash
# Pipeline veille complète
ai run watch.collect --since 7d && \
ai run watch.analyze --input .ai/artefacts/watch/watch.ndjson && \
ai run curate.digest --input .ai/reports/watch.analysis.json --format md

# Pipeline sécurité + tests
ai run security.audit --diff HEAD~1 --blocking && \
ai run test.coverage --path src --min 70 --blocking
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: SuperClaude CI

on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup SuperClaude
        run: |
          pip install -r requirements.txt
          chmod +x ai

      - name: Security Audit
        run: ./ai run security.audit --diff HEAD~1 --blocking --profile ci
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

      - name: PR Lint
        run: ./ai run pr.lint --pr ${{ github.event.pull_request.number }} --format md
```

### GitLab CI

```yaml
superclaude:review:
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - chmod +x ai
    - ./ai run security.audit --diff HEAD~1 --blocking --profile ci
    - ./ai run pr.lint --pr $CI_MERGE_REQUEST_IID --format json
  only:
    - merge_requests
```

---

## Variables d'environnement

| Variable | Description | Requis |
|----------|-------------|--------|
| `ANTHROPIC_API_KEY` | Clé API Anthropic | Oui (équipe Anthropic) |
| `GOOGLE_API_KEY` | Clé API Gemini | Oui (équipe ADK) |
| `OPENAI_API_KEY` | Clé API OpenAI | Oui (équipe OpenAI, Phase 3) |
| `GITHUB_TOKEN` | Token GitHub | Optionnel (pour `github.label`) |

---

## Troubleshooting

### Erreur: "No agent available for intent"

**Cause**: Intent inconnu ou mal formaté

**Solution**:
```bash
# Vérifier les intents disponibles
ai list

# Format attendu: <category>.<action>
ai run watch.collect  # ✓ Correct
ai run watchcollect   # ✗ Incorrect
```

### Erreur: "Budget check failed"

**Cause**: Budget journalier ou par tâche dépassé

**Solution**:
```bash
# Vérifier le budget restant
ai status

# Réduire le budget de la tâche
ai run <intent> --budget 0.25

# Utiliser le profil eco
ai run <intent> --profile eco
```

### Erreur: "Bridge timeout"

**Cause**: Agent trop lent ou timeout trop court

**Solution**:
```bash
# Augmenter la latence autorisée
ai run <intent> --latency 120

# Vérifier les logs
cat .ai/logs/<task_id>.ndjson
```

---

## Artefacts et Logs

Tous les artefacts sont stockés dans `.ai/`:

```bash
# Voir l'index des artefacts
cat .ai/INDEX.md

# Logs d'usage
cat .ai/USAGE.ndjson | jq

# Logs détaillés d'une tâche
cat .ai/logs/<task_id>.ndjson | jq

# Rapports générés
ls .ai/reports/

# Artefacts
ls .ai/artefacts/
```

---

## Ressources

- [Architecture](./ARCHITECTURE.md)
- [Contrats A2A](./CONTRACTS.md)
- [Catalogue Agents](./AGENTS.md)
- [Configuration](./.ai/config.yaml)

---

*SuperClaude Multi-Agents CLI v1.0 - 2025-11-07*
