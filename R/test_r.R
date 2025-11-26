# ========================================
# 📊 TEST R DANS VS CODE
# ========================================

cat("="*60, "\n")
cat("📊 CONFIGURATION R\n")
cat("="*60, "\n")
cat("Version R    :", R.version.string, "\n")
cat("Plateforme   :", R.version$platform, "\n")
cat("="*60, "\n\n")

cat("📦 TEST DES PACKAGES :\n")
cat("-"*60, "\n")

# Packages à tester
packages <- c("ggplot2", "dplyr", "tidyverse", "readr", "knitr")

for (pkg in packages) {
  if (require(pkg, character.only = TRUE, quietly = TRUE)) {
    version <- as.character(packageVersion(pkg))
    cat(sprintf("✅ %-15s : %s\n", pkg, version))
  } else {
    cat(sprintf("❌ %-15s : Non installé\n", pkg))
  }
}

cat("="*60, "\n")
cat("🎯 Pour exécuter du code R :\n")
cat("   - Ctrl+Enter : Exécuter la ligne\n")
cat("   - Ctrl+Shift+S : Exécuter tout le script\n")
cat("="*60, "\n")
