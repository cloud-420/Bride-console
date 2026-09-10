import json
import os

import streamlit as st
from openai import OpenAI


# ============================================================
# HORIZON AI
# ============================================================

st.set_page_config(
    page_title="Horizon AI",
    page_icon="🌅",
    layout="wide",
)

MEMORY_FILE = "horizon_memory.json"


# ============================================================
# DEFAULT PERSONALITY
# ============================================================

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

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 2048

if "model" not in st.session_state:
    st.session_state.model = "gpt-5"

if "memory_enabled" not in st.session_state:
    st.session_state.memory_enabled = True


# ============================================================
# MEMORY
# ============================================================

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

    except (OSError, json.JSONDecodeError):
        pass

    return []


def save_memory(memory):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as file:
            json.dump(memory, file, indent=2)

    except OSError:
        pass


if "memory" not in st.session_state:
    st.session_state.memory = load_memory()


# ============================================================
# OPENAI CLIENT
# ============================================================

def get_client():
    """
    Read the API key from Streamlit Secrets.

    Never put the API key directly into app.py.
    """

    api_key = st.secrets.get("OPENAI_API_KEY")

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
            "OPENAI_API_KEY has not been configured."
        )

    conversation = [
        {
            "role": "developer",
            "content": st.session_state.personality,
        }
    ]

    if st.session_state.memory_enabled:

        conversation.extend(user_messages)

    else:

        if user_messages:
            conversation.append(
                user_messages[-1]
            )

    response = client.responses.create(
        model=st.session_state.model,
        input=conversation,
        temperature=st.session_state.temperature,
        max_output_tokens=st.session_state.max_tokens,
    )

    return response.output_text


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🌅 Horizon")

    st.caption(
        "Customizable personal AI"
    )

    st.divider()

    st.subheader("🤖 Model")

    st.session_state.model = st.text_input(
        "Model",
        value=st.session_state.model,
    )

    st.session_state.temperature = st.slider(
        "Creativity",
        min_value=0.0,
        max_value=1.5,
        value=st.session_state.temperature,
        step=0.1,
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

    if st.button(
        "🗑️ Clear conversation",
        use_container_width=True,
    ):

        st.session_state.messages = []
        st.rerun()

    if st.button(
        "🧹 Clear saved memory",
        use_container_width=True,
    ):

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


# ============================================================
# STATUS
# ============================================================

client_available = get_client() is not None

if client_available:

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

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# QUICK PROMPTS
# ============================================================

st.write("### ⚡ Quick Prompts")

col1, col2, col3 = st.columns(3)

with col1:

    quantum = st.button(
        "🌌 Quantum Physics",
        use_container_width=True,
    )

with col2:

    coding = st.button(
        "💻 Help Me Code",
        use_container_width=True,
    )

with col3:

    creative = st.button(
        "✨ Creative Mode",
        use_container_width=True,
    )


# ============================================================
# USER INPUT
# ============================================================

typed_prompt = st.chat_input(
    "Ask Horizon anything..."
)

prompt = None

if typed_prompt:
    prompt = typed_prompt

elif quantum:

    prompt = (
        "Explain quantum physics in a way that "
        "is easy to understand but still scientifically accurate."
    )

elif coding:

    prompt = (
        "Help me solve a programming problem. "
        "Ask for the relevant code if you need it."
    )

elif creative:

    prompt = (
        "Switch into creative mode and help me "
        "brainstorm an interesting original idea."
    )


# ============================================================
# PROCESS REQUEST
# ============================================================

if prompt:

    # Add user message.
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate answer.
    with st.chat_message("assistant"):

        with st.spinner(
            "Horizon is thinking..."
        ):

            try:

                answer = ask_horizon(
                    st.session_state.messages
                )

                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

                # Save a lightweight memory record.
                st.session_state.memory.append(
                    {
                        "user": prompt,
                        "assistant": answer,
                    }
                )

                # Keep memory from growing indefinitely.
                st.session_state.memory = (
                    st.session_state.memory[-50:]
                )

                save_memory(
                    st.session_state.memory
                )

            except Exception as error:

                st.error(
                    "Horizon could not generate a response."
                )

                st.code(
                    str(error)
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Horizon AI • Customizable • Cloud powered"
)
