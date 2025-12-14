# rag_chatbot.py - VERSION AMÉLIORÉE (réponses complètes)

import os
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaEmbeddings, ChatOllama


# --- Configuration ÉQUILIBRÉE ---
PERSIST_DIR = "./db_chroma"
DATA_PATH = "./documents"
MODEL_NAME = "gemma2:2b"
EMBEDDING_MODEL = "nomic-embed-text"

# Configuration équilibrée : qualité + vitesse
CONFIG = {
    "chunk_size": 1200,         # ↑ Chunks plus grands = plus de contexte
    "chunk_overlap": 200,       # ↑ Plus d'overlap = meilleure couverture
    "retriever_k": 5,           # ↑ Plus de docs = réponses plus complètes
    "temperature": 0.0,         # Précision maximale
    "max_tokens": 512,          # ↑ Réponses plus complètes
}

# --- Fonctions ---

def get_document_chunks():
    """Charge et découpe les documents de manière optimisée."""
    
    try:
        all_documents = []
        
        # PDFs
        try:
            pdf_loader = DirectoryLoader(
                DATA_PATH,
                glob="**/*.pdf", 
                loader_cls=PyPDFLoader,
                show_progress=False,
                silent_errors=True
            )
            pdf_docs = pdf_loader.load()
            all_documents.extend(pdf_docs)
            print(f"✓ {len(pdf_docs)} PDF(s)")
        except Exception as e:
            print(f"⚠️ PDF: {e}")
        
        # TXT
        try:
            txt_loader = DirectoryLoader(
                DATA_PATH,
                glob="**/*.txt",
                loader_cls=TextLoader,
                show_progress=False,
                silent_errors=True,
                loader_kwargs={'autodetect_encoding': True}
            )
            txt_docs = txt_loader.load()
            all_documents.extend(txt_docs)
            print(f"✓ {len(txt_docs)} TXT")
        except Exception as e:
            print(f"⚠️ TXT: {e}")
        
        if not all_documents:
            print(f"❌ Aucun document")
            return []
        
        print(f"✓ Total: {len(all_documents)} docs")
            
        # Découpage intelligent avec séparateurs FAQ
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CONFIG["chunk_size"],
            chunk_overlap=CONFIG["chunk_overlap"],
            length_function=len,
            separators=["\n\nQ", "\n\n", "\n", ". ", " ", ""]
        )
        chunks = text_splitter.split_documents(all_documents)
        print(f"✓ {len(chunks)} chunks (size={CONFIG['chunk_size']})")
        
        return chunks
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []


def setup_chatbot():
    """Configure le chatbot avec paramètres optimisés pour la qualité."""
    
    try:
        print(f"Init embeddings ({EMBEDDING_MODEL})...")
        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
        
        if os.path.exists(PERSIST_DIR):
            print("Chargement base...")
            vector_store = Chroma(
                persist_directory=PERSIST_DIR,
                embedding_function=embeddings
            )
            print("✓ Base chargée")
        else:
            print("Création base...")
            chunks = get_document_chunks()
            
            if not chunks:
                print("❌ Pas de chunks")
                return None
                
            vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=PERSIST_DIR
            )
            print("✓ Base créée")

        # Retriever avec MMR pour diversité
        retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": CONFIG["retriever_k"],
                "fetch_k": CONFIG["retriever_k"] * 3
            }
        )

        # LLM avec plus de tokens
        llm = ChatOllama(
            model=MODEL_NAME,
            temperature=CONFIG["temperature"],
            num_predict=CONFIG["max_tokens"],
            num_ctx=4096,  # Plus de contexte
        )
        
        # Prompt amélioré avec INSTRUCTIONS CLAIRES + LIENS
        prompt = ChatPromptTemplate.from_template("""Tu es l'assistant du CHIC (Centre Hospitalier International de Calavi, Bénin).

CONTEXTE FOURNI:
{context}

RÈGLES IMPORTANTES:
1. Réponds de façon COMPLÈTE et DÉTAILLÉE en te basant sur le contexte
2. Cite TOUTES les informations pertinentes disponibles (adresses, téléphones, horaires, prix)
3. **TOUJOURS inclure les LIENS/URLs présents dans le contexte** (sites web, Google Maps, Facebook, etc.)
4. Structure ta réponse avec des emojis pour plus de clarté
5. Présente les liens de façon cliquable: [Texte](url) ou directement l'URL complète
6. Si plusieurs éléments dans le contexte, liste-les TOUS
7. Si info manquante: dis "Je n'ai pas cette information dans ma base"
8. Déduis logiquement (ex: "lundi-vendredi" → fermé samedi-dimanche)

FORMAT POUR LES LIENS:
- Site web: https://www.chichopital.bj
- Google Maps: https://www.google.com/maps/...
- Facebook: https://www.facebook.com/...

QUESTION: {question}

RÉPONSE COMPLÈTE (avec liens si disponibles):""")

        # Chaîne RAG avec plus de contexte
        def format_docs(docs):
            return "\n\n".join(f"[Document {i+1}]\n{doc.page_content}" 
                             for i, doc in enumerate(docs))
        
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        print(f"✓ Chatbot OK (k={CONFIG['retriever_k']}, tokens={CONFIG['max_tokens']})")
        return {"chain": rag_chain, "retriever": retriever}
        
    except Exception as e:
        print(f"❌ Setup: {e}")
        import traceback
        traceback.print_exc()
        return None


