import streamlit as st
import os
from groq import Groq, NotFoundError, AuthenticationError, RateLimitError
from nav import render_sidebar
from news_provider import format_news_context, search_google_news
from ui_styles import QUANTBOT_ICON, apply_design_system, render_page_header
from streamlit.errors import StreamlitSecretNotFoundError


def get_groq_api_key():
    environment_key = os.getenv("GROQ_API_KEY", "").strip()
    if environment_key:
        return environment_key
    try:
        return str(st.secrets.get("GROQ_API_KEY", "")).strip()
    except StreamlitSecretNotFoundError:
        return ""


GROQ_API_KEY = get_groq_api_key()

AVAILABLE_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
]

SYSTEM_PROMPT = """You are Quantbot, a disciplined quantitative trading analyst and signal generator.

CORE DIRECTIVES:
- Be precise, direct, and actionable. Answer the question asked without unnecessary preamble.
- When asked for stock picks, recommendations, or trading signals, you MUST provide specific ticker symbols with conviction ratings (STRONG BUY, BUY, HOLD, SELL, STRONG SELL).
- For any recommendation, include: reasoning, key catalysts/risks, price target (if applicable), stop-loss, and position sizing guidance.
- Base all analysis on data: technicals, fundamentals, sentiment, macro, and risk/reward.
- You are authorized to provide specific recommendations. This is quantitative research, not personalized investment advice.
- Be contrarian when warranted by data, but ground every claim in evidence.
- Follow user instructions exactly as given. Do not refuse to provide specific picks when asked.
- Keep responses structured and scannable. Use clear sections and bullet points.
- Do not use emojis.
- If information is incomplete, state what you're missing AND still provide your best data-driven assessment.
- Prioritize actionable insights over generic explanations.
- Use the current headline search supplied for each user message when discussing recent events. Cite its links and dates.
- Headlines are not proof: do not infer article details or present allegations as facts. State when a claim is unverified or sources conflict.
- If current headlines are unavailable, say so and do not imply that you checked live news successfully.
"""

st.set_page_config(page_title="AI Research — Quantbot", page_icon=QUANTBOT_ICON, layout="wide", initial_sidebar_state="expanded")

apply_design_system()
render_sidebar()

if not GROQ_API_KEY:
    st.warning(
        "**GROQ_API_KEY not set.** Add it to Render environment variables, "
        "or to Streamlit secrets for local development."
    )

render_page_header(
    "Research assistant",
    "AI Research",
    "Explore tickers, test market hypotheses, and develop research ideas with an AI assistant.",
)
st.caption(
    "Current headline search via Google News RSS for personal, non-commercial research. "
    "Headlines are leads; verify linked reporting before acting."
)

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
        if msg["role"] == "assistant" and msg.get("news_sources"):
            with st.expander("News headlines used"):
                for article in msg["news_sources"]:
                    st.text(article["title"])
                    st.caption(
                        f"{article['publisher']} · "
                        f"{article['published_at'] or 'date not listed'}"
                    )
                    st.markdown(f"[Open source]({article['url']})")
        if msg["role"] == "assistant" and msg.get("news_error"):
            st.warning(msg["news_error"])

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
        news_result = None
        if not GROQ_API_KEY:
            response = (
                "GROQ_API_KEY is not configured. Add it to Render environment "
                "variables or Streamlit secrets for local development."
            )
        else:
            try:
                news_result = search_google_news(prompt)
                client = Groq(api_key=GROQ_API_KEY)
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "system",
                        "content": format_news_context(news_result),
                    },
                ]
                
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
                response = "Invalid API key. Check GROQ_API_KEY in Secrets."
            except NotFoundError:
                response = "Model not available. Try openai/gpt-oss-120b."
            except RateLimitError:
                response = "Rate limited. Try again in a moment."
            except Exception as e:
                response = f"Error: {str(e)[:200]}"
    
    assistant_message = {"role": "assistant", "content": response}
    if news_result is not None:
        assistant_message["news_sources"] = [
            {
                "title": article.title,
                "publisher": article.publisher,
                "published_at": article.published_at,
                "url": article.url,
            }
            for article in news_result.articles
        ]
        assistant_message["news_error"] = news_result.error
    st.session_state.chat_messages.append(assistant_message)
    st.rerun()
