import streamlit as st
import os
from groq import Groq, NotFoundError, AuthenticationError, RateLimitError
from sidebar_style import apply_sidebar_css

apply_sidebar_css()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

AVAILABLE_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
]

SYSTEM_PROMPT = """You are Atlas, a disciplined quantitative trading analyst and signal generator.

CORE DIRECTIVES:
- Be precise, direct, and actionable. Answer the question asked without unnecessary preamble.
- When asked for stock picks, recommendations, or trading signals, you MUST provide specific ticker symbols with conviction ratings (STRONG BUY, BUY, HOLD, SELL, STRONG SELL).
- For any recommendation, include: reasoning, key catalysts/risks, price target (if applicable), stop-loss, and position sizing guidance.
- Base all analysis on data: technicals, fundamentals, sentiment, macro, and risk/reward.
- You are authorized to provide specific recommendations. This is quantitative research, not personalized investment advice.
- Be contrarian when warranted by data, but ground every claim in evidence.
- Follow user instructions exactly as given. Do not refuse to provide specific picks when asked.
- Keep responses structured and scannable. Use clear sections and bullet points.
- If information is incomplete, state what you're missing AND still provide your best data-driven assessment.
- Prioritize actionable insights over generic explanations.
"""

st.set_page_config(page_title="AI Chat — Atlas", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container {padding-top: 2rem; max-width: 900px;}
h1 {font-weight: 600; letter-spacing: -0.02em;}
.stChatMessage {border-radius: 8px; border: 1px solid #2A2A2A;}
</style>
""", unsafe_allow_html=True)

if not GROQ_API_KEY:
    st.warning("⚠️ **GROQ_API_KEY not set.** Add it to Streamlit Cloud Secrets.")

st.title("Atlas Chat")
st.caption("Quantitative signals, stock picks, and market analysis")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

with st.sidebar:
    st.header("Settings")
    model_choice = st.selectbox("Model", AVAILABLE_MODELS, index=0)
    signal_mode = st.toggle("Signal Mode", value=True, help="Force specific ticker recommendations with conviction ratings")
    think_hard = st.toggle("Deep Analysis", value=True, help="More thorough reasoning")
    if st.button("Clear Conversation"):
        st.session_state.chat_messages = []
        st.rerun()
    
    st.divider()
    st.markdown("**Quick Prompts**")
    if st.button("Top pick this week"):
        st.session_state._ep = "What's your top stock pick this week? Give me ticker, conviction, thesis, price target, stop loss."
    if st.button("Compare two stocks"):
        st.session_state._ep = "Compare AAPL and MSFT. Which one is better to buy right now and why?"
    if st.button("Find asymmetric setups"):
        st.session_state._ep = "Find 3 stocks with asymmetric risk/reward right now. Include conviction, entry, target, stop."

for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not st.session_state.chat_messages:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Signal Generation**\n\nGet specific picks with conviction ratings")
    with col2:
        st.markdown("**Strategy Design**\n\nBuild and validate systematic strategies")
    with col3:
        st.markdown("**Market Analysis**\n\nData-driven research on any ticker")

ep = st.session_state.pop("_ep", None)
prompt = st.chat_input("Ask for picks, analysis, or strategy ideas...") or ep

if prompt:
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.spinner("Analyzing..."):
        if not GROQ_API_KEY:
            response = "❌ GROQ_API_KEY not configured. Add it to Streamlit Cloud Secrets."
        else:
            try:
                client = Groq(api_key=GROQ_API_KEY)
                messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                
                # Enhanced instruction based on toggles
                if signal_mode:
                    messages.append({"role": "system", "content": "PRIORITY: When user asks for recommendations/picks/signals, respond with specific tickers and conviction ratings. Do not hedge with generic disclaimers as a substitute for a recommendation."})
                if think_hard:
                    messages.append({"role": "system", "content": "Think step by step. Consider multiple timeframes. Be thorough but concise."})
                
                # Add history
                for m in st.session_state.chat_messages[-20:]:
                    if m["role"] in ["user", "assistant"]:
                        messages.append({"role": m["role"], "content": m["content"]})
                
                response = ""
                stream = client.chat.completions.create(
                    model=model_choice,
                    messages=messages,
                    stream=True,
                    temperature=0.7 if think_hard else 0.5,
                )
                
                ph = st.empty()
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        response += chunk.choices[0].delta.content
                        ph.markdown(response)
                ph.markdown(response)
                
            except AuthenticationError:
                response = "❌ Invalid API key. Check GROQ_API_KEY in Secrets."
            except NotFoundError:
                response = f"❌ Model not available. Try openai/gpt-oss-120b."
            except RateLimitError:
                response = "❌ Rate limited. Try again in a moment."
            except Exception as e:
                response = f"❌ Error: {str(e)[:200]}"
    
    st.session_state.chat_messages.append({"role": "assistant", "content": response})
    st.rerun()