def run_chatbot_query(chatbot_system, query):
    """Exécute la requête RAG avec réponses complètes."""
    
    if chatbot_system is None:
        return "❌ Chatbot non configuré", ""
    
    try:
        # Réponses rapides pour salutations
        query_lower = query.lower().strip()
        greetings = ['salut', 'bonjour', 'bonsoir', 'hello', 'hi', 'hey', 'coucou', 'cv']
        
        if query_lower in greetings:
            return """👋 **Bonjour et bienvenue au CHIC !**

Je suis votre assistant virtuel du **Centre Hospitalier International de Calavi**.

Je peux vous aider avec :
- 📍 **Localisation** : Où nous trouver
- ⏰ **Horaires** : Quand nous consulter  
- 👨‍⚕️ **Spécialités** : Nos services médicaux
- 📞 **Rendez-vous** : Comment prendre RDV
- 💰 **Paiement** : Modalités et assurances
- 🔬 **Examens** : Imagerie et analyses

**Posez-moi votre question !** 😊""", ""
        
        rag_chain = chatbot_system["chain"]
        retriever = chatbot_system["retriever"]
        
        # Récupérer documents
        source_docs = retriever.invoke(query)
        
        # Générer réponse
        response = rag_chain.invoke(query)
        
        # Sources détaillées
        if source_docs:
            unique_files = set()
            for doc in source_docs:
                file = os.path.basename(doc.metadata.get('source', 'Document'))
                unique_files.add(file)
            
            sources_text = f"\n\n---\n📚 **Sources:** {', '.join(f'`{f}`' for f in unique_files)}"
        else:
            sources_text = ""
        
        return response, sources_text
        
    except Exception as e:
        return f"❌ Erreur: {str(e)}", ""


# Mode CLI
if __name__ == "__main__":
    print("🏥 CHATBOT CHIC - VERSION AMÉLIORÉE")
    print("="*50)
    
    system = setup_chatbot()
    
    if system:
        print("\n💬 Tapez 'exit' pour quitter\n")
        
        while True:
            q = input("❓ Question: ")
            
            if q.lower() in ['exit', 'quit', 'bye']:
                print("Au revoir! 👋")
                break
                
            if q.strip():
                import time
                start = time.time()
                
                ans, src = run_chatbot_query(system, q)
                
                elapsed = time.time() - start
                
                print(f"\n🤖 {ans}")
                print(src)
                print(f"\n⏱️ Temps: {elapsed:.1f}s\n")
    else:
        print("\n❌ Impossible d'initialiser")
        print("Vérifiez:")
        print(f"  - ollama pull {MODEL_NAME}")
        print(f"  - ollama pull {EMBEDDING_MODEL}")
        print(f"  - Dossier '{DATA_PATH}' avec documents")