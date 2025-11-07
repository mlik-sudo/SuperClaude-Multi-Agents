# 📇 FICHES AGENTS - RÉFÉRENCE RAPIDE

## 🟢 CLAUDE CODE CLI (3 AGENTS)

### 🔍 research_agent
```
Nom       : research_agent
CLI       : Claude Code (Anthropic MCP)
Rôle      : Recherche & synthèse intelligente
Modèle    : Claude 3.5 Sonnet
Entrée    : query (string), depth (quick|standard|deep)
Sortie    : {summary, key_points[], insights[], recommendations[]}
Latence   : 5-15s
Tokens    : 2-8K (selon depth)
Fichiers  : agents/anthropic/bridge.py (40-94)
            mcp/servers.json (14-27)
            docs/ANTHROPIC_SETUP.md (105-145)
```

### 💻 code_agent
```
Nom       : code_agent
CLI       : Claude Code (Anthropic MCP)
Rôle      : Génération & analyse de code
Modèle    : Claude 3.5 Sonnet
Entrée    : task (string), language (python|js|java|go|rust|etc), context (string)
Sortie    : {code, explanation, tests, notes[]}
Latence   : 5-15s
Tokens    : 4K max
Langages  : Python, JavaScript, Java, Go, Rust, C++, C#, TypeScript
Fichiers  : agents/anthropic/bridge.py (96-158)
            mcp/servers.json (30-47)
            docs/ANTHROPIC_SETUP.md (149-186)
```

### ✍️ writing_agent
```
Nom       : writing_agent
CLI       : Claude Code (Anthropic MCP)
Rôle      : Rédaction & édition de contenu
Modèle    : Claude 3.5 Sonnet
Entrée    : content (string), 
            style (professional|casual|technical|marketing),
            task (improve|summarize|expand|translate)
Sortie    : {result, metadata{word_count, tone, changes[]}}
Latence   : 5-15s
Tokens    : 4K max
Fichiers  : agents/anthropic/bridge.py (160-219)
            mcp/servers.json (50-69)
            docs/ANTHROPIC_SETUP.md (190-235)
```

---

## 🔵 GEMINI CLI (4 AGENTS)

### 🔍 watch_collect
```
Nom       : watch_collect
CLI       : Gemini (Google A2A)
Rôle      : Surveillance & collecte de données
Sources   : GitHub, PyPI, NPM
Entrée    : sources[] (github|pypi|npm), output_format (markdown|json), 
            limit (50), timeframe (24h|7d|30d)
Sortie    : {rapport markdown ou json avec repos/packages}
Latence   : <2s
Timeout   : 300s (5 min)
Capacité  : 1000+ repos par requête
Fichiers  : agents/adk/bridge.py (27-31, 143-151)
            mcp/servers.json (89-104)
            agents/adk/README.md (11-15)
```

### 🧠 analyse_watch_report
```
Nom       : analyse_watch_report
CLI       : Gemini (Google A2A)
Rôle      : Analyse intelligente de rapports
API       : Google Gemini
Entrée    : report (string) OU report_path (string)
Sortie    : {trends[], key_insights[], patterns[], 
            emerging_technologies[], recommendations[], sentiment}
Latence   : <2s
Timeout   : 300s (5 min)
Capacité  : Rapports jusqu'à 50K lignes
Fichiers  : agents/adk/bridge.py (32-36, 153-158)
            mcp/servers.json (93-94)
            agents/adk/README.md (17-21)
```

### 📰 curate_digest
```
Nom       : curate_digest
CLI       : Gemini (Google A2A)
Rôle      : Curation & génération de contenu
Format    : newsletter|social|blog|summary
Output    : markdown|html
Entrée    : analysis_json (object), format, output
Sortie    : {contenu formaté newsletter/social/blog}
Latence   : <2s
Timeout   : 300s (5 min)
Supports  : Email, Twitter, LinkedIn, Discord, Blog, RSS
Fichiers  : agents/adk/bridge.py (37-41, 160-167)
            mcp/servers.json (97-98)
            agents/adk/README.md (23-27)
```

