# 📚 SuperClaude Artefacts Index

> Index central des artefacts générés par les agents SuperClaude
> Dernière mise à jour: 2025-11-07

## 📁 Structure

```
.ai/
├── INDEX.md              # Ce fichier - index central
├── logs/                 # Logs d'exécution (NDJSON)
│   └── *.ndjson         # Logs par task_id
├── reports/              # Rapports d'analyse
│   ├── *.md             # Rapports markdown
│   ├── *.json           # Rapports JSON
│   └── *.sarif          # Rapports SARIF (sécurité)
├── artefacts/            # Artefacts générés
│   ├── watch/           # Données de veille
│   ├── patches/         # Patches de code
│   ├── digests/         # Newsletters et digests
│   └── proto/           # Prototypes éphémères (TTL 24h)
├── cache/                # Cache et données temporaires
│   └── embeddings/      # Embeddings pour RAG
└── index/                # Index de recherche
    └── *.index          # Index vectoriels
```

## 📊 Métadonnées

- **Version du schema**: 1.0.0
- **Format de logs**: NDJSON (Newline Delimited JSON)
- **Politique de rétention**:
  - Logs: 30 jours
  - Rapports: 90 jours
  - Artefacts: selon TTL ou permanent
  - Cache: 7 jours
  - Prototypes: 24 heures

## 🔍 Sources de données

Les agents peuvent citer les sources suivantes dans leurs résultats:

- `github:owner/repo@commit` - Source GitHub
- `pypi:package@version` - Package PyPI
- `npm:package@version` - Package NPM
- `sonarqube:project` - Analyse SonarQube
- `gemini:model@version` - Sortie Gemini
- `claude:model@version` - Sortie Claude
- `openai:model@version` - Sortie OpenAI
- `mcp:server/tool` - Outil MCP
- `file:path/to/file:line` - Fichier local

## 📝 Format des logs

Chaque ligne du fichier `.ai/logs/<task_id>.ndjson` est un événement JSON:

```json
{
  "timestamp": "2025-11-07T10:00:00Z",
  "task_id": "uuid",
  "event": "task.started|task.completed|agent.called|error",
  "agent": "team:agent",
  "data": {}
}
```

## 🎯 Artefacts par agent

### Équipe ADK
- **watch-collect**: `.ai/artefacts/watch/watch.ndjson`, `sources.json`
- **watch-analyze**: `.ai/reports/watch.analysis.json`, `insights.md`
- **curate-digest**: `.ai/artefacts/digests/DIGEST.md`, `digest.html`
- **label-github-issue**: `.ai/reports/triage.report.json`

### Équipe Anthropic
- **doc-hunter**: `.ai/cache/docs/*.md`
- **test-architect**: `.ai/artefacts/tests/*.test.{js,py}`
- **refactor-master**: `.ai/artefacts/patches/*.diff`, `migration-plan.md`
- **pr-linter**: `.ai/reports/pr-review.md`
- **writing-studio**: `.ai/artefacts/*.md`

### Équipe OpenAI
- **ui-to-code**: `.ai/artefacts/components/*.{jsx,tsx}`
- **migrator-5000**: `.ai/artefacts/patches/*.diff`, `compat-matrix.json`
- **creative-studio**: `.ai/artefacts/creative/*`

---

*Généré par SuperClaude Multi-Agents v1.0*
