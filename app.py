import uuid
import re
import streamlit as st
import streamlit.components.v1 as components
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

# Custom High-Contrast & Glassmorphism Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .hero-card {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 18px;
        padding: 24px 20px;
        text-align: center;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }
    
    .reset-chip {
        background: rgba(56, 189, 248, 0.1);
        border-left: 4px solid #38bdf8;
        padding: 18px;
        border-radius: 12px;
        margin: 16px 0;
        line-height: 1.7;
    }
    
    .journal-chip {
        background: rgba(168, 85, 247, 0.1);
        border-left: 4px solid #a855f7;
        padding: 18px;
        border-radius: 12px;
        margin: 16px 0;
        line-height: 1.7;
    }
    
    .rag-badge {
        background: rgba(34, 197, 94, 0.12);
        border: 1px solid rgba(34, 197, 94, 0.3);
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
        color: #22c55e !important;
        font-weight: 600;
        margin-bottom: 12px;
        display: inline-block;
    }
    
    .author-badge {
        font-size: 0.9rem;
        opacity: 0.8;
        text-align: center;
        margin-top: 1rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

def speak_text(text_to_speak: str):
    """Triggers native browser Text-to-Speech synthesis."""
    clean_text = re.sub(r'[^\w\s.,!?-]', '', text_to_speak).replace('\n', ' ')
    js_code = f"""
        <script>
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance("{clean_text}");
            utterance.rate = 0.92;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
        </script>
    """
    components.html(js_code, height=0)

# Sidebar
with st.sidebar:
    st.markdown("## 🌿 Mitra AI")
    st.markdown("<p class='author-badge'>Made with ❤️ by <b>Sumit Agarwal</b></p>", unsafe_allow_html=True)
    st.divider()
    total_logs = fetch_total_count()
    st.metric(label="Total Wellness Check-ins", value=total_logs)
    st.caption("🧠 **RAG Engine:** ChromaDB Memory Active")
    st.caption("🎙️ **Voice Engine:** Web Speech Synthesis Active")

# Hero Banner
st.markdown("""
<div class="hero-card">
    <h1 style="margin: 0; font-size: 2.2rem; font-weight: 700;">🌿 Mitra AI</h1>
    <p style="margin-top: 8px; margin-bottom: 0; opacity: 0.85; font-size: 1.05rem;">
        Your creative space for deep reflection, mindfulness, and audio resets
    </p>
</div>
""", unsafe_allow_html=True)

tab_chat, tab_analytics = st.tabs(["💬 Chat & Listen", "📊 Mood History"])

with tab_chat:
    user_prompt = st.chat_input("Talk to Mitra... how is your day going?")

    if user_prompt:
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_prompt)

        with st.chat_message("assistant", avatar="🌿"):
            with st.spinner("Mitra is listening deeply and weaving a creative response..."):
                try:
                    rag_memory = retrieve_relevant_context(user_prompt, n_results=2)
                    rec = analyze_vibe_and_recommend(user_prompt, rag_context=rag_memory)

                    save_checkin(user_prompt, rec)
                    store_reflection(str(uuid.uuid4()), user_prompt, rec.mood_analysis)

                    if rag_memory != "No prior relevant reflections found.":
                        st.markdown("<div class='rag-badge'>🧠 Recalled relevant past reflections via ChromaDB</div>", unsafe_allow_html=True)

                    st.markdown(f"**Deep Reflection**\n\n{rec.mood_analysis}")
                    
                    st.markdown(f"""
                    <div class="reset-chip">
                        <strong style="color: #38bdf8; font-size: 1.05rem;">⚡ Sensory Reset Exercise</strong><br><br>
                        {rec.micro_exercise}
                    </div>
                    <div class="journal-chip">
                        <strong style="color: #a855f7; font-size: 1.05rem;">✍️ Creative Exploration Prompt</strong><br><br>
                        <em>"{rec.journal_prompt}"</em>
                    </div>
                    """, unsafe_allow_html=True)

                    search_url = f"https://www.youtube.com/results?search_query={rec.youtube_search_query.replace(' ', '+')}"
                    st.markdown(f"▶️ **Suggested Soundscape:** [{rec.youtube_search_query}]({search_url})")

                    # Voice Output Trigger Button
                    if st.button("🔊 Listen to Mitra"):
                        audio_script = f"{rec.mood_analysis}. Here is your reset exercise: {rec.micro_exercise}"
                        speak_text(audio_script)

                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # Recent Reflections Section
    st.divider()
    st.markdown("### 📜 Recent Reflections")
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
    st.markdown("### 📊 Reflection Archive")
    history = fetch_history()
    if history:
        for item in history:
            timestamp, prompt, analysis, reset, journal, yt = item
            st.markdown(f"**{timestamp}**")
            st.caption(f"Prompt: \"{journal}\"")
            st.divider()
    else:
        st.caption("Archive empty.")