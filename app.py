import uuid
import streamlit as st
from agent import analyze_vibe_and_recommend
from database import init_db, save_checkin, fetch_history, fetch_total_count
from rag_memory import store_reflection, retrieve_relevant_context

# Initialize SQLite Database
init_db()

# Page Configuration
st.set_page_config(
    page_title="Mitra AI | Personal Wellness Space",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Light Serene Aesthetics & Card Layout Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Light Serene Ambient Background */
    .stApp {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%) !important;
        color: #0f172a !important;
    }
    
    /* High Contrast Typography */
    .stMarkdown, p, h1, h2, h3, h4, span, label {
        color: #0f172a !important;
    }
    
    /* Hero Layout Container Behind Heading */
    .hero-banner {
        background: linear-gradient(135deg, #ffffff 0%, #ecfdf5 50%, #f0f9ff 100%);
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 28px 20px;
        text-align: center;
        box-shadow: 0 10px 30px -10px rgba(16, 185, 129, 0.12);
        margin-bottom: 24px;
    }
    
    /* Reset & Reflection Chips */
    .reset-chip {
        background: #f0f9ff;
        border-left: 5px solid #0284c7;
        padding: 16px;
        border-radius: 12px;
        margin: 14px 0;
        font-size: 1rem;
        line-height: 1.6;
        box-shadow: 0 2px 8px rgba(2, 132, 199, 0.05);
    }
    
    .journal-chip {
        background: #faf5ff;
        border-left: 5px solid #9333ea;
        padding: 16px;
        border-radius: 12px;
        margin: 14px 0;
        font-size: 1rem;
        line-height: 1.6;
        box-shadow: 0 2px 8px rgba(147, 51, 234, 0.05);
    }
    
    .rag-badge {
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        padding: 10px 14px;
        border-radius: 10px;
        font-size: 0.88rem;
        color: #047857 !important;
        font-weight: 500;
        margin-bottom: 14px;
        display: inline-block;
    }
    
    .author-badge {
        font-size: 0.9rem;
        color: #64748b !important;
        text-align: center;
        margin-top: 1rem;
        font-weight: 500;
    }
    
    /* Custom Tab List Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #ffffff;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #475569 !important;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar with Creator Attribution & RAG Indicator
with st.sidebar:
    st.markdown("## 🌿 Mitra AI")
    st.markdown("<p class='author-badge'>Made with ❤️ by <b>Sumit Agarwal</b></p>", unsafe_allow_html=True)
    st.divider()
    total_logs = fetch_total_count()
    st.metric(label="Total Wellness Check-ins", value=total_logs)
    st.caption("🧠 **RAG Memory Engine:** ChromaDB Vector Search Enabled")
    st.caption("✨ Light Serene Mode Active")

# Main Hero Layout Banner Behind Heading
st.markdown("""
<div class="hero-banner">
    <h1 style="margin: 0; font-size: 2.4rem; font-weight: 700; color: #0f172a !important;">🌿 Mitra AI</h1>
    <p style="margin-top: 8px; margin-bottom: 0; color: #475569 !important; font-size: 1.05rem;">
        Your personal space for calm, mental clarity, and energetic resets
    </p>
</div>
""", unsafe_allow_html=True)

tab_chat, tab_analytics = st.tabs(["💬 Chat with Mitra", "📊 Mood History"])

with tab_chat:
    user_prompt = st.chat_input("Talk to Mitra... how is your day going?")

    if user_prompt:
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_prompt)

        with st.chat_message("assistant", avatar="🌿"):
            with st.spinner("Mitra is recalling vector memory & crafting your reset..."):
                try:
                    # 1. Retrieve RAG Memory Context from ChromaDB
                    rag_memory = retrieve_relevant_context(user_prompt, n_results=2)

                    # 2. Generate LLM Analysis with RAG Context
                    rec = analyze_vibe_and_recommend(user_prompt, rag_context=rag_memory)

                    # 3. Save to SQL Database & ChromaDB Vector Store
                    save_checkin(user_prompt, rec)
                    store_reflection(str(uuid.uuid4()), user_prompt, rec.mood_analysis)

                    # Display RAG memory status indicator
                    if rag_memory != "No prior relevant reflections found.":
                        st.markdown("<div class='rag-badge'>🧠 <i>Recalled relevant past reflections via ChromaDB Vector Memory</i></div>", unsafe_allow_html=True)

                    st.markdown(f"**Vibe Assessment**\n\n{rec.mood_analysis}")
                    st.markdown(f"""
                    <div class="reset-chip">
                        <strong style="color: #0284c7 !important;">⚡ 2-Minute Micro Reset</strong><br>
                        <span style="color: #334155 !important;">{rec.micro_exercise}</span>
                    </div>
                    <div class="journal-chip">
                        <strong style="color: #9333ea !important;">✍️ Reflection Prompt</strong><br>
                        <span style="color: #334155 !important;"><em>"{rec.journal_prompt}"</em></span>
                    </div>
                    """, unsafe_allow_html=True)

                    search_url = f"https://www.youtube.com/results?search_query={rec.youtube_search_query.replace(' ', '+')}"
                    st.markdown(f"▶️ **YouTube Practice:** [{rec.youtube_search_query}]({search_url})")

                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # Persistent Recent Reflections Section
    st.divider()
    st.markdown("<h3 style='font-size: 1.3rem;'>📜 Recent Reflections</h3>", unsafe_allow_html=True)
    history = fetch_history()
    if history:
        for item in history[:5]:
            timestamp, prompt, analysis, reset, journal, yt = item
            with st.expander(f"🗓️ {timestamp} - {prompt[:40]}..."):
                st.write(f"**Your Note:** {prompt}")
                st.write(f"**Mitra's Assessment:** {analysis}")
                st.info(f"**Reset:** {reset}")
                search_url = f"https://www.youtube.com/results?search_query={yt.replace(' ', '+')}"
                st.markdown(f"▶️ [{yt}]({search_url})")
    else:
        st.caption("No check-ins logged yet. Send a message above to get started!")

with tab_analytics:
    st.markdown("<h3 style='font-size: 1.3rem;'>📊 Reflection Archive</h3>", unsafe_allow_html=True)
    history = fetch_history()
    if history:
        for item in history:
            timestamp, prompt, analysis, reset, journal, yt = item
            st.markdown(f"**{timestamp}**")
            st.caption(f"Prompt: \"{journal}\"")
            st.divider()
    else:
        st.caption("Archive empty.")