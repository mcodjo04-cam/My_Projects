import streamlit as st
import os
from rag_chatbot import setup_chatbot, run_chatbot_query
from chat_history import ChatHistoryManager
from datetime import datetime

# --- Configuration de la page ---
st.set_page_config(
    page_title="Assistant CHIC",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé - COULEURS MOOV
st.markdown("""
<style>
    /* Couleurs Moov : Bleu #0066CC et Orange #FF6600 */
    
    .main {
        background: linear-gradient(135deg, #f0f7ff 0%, #fff5f0 100%);
    }
    
    .title-container {
        background: linear-gradient(135deg, #0066CC 0%, #0052A3 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,102,204,0.3);
        border: 3px solid #FF6600;
    }
    
    .robot-avatar {
        font-size: 80px;
        animation: float 3s ease-in-out infinite;
        filter: drop-shadow(0 0 10px #FF6600);
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #0066CC 0%, #FF6600 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.6rem 1.2rem;
        font-size: 0.95rem;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(0,102,204,0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255,102,0,0.5);
        background: linear-gradient(135deg, #FF6600 0%, #0066CC 100%);
    }
    
    /* Messages chat */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #e6f2ff 0%, #ffffff 100%);
        border-left: 4px solid #0066CC;
    }
    
    .stChatMessage[data-testid="assistant-message"] {
        background: linear-gradient(135deg, #fff5f0 0%, #ffffff 100%);
        border-left: 4px solid #FF6600;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0066CC 0%, #0052A3 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Boutons de l'historique - Style spécial */
    [data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.15) !important;
        color:  black !important;
        border: 1px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(10px);
        text-align: left !important;
        padding: 0.5rem 0.75rem !important;
    }
    
    [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
        background: rgba(255, 102, 0, 0.8) !important;
        border-color: #FF6600;
        transform: translateX(5px);
    }
    
    /* Boutons d'action principaux dans sidebar */
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #FF6600 !important;
        color: white !important;
        border: 2px solid white;
        font-weight: 600;
    }        

    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: white !important;
        color: #0066CC !important;
        border-color: #FF6600;
    }
    
    /* Bouton supprimer individuel */
    [data-testid="stSidebar"] button[key*="del_"] {
        background: rgba(255, 0, 0, 0.2) !important;
        color: black !important;
        border: 1px solid rgba(255, 0, 0, 0.5);
        padding: 0.25rem 0.5rem !important;
        font-size: 0.85rem !important;
    }
    
    [data-testid="stSidebar"] button[key*="del_"]:hover {
        background: rgba(255, 0, 0, 0.8) !important;
        border-color: red;
    }
    
    /* Toggle dans sidebar */
    [data-testid="stSidebar"] .stCheckbox {
        background: rgba(255, 255, 255, 0.1);
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #0066CC 0%, #FF6600 100%);
        color: white;
        border-radius: 10px;
    }
    
    /* Chat input */
    .stChatInput {
        border: 2px solid #0066CC;
        border-radius: 25px;
    }
    
    .stChatInput:focus {
        border-color: #FF6600;
        box-shadow: 0 0 10px rgba(255,102,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- Initialisation du chatbot ---
@st.cache_resource
def initialize_chatbot():
    return setup_chatbot()

@st.cache_resource
def initialize_history_manager():
    return ChatHistoryManager()

try:
    qa_chain = initialize_chatbot()
    chatbot_ready = True
except Exception as e:
    st.error(f"❌ Erreur d'initialisation : {e}")
    qa_chain = None
    chatbot_ready = False

# Gestionnaire d'historique
history_manager = initialize_history_manager()

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🏥 CHIC")
    st.markdown("**Centre Hospitalier International de Calavi**")
    st.markdown("---")
    
    if os.path.exists("./db_chroma"):
        st.success("✅ Base de données active")
    else:
        st.warning("⚠️ Base de données introuvable")
    
    st.markdown("---")
    
    # Options d'affichage
    show_sources = st.toggle("📚 Afficher les sources", value=True)
    
    st.markdown("---")
    
    # NOUVELLE SECTION : Gestion des conversations
    st.markdown("### 💬 Historique")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Sauvegarder", use_container_width=True):
            if "messages" in st.session_state and len(st.session_state.messages) > 1:
                conv_id = history_manager.save_conversation(st.session_state.messages)
                st.success(f"✅ Sauvegardé !")
                st.session_state.last_saved_id = conv_id
            else:
                st.warning("Rien à sauvegarder")
    
    with col2:
        if st.button("🆕 Nouveau", use_container_width=True):
            # Sauvegarder automatiquement avant de créer une nouvelle conversation
            if "messages" in st.session_state and len(st.session_state.messages) > 1:
                history_manager.save_conversation(st.session_state.messages)
            st.session_state.clear()
            st.rerun()
    
    # Liste des conversations sauvegardées
    conversations = history_manager.list_conversations()
    
    if conversations:
        st.markdown(f"**{len(conversations)} conversation(s)**")
        
        # Afficher les conversations dans un conteneur scrollable
        for conv in conversations[:10]:  # Limiter à 10 plus récentes
            timestamp = datetime.fromisoformat(conv["timestamp"])
            date_str = timestamp.strftime("%d/%m/%Y %H:%M")
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if st.button(
                        f"📄 {conv['title'][:30]}",
                        key=f"load_{conv['id']}",
                        help=f"{date_str} - {conv['message_count']} messages",
                        use_container_width=True
                    ):
                        # Charger la conversation
                        loaded = history_manager.load_conversation(conv['id'])
                        if loaded:
                            st.session_state.messages = loaded['messages']
                            st.session_state.current_conversation_id = conv['id']
                            st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"del_{conv['id']}", help="Supprimer"):
                        history_manager.delete_conversation(conv['id'])
                        st.rerun()
        
        st.markdown("---")
        
        if st.button("🗑️ Tout supprimer", use_container_width=True):
            history_manager.delete_all_conversations()
            st.success("✅ Historique effacé")
            st.rerun()
    

# --- Titre ---
st.markdown("""
<div class="title-container">
    <div class="robot-avatar">🤖</div>
    <h1>Assistant CHIC</h1>
    <p style='font-size: 1.2rem; margin-top: 1rem;'>Votre assistant intelligent pour le Centre Hospitalier International de Calavi</p>
</div>
""", unsafe_allow_html=True)

# --- Initialisation session ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": """👋 **Bonjour et bienvenue au CHIC !**

Je suis votre assistant virtuel du **Centre Hospitalier International de Calavi**.

Je peux vous aider avec :
- 📍 **Localisation** : Où nous trouver
- ⏰ **Horaires** : Quand nous consulter
- 👨‍⚕️ **Spécialités** : Nos services médicaux
- 📞 **Rendez-vous** : Comment prendre RDV
- 💰 **Paiement** : Modalités et assurances
- 🔬 **Examens** : Imagerie et analyses

**Posez-moi votre question !** 😊"""
    })

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

if "processing" not in st.session_state:
    st.session_state.processing = False

if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

# Auto-sauvegarde périodique (tous les 5 messages)
if len(st.session_state.messages) > 1 and len(st.session_state.messages) % 5 == 0:
    if "last_auto_save_count" not in st.session_state or st.session_state.last_auto_save_count != len(st.session_state.messages):
        conv_id = st.session_state.get("current_conversation_id")
        history_manager.save_conversation(st.session_state.messages, conv_id)
        st.session_state.last_auto_save_count = len(st.session_state.messages)
        if conv_id is None:
            st.session_state.current_conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")

# --- Questions suggérées ---
if len(st.session_state.messages) <= 1 and chatbot_ready and not st.session_state.processing:
    st.markdown("### 💡 Questions fréquentes")
    
    questions = [
        "📍 Où se trouve exactement le CHIC ?",
        "⏰ Quels sont vos horaires d'ouverture ?",
        "📅 Comment prendre rendez-vous ?",
        "👨‍⚕️ Quelles sont les spécialités disponibles ?",
        "🔬 Quels examens d'imagerie proposez-vous ?",
        "💳 Quels sont les moyens de paiement ?"
    ]
    
    cols = st.columns(3)
    for idx, q in enumerate(questions):
        with cols[idx % 3]:
            if st.button(q, key=f"q{idx}"):
                st.session_state.pending_question = q
                st.rerun()
    
    st.markdown("---")

# --- Traitement question en attente ---
if st.session_state.pending_question and chatbot_ready:
    st.session_state.processing = True
    question = st.session_state.pending_question
    st.session_state.pending_question = None
    
    st.session_state.messages.append({"role": "user", "content": question})
    
    with st.spinner("🔍 Recherche dans la base de connaissances..."):
        try:
            response, sources = run_chatbot_query(qa_chain, question)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "sources": sources
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ Erreur lors du traitement : {str(e)}"
            })
    
    st.session_state.processing = False
    st.rerun()

# --- Affichage historique ---
for msg in st.session_state.messages:
    avatar = "🤖" if msg["role"] == "assistant" else "👤"
    
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        
        if msg["role"] == "assistant" and "sources" in msg and show_sources:
            if msg.get("sources"):
                with st.expander("📚 Sources consultées", expanded=False):
                    st.markdown(msg["sources"])

# --- Zone de saisie ---
if chatbot_ready and qa_chain:
    if st.session_state.processing:
        st.info("⏳ **Traitement en cours...** Veuillez patienter.")
        st.chat_input("💬 Votre question...", disabled=True)
    else:
        user_input = st.chat_input("💬 Posez votre question sur le CHIC...")
        
        if user_input:
            st.session_state.processing = True
            
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_input)
            
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Un instant..."):
                    try:
                        response, sources = run_chatbot_query(qa_chain, user_input)
                        st.markdown(response)
                        
                        if show_sources and sources:
                            with st.expander("📚 Sources consultées", expanded=False):
                                st.markdown(sources)
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "sources": sources
                        })
                    except Exception as e:
                        error = f"❌ Erreur : {str(e)}"
                        st.error(error)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error
                        })
            
            st.session_state.processing = False
else:
    st.error("⚠️ Le chatbot n'est pas disponible. Vérifiez qu'Ollama est en cours d'exécution.")

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #0066CC; font-weight: 600;'>
    <p>🏥 <strong style='color: #FF6600;'>CHIC</strong> - Centre Hospitalier International de Calavi</p>
    <p style='font-size: 0.9rem;'>Assistant intelligent propulsé par IA | Décembre 2025</p>
</div>
""", unsafe_allow_html=True)