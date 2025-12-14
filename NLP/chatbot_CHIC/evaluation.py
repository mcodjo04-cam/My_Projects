# evaluation.py - Système d'évaluation SANS import circulaire

import json
import time
from datetime import datetime
from pathlib import Path


class ChatbotEvaluator:
    """Évalue les performances du chatbot RAG."""
    
    def __init__(self, chatbot_system):
        self.chatbot = chatbot_system
        self.results = []
    
    def evaluate_dataset(self, dataset_file):
        """Évalue le chatbot sur un dataset."""
        print("🧪 ÉVALUATION DU CHATBOT")
        print("="*60)
        
        with open(dataset_file, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        total = len(dataset)
        print(f"📊 {total} questions à évaluer\n")
        
        results = {
            "total": total,
            "correct": 0,
            "partial": 0,
            "incorrect": 0,
            "response_times": [],
            "by_category": {},
            "details": []
        }
        
        # Import local pour éviter l'import circulaire
        from rag_chatbot import run_chatbot_query
        
        for i, item in enumerate(dataset, 1):
            print(f"\n[{i}/{total}] {item['question']}")
            
            start = time.time()
            response, sources = run_chatbot_query(self.chatbot, item['question'])
            elapsed = time.time() - start
            
            results["response_times"].append(elapsed)
            
            score = self._evaluate_response(
                response, 
                item.get('expected_keywords', [])
            )
            
            category = item.get('category', 'general')
            if category not in results["by_category"]:
                results["by_category"][category] = {
                    "total": 0, "correct": 0, "partial": 0, "incorrect": 0
                }
            
            results["by_category"][category]["total"] += 1
            
            if score >= 0.8:
                results["correct"] += 1
                results["by_category"][category]["correct"] += 1
                print(f"✅ CORRECT (score: {score:.2f})")
            elif score >= 0.4:
                results["partial"] += 1
                results["by_category"][category]["partial"] += 1
                print(f"⚠️ PARTIEL (score: {score:.2f})")
            else:
                results["incorrect"] += 1
                results["by_category"][category]["incorrect"] += 1
                print(f"❌ INCORRECT (score: {score:.2f})")
            
            print(f"⏱️ Temps: {elapsed:.2f}s")
            
            results["details"].append({
                "question": item['question'],
                "response": response[:200] + "...",
                "score": score,
                "time": elapsed,
                "category": category
            })
        
        self._calculate_metrics(results)
        self._save_results(results)
        
        return results
    
    def _evaluate_response(self, response, expected_keywords):
        """Calcule un score de 0 à 1."""
        response_lower = response.lower()
        
        if not expected_keywords:
            return 0.0
        
        found = sum(1 for kw in expected_keywords if kw.lower() in response_lower)
        return found / len(expected_keywords)
    
    def _calculate_metrics(self, results):
        """Calcule précision, rappel, F1-score."""
        
        total = results["total"]
        correct = results["correct"]
        partial = results["partial"]
        
        precision = correct / total if total > 0 else 0
        recall = (correct + partial) / total if total > 0 else 0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        avg_time = sum(results["response_times"]) / len(results["response_times"])
        
        results["metrics"] = {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "accuracy": correct / total,
            "avg_response_time": avg_time,
        }
        
        print("\n" + "="*60)
        print("📊 RÉSULTATS GLOBAUX")
        print("="*60)
        print(f"✅ Correctes:  {correct}/{total} ({correct/total*100:.1f}%)")
        print(f"⚠️ Partielles: {partial}/{total} ({partial/total*100:.1f}%)")
        print(f"❌ Incorrectes: {results['incorrect']}/{total}")
        print(f"\n📈 MÉTRIQUES")
        print(f"  • Précision:  {precision:.3f}")
        print(f"  • Rappel:     {recall:.3f}")
        print(f"  • F1-Score:   {f1:.3f}")
        print(f"\n⏱️ PERFORMANCE")
        print(f"  • Temps moyen: {avg_time:.2f}s")
        
        print(f"\n📂 PAR CATÉGORIE")
        for cat, stats in results["by_category"].items():
            acc = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            print(f"  • {cat.capitalize()}: {stats['correct']}/{stats['total']} ({acc*100:.1f}%)")
    
    def _save_results(self, results):
        """Sauvegarde les résultats."""
        
        output_dir = Path("./evaluation_results")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = output_dir / f"evaluation_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Résultats: {filepath}")


def create_test_dataset():
    """Crée un dataset de test."""
    
    dataset = [
        {
            "question": "Où se trouve le CHIC ?",
            "expected_keywords": ["Abomey-Calavi", "18 km", "Cotonou"],
            "category": "localisation"
        },
        {
            "question": "Quels sont les horaires d'ouverture ?",
            "expected_keywords": ["lundi", "vendredi", "08h00", "17h00"],
            "category": "horaires"
        },
        {
            "question": "Comment prendre rendez-vous ?",
            "expected_keywords": ["téléphone", "+229 01 21 400 111"],
            "category": "rendez-vous"
        },
        {
            "question": "Quels sont les tarifs de consultation ?",
            "expected_keywords": ["25 000", "F CFA"],
            "category": "tarifs"
        },
        {
            "question": "Quelles spécialités sont disponibles ?",
            "expected_keywords": ["cardiologie", "néphrologie", "oncologie"],
            "category": "spécialités"
        },
        {
            "question": "Le CHIC accepte-t-il les urgences ?",
            "expected_keywords": ["non", "pas encore"],
            "category": "services"
        },
        {
            "question": "Quels examens d'imagerie proposez-vous ?",
            "expected_keywords": ["IRM", "scanner", "échographie"],
            "category": "examens"
        },
        {
            "question": "Le CHIC accepte-t-il les assurances ?",
            "expected_keywords": ["oui", "conventionné"],
            "category": "paiement"
        },
        {
            "question": "Combien coûte une IRM ?",
            "expected_keywords": ["200 000", "250 000"],
            "category": "tarifs"
        },
        {
            "question": "Comment contacter le CHIC ?",
            "expected_keywords": ["+229 01 21 400 100", "contact@chichopital.bj"],
            "category": "contact"
        }
    ]
    
    with open("test_dataset.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Dataset créé: test_dataset.json ({len(dataset)} questions)")
    return dataset


if __name__ == "__main__":
    print("🏥 SYSTÈME D'ÉVALUATION - CHATBOT CHIC")
    print("="*60)
    
    print("\n1️⃣ Création du dataset...")
    create_test_dataset()
    
    print("\n2️⃣ Initialisation du chatbot...")
    # Import local ici pour éviter l'import circulaire
    from rag_chatbot import setup_chatbot
    
    chatbot = setup_chatbot()
    
    if not chatbot:
        print("❌ Impossible d'initialiser")
        exit(1)
    
    print("\n3️⃣ Lancement de l'évaluation...")
    evaluator = ChatbotEvaluator(chatbot)
    results = evaluator.evaluate_dataset("test_dataset.json")
    
    print("\n✅ Terminé !")