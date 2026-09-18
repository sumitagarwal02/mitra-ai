import streamlit as st
from agent import analyze_vibe_and_recommend
from database import init_db, save_checkin, fetch_history, fetch_total_count

# Initialize SQLite Database
init_db()

# Page Configuration
st.set_page_config(
    page_title="Mitra AI | Personal Wellness Space",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom High-Contrast Theme (Ensures readability in light & dark mode)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .stApp {
        background-color: #0f172a !important;
        color: #f8fafc !important;
    }
    .stMarkdown, p, h1, h2, h3, h4, span, label {
        color: #f8fafc !important;
    }
    .stTextArea textarea {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        font-size: 1.05rem !important;
    }
    .reset-chip {
        background: rgba(56, 189, 248, 0.12);
        border-left: 4px solid #38bdf8;
        padding: 16px;
        border-radius: 12px;
        margin: 14px 0;
        font-size: 1.02rem;
        line-height: 1.6;
    }
    .journal-chip {
        background: rgba(168, 85, 247, 0.12);
        border-left: 4px solid #a855f7;
        padding: 16px;
        border-radius: 12px;
        margin: 14px 0;
        font-size: 1.02rem;
        line-height: 1.6;
    }
    .author-badge {
        font-size: 0.9rem;
        color: #94a3b8 !important;
        text-align: center;
        margin-top: 1rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar with Creator Attribution & Controls
with st.sidebar:
    st.markdown("## 🌿 Mitra AI")
    st.markdown("<p class='author-badge'>Made with ❤️ by <b>Sumit Agarwal</b></p>", unsafe_allow_html=True)
    st.divider()

    total_logs = fetch_total_count()
    st.metric(label="Total Wellness Check-ins", value=total_logs)

    st.divider()
    st.caption("Engineered for real-time energy alignment, mindfulness, and fast micro-resets.")

# Main Interface Header
st.markdown("<h1 style='text-align: center; font-size: 2.3rem; font-weight: 700;'>🌿 Mitra AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8 !important; font-size: 1.1rem;'>Your personal companion for calm, mental clarity, and resets</p>", unsafe_allow_html=True)

tab_chat, tab_analytics = st.tabs(["💬 Chat with Mitra", "📊 Mood History"])

with tab_chat:
    user_prompt = st.chat_input("Talk to Mitra... how is your day going?")

    if user_prompt:
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_prompt)

        with st.chat_message("assistant", avatar="🌿"):
            with st.spinner("Mitra is processing your response..."):
                try:
                    rec = analyze_vibe_and_recommend(user_prompt)
                    save_checkin(user_prompt, rec)

                    st.markdown(f"**Vibe Assessment**\n\n{rec.mood_analysis}")
                    st.markdown(f"""
                    <div class="reset-chip">
                        <strong style="color: #38bdf8 !important;">⚡ 2-Minute Micro Reset</strong><br>{rec.micro_exercise}
                    </div>
                    <div class="journal-chip">
                        <strong style="color: #a855f7 !important;">✍️ Reflection Prompt</strong><br><em>"{rec.journal_prompt}"</em>
                    </div>
                    """, unsafe_allow_html=True)

                    search_url = f"https://www.youtube.com/results?search_query={rec.youtube_search_query.replace(' ', '+')}"
                    st.markdown(f"▶️ **YouTube Practice:** [{rec.youtube_search_query}]({search_url})")

                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # Persistent Recent History
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