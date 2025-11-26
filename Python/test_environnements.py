"""
🧪 Test de tous les environnements conda
"""

import sys
import os

print("="*60)
print("🐍 CONFIGURATION PYTHON ACTUELLE")
print("="*60)
print(f"Version Python : {sys.version}")
print(f"Exécutable     : {sys.executable}")
print(f"Environnement  : {os.environ.get('CONDA_DEFAULT_ENV', 'Aucun')}")
print("="*60)

# Test des imports
print("\n📦 TEST DES PACKAGES :")
print("-"*60)

packages = {
    'numpy': 'NumPy',
    'pandas': 'Pandas',
    'matplotlib': 'Matplotlib',
    'seaborn': 'Seaborn',
    'scikit-learn': 'Scikit-learn (sklearn)',
    'jupyter': 'Jupyter'
}

for module, name in packages.items():
    module_name = module if module != 'scikit-learn' else 'sklearn'
    try:
        mod = __import__(module_name)
        version = getattr(mod, '__version__', 'N/A')
        print(f"✅ {name:20} : {version}")
    except ImportError:
        print(f"❌ {name:20} : Non installé")

print("="*60)
print("🎯 Pour changer d'environnement :")
print("   1. Cliquez en bas à droite sur la version Python")
print("   2. Sélectionnez un environnement conda")
print("   3. Ou dans le terminal : conda activate <nom_env>")
print("="*60)
