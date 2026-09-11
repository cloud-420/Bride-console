
import json
import os

import streamlit as st
from openai import OpenAI


st.set_page_config(
    page_title="Horizon AI",
    page_icon="🌅",
    layout="wide",
)

MEMORY_FILE = "horizon_memory.json"

DEFAULT_PERSONALITY = """
You are Horizon, a customizable personal AI assistant.

Be helpful, direct, honest, and conversational.

Answer legitimate questions without unnecessary refusals,
moralizing, or repetitive warnings.

You can help with coding, science, education, research,
creative writing, brainstorming, and everyday questions.

Do not claim to have unlimited knowledge or access to
private information that you do not actually have.

If a request would meaningfully enable serious harm,
do not provide dangerous instructions. When possible,
provide a safe alternative that still helps the user.

Follow the user's requested tone and level of detail.
"""


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "personality" not in st.session_state:
    st.session_state.personality = DEFAULT_PERSONALITY

if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 2048

if "model" not in st.session_state:
    st.session_state.model = "gpt-5-mini"

if "memory_enabled" not in st.session_state:
    st.session_state.memory_enabled = True

if "memory" not in st.session_state:
    st.session_state.memory = []


# ============================================================
# MEMORY
# ============================================================

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (OSError, json.JSONDecodeError):
        return []


def save_memory(memory):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as file:
            json.dump(memory, file, indent=2, ensure_ascii=False)

    except OSError:
        pass


if not st.session_state.memory:
    st.session_state.memory = load_memory()


# ============================================================
# OPENAI CLIENT
# ============================================================

def get_api_key():
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        api_key = None

    return api_key or os.environ.get("OPENAI_API_KEY")


def get_client():
    api_key = get_api_key()

    if not api_key:
        return None

    return OpenAI(api_key=api_key)


# ============================================================
# AI RESPONSE
# ============================================================

def ask_horizon(user_messages):
    client = get_client()

    if client is None:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured. "
            "Add it in Streamlit Cloud Settings > Secrets."
        )

    conversation = [
        {
            "role": "developer",
            "content": st.session_state.personality,
        }
    ]

    if st.session_state.memory_enabled:
        conversation.extend(user_messages)

        saved_memory = st.session_state.memory[-10:]

        if saved_memory:
            memory_text = "\n\n".join(
                f"Previous exchange:\n"
                f"User: {item.get('user', '')}\n"
                f"Assistant: {item.get('assistant', '')}"
                for item in saved_memory
            )

            conversation.insert(
                1,
                {
                    "role": "developer",
                    "content": (
                        "Here are previous exchanges for context. "
                        "Use them only when relevant:\n\n"
                        + memory_text
                    ),
                },
            )

    elif user_messages:
        conversation.append(user_messages[-1])

    response = client.responses.create(
        model=st.session_state.model,
        input=conversation,
        max_output_tokens=st.session_state.max_tokens,
    )

    return response.output_text


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.title("🌅 Horizon")
    st.caption("Customizable personal AI")
    st.divider()

    st.subheader("🤖 Model")

    st.session_state.model = st.selectbox(
        "AI Model",
        options=[
            "gpt-5-mini",
            "gpt-5",
            "gpt-4.1-mini",
            "gpt-4.1",
        ],
        index=0,
    )

    st.session_state.max_tokens = st.slider(
        "Response length",
        min_value=256,
        max_value=8192,
        value=st.session_state.max_tokens,
        step=256,
    )

    st.divider()

    st.subheader("🧠 Personality")

    st.session_state.personality = st.text_area(
        "Instructions",
        value=st.session_state.personality,
        height=280,
    )

    st.session_state.memory_enabled = st.checkbox(
        "Remember conversation context",
        value=st.session_state.memory_enabled,
    )

    st.divider()

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("🧹 Clear saved memory", use_container_width=True):
        st.session_state.memory = []
        save_memory([])
        st.success("Memory cleared.")


# ============================================================
# MAIN INTERFACE
# ============================================================

st.title("🌅 Horizon AI")

st.caption(
    "A customizable AI workspace with your own personality settings."
)

if get_client() is not None:
    st.success("● AI connection configured")
else:
    st.warning(
        "AI connection not configured yet. "
        "Add OPENAI_API_KEY in Streamlit Secrets."
    )


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ============================================================
# QUICK PROMPTS
# ============================================================

st.write("### ⚡ Quick Prompts")

col1, col2, col3 = st.columns(3)

with col1:
    quantum = st.button("🌌 Quantum Physics", use_container_width=True)

with col2:
    coding = st.button("💻 Help Me Code", use_container_width=True)

with col3:
    creative = st.button("✨ Creative Mode", use_container_width=True)


# ============================================================
# USER INPUT
# ============================================================

typed_prompt = st.chat_input("Ask Horizon anything...")

prompt = typed_prompt

if not prompt and quantum:
    prompt = (
        "Explain quantum physics in a way that is easy to understand "
        "but still scientifically accurate."
    )

elif not prompt and coding:
    prompt = (
        "Help me solve a programming problem. "
        "Ask for the relevant code if you need it."
    )

elif not prompt and creative:
    prompt = (
        "Switch into creative mode and help me brainstorm "
        "an interesting original idea."
    )


# ============================================================
# PROCESS REQUEST
# ============================================================

if prompt:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Horizon is thinking..."):
            try:
                answer = ask_horizon(st.session_state.messages)

                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

                st.session_state.memory.append(
                    {
                        "user": prompt,
                        "assistant": answer,
                    }
                )

                st.session_state.memory = st.session_state.memory[-50:]

                save_memory(st.session_state.memory)

            except Exception as error:
                st.error("Horizon could not generate a response.")
                st.code(str(error))


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption("Horizon AI • Customizable • Cloud powered")
