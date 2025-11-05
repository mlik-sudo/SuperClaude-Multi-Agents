#!/bin/bash
# Script pour appliquer le patch Phase 3 - Anthropic Integration

set -e

echo "🚀 Application du patch Phase 3 - Anthropic Integration"
echo "========================================================="
echo ""

# Vérifier qu'on est dans le bon dépôt
if [ ! -d ".git" ]; then
    echo "❌ Erreur: Ce script doit être exécuté à la racine du dépôt SuperClaude-Multi-Agents"
    exit 1
fi

# Vérifier que le patch existe
if [ ! -f "phase3-anthropic.patch" ]; then
    echo "❌ Erreur: Le fichier phase3-anthropic.patch n'existe pas"
    echo "   Assurez-vous que le patch est dans le répertoire actuel"
    exit 1
fi

# Sauvegarder l'état actuel
echo "📸 Sauvegarde de l'état actuel..."
BACKUP_BRANCH="backup-before-phase3-$(date +%Y%m%d-%H%M%S)"
git branch "$BACKUP_BRANCH" 2>/dev/null || true
echo "   ✅ Branche de sauvegarde créée: $BACKUP_BRANCH"
echo ""

# Vérifier qu'il n'y a pas de modifications non commitées
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Attention: Vous avez des modifications non commitées"
    echo ""
    echo "Options:"
    echo "  1. Committez vos changements avant d'appliquer le patch"
    echo "  2. Stashez vos changements avec: git stash"
    echo "  3. Continuez quand même (risqué)"
    echo ""
    read -p "Voulez-vous continuer quand même ? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Application annulée"
        exit 1
    fi
fi

# Appliquer le patch
echo "📦 Application du patch..."
if git apply --check phase3-anthropic.patch 2>/dev/null; then
    git apply phase3-anthropic.patch
    echo "   ✅ Patch appliqué avec succès!"
else
    echo "❌ Erreur lors de la vérification du patch"
    echo ""
    echo "Essai avec git am (inclut les commits)..."
    if git am < phase3-anthropic.patch; then
        echo "   ✅ Patch appliqué avec git am!"
    else
        echo "❌ Échec de l'application du patch"
        echo ""
        echo "Pour annuler les changements partiels:"
        echo "  git am --abort"
        echo "  git reset --hard $BACKUP_BRANCH"
        exit 1
    fi
fi

echo ""
echo "🎉 Phase 3 appliquée avec succès!"
echo ""
echo "📊 Résumé des changements:"
git diff --stat "$BACKUP_BRANCH" 2>/dev/null || git diff --stat HEAD~2 2>/dev/null || echo "  (voir git status pour les détails)"
echo ""
echo "📝 Prochaines étapes:"
echo "  1. Vérifiez les changements: git status"
echo "  2. Installez les dépendances: pip install -r requirements.txt"
echo "  3. Configurez votre API key dans .env: ANTHROPIC_API_KEY=sk-ant-..."
echo "  4. Lancez les tests: pytest tests/integration/test_anthropic_integration.py"
echo ""
echo "Pour annuler tous les changements si nécessaire:"
echo "  git reset --hard $BACKUP_BRANCH"
echo ""
