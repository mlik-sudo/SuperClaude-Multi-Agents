# 🟠 Agents OpenAI — Phase 3

Cette documentation décrit l'état actuel des agents OpenAI prévus pour SuperClaude. Les bridges et appels API sont encore prototypes : **aucun agent n'est activé par défaut**.

## 📌 Statut général

- **Bridge** : à implémenter (`agents/openai/bridge.py`).
- **Modèles recommandés** : GPT-4o, GPT-4o-mini, gpt-4.1.
- **Environnements conseillés** : sandbox dédiée ou compte OpenAI de test (clés restreintes).
- **Sécurité** : suivre la check-list `docs/SECURITY.md` avant toute activation.

## 🧩 Catalogue détaillé

| Agent | Intent | Maturité | Cas d'usage | Artefacts attendus |
|-------|--------|----------|-------------|--------------------|
| `ui-to-code` | `ui.convert` | Prototype | Convertir une capture Figma/PNG en composants UI conformes WCAG. | `artefacts/ui/<task_id>/component.tsx`, `report.md` |
| `migrator-5000` | `code.migrate.complex` | Prototype | Migrations majeures (framework, SDK) avec plan + patchs. | `artefacts/migrations/<task_id>/plan.md`, `patch.diff` |
| `creative-studio` | `creative.generate` | Prototype | Génération créative multi-canal (email, social, visuel). | `artefacts/creative/<task_id>/*.md`, `assets/*.png` |

### ui-to-code
- **Entrées** : maquette (URL/chemin), stack cible (`react`, `vue`, `flutter`), politiques d'accessibilité.
- **Sorties** : composant UI + rapport WCAG.
- **Dépendances** : GPT-4o (vision) + renderer local optionnel.

### migrator-5000
- **Entrées** : repo cible, diff de référence, contraintes de compatibilité.
- **Sorties** : plan en plusieurs étapes, estimation coût/latence, patch Git optionnel.
- **Notes** : nécessite un accès lecture au repo (SSH/https) depuis l'environnement du bridge.

### creative-studio
- **Entrées** : brief marketing, canaux (`twitter`, `linkedin`, `email`), contraintes marque.
- **Sorties** : variantes textuelles + éventuellement prompts DALL·E/GPT-4o pour visuels.
- **Notes** : prévoir un dossier `artefacts/creative/` pour les rendus HTML/Markdown.

## 🚀 Roadmap d'activation

1. **Implémenter `agents/openai/bridge.py`** avec un schéma similaire aux bridges ADK/Anthropic (STDIO + JSON-RPC).
2. **Déclarer les agents** dans `core/ai_core.py -> AgentRegistry` avec des coûts/latences réalistes.
3. **Ajouter des drapeaux de feature** (`OPENAI_AGENTS_ENABLED=false` par défaut) pour éviter l'exécution accidentelle.
4. **Écrire des tests dry-run** dans `tests/openai/` qui mockent la réponse OpenAI.
5. **Mettre à jour la CLI** (`ai run ui.convert ...`) une fois le bridge stabilisé.

## ✅ Check-list avant merge

- [ ] Clés OpenAI stockées hors dépôt (`OPENAI_API_KEY` via secret manager).
- [ ] Mode sandbox documenté dans `docs/SECURITY.md`.
- [ ] Dry-run (`TEST_MODE=true`) validé sur chaque agent.
- [ ] Artefacts générés référencés dans `.ai/INDEX.md`.

_Toute contribution sur l'équipe OpenAI doit inclure un lien vers ce document dans la PR._
