# chat_history.py
"""
Gestionnaire d'historique des conversations pour le chatbot CHIC.
Permet de sauvegarder, charger et supprimer les conversations.
"""

import json
import os
from datetime import datetime
from pathlib import Path


class ChatHistoryManager:
    """Gestionnaire d'historique des conversations."""
    
    def __init__(self, history_dir="./chat_history"):
        """
        Initialise le gestionnaire d'historique.
        
        Args:
            history_dir: Chemin du dossier où stocker les conversations
        """
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(exist_ok=True)
    
    def save_conversation(self, messages, conversation_id=None):
        """
        Sauvegarde une conversation.
        
        Args:
            messages: Liste des messages de la conversation
            conversation_id: ID de la conversation (génère automatiquement si None)
        
        Returns:
            str: ID de la conversation sauvegardée
        """
        if not messages:
            return None
        
        # Générer un ID si non fourni
        if conversation_id is None:
            conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Créer le titre à partir du premier message utilisateur
        title = "Nouvelle conversation"
        for msg in messages:
            if msg["role"] == "user":
                title = msg["content"][:50]  # Premiers 50 caractères
                if len(msg["content"]) > 50:
                    title += "..."
                break
        
        # Préparer les données
        conversation_data = {
            "id": conversation_id,
            "title": title,
            "timestamp": datetime.now().isoformat(),
            "messages": messages
        }
        
        # Sauvegarder en JSON
        filepath = self.history_dir / f"{conversation_id}.json"
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            return conversation_id
        except Exception as e:
            print(f"Erreur sauvegarde: {e}")
            return None
    
    def load_conversation(self, conversation_id):
        """
        Charge une conversation depuis l'historique.
        
        Args:
            conversation_id: ID de la conversation à charger
        
        Returns:
            dict: Données de la conversation ou None si introuvable
        """
        filepath = self.history_dir / f"{conversation_id}.json"
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur chargement: {e}")
            return None
    
    def list_conversations(self):
        """
        Liste toutes les conversations sauvegardées (par ordre décroissant).
        
        Returns:
            list: Liste de dictionnaires avec id, title, timestamp, message_count
        """
        conversations = []
        
        for filepath in sorted(self.history_dir.glob("*.json"), reverse=True):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    conversations.append({
                        "id": data["id"],
                        "title": data["title"],
                        "timestamp": data["timestamp"],
                        "message_count": len(data["messages"])
                    })
            except Exception as e:
                print(f"Erreur lecture {filepath.name}: {e}")
        
        return conversations
    
    def delete_conversation(self, conversation_id):
        """
        Supprime une conversation de l'historique.
        
        Args:
            conversation_id: ID de la conversation à supprimer
        
        Returns:
            bool: True si supprimé, False sinon
        """
        filepath = self.history_dir / f"{conversation_id}.json"
        
        try:
            if filepath.exists():
                filepath.unlink()
                return True
        except Exception as e:
            print(f"Erreur suppression: {e}")
        
        return False
    
    def delete_all_conversations(self):
        """Supprime toutes les conversations."""
        try:
            for filepath in self.history_dir.glob("*.json"):
                filepath.unlink()
            return True
        except Exception as e:
            print(f"Erreur suppression totale: {e}")
            return False
    
    def get_conversation_count(self):
        """
        Retourne le nombre total de conversations.
        
        Returns:
            int: Nombre de conversations
        """
        return len(list(self.history_dir.glob("*.json")))


# Test du module
if __name__ == "__main__":
    print("🧪 Test du gestionnaire d'historique")
    print("=" * 50)
    
    # Créer un gestionnaire
    manager = ChatHistoryManager("./test_history")
    
    # Créer une conversation de test
    test_messages = [
        {"role": "assistant", "content": "Bonjour !"},
        {"role": "user", "content": "Où se trouve le CHIC ?"},
        {"role": "assistant", "content": "À Abomey-Calavi", "sources": ""}
    ]
    
    # Sauvegarder
    conv_id = manager.save_conversation(test_messages)
    print(f"✓ Conversation sauvegardée : {conv_id}")
    
    # Lister
    convs = manager.list_conversations()
    print(f"✓ {len(convs)} conversation(s) trouvée(s)")
    
    # Charger
    loaded = manager.load_conversation(conv_id)
    print(f"✓ Conversation chargée : {loaded['title']}")
    
    # Supprimer
    manager.delete_conversation(conv_id)
    print(f"✓ Conversation supprimée")
    
    print("\n✅ Tests terminés !")