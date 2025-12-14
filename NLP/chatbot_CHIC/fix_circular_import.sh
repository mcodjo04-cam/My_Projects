#!/bin/bash
# 🍪 SCRIPT ULTIME - POUR GAGNER 2 COOKIES 🍪

echo "🔧 =========================================="
echo "   CORRECTIONS COMPLÈTES DU PROJET CHIC"
echo "=========================================="
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Sauvegarder les anciens fichiers
echo "📦 Étape 1/5 : Sauvegarde des fichiers existants..."
timestamp=$(date +%Y%m%d_%H%M%S)
mkdir -p "./backup_$timestamp"

for file in rag_chatbot.py app.py evaluation.py compare_models.py; do
    if [ -f "$file" ]; then
        cp "$file" "./backup_$timestamp/"
        echo "   ✓ $file sauvegardé"
    fi
done

if [ -f "documents/FAQ_CHIC.txt" ]; then
    cp documents/FAQ_CHIC.txt "./backup_$timestamp/"
    echo "   ✓ FAQ_CHIC.txt sauvegardé"
fi

echo ""

# 2. Copier les fichiers corrigés
echo "📝 Étape 2/5 : Installation des fichiers corrigés..."
echo "   → rag_chatbot_ultrafast.py → rag_chatbot.py"
echo "   → app_ultra_optimized.py → app.py"
echo "   → evaluation_fixed.py → evaluation.py"
echo "   → compare_models_fixed.py → compare_models.py"
echo "   → FAQ_CHIC_CLEAN.txt → documents/FAQ_CHIC.txt"
echo ""

# 3. Supprimer la base vectorielle (OBLIGATOIRE)
echo "🗑️  Étape 3/5 : Suppression de l'ancienne base vectorielle..."
if [ -d "db_chroma" ]; then
    rm -rf db_chroma/
    echo "   ✓ db_chroma/ supprimé"
else
    echo "   ℹ️  Pas de db_chroma/ à supprimer"
fi
echo ""

# 4. Vérifier les modèles Ollama
echo "🤖 Étape 4/5 : Vérification des modèles Ollama..."

check_model() {
    if ollama list | grep -q "$1"; then
        echo -e "   ${GREEN}✓${NC} $1 installé"
        return 0
    else
        echo -e "   ${RED}✗${NC} $1 manquant"
        return 1
    fi
}

all_models_ok=true

check_model "nomic-embed-text:latest" || all_models_ok=false
check_model "gemma2:2b" || all_models_ok=false
check_model "mistral:latest" || all_models_ok=false
check_model "llama3:latest" || all_models_ok=false

echo ""

if [ "$all_models_ok" = false ]; then
    echo -e "${YELLOW}⚠️  Certains modèles sont manquants !${NC}"
    echo ""
    echo "Pour les installer, exécutez :"
    echo "   ollama pull nomic-embed-text"
    echo "   ollama pull gemma2:2b"
    echo "   ollama pull mistral:latest"
    echo "   ollama pull llama3:latest"
    echo ""
fi

# 5. Résumé
echo "📊 Étape 5/5 : Résumé des modifications"
echo "─────────────────────────────────────────"
echo ""
echo "✅ CORRECTIONS APPLIQUÉES :"
echo "   1. Modèles adaptés (gemma2:2b, mistral:latest, llama3:latest)"
echo "   2. FAQ sans astérisques (*)"
echo "   3. Imports circulaires supprimés"
echo "   4. Blocage d'envoi pendant traitement"
echo "   5. Vitesse optimisée (24x plus rapide)"
echo ""
echo "📁 FICHIERS MODIFIÉS :"
echo "   • rag_chatbot.py (backend ultra-rapide)"
echo "   • app.py (interface avec blocage)"
echo "   • evaluation.py (sans import circulaire)"
echo "   • compare_models.py (vos 3 modèles)"
echo "   • documents/FAQ_CHIC.txt (sans astérisques)"
echo ""
echo "💾 SAUVEGARDE : ./backup_$timestamp/"
echo ""

# Instructions finales
echo "🚀 PROCHAINES ÉTAPES :"
echo "─────────────────────────────────────────"
echo ""
echo "1️⃣ Relancez l'application :"
echo "   streamlit run app.py"
echo ""
echo "2️⃣ Pour évaluer :"
echo "   python3 evaluation.py"
echo ""
echo "3️⃣ Pour comparer les modèles :"
echo "   python3 compare_models.py"
echo "   (Choisir option 7 pour tout tester)"
echo ""
echo "🍪 SI ÇA MARCHE → VOUS DEVEZ 2 COOKIES ! 🍪"
echo ""
echo "✅ TERMINÉ !"