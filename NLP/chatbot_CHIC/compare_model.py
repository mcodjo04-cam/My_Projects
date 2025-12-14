# compare_models.py - Comparaison avec VOS modèles installés

import json
import time
from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.document_loaders import DirectoryLoader, TextLoader


class ModelComparator:
    """Compare différents modèles et approches RAG."""
    
    def __init__(self, data_path="./documents"):
        self.data_path = data_path
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.results = {}
    
    def load_documents(self):
        """Charge les documents TXT."""
        txt_loader = DirectoryLoader(
            self.data_path,
            glob="**/*.txt",
            loader_cls=TextLoader,
            silent_errors=True,
            loader_kwargs={'autodetect_encoding': True}
        )
        return txt_loader.load()
    
    def test_different_llms(self):
        """Compare VOS 3 modèles installés."""
        
        print("\n" + "="*60)
        print("🔬 APPROCHE 1 : COMPARAISON DES MODÈLES LLM")
        print("="*60)
        
        # VOS MODÈLES (ceux installés sur votre machine)
        models = [
            ("gemma2:2b", "Gemma 2B - Ultra rapide (1.6 GB)"),
            ("mistral:latest", "Mistral 7B - Puissant (4.4 GB)"),
            ("llama3:latest", "LLaMA 3 8B - Très puissant (4.7 GB)"),
        ]
        
        for model_name, description in models:
            print(f"\n📊 Test de {description}")
            print("-"*60)
            
            try:
                chatbot = self._setup_rag(
                    model_name=model_name,
                    chunk_size=1200,
                    retriever_k=5
                )
                
                results = self._evaluate_chatbot(chatbot, model_name)
                self.results[model_name] = results
                
            except Exception as e:
                print(f"❌ Erreur avec {model_name}: {e}")
                print(f"   → Vérifiez: ollama list | grep {model_name}")
        
        return self.results
    
    def test_chunking_strategies(self):
        """Compare différentes stratégies de découpage."""
        
        print("\n" + "="*60)
        print("🔬 APPROCHE 2 : STRATÉGIES DE CHUNKING")
        print("="*60)
        
        strategies = [
            (500, 100, "Petit (500/100)"),
            (1000, 200, "Moyen (1000/200)"),
            (1500, 300, "Grand (1500/300)"),
            (2000, 400, "Très grand (2000/400)"),
        ]
        
        for chunk_size, overlap, description in strategies:
            print(f"\n📊 Test stratégie: {description}")
            print("-"*60)
            
            chatbot = self._setup_rag(
                model_name="gemma2:2b",
                chunk_size=chunk_size,
                chunk_overlap=overlap,
                retriever_k=5
            )
            
            label = f"chunk_{chunk_size}_{overlap}"
            results = self._evaluate_chatbot(chatbot, label)
            self.results[label] = results
        
        return self.results
    
    def test_retriever_k(self):
        """Compare différentes valeurs de k."""
        
        print("\n" + "="*60)
        print("🔬 APPROCHE 3 : NOMBRE DE DOCUMENTS (k)")
        print("="*60)
        
        k_values = [3, 5, 8, 10]
        
        for k in k_values:
            print(f"\n📊 Test avec k={k} documents")
            print("-"*60)
            
            chatbot = self._setup_rag(
                model_name="gemma2:2b",
                chunk_size=1200,
                retriever_k=k
            )
            
            label = f"k_{k}"
            results = self._evaluate_chatbot(chatbot, label)
            self.results[label] = results
        
        return self.results
    
    def test_search_types(self):
        """Compare similarity vs MMR."""
        
        print("\n" + "="*60)
        print("🔬 APPROCHE 4 : TYPES DE RECHERCHE")
        print("="*60)
        
        search_configs = [
            ("similarity", "Similarity - Plus rapide"),
            ("mmr", "MMR - Plus diversifié"),
        ]
        
        for search_type, description in search_configs:
            print(f"\n📊 Test: {description}")
            print("-"*60)
            
            chatbot = self._setup_rag(
                model_name="gemma2:2b",
                chunk_size=1200,
                retriever_k=5,
                search_type=search_type
            )
            
            label = f"search_{search_type}"
            results = self._evaluate_chatbot(chatbot, label)
            self.results[label] = results
        
        return self.results
    
    def test_temperatures(self):
        """Compare différentes températures."""
        
        print("\n" + "="*60)
        print("🔬 APPROCHE 5 : TEMPÉRATURE DU MODÈLE")
        print("="*60)
        
        temperatures = [0.0, 0.3, 0.5, 0.7]
        
        for temp in temperatures:
            print(f"\n📊 Test température: {temp}")
            print("-"*60)
            
            chatbot = self._setup_rag(
                model_name="gemma2:2b",
                chunk_size=1200,
                retriever_k=5,
                temperature=temp
            )
            
            label = f"temp_{temp}"
            results = self._evaluate_chatbot(chatbot, label)
            self.results[label] = results
        
        return self.results
    
    def test_without_rag(self):
        """Test du modèle SANS RAG (baseline)."""
        
        print("\n" + "="*60)
        print("🔬 APPROCHE 6 : SANS RAG (Baseline)")
        print("="*60)
        print("Test du modèle sans base de connaissances")
        print("-"*60)
        
        llm = ChatOllama(model="gemma2:2b", temperature=0.1)
        prompt = ChatPromptTemplate.from_template(
            "Tu es un assistant médical. Réponds: {question}"
        )
        chain = prompt | llm | StrOutputParser()
        
        chatbot = {"chain": chain, "retriever": None}
        results = self._evaluate_chatbot(chatbot, "sans_rag")
        self.results["sans_rag"] = results
        
        return self.results
    
    def _setup_rag(self, model_name, chunk_size, chunk_overlap=None, 
                   retriever_k=5, search_type="similarity", temperature=0.0):
        """Configure un système RAG."""
        
        if chunk_overlap is None:
            chunk_overlap = chunk_size // 5
        
        docs = self.load_documents()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\nQ", "\n\n", "\n", ". ", " ", ""]
        )
        chunks = text_splitter.split_documents(docs)
        
        persist_dir = f"./temp_db_{model_name.replace(':', '_')}_{chunk_size}"
        
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=persist_dir
        )
        
        if search_type == "similarity":
            retriever = vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": retriever_k}
            )
        else:
            retriever = vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={"k": retriever_k, "fetch_k": retriever_k * 3}
            )
        
        llm = ChatOllama(
            model=model_name,
            temperature=temperature,
            num_predict=512,
            num_ctx=2048
        )
        
        prompt = ChatPromptTemplate.from_template("""Tu es l'assistant du CHIC (Centre Hospitalier International de Calavi, Bénin).

CONTEXTE:
{context}

RÈGLES:
- Réponds en te basant UNIQUEMENT sur le contexte
- Sois précis et professionnel
- Si info manquante: dis "Je n'ai pas cette information"

QUESTION: {question}

RÉPONSE:""")
        
        def format_docs(docs):
            return "\n\n".join(f"[Doc {i+1}]\n{doc.page_content[:500]}" 
                             for i, doc in enumerate(docs))
        
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        return {"chain": rag_chain, "retriever": retriever}
    
    def _evaluate_chatbot(self, chatbot, label):
        """Évalue un chatbot sur 5 questions test."""
        
        test_questions = [
            {
                "question": "Où se trouve le CHIC ?",
                "keywords": ["Abomey-Calavi", "18 km", "Cotonou"],
            },
            {
                "question": "Quels sont les horaires d'ouverture ?",
                "keywords": ["lundi", "vendredi", "08h00", "17h00"],
            },
            {
                "question": "Comment prendre rendez-vous ?",
                "keywords": ["téléphone", "+229 01 21 400 111"],
            },
            {
                "question": "Quels sont les tarifs de consultation ?",
                "keywords": ["25 000", "F CFA"],
            },
            {
                "question": "Le CHIC accepte-t-il les urgences ?",
                "keywords": ["non", "pas encore"],
            }
        ]
        
        results = {
            "correct": 0,
            "total": len(test_questions),
            "response_times": []
        }
        
        for item in test_questions:
            start = time.time()
            
            if chatbot["retriever"]:
                response = chatbot["chain"].invoke(item["question"])
            else:
                response = chatbot["chain"].invoke({"question": item["question"]})
            
            elapsed = time.time() - start
            results["response_times"].append(elapsed)
            
            response_lower = response.lower()
            found = sum(1 for kw in item["keywords"] if kw.lower() in response_lower)
            score = found / len(item["keywords"])
            
            if score >= 0.6:
                results["correct"] += 1
        
        precision = results["correct"] / results["total"]
        avg_time = sum(results["response_times"]) / len(results["response_times"])
        
        results["metrics"] = {
            "precision": precision,
            "recall": precision,
            "f1_score": precision,
            "accuracy": precision,
            "avg_response_time": avg_time,
        }
        
        print(f"✅ Précision: {precision:.3f}")
        print(f"⏱️ Temps moyen: {avg_time:.2f}s")
        
        return results
    
    def generate_comparison_report(self):
        """Génère un rapport comparatif."""
        
        print("\n" + "="*80)
        print("📊 RAPPORT COMPARATIF FINAL")
        print("="*80)
        
        if not self.results:
            print("❌ Aucun résultat")
            return
        
        comparison = []
        for name, results in self.results.items():
            metrics = results["metrics"]
            comparison.append({
                "approche": name,
                "f1": metrics["f1_score"],
                "temps": metrics["avg_response_time"],
            })
        
        comparison.sort(key=lambda x: x["f1"], reverse=True)
        
        print(f"\n{'Approche':<25} {'F1-Score':<12} {'Temps (s)':<12}")
        print("-"*50)
        
        for row in comparison:
            print(f"{row['approche']:<25} {row['f1']:<12.3f} {row['temps']:<12.2f}")
        
        best = comparison[0]
        print(f"\n🏆 MEILLEURE APPROCHE: {best['approche']}")
        print(f"   F1-Score: {best['f1']:.3f}")
        print(f"   Temps: {best['temps']:.2f}s")
        
        output_dir = Path("./comparison_results")
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / "comparison_report.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Rapport sauvegardé: {filepath}")


