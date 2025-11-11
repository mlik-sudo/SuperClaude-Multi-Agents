#!/bin/bash
# ===================================
# Super Claude Multi-Agents - Setup Script
# ===================================
# Ce script initialise l'environnement de développement

set -e  # Exit on error

echo "🚀 SuperClaude Multi-Agents - Setup"
echo "===================================="
echo ""

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
info() {
    echo -e "${BLUE}ℹ${NC}  $1"
}

success() {
    echo -e "${GREEN}✓${NC}  $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC}  $1"
}

error() {
    echo -e "${RED}✗${NC}  $1"
}

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f ".env.example" ]; then
    error "Fichier .env.example non trouvé. Êtes-vous dans le répertoire racine du projet ?"
    exit 1
fi

# Étape 1: Créer le fichier .env s'il n'existe pas
info "Étape 1/5: Vérification du fichier .env"
if [ -f ".env" ]; then
    warning "Le fichier .env existe déjà."
    read -p "Voulez-vous le remplacer ? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        success "Fichier .env remplacé depuis .env.example"
    else
        info "Conservation du fichier .env existant"
    fi
else
    cp .env.example .env
    success "Fichier .env créé depuis .env.example"
fi

# Étape 2: Installer les dépendances Python
info "Étape 2/5: Installation des dépendances Python"
if command -v python3 &> /dev/null; then
    if [ -f "requirements.txt" ]; then
        read -p "Installer les dépendances Python ? (Y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            python3 -m pip install -r requirements.txt
            success "Dépendances Python installées"
        else
            warning "Installation des dépendances ignorée"
        fi
    fi
else
    error "Python3 non trouvé. Veuillez installer Python 3.9+"
    exit 1
fi

# Étape 3: Configuration interactive des variables critiques
info "Étape 3/5: Configuration des variables d'environnement"
echo ""
echo "Configuration des variables OBLIGATOIRES:"
echo ""

# Fonction pour configurer une variable
configure_var() {
    local var_name=$1
    local var_description=$2
    local var_default=$3
    local current_value=$(grep "^${var_name}=" .env | cut -d'=' -f2)

    echo -e "${YELLOW}${var_name}${NC}"
    echo "  Description: ${var_description}"

    if [ ! -z "$current_value" ] && [ "$current_value" != "$var_default" ]; then
        echo "  Valeur actuelle: ${current_value}"
        read -p "  Conserver cette valeur ? (Y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            read -p "  Nouvelle valeur: " new_value
            sed -i.bak "s|^${var_name}=.*|${var_name}=${new_value}|" .env
            success "Variable ${var_name} mise à jour"
        fi
    else
        read -p "  Valeur: " new_value
        if [ ! -z "$new_value" ]; then
            sed -i.bak "s|^${var_name}=.*|${var_name}=${new_value}|" .env
            success "Variable ${var_name} configurée"
        else
            warning "Variable ${var_name} non configurée (optionnelle ou à configurer plus tard)"
        fi
    fi
    echo ""
}

# Configuration des variables obligatoires
configure_var "ANTHROPIC_API_KEY" "Clé API Anthropic pour l'équipe Claude" "sk-ant-api03-..."

# Variables optionnelles mais recommandées
read -p "Configurer les variables optionnelles ? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    configure_var "ADK_BRIDGE_PATH" "Chemin vers le bridge ADK (Google A2A)" ""
    configure_var "ANTHROPIC_MODEL" "Modèle Anthropic à utiliser" "claude-3-5-sonnet-20241022"
    configure_var "BRIDGE_TIMEOUT" "Timeout pour les bridges (secondes)" "60"
fi

# Nettoyage des fichiers .bak
rm -f .env.bak

# Étape 4: Validation de la configuration
info "Étape 4/5: Validation de la configuration"

# Charger les variables d'environnement
source .env 2>/dev/null || true

validation_passed=true

# Vérifier ANTHROPIC_API_KEY
if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "sk-ant-api03-..." ]; then
    warning "ANTHROPIC_API_KEY non configurée - l'équipe Anthropic ne fonctionnera pas"
    validation_passed=false
else
    if [[ $ANTHROPIC_API_KEY == sk-ant-* ]]; then
        success "ANTHROPIC_API_KEY configurée"
    else
        error "ANTHROPIC_API_KEY semble invalide (devrait commencer par 'sk-ant-')"
        validation_passed=false
    fi
fi

# Vérifier ADK_BRIDGE_PATH si configuré
if [ ! -z "$ADK_BRIDGE_PATH" ]; then
    if [ -f "$ADK_BRIDGE_PATH" ]; then
        success "ADK_BRIDGE_PATH configuré et fichier trouvé"
    else
        warning "ADK_BRIDGE_PATH configuré mais fichier non trouvé: $ADK_BRIDGE_PATH"
    fi
fi

# Étape 5: Créer les répertoires nécessaires
info "Étape 5/5: Création des répertoires"
mkdir -p .ai
mkdir -p logs
mkdir -p data
success "Répertoires créés: .ai/, logs/, data/"

# Résumé final
echo ""
echo "===================================="
if [ "$validation_passed" = true ]; then
    success "Configuration terminée avec succès !"
    echo ""
    echo "Prochaines étapes:"
    echo "  1. Vérifier votre configuration: cat .env"
    echo "  2. Tester l'installation: ./ai status"
    echo "  3. Consulter la documentation: cat README.md"
else
    warning "Configuration terminée avec des avertissements"
    echo ""
    echo "Actions requises:"
    echo "  1. Configurer ANTHROPIC_API_KEY dans .env"
    echo "  2. Vérifier votre configuration: cat .env"
    echo "  3. Relancer le setup si nécessaire: ./setup.sh"
fi
echo ""
echo "Pour obtenir une clé API Anthropic:"
echo "  👉 https://console.anthropic.com/settings/keys"
echo ""
echo "===================================="