### 🏷️ label_github_issue
```
Nom       : label_github_issue
CLI       : Gemini (Google A2A)
Rôle      : Classification & labeling automatique
API       : GitHub REST + GraphQL
Entrée    : repo_name (owner/repo), issue_number (int), dry_run (bool)
Sortie    : {issue, analysis{type, priority, area, confidence}, 
            labels_assigned[], actions}
Latence   : <2s
Timeout   : 300s (5 min)
Accuracy  : 90-95%
Labels    : bug, feature, doc, type, priority, area, status, platform
Fichiers  : agents/adk/bridge.py (22-26, 129-141)
            mcp/servers.json (101-104)
            agents/adk/README.md (29-33)
```

---

## 🟠 CODEX CLI (PLANIFIÉ - PHASE 3)

### 👁️ vision_agent (PLANIFIÉ)
```
Nom       : vision_agent
CLI       : Codex (OpenAI - Phase 3)
Rôle      : Analyse d'images & vision
Modèle    : GPT-4 Vision (prévu)
Entrée    : image (url|base64), query (string)
Sortie    : {description, objects[], ocr, analysis}
Latence   : TBD
Status    : 🔄 EN PLANIFICATION
ETA       : Q4 2025
Fichiers  : agents/openai/bridge.py (À créer)
```

### 🎨 creative_agent (PLANIFIÉ)
```
Nom       : creative_agent
CLI       : Codex (OpenAI - Phase 3)
Rôle      : Génération créative
Modèle    : GPT-4 (prévu)
Entrée    : prompt (string), style (brainstorm|ideation|campaign)
Sortie    : {ideas[], suggestions[], creative_concepts[]}
Latence   : TBD
Status    : 🔄 EN PLANIFICATION
ETA       : Q4 2025
Fichiers  : agents/openai/bridge.py (À créer)
```

### ⚡ reasoning_agent (PLANIFIÉ)
```
Nom       : reasoning_agent
CLI       : Codex (OpenAI - Phase 3)
Rôle      : Raisonnement avancé
Modèle    : GPT-4 (prévu)
Entrée    : problem (string), constraints (string[])
Sortie    : {solution, reasoning[], steps[], alternatives[]}
Latence   : TBD
Status    : 🔄 EN PLANIFICATION
ETA       : Q4 2025
Fichiers  : agents/openai/bridge.py (À créer)
```

---

## 🔗 TABLEAU COMPARATIF

| Propriété | Claude Code | Gemini | Codex |
|-----------|------------|--------|-------|
| **Status** | ✅ Actif | ✅ Actif | 🔄 Phase 3 |
| **Agents** | 3/3 | 4/4 | 0/3 |
| **Latence** | 5-15s | <2s | TBD |
| **Timeout** | 60s | 300s | 120s (prévu) |
| **API** | Anthropic | Google A2A | OpenAI |
| **Modèle** | Claude 3.5 Sonnet | Gemini | GPT-4 |
| **Contexte** | 200K tokens | N/A | TBD |
| **Bridge** | agents/anthropic/bridge.py | agents/adk/bridge.py | agents/openai/bridge.py |
| **Documentation** | ✅ ANTHROPIC_SETUP.md | ✅ adk/README.md | ❌ Phase 3 |

---

## 📞 APPELS D'API RAPIDES

### Research Agent
```bash
# Direct
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"research_agent","arguments":{"query":"Python 2024","depth":"standard"}}}' | python3 agents/anthropic/bridge.py

# Via Super Claude
from core.super_claude import SuperClaude
sc = SuperClaude()
result = await sc.delegate_to_anthropic("research_agent", {"query": "...", "depth": "standard"})
```

### Code Agent
```bash
# Via Super Claude
from core.super_claude import SuperClaude
sc = SuperClaude()
result = await sc.delegate_to_anthropic("code_agent", {"task": "...", "language": "python"})
```

### Writing Agent
```bash
# Via Super Claude
from core.super_claude import SuperClaude
sc = SuperClaude()
result = await sc.delegate_to_anthropic("writing_agent", {"content": "...", "style": "professional"})
```

