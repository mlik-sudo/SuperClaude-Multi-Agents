# 🔐 Guide de Sécurité SuperClaude

Ce document décrit le modèle de menace, les bonnes pratiques de gestion des secrets et les réflexes de réponse à incident pour l'orchestrateur SuperClaude Multi-Agents. Il complète les instructions du README et doit être consulté avant l'activation d'un bridge externe (ADK, Anthropic, OpenAI).

## 🎯 Objectifs de sécurité

- Empêcher l'exécution de code non approuvé via les bridges STDIO.
- Réduire la surface d'exposition des clés API (Anthropic, Google ADK, OpenAI).
- Garantir la traçabilité des actions agents grâce aux artefacts `.ai/`.
- Fournir une procédure de réponse en cas de fuite ou de comportement anormal.

## ⚠️ Modèle de menace

| Menace | Description | Mitigation rapide |
|--------|-------------|-------------------|
| Subprocess compromis | Les bridges ADK/OpenAI invoquent des scripts présents dans `~/adk-workspace` ou `agents/openai`. Un script modifié peut exécuter du code arbitraire. | Restreindre les chemins via `config/settings.py`, exécuter dans un venv dédié, vérifier les checksums avant chaque run. |
| Clés API exposées | `.env` ou historiques Git contenant des secrets. | Ne jamais commiter `.env`, utiliser un secret manager et scanner `gitleaks protect --staged`. |
| Artefacts sensibles | Les rapports `.ai/artefacts/**` peuvent contenir du code propriétaire. | Chiffrer les artefacts avant export externe, purger avec la politique de rétention (`.ai/config.yaml`). |
| Bridge bloqué | Un subprocess peut boucler et consommer le budget. | Configurer `BRIDGE_TIMEOUT`, `AGENT_TIMEOUT`, surveiller `.ai/logs/` et `~/.gemini/bridge.log`. |

## 🧰 Check-list opérationnelle

1. **Isoler les environnements**
   - Créez un virtualenv spécifique (`python -m venv .venv-bridges`) pour exécuter `agents/*/bridge.py`.
   - Sur macOS/Linux, lancez les bridges dans un shell restreint (`firejail`, `sandbox-exec`, conteneur Docker) pour les tests sensibles.

2. **Sécuriser les chemins**
   - Utilisez `config/settings.py` pour forcer des chemins relatifs (par défaut `agents/<team>/bridge.py`).
   - Supprimez les chemins absolus (`/Users/.../.gemini/bridge.py`) après migration.

3. **Gérer les secrets**
   - Dupliquez `.env.example` en `.env.local`, `.env.ci` avec des clés distinctes.
   - Exportez vos secrets via un manager (`aws secretsmanager`, `vault kv get`, `1password op run`).
   - Ajoutez un scan pré-commit : `gitleaks protect --staged`.

4. **Surveiller les coûts**
   - Inspectez `.ai/USAGE.ndjson` après chaque run et vérifiez les champs `cost_usd` / `tokens`.
   - Activez un export Prometheus ou envoyez les métriques vers votre SIEM si vous intégrez SuperClaude en production.

## 🛠️ Durcissement des bridges

| Équipe | Mesure principale | Détails |
|--------|-------------------|---------|
| ADK | Contrôler `ADK_WORKSPACE` | Placez les agents ADK dans un dépôt en lecture seule et validez les hash (`shasum -a 256`). |
| Anthropic | Limiter les permissions API | Créez une clé spécifique avec quota réduit et activez `TEST_MODE=true` pour les dry-runs. |
| OpenAI (Phase 3) | Activer sur environnement jetable | Les agents sont encore prototypes : utilisez un compte de test et supprimez la clé après usage. |

## 🚨 Réponse à incident

1. **Isoler** : stoppez immédiatement les bridges (`pkill -f bridge.py`) et videz la queue `ai_core.queue`.
2. **Révoquer** : supprimez les clés API compromises (`anthropic keys delete`, `openai api keys delete`).
3. **Auditer** : exportez les logs `.ai/logs/<task_id>.ndjson` et `~/.gemini/bridge.log` pour analyse.
4. **Nettoyer** : purgez les artefacts sensibles (`rm -rf .ai/artefacts/<task_id>`), re-générez les secrets et documentez dans votre gestionnaire d'incidents.

## 📚 Ressources utiles

- [README.md](../README.md) — Vue d'ensemble et commandes clés.
- [docs/ARCHITECTURE.md](./ARCHITECTURE.md) — Flux détaillés et politique de rétention.
- [docs/OPENAI_AGENTS.md](./OPENAI_AGENTS.md) — Statut des agents Phase 3.
- [gitleaks](https://github.com/gitleaks/gitleaks) — Scanner de secrets recommandé.

_N'oubliez pas : aucun agent ne devrait être activé sans avoir relu cette check-list._
