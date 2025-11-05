# 📚 SuperClaude Multi-Agents - Documentation

**Généré le** : 2025-11-05 14:35

---

## 📋 Table des Matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Référence API](#référence-api)
- [Exemples d'Usage](#exemples-dusage)
- [Configuration](#configuration)
- [FAQ](#faq)

---

## 🎯 Vue d'ensemble

Framework d'orchestration multi-agents avec support ADK, Anthropic et OpenAI

### ✨ Fonctionnalités Clés

- Architecture modulaire et extensible
- Support de 3 équipes d'agents (ADK, Anthropic, OpenAI)
- Protocole MCP pour isolation et sécurité
- Progressive disclosure pour économie de tokens

---

## 🏗️ Architecture

SuperClaude utilise une architecture modulaire basée sur le protocole MCP (Model Context Protocol).

### Composants Principaux

#### SuperClaude (core/super_claude.py)

Orchestrateur principal qui gère :
- La délégation de tâches aux différentes équipes d'agents
- Le routage intelligent basé sur le type de tâche
- Le tracking des métriques de performance

**Usage :**

```python
from core.super_claude import SuperClaude, AgentTask, AgentTeam

sc = SuperClaude()
task = AgentTask(
    agent_team=AgentTeam.ANTHROPIC,
    agent_name="research_agent",
    task_description="Analyse les tendances IA 2025",
    context={}
)
result = await sc.delegate_task(task)
```

#### AnthropicBridge (agents/anthropic/bridge.py)

Passerelle MCP vers l'équipe Anthropic exposant 3 agents spécialisés.

---

## 📖 Référence API

### AnthropicBridge

**Description** : Bridge MCP JSON-RPC pour l'équipe Anthropic

#### Agents Disponibles

**1. research_agent**

Agent de recherche et synthèse d'informations.

```python
task = AgentTask(
    agent_team=AgentTeam.ANTHROPIC,
    agent_name="research_agent",
    task_description="Synthétise les meilleures pratiques Python async",
    context={"domain": "python"}
)
```

**2. code_agent**

Agent de génération et analyse de code.

```python
task = AgentTask(
    agent_team=AgentTeam.ANTHROPIC,
    agent_name="code_agent",
    task_description="Génère une fonction de tri optimisée",
    context={"language": "python"}
)
```

**3. writing_agent**

Agent de rédaction et édition de contenu.

```python
task = AgentTask(
    agent_team=AgentTeam.ANTHROPIC,
    agent_name="writing_agent",
    task_description="Améliore cette description produit",
    context={"style": "professionnel"}
)
```

---

## 💡 Exemples d'Usage

### Workflow Hybride : Tech Digest

Combine ADK (collecte) + Filtrage local + Anthropic (analyse + rédaction)

```python
# 1. Collecte ADK (trending repos GitHub)
repos = await adk_client.fetch_trending()

# 2. Filtrage local (top 20 Python)
filtered = [r for r in repos if r['language'] == 'Python'][:20]

# 3. Analyse research_agent
analysis_task = AgentTask(
    agent_team=AgentTeam.ANTHROPIC,
    agent_name="research_agent",
    task_description=f"Analyse ces {len(filtered)} repos Python",
    context={"repos": filtered}
)
analysis = await sc.delegate_task(analysis_task)

# 4. Rédaction writing_agent
newsletter_task = AgentTask(
    agent_team=AgentTeam.ANTHROPIC,
    agent_name="writing_agent",
    task_description="Rédige une newsletter des tendances",
    context={"analysis": analysis.result}
)
newsletter = await sc.delegate_task(newsletter_task)
```

**Économie** : ~98% de tokens (300K → 6K)

---

## ⚙️ Configuration

### Variables d'Environnement

```bash
# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Serveurs MCP
MCP_ANTHROPIC_COMMAND=python3
MCP_ANTHROPIC_ARGS=agents/anthropic/bridge.py
```

### Fichier .env.example

Copiez `.env.example` vers `.env` et configurez vos clés API.

---

## ❓ FAQ

**Q: Quelle est la différence entre les 3 agents Anthropic ?**

A: Chaque agent est spécialisé :
- `research_agent` : Analyse et synthèse (questions, veille, résumés)
- `code_agent` : Génération et revue de code (dev, refactoring, debugging)
- `writing_agent` : Rédaction professionnelle (docs, newsletters, amélioration)

**Q: Comment économiser des tokens ?**

A: Utilisez le pattern "Progressive Disclosure" :
1. Filtrez localement en Python avant d'appeler l'API
2. N'envoyez que les données pertinentes
3. Réutilisez les résultats en cache quand possible

**Q: Les agents Anthropic fonctionnent en mode mock ?**

A: Par défaut, les tests utilisent des mocks. Pour utiliser la vraie API :
1. Configurez `ANTHROPIC_API_KEY` dans `.env`
2. Le bridge détectera automatiquement la clé
3. Les métriques réelles seront trackées

---

## 📈 Métriques de Performance

| Métrique | Valeur |
|----------|--------|
| **Tokens ADK** | 800 |
| **Tokens Extraction Locale** | 1,200 |
| **Tokens Research Agent** | 4,200 |
| **Tokens Writing Agent** | 4,700 |
| **Total** | 10,900 |
| **Économie vs Naïf** | 98.0% |

---

## 🚀 Getting Started

### Installation

```bash
# Clone le repository
git clone https://github.com/mlik-sudo/SuperClaude-Multi-Agents.git
cd SuperClaude-Multi-Agents

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Éditez .env et ajoutez votre ANTHROPIC_API_KEY
```

### Premier Usage

```bash
# Test du bridge Anthropic
python agents/anthropic/bridge.py

# Exécuter un skill hybride
python skills/hybrid/tech_digest_anthropic.py
```

---

## 🤝 Contribution

Contributions bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les guidelines.

---

## 📄 License

MIT License - Voir [LICENSE](LICENSE) pour détails.

---

## 🙏 Credits

Construit avec :
- **Anthropic Claude 3.5 Sonnet** - Intelligence des agents
- **Python AsyncIO** - Orchestration performante
- **MCP Protocol** - Communication sécurisée

---

*Documentation générée par SuperClaude Multi-Agents - Docs Generator Skill*
*Temps de génération : 12.5s*
*Coût : $0.030*
*Économie vs naïf : 98.1% ($1.566 économisés)*