### Watch Collect
```bash
# Via Super Claude
from core.super_claude import SuperClaude
sc = SuperClaude()
result = await sc.delegate_to_adk("watch_collect", {"sources": ["github", "pypi"]})
```

### Analyse Watch Report
```bash
# Via Super Claude
from core.super_claude import SuperClaude
sc = SuperClaude()
result = await sc.delegate_to_adk("analyse_watch_report", {"report_path": "..."})
```

### Curate Digest
```bash
# Via Super Claude
from core.super_claude import SuperClaude
sc = SuperClaude()
result = await sc.delegate_to_adk("curate_digest", {"analysis_json": {...}, "format": "newsletter"})
```

### Label GitHub Issue
```bash
# Via Super Claude
from core.super_claude import SuperClaude
sc = SuperClaude()
result = await sc.delegate_to_adk("label_github_issue", {"repo_name": "owner/repo", "issue_number": 123})
```

---

## 🎯 UTILISATION PAR CAS D'USU

### Veille Technologique Complète
```
1. watch_collect → Collecte données (Gemini)
2. analyse_watch_report → Analyse rapport (Gemini)
3. curate_digest → Génère newsletter (Gemini)
4. writing_agent → Améliore contenu (Claude Code)
```

### Code Review Automatisé
```
1. watch_collect → Récupère code (Gemini)
2. code_agent → Analyse code (Claude Code)
3. writing_agent → Rédige rapport (Claude Code)
```

### GitHub Triage Automatisé
```
1. label_github_issue → Classifie issues (Gemini)
2. writing_agent → Crée résumés (Claude Code)
```

### Recherche & Synthèse
```
1. research_agent → Cherche & synthétise (Claude Code)
2. writing_agent → Formate présentation (Claude Code)
```

---

## ⚙️ CONFIGURATION REQUISE

### Environment Variables
```bash
# Claude Code CLI
export ANTHROPIC_API_KEY=sk-ant-api03-...
export ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
export ANTHROPIC_BRIDGE_PATH=/path/to/agents/anthropic/bridge.py

# Gemini CLI
export ADK_BRIDGE_PATH=/path/to/agents/adk/bridge.py

# Global
export BRIDGE_TIMEOUT=60
export LOG_LEVEL=INFO
```

### Dépendances
```bash
pip install anthropic
pip install requests
pip install python-dotenv
```

---

## 📊 PERFORMANCES

### Claude Code CLI
- **research_agent** : 5-15s (2-8K tokens selon depth)
- **code_agent** : 5-15s (4K tokens max)
- **writing_agent** : 5-15s (4K tokens max)
- **Taux succès** : 95%+

### Gemini CLI
- **watch_collect** : <2s (50+ résultats)
- **analyse_watch_report** : <2s (50K lignes max)
- **curate_digest** : <2s (10K items max)
- **label_github_issue** : <2s (90-95% accuracy)
- **Taux succès** : 95%+

### Codex CLI (Phase 3)
- **Status** : 🔄 EN PLANIFICATION
- **ETA** : Q4 2025

---

## 🚀 DÉMARRAGE RAPIDE

### 1. Installation
```bash
git clone https://github.com/mlik-sudo/SuperClaude-Multi-Agents.git
cd SuperClaude-Multi-Agents
pip install -r requirements.txt
cp .env.example .env
# Remplir ANTHROPIC_API_KEY dans .env
```

### 2. Test d'une agent
```bash
python3 -c "
import asyncio
from core.super_claude import SuperClaude

async def main():
    sc = SuperClaude()
    result = await sc.delegate_to_anthropic('research_agent', {
        'query': 'Tendances IA 2024',
        'depth': 'standard'
    })
    print(result)

asyncio.run(main())
"
```

### 3. Orchestration Multi-Agents
```bash
python3 core/super_claude.py
```

---

**Référence rapide agents** | **SuperClaude-Multi-Agents** | **7 agents actifs** | **Phase 2 opérationnelle**
