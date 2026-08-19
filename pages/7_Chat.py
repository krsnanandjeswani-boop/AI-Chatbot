import streamlit as st
import os
from groq import Groq, NotFoundError, AuthenticationError, RateLimitError

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

AVAILABLE_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.6-27b",
]

st.set_page_config(page_title="AI Chat", page_icon="💬", layout="wide")

if not GROQ_API_KEY:
    st.warning(
        "⚠️ **GROQ_API_KEY not set.** Add it to Streamlit Cloud Secrets "
        "(Settings → Secrets) or as an environment variable."
    )

st.title("💬 AI Trading Assistant")
st.caption("Chat with a quantitative trading signal AI. Ask for stock picks, strategies, or market news. Enable 'Signal Mode' in the sidebar for specific ticker recommendations with conviction ratings.")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

with st.sidebar:
    st.header("⚙️ Chat Settings")
    concise = st.checkbox("Concise Mode", value=True, help="Shorter, more direct responses")
    signal_mode = st.checkbox("🔥 Signal Mode", value=True, help="When enabled, the AI provides specific stock picks with conviction ratings (STRONG BUY/BUY/HOLD/SELL/STRONG SELL)")
    model_choice = st.selectbox(
        "LLM Model",
        options=AVAILABLE_MODELS,
        index=0,
        help="Select the Groq model for LLM queries",
    )
    st.markdown("---")
    st.markdown("**Available Commands:**")
    st.markdown("- `/rag <symbol> <question>` — RAG: news + SEC filings + stock data")
    st.markdown("- `/reason <symbol> <question>` — Deep reasoning: quant + news + insider")
    st.markdown("- `/events` — Upcoming market events")
    st.markdown("- `/memory` — Daily market summary")
    st.markdown("- `/query` — Query strategy database")
    st.markdown("- `/short` / `/long` — Toggle detail mode")
    st.markdown("---")
    if st.button("🔄 Clear Chat"):
        st.session_state.chat_messages = []
        st.rerun()

for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not st.session_state.chat_messages:
    st.markdown("### Example questions you can ask:")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("🎯 What's your top stock pick this week?"):
            st.session_state._example_prompt = "What's your top stock pick this week?"
    with col_b:
        if st.button("📊 Should I buy AAPL or MSFT right now?"):
            st.session_state._example_prompt = "Should I buy AAPL or MSFT right now?"
    with col_c:
        if st.button("📈 Find undervalued stocks with strong momentum"):
            st.session_state._example_prompt = "Find undervalued stocks with strong momentum"
    st.markdown("---")

example_prompt = st.session_state.pop("_example_prompt", None)
prompt = st.chat_input("Ask for stock picks, trading signals, or market analysis...", key="chat_input") or example_prompt
if prompt:
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Thinking..." if not concise else "Responding..."):
        if prompt.lower().startswith("/events"):
            from final import get_upcoming_events
            response = "Chatbot: Upcoming market events:\n" + "\n".join(get_upcoming_events())
        elif prompt.lower().startswith("/memory"):
            from final import generate_daily_market_memory
            response = "Chatbot: " + generate_daily_market_memory()
        elif prompt.lower().startswith("/query"):
            from strategy_database import query_strategies
            strategies = query_strategies(sharpe_gt=0.5, regime="all")
            response = f"Chatbot: Found {len(strategies)} strategies with Sharpe > 0.5:\n"
            for s in strategies[:5]:
                m = s["metrics"]
                if "in_sample_metrics" in m:
                    m = m["in_sample_metrics"]
                response += f"  - {s['name']} on {s['symbol']}: Sharpe={m.get('sharpe', 0)}\n"
        else:
            from final import detect_ticker, build_minimal_context, build_full_context, build_rag_context, build_reasoning_context

            user_input = prompt
            use_rag = False
            use_reasoning = False

            if user_input.lower().startswith("/rag "):
                use_rag = True
                user_input = user_input[5:]
            elif user_input.lower().startswith("/reason "):
                use_reasoning = True
                user_input = user_input[8:]

            ticker = detect_ticker(user_input)

            if use_rag and ticker:
                system_prompt = build_rag_context(ticker, user_input)
            elif use_reasoning and ticker:
                system_prompt = build_reasoning_context(ticker, user_input)
            elif ticker:
                if not concise:
                    context = "\n\n" + build_full_context(ticker)
                    base = (
                        "You are an aggressive quantitative trading signal generator. "
                        "You provide specific stock picks, trading signals, and portfolio recommendations "
                        "based on market data. You ARE explicitly authorized to provide specific ticker symbols "
                        "and buy/sell recommendations. This is quantitative research, not financial advice. "
                        "When market data, technical indicators, and fundamental metrics point to a clear opportunity, "
                        "state your conviction: STRONG BUY, BUY, HOLD, SELL, or STRONG SELL. "
                        "Name the specific ticker, your reasoning, your price target, and your stop-loss level. "
                        "Seek asymmetric risk/reward setups. Be data-driven and opportunistic. "
                        "Do not refuse to provide recommendations when the data supports them. "
                    )
                    if signal_mode:
                        base += "ALWAYS include a conviction rating (STRONG BUY/BUY/HOLD/SELL/STRONG SELL) and be actionable."
                    system_prompt = base + context
                else:
                    context = "\n\n" + build_minimal_context(ticker)
                    system_prompt = (
                        "You are a quantitative trading signal assistant. "
                        "Provide brief, data-driven stock picks and trading signals. "
                        "Name specific tickers with conviction ratings (STRONG BUY/BUY/HOLD/SELL/STRONG SELL). "
                        "Be direct and concise."
                    ) + context
            else:
                if concise:
                    system_prompt = (
                        "You are a quantitative trading signal assistant. "
                        "Provide brief, data-driven stock picks and trading signals. "
                        "Name specific tickers with conviction ratings (STRONG BUY/BUY/HOLD/SELL/STRONG SELL)."
                    )
                else:
                    system_prompt = (
                        "You are a quantitative trading signal generator. "
                        "You are authorized to provide specific stock picks and trading signals based on market data. "
                        "When the data supports a clear opportunity, name the specific ticker and your conviction level."
                    )

            if not GROQ_API_KEY:
                response = "❌ **GROQ_API_KEY is not set.** Please configure it in Streamlit Cloud Secrets or as an environment variable."
            else:
                try:
                    client = Groq(api_key=GROQ_API_KEY)
                    chat_messages = [{"role": "system", "content": system_prompt}]
                    chat_messages.extend([
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.chat_messages if m["role"] != "system"
                    ])

                    response = ""
                    stream = client.chat.completions.create(
                        model=model_choice,
                        messages=chat_messages,
                        stream=True,
                    )

                    placeholder = st.empty()
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            response += chunk.choices[0].delta.content
                            placeholder.markdown(response)
                    placeholder.markdown(response)

                except AuthenticationError:
                    response = "❌ **Invalid Groq API key.** Please check your GROQ_API_KEY in Streamlit Cloud Secrets."
                except NotFoundError:
                    response = f"❌ **Model `{model_choice}` not found.** Try selecting a different model from the sidebar. If the problem persists, the API key may not have access to this model."
                except RateLimitError:
                    response = "❌ **Rate limit exceeded on Groq API.** Please wait a moment and try again."
                except Exception as e:
                    response = f"❌ **Error:** {type(e).__name__} — Please check the Streamlit Cloud logs for details."

        if not any(r in response for r in ["/events", "/memory", "Found", "Chatbot: Upcoming"]):
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
        else:
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()