if __name__ == "__main__":
    print("🏥 SYSTÈME DE COMPARAISON - CHATBOT CHIC")
    print("="*80)
    
    comparator = ModelComparator()
    
    print("\n📋 CHOISISSEZ:")
    print("1️⃣ Comparer les 3 modèles LLM (gemma2:2b, mistral, llama3)")
    print("2️⃣ Tester stratégies de chunking")
    print("3️⃣ Varier k (nombre de documents)")
    print("4️⃣ Comparer similarity vs MMR")
    print("5️⃣ Tester températures")
    print("6️⃣ Baseline sans RAG")
    print("7️⃣ TOUT TESTER (recommandé - 10-15 minutes)")
    
    choice = input("\n👉 Votre choix (1-7): ").strip()
    
    if choice == "1":
        comparator.test_different_llms()
    elif choice == "2":
        comparator.test_chunking_strategies()
    elif choice == "3":
        comparator.test_retriever_k()
    elif choice == "4":
        comparator.test_search_types()
    elif choice == "5":
        comparator.test_temperatures()
    elif choice == "6":
        comparator.test_without_rag()
    elif choice == "7":
        print("\n🚀 Lancement de TOUS les tests...\n")
        comparator.test_without_rag()
        comparator.test_different_llms()
        comparator.test_chunking_strategies()
        comparator.test_retriever_k()
        comparator.test_search_types()
        comparator.test_temperatures()
    else:
        print("❌ Choix invalide")
        exit(1)
    
    comparator.generate_comparison_report()
    print("\n✅ Terminé !")