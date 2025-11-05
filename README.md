# 🧠 Super Claude Multi-Agents

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-pytest-green.svg)](https://docs.pytest.org/)

**Architecture orchestrée d'agents IA spécialisés avec Super Claude comme chef d'orchestre**

## 🎯 Vision

Créer un écosystème d'agents IA collaboratifs où Super Claude orchestre différentes équipes d'agents spécialisés selon une approche Agent-to-Agent (A2A), combinant les forces des principaux providers IA.

## 🏗️ Architecture

```
           🧠 SUPER CLAUDE (Orchestrateur Central)
                    ↕️
              📚 Assistant Mémoire + RAG
                 (LangGraph Core)
                    ↕️
    ┌─────────────────┼─────────────────┐
    ▼                 ▼                 ▼
🔵 ÉQUIPE ADK     🟢 ÉQUIPE ANT     🟠 ÉQUIPE OPENAI
(Google A2A)    (Anthropic MCP)   (OpenAI Agents)
```

## 📋 Roadmap de Développement

### 🎯 Phase 1 : Agents ADK (Google A2A) - *En cours*
- [x] ✅ **Bridge ADK opérationnel** - Communication Super Claude ↔ ADK
- [x] ✅ **4 Agents validés** : Veille, Analyse, Curation, Labeling
- [ ] 🔧 **Optimisation workflows ADK**
- [ ] 🛠️ **Outillage et monitoring**
- [ ] 📊 **Métriques et performance**

### 🎯 Phase 2 : Agents Anthropic (MCP)
- [ ] 🔗 **Intégration Claude MCP**
- [ ] 🧠 **Agents spécialisés** : Research, Code, Writing
- [ ] 🔄 **Orchestration inter-équipes**

### 🎯 Phase 3 : Agents OpenAI
- [ ] 🤖 **GPT Agents integration**
- [ ] 👁️ **Vision et créativité**
- [ ] 🔧 **Function calling avancé**

### 🎯 Phase 4 : Assistant Mémoire + RAG
- [ ] 📚 **LangGraph Core**
- [ ] 🧠 **Contexte persistant**
- [ ] 📈 **Apprentissage continu**

## 🔧 Structure du Projet

```
SuperClaude-Multi-Agents/
├── core/                    # Super Claude orchestrateur
├── agents/
│   ├── adk/                # Agents ADK (Google A2A)
│   ├── anthropic/          # Agents Anthropic (MCP)
│   └── openai/             # Agents OpenAI
├── memory/                 # Assistant Mémoire + RAG
├── tools/                  # Outils communs
├── docs/                   # Documentation
└── tests/                  # Tests et validation
```

## ✨ Nouveautés

- ✅ **Configuration Centralisée** - Gestion des variables d'environnement avec validation Pydantic
- ✅ **Suite de Tests Complète** - Tests unitaires et d'intégration avec pytest (>70% coverage)
- ✅ **CI/CD GitHub Actions** - Tests automatisés, linting, security scanning
- ✅ **Logging Structuré** - Logs JSON avec rotation et performance tracking
- ✅ **Validation des Schémas** - Validation stricte des inputs avec Pydantic
- ✅ **Outils de Développement** - Makefile, pre-commit hooks, auto-formatage
- ✅ **Documentation Complète** - Setup, Contributing, Architecture

## 🚀 Quick Start

### Installation Automatique

```bash
# Clone du repository
git clone https://github.com/mlik-sudo/SuperClaude-Multi-Agents.git
cd SuperClaude-Multi-Agents

# Setup automatique (recommandé)
make setup-dev
```

Cette commande va :
- Installer toutes les dépendances (production + dev)
- Créer votre fichier `.env` depuis le template
- Installer les pre-commit hooks
- Configurer l'environnement de développement

### Configuration

```bash
# Éditer la configuration
nano .env

# Variables requises :
# ADK_BRIDGE_PATH=/path/to/adk-workspace/bridge.py
# ADK_WORKSPACE=/path/to/adk-workspace
```

### Validation

```bash
# Vérifier l'installation
make test              # Lancer les tests
make validate-config   # Valider la configuration
make run-demo          # Tester SuperClaude
```

Pour plus de détails, consultez [docs/SETUP.md](docs/SETUP.md)

## 📊 Status Agents

| Équipe | Status | Agents | Communication |
|--------|--------|---------|---------------|
| 🔵 ADK (Google) | ✅ **ACTIVE** | 4/4 | Super Claude ↔ Bridge Python |
| 🟢 Anthropic | 🔄 **PLANNED** | 0/3 | - |
| 🟠 OpenAI | 🔄 **PLANNED** | 0/3 | - |

## 🎭 Agents Disponibles

### 🔵 Équipe ADK (Google A2A)
- **🔍 Agent Veille** - Surveillance GitHub/PyPI/NPM
- **🧠 Agent Analyse** - Analyse Gemini des rapports  
- **📰 Agent Curation** - Newsletter et threads sociaux
- **🏷️ Agent Labeling** - Étiquetage GitHub automatique

### 🟢 Équipe Anthropic (Prévue)
- **🔬 Agent Research** - Recherche et synthèse
- **💻 Agent Code** - Développement et review
- **✍️ Agent Writing** - Rédaction et documentation

### 🟠 Équipe OpenAI (Prévue)
- **👁️ Agent Vision** - Analyse d'images et vision
- **🎨 Agent Créatif** - Génération créative
- **⚡ Agent Raisonnement** - Logique et problem-solving

## 🛠️ Développement

### Commandes Utiles

```bash
make test              # Lancer les tests avec coverage
make lint              # Vérifier la qualité du code
make format            # Auto-formater le code (Black + isort)
make security          # Scanner les vulnérabilités
make ci                # Exécuter le pipeline CI complet localement
make clean             # Nettoyer les fichiers temporaires
make help              # Afficher toutes les commandes disponibles
```

### Structure du Code

```
SuperClaude-Multi-Agents/
├── core/                    # Orchestrateur SuperClaude
│   └── super_claude.py      # Orchestrateur central
├── config/                  # Configuration centralisée
│   └── settings.py          # Gestion des settings avec Pydantic
├── agents/
│   └── adk/                 # Agents ADK (Phase 1)
│       ├── bridge.py        # Bridge MCP vers ADK
│       └── README.md
├── utils/                   # Utilitaires
│   ├── logging.py           # Logging structuré
│   └── validation.py        # Validation des schémas
├── tests/                   # Suite de tests
│   ├── unit/                # Tests unitaires
│   ├── integration/         # Tests d'intégration
│   └── conftest.py          # Fixtures pytest
├── docs/                    # Documentation
│   ├── SETUP.md             # Guide d'installation
│   ├── CONTRIBUTING.md      # Guide de contribution
│   ├── ARCHITECTURE.md      # Architecture détaillée
│   └── ROADMAP.md           # Feuille de route
└── .github/workflows/       # CI/CD GitHub Actions
```

## 📚 Documentation

- **[Setup Guide](docs/SETUP.md)** - Installation et configuration complète
- **[Contributing](docs/CONTRIBUTING.md)** - Guide de contribution
- **[Architecture](docs/ARCHITECTURE.md)** - Documentation technique détaillée
- **[Roadmap](docs/ROADMAP.md)** - Feuille de route du projet
- **[Security](SECURITY.md)** - Politiques de sécurité
- **[Changelog](CHANGELOG.md)** - Historique des versions

## 🔒 Sécurité

- ✅ Aucun secret hardcodé
- ✅ Validation stricte des inputs
- ✅ Scanning automatique des vulnérabilités (Bandit, Safety, CodeQL)
- ✅ Pre-commit hooks pour détecter les secrets
- ✅ Isolation des processus agents

Pour signaler une vulnérabilité, consultez [SECURITY.md](SECURITY.md).

## 🤝 Contribution

Nous accueillons les contributions ! Pour contribuer :

1. Consultez [CONTRIBUTING.md](docs/CONTRIBUTING.md)
2. Fork le projet
3. Créez une branche (`git checkout -b feature/amazing-feature`)
4. Committez vos changements (`git commit -m 'feat: add amazing feature'`)
5. Push vers la branche (`git push origin feature/amazing-feature`)
6. Ouvrez une Pull Request

**Standards de code :**
- Tests unitaires requis (>80% coverage)
- Formatage avec Black
- Linting avec flake8
- Type hints avec mypy

## 📊 Statut du Projet

- **Version Actuelle:** 0.1.0
- **Phase Active:** Phase 1 - Optimisation ADK
- **Couverture Tests:** >70%
- **Python Supporté:** 3.8, 3.9, 3.10, 3.11, 3.12
- **Status:** ✅ Prêt pour développement collaboratif

## 📄 License

MIT License - Voir [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- **Model Context Protocol (MCP)** par Anthropic
- **Google Agent Development Kit (ADK)**
- **Claude Code** pour l'orchestration

---

**🧠 Super Claude Multi-Agents** - *Orchestration intelligente d'agents IA spécialisés*

Made with ❤️ using Python, Pydantic, and asyncio