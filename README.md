# 🧠 SuperClaude Multi-Agents

**Architecture orchestrée d'agents IA spécialisés avec protocole A2A (Agent-to-Agent)**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/mlik-sudo/SuperClaude-Multi-Agents)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)

---

## 🎯 Vision

SuperClaude Multi-Agents est un système d'orchestration intelligent qui coordonne plusieurs équipes d'agents IA spécialisés pour automatiser des tâches complexes de développement, de sécurité, de veille technologique et de rédaction.

**Architecture unifiée** avec protocole A2A standardisé pour la communication inter-agents.

---

## ✨ Nouveautés v1.0

🎉 **Architecture complète implémentée !**

- ✅ **CLI unifié** - `ai run <intent>` pour toutes les tâches
- ✅ **Contrats A2A** - Protocole standardisé (TaskMessage + TaskResult)
- ✅ **AI Core** - Orchestrateur avec queue, budgets, router intelligent
- ✅ **Store .ai/** - Artefacts, logs, rapports centralisés
- ✅ **Profils configurables** - eco, default, premium, ci
- ✅ **Observabilité** - Métriques temps réel, tracking des coûts
- ✅ **15 agents** opérationnels (ADK + Anthropic)

---

## 🏗️ Architecture

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

### Composants

- **AI Core**: Queue prioritaire, budgets, router, observabilité
- **Contrats A2A**: Messages et résultats standardisés
- **CLI Unifié**: Interface `ai` pour toutes les opérations
- **Bridges**: ADK (JSON-RPC), Anthropic (SDK), OpenAI (Phase 3)
- **Store .ai/**: Artefacts, logs, rapports, cache

📖 [Documentation Architecture Complète](docs/ARCHITECTURE.md)

---

## 🚀 Quick Start

### Installation

```bash
# Cloner le repository
git clone https://github.com/mlik-sudo/SuperClaude-Multi-Agents.git
cd SuperClaude-Multi-Agents

# Installer les dépendances
pip install -r requirements.txt

# Configurer les clés API
cp .env.example .env
# Éditer .env avec vos clés API

# Rendre le CLI exécutable
chmod +x ai
```

### Premiers pas

```bash
# Afficher les agents disponibles
./ai list

# Vérifier le statut
./ai status

# Exécuter une première tâche (veille GitHub/PyPI)
./ai run watch.collect --ecosystems github pypi --since 7d

# Voir les métriques
./ai metrics
```

📖 [Guide CLI Complet](docs/CLI_GUIDE.md)

---

## 🎯 Catalogue d'Agents

### 🔵 Équipe ADK (Google A2A) - **ACTIF**

| Agent | Intent | Rôle |
|-------|--------|------|
| **watch-collect** | `watch.collect` | Scraping GitHub/PyPI/NPM normalisé |
| **watch-analyze** | `watch.analyze` | Détection tendances/patterns (Gemini) |
| **curate-digest** | `curate.digest` | Curation newsletter/blog/social |
| **label-github-issue** | `github.label` | Multi-label + confiance + actions |

### 🟢 Équipe Anthropic (MCP) - **ACTIF**

| Agent | Intent | Rôle |
|-------|--------|------|
| **doc-hunter** | `doc.search` | Recherche doc officielle + cache |
| **test-architect** | `test.generate` | Génération tests (unit, E2E, mutation) |
| **refactor-master** | `code.refactor` | Codemods AST + plans migration |
| **pr-linter** | `pr.review` | Review PR low-cost |
| **writing-studio** | `writing.docs` | Rédaction contrôlée |

**Agents legacy** (compatibility): `research_agent`, `code_agent`, `writing_agent`

### 🟠 Équipe OpenAI - **PHASE 3**

| Agent | Intent | Rôle |
|-------|--------|------|
| **ui-to-code** | `ui.convert` | UI/maquettes → composants WCAG |
| **migrator-5000** | `code.migrate.complex` | Migrations complexes + tests |
| **creative-studio** | `creative.generate` | Variantes créatives multi-canal |

---

## 💡 Exemples d'utilisation

### Veille technologique automatisée

```bash
# Pipeline complet: collecte → analyse → newsletter
ai run watch.collect --since 7d && \
ai run watch.analyze --input .ai/artefacts/watch/watch.ndjson && \
ai run curate.digest --input .ai/reports/watch.analysis.json --format md
```

### Review de Pull Request

```bash
# Linter rapide (advisory)
ai run pr.lint --pr 128 --format md

# Review approfondie (blocking)
ai run pr.review --pr 128 --blocking --budget 1.5
```

### Sécurité et Tests

```bash
# Audit sécurité sur diff (mode blocking)
ai run security.audit --diff HEAD~1 --blocking

# Génération tests + vérification couverture
ai run test.generate --path src/components/Button.tsx
ai run test.coverage --path src --min 70
```

### Recherche et Documentation

```bash
# Recherche dans la doc officielle
ai run doc.search --query "Claude API rate limits"

# Génération guide
ai run writing.guide --topic "Getting started" --style technical
```

### Code et Refactoring

```bash
# Génération de code
ai run code.generate --query "React hook for user authentication"

# Refactoring
ai run code.refactor --path src/legacy --target es2022

# Migration
ai run code.migrate --from vue2 --to vue3 --path src/
```

---

## 📊 Budgets et Profils

Profils configurables dans `.ai/config.yaml`:

| Profil | Par tâche | Journalier | Usage |
|--------|-----------|------------|-------|
| **eco** | $0.25 | $3 | Dev, tests locaux |
| **default** | $0.75 | $10 | Usage quotidien |
| **premium** | $2.00 | $30 | Production, qualité max |
| **ci** | $1.00 | $20 | CI/CD, automatisation |

```bash
# Utiliser un profil spécifique
ai run watch.collect --profile eco

# Vérifier les dépenses
ai status
```

Toutes les dépenses sont trackées dans `.ai/USAGE.ndjson`.

---

## 🔒 Policies et Sécurité

### Blocking Policies

Défaillances qui **bloquent** le pipeline:

- ❌ **Secrets détectés** (gitleaks, truffleHog)
- ❌ **Vulnérabilités exploitables** (CVSS ≥ 7.0)
- ❌ **Licences interdites** (GPL, AGPL, SSPL)
- ❌ **Mutation-survived** > seuil

### Advisory Policies

Défaillances qui génèrent des **warnings**:

- ⚠️ Style et conventions
- ⚠️ Micro-performances
- ⚠️ Wording et documentation
- ⚠️ Couverture de tests < seuil

Configuration dans `.ai/config.yaml`.

---

## 📁 Structure du Projet

```
SuperClaude-Multi-Agents/
├── ai                       # 🚀 CLI exécutable
├── core/
│   ├── super_claude.py      # Orchestrateur central
│   ├── ai_core.py           # Queue, budgets, router
│   └── contracts.py         # Contrats A2A
├── cli/ai/
│   └── main.py              # Interface CLI
├── agents/
│   ├── adk/                 # 🔵 Agents ADK (Google A2A)
│   ├── anthropic/           # 🟢 Agents Anthropic (MCP)
│   └── openai/              # 🟠 Agents OpenAI (Phase 3)
├── .ai/                     # 📦 Store d'artefacts
│   ├── INDEX.md             # Index central
│   ├── USAGE.ndjson         # Log d'usage
│   ├── config.yaml          # Configuration
│   ├── logs/                # Logs d'exécution
│   ├── reports/             # Rapports
│   ├── artefacts/           # Artefacts générés
│   └── cache/               # Cache temporaire
├── docs/                    # 📚 Documentation
│   ├── ARCHITECTURE.md      # Architecture détaillée
│   ├── CLI_GUIDE.md         # Guide CLI
│   └── CONTRACTS.md         # Spécification A2A
├── config/                  # Configuration globale
├── tests/                   # Tests unitaires et E2E
└── requirements.txt         # Dépendances Python
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | Architecture complète et flux d'exécution |
| [Guide CLI](docs/CLI_GUIDE.md) | Commandes, exemples, troubleshooting |
| [Contrats A2A](docs/CONTRACTS.md) | Spécification protocole A2A |
| [Configuration](.ai/config.yaml) | Profils, policies, budgets |
| [Index Artefacts](.ai/INDEX.md) | Catalogue des artefacts générés |

---

## 🧪 Tests

```bash
# Tests unitaires
python -m pytest tests/unit/

# Tests de contrats
python core/contracts.py
python core/ai_core.py

# Tests d'intégration
python -m pytest tests/validation/
```

---

## 📋 Roadmap

### ✅ Phase 1 : Agents ADK (Google A2A) - **COMPLÉTÉ**
- [x] ✅ Bridge ADK opérationnel
- [x] ✅ 4 Agents validés (veille, analyse, curation, labeling)
- [x] ✅ CLI unifié
- [x] ✅ Contrats A2A
- [x] ✅ AI Core (queue, budgets, router)

### ✅ Phase 2 : Agents Anthropic (MCP) - **COMPLÉTÉ**
- [x] ✅ Bridge Anthropic SDK
- [x] ✅ 5 agents spécialisés (doc, test, refactor, pr, writing)
- [x] ✅ Observabilité complète
- [x] ✅ Configuration multi-profils

### 🔄 Phase 3 : Agents OpenAI - **EN COURS**
- [ ] 🔧 Bridge OpenAI SDK
- [ ] 🔧 ui-to-code (Vision GPT-4o)
- [ ] 🔧 migrator-5000 (Migrations complexes)
- [ ] 🔧 creative-studio (DALL-E + GPT-4o)

### 📅 Phase 4 : Assistant Mémoire + RAG - **PLANIFIÉ**
- [ ] 📚 LangGraph Core
- [ ] 🧠 Mémoire épisodique/sémantique/intentionnelle
- [ ] 📈 Grounding strict + politique d'oubli

---

## 🤝 Contribution

Ce projet suit une approche de développement par phases.

**Phase actuelle**: Phase 2 complétée, Phase 3 en préparation

Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les guidelines.

---

## 📊 Status Agents

| Équipe | Status | Agents Actifs | Communication |
|--------|--------|---------------|---------------|
| 🔵 ADK (Google) | ✅ **ACTIF** | 4/4 | JSON-RPC Bridge |
| 🟢 Anthropic | ✅ **ACTIF** | 8/8 | SDK Officiel |
| 🟠 OpenAI | 🔄 **PHASE 3** | 0/3 | En développement |

---

## 🔗 Liens utiles

- [Repository GitHub](https://github.com/mlik-sudo/SuperClaude-Multi-Agents)
- [Issues](https://github.com/mlik-sudo/SuperClaude-Multi-Agents/issues)
- [Pull Requests](https://github.com/mlik-sudo/SuperClaude-Multi-Agents/pulls)
- [Releases](https://github.com/mlik-sudo/SuperClaude-Multi-Agents/releases)

---

## 📄 License

MIT License - Voir [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Acknowledgments

- **Google ADK** pour le framework A2A
- **Anthropic** pour le SDK Claude et MCP
- **OpenAI** pour GPT-4o et DALL-E
- **LangGraph** pour la gestion de mémoire (Phase 4)

---

**🧠 SuperClaude Multi-Agents v1.0** - *Orchestration intelligente d'agents IA spécialisés*

---

### Quick Links

```bash
# Commencer rapidement
./ai list              # Liste des agents
./ai status            # Statut système
./ai metrics           # Métriques détaillées

# Exemples pratiques
./ai run watch.collect --since 7d                    # Veille
./ai run pr.review --pr 128                          # Review PR
./ai run security.audit --diff HEAD~1 --blocking     # Sécurité
./ai run test.generate --path src/                   # Tests
./ai run doc.search --query "Claude API"             # Doc
```

📖 **[Guide CLI Complet](docs/CLI_GUIDE.md)** | 🏗️ **[Architecture](docs/ARCHITECTURE.md)**
