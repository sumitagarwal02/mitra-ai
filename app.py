import streamlit as st
from agent import analyze_vibe_and_recommend

# Page Configuration
st.set_page_config(
    page_title="Mitra AI | Personal Wellness Space",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Gemini-Inspired Warm UI Styling
st.markdown("""
<style>
    .stApp {
        background-color: #131314;
        color: #e3e3e3;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 6rem;
        max-width: 760px;
    }
    .stChatMessage {
        background-color: transparent !important;
        border-radius: 16px;
        padding: 8px 12px;
    }
    .card-box {
        background-color: #1e1f20;
        border: 1px solid #333537;
        border-radius: 14px;
        padding: 16px;
        margin-top: 10px;
    }
    .reset-chip {
        background: rgba(56, 189, 248, 0.1);
        border-left: 3px solid #38bdf8;
        padding: 10px 14px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .journal-chip {
        background: rgba(168, 85, 247, 0.1);
        border-left: 3px solid #a855f7;
        padding: 10px 14px;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi there! I'm **Mitra** 🌿. I'm here to listen, support you, and help you find balance whenever you feel stressed, tired, or overwhelmed. How are you feeling right now?"
        }
    ]

# Sidebar Controls & Quick Starters
with st.sidebar:
    st.title("🌿 Mitra AI")
    st.caption("Personal Wellness Companion")
    st.divider()
    
    st.markdown("### 💬 Quick Prompts")
    if st.button("🖥️ Screen fatigue & eye strain", use_container_width=True):
        st.session_state.preset = "I've been staring at screens all day, my eyes hurt and my shoulders feel tight."
    if st.button("🔋 Low energy & overwhelmed", use_container_width=True):
        st.session_state.preset = "Feeling burnt out, low energy, and stressed about deadlines."
    if st.button("🧘 Need a 2-minute reset", use_container_width=True):
        st.session_state.preset = "I need a quick 2-minute relaxation exercise right now."
        
    st.divider()
    if st.button("🗑️ Reset Conversation", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hi there! I'm **Mitra** 🌿. I'm here to listen, support you, and help you find balance whenever you feel stressed, tired, or overwhelmed. How are you feeling right now?"
            }
        ]
        st.rerun()

# Header Section
st.markdown("<h1 style='text-align: center; color: #f8fafc;'>🌿 Mitra AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.05rem;'>Your personal space for calm, reflection, and instant resets</p>", unsafe_allow_html=True)
st.divider()

# Render Chat History
for msg in st.session_state.messages:
    avatar = "🌿" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        if isinstance(msg["content"], dict):
            rec = msg["content"]
            st.markdown(f"**Vibe Assessment**\n\n{rec['mood_analysis']}")
            
            st.markdown(f"""
            <div class="reset-chip">
                <strong>⚡ 2-Minute Micro Reset</strong><br>{rec['micro_exercise']}
            </div>
            <div class="journal-chip">
                <strong>✍️ Reflection Prompt</strong><br><em>"{rec['journal_prompt']}"</em>
            </div>
            """, unsafe_allow_html=True)
            
            search_url = f"https://www.youtube.com/results?search_query={rec['youtube_search_query'].replace(' ', '+')}"
            st.markdown(f"📺 **Suggested Content:** [{rec['youtube_search_query']}]({search_url})")
        else:
            st.markdown(msg["content"])

# Capture User Input or Preset
user_prompt = None
if "preset" in st.session_state and st.session_state.preset:
    user_prompt = st.session_state.preset
    st.session_state.preset = None

if not user_prompt:
    user_prompt = st.chat_input("Talk to Mitra... how is your day going?")

# Handle Response Generation
if user_prompt:
    # Append & Display User Input
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_prompt)

    # Generate Mitra AI Response
    with st.chat_message("assistant", avatar="🌿"):
        with st.spinner("Mitra is listening and crafting your response..."):
            try:
                rec = analyze_vibe_and_recommend(user_prompt)
                res_data = {
                    "mood_analysis": rec.mood_analysis,
                    "micro_exercise": rec.micro_exercise,
                    "journal_prompt": rec.journal_prompt,
                    "youtube_search_query": rec.youtube_search_query
                }
                
                st.markdown(f"**Vibe Assessment**\n\n{rec.mood_analysis}")
                st.markdown(f"""
                <div class="reset-chip">
                    <strong>⚡ 2-Minute Micro Reset</strong><br>{rec.micro_exercise}
                </div>
                <div class="journal-chip">
                    <strong>✍️ Reflection Prompt</strong><br><em>"{rec.journal_prompt}"</em>
                </div>
                """, unsafe_allow_html=True)
                
                search_url = f"https://www.youtube.com/results?search_query={rec.youtube_search_query.replace(' ', '+')}"
                st.markdown(f"📺 **Suggested Content:** [{rec.youtube_search_query}]({search_url})")

                st.session_state.messages.append({"role": "assistant", "content": res_data})
            except Exception as e:
                st.error(f"Error connecting to Mitra AI: {str(e)}")