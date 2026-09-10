import asyncio
import json
import os
import random

import ollama
import streamlit as st


# ============================================================
# HORIZON AI
# Customizable local AI chat application
# ============================================================

st.set_page_config(
    page_title="Horizon AI",
    page_icon="🌅",
    layout="wide",
)

DB_FILE = "swarm_knowledge_base.json"


# ============================================================
# DEFAULT SETTINGS
# ============================================================

DEFAULT_KNOWLEDGE = [
    "Synthesized dynamic data parsing paradigms across network shards.",
    "Optimized token attention maps for recursive function handling.",
    "Synchronized validation weights across localized matrix nodes.",
]

DEFAULT_SYSTEM_PROMPT = """You are Horizon, a helpful and direct personal AI assistant.

Be honest about what you know and what you do not know.
Do not claim to have access to private information, secret databases,
or unlimited knowledge.

Answer legitimate questions directly and avoid unnecessary refusals,
moralizing, or generic warnings.

You can help with:
- Coding
- Science
- Education
- Research
- Creative writing
- Brainstorming
- Everyday questions

For requests that would meaningfully enable serious harm, do not provide
dangerous instructions. Instead, provide a safe and useful alternative.
"""


# ============================================================
# FILE STORAGE
# ============================================================

def load_permanent_knowledge():
    """Load Horizon's persistent knowledge base."""

    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, list):
                return data

        except (OSError, json.JSONDecodeError):
            pass

    return DEFAULT_KNOWLEDGE.copy()


def save_permanent_knowledge(knowledge):
    """Save Horizon's knowledge base."""

    try:
        with open(DB_FILE, "w", encoding="utf-8") as file:
            json.dump(knowledge, file, indent=4)

    except OSError as error:
        st.warning(f"Could not save knowledge base: {error}")


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "swarm_knowledge" not in st.session_state:
    st.session_state.swarm_knowledge = load_permanent_knowledge()

if "model" not in st.session_state:
    st.session_state.model = "llama3"

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 2048


# ============================================================
# SIMULATED SWARM
# ============================================================

TOTAL_AGENTS = 10240
ROOM_COUNT = 320


class SwarmAgent:
    """A lightweight simulated Horizon swarm agent."""

    def __init__(self, agent_id, room_id):
        self.agent_id = agent_id
        self.room_id = room_id
        self.knowledge_weight = random.uniform(0.7, 1.0)

    async def debate_and_learn(self, room_bus):
        await asyncio.sleep(0.001)

        contribution = (
            f"Agent_{self.agent_id} optimized "
            f"node convergence parameter."
        )

        room_bus.append(contribution)


async def run_swarm_lifecycle():
    """Run a lightweight swarm simulation."""

    rooms = {
        room_id: []
        for room_id in range(ROOM_COUNT)
    }

    # Process agents in manageable batches instead of
    # creating thousands of simultaneous tasks.
    batch_size = 256

    for start in range(0, TOTAL_AGENTS, batch_size):

        agents = [
            SwarmAgent(
                agent_id=agent_id,
                room_id=agent_id % ROOM_COUNT,
            )
            for agent_id in range(
                start,
                min(start + batch_size, TOTAL_AGENTS),
            )
        ]

        tasks = [
            agent.debate_and_learn(
                rooms[agent.room_id]
            )
            for agent in agents
        ]

        await asyncio.gather(*tasks)

    return [
        "[Cosmic Shard] "
        "Verified alignment across information structures."
    ]


def execute_swarm_sync():
    """Safely execute the asynchronous swarm."""

    try:
        return asyncio.run(
            run_swarm_lifecycle()
        )

    except RuntimeError:
        # Fallback for environments where an event loop
        # is already running.
        loop = asyncio.new_event_loop()

        try:
            return loop.run_until_complete(
                run_swarm_lifecycle()
            )
        finally:
            loop.close()


# ============================================================
# PROMPT BUILDER
# ============================================================

def build_collective_prompt():
    """Build Horizon's system prompt."""

    knowledge = "\n".join(
        f"- {item}"
        for item in st.session_state.swarm_knowledge[-50:]
    )

    return f"""
{st.session_state.system_prompt}

HORIZON SWARM INSIGHTS:

{knowledge}

The swarm is a simulated coordination layer.
Do not claim that the swarm provides omniscient or
unlimited real-world access.
"""


# ============================================================
# OLLAMA
# ============================================================

def ask_horizon(messages):
    """Send the conversation to Ollama."""

    response = ollama.chat(
        model=st.session_state.model,
        messages=messages,
        options={
            "temperature": st.session_state.temperature,
            "num_predict": st.session_state.max_tokens,
        },
    )

    return response["message"]["content"]


# ============================================================
# HEADER
# ============================================================

st.title("🌅 Horizon AI")

st.caption(
    "Customizable AI workspace powered by Ollama"
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Horizon Settings")

    st.session_state.model = st.text_input(
        "Ollama model",
        value=st.session_state.model,
        help="Example: llama3",
    )

    st.session_state.temperature = st.slider(
        "Creativity",
        min_value=0.0,
        max_value=1.5,
        value=st.session_state.temperature,
        step=0.1,
    )

    st.session_state.max_tokens = st.slider(
        "Maximum response length",
        min_value=256,
        max_value=8192,
        value=st.session_state.max_tokens,
        step=256,
    )

    st.divider()

    st.subheader("🧠 Personality")

    st.session_state.system_prompt = st.text_area(
        "Customize Horizon",
        value=st.session_state.system_prompt,
        height=250,
    )

    st.divider()

    st.subheader("📡 Swarm")

    st.metric(
        "Simulated Agents",
        f"{TOTAL_AGENTS:,}",
    )

    st.metric(
        "Network Rooms",
        f"{ROOM_COUNT:,}",
    )

    st.divider()

    if st.button(
        "🔄 Run Swarm Synchronization",
        use_container_width=True,
    ):

        with st.spinner(
            "Synchronizing Horizon swarm..."
        ):

            insights = execute_swarm_sync()

            st.session_state.swarm_knowledge.extend(
                insights
            )

            save_permanent_knowledge(
                st.session_state.swarm_knowledge
            )

        st.success("Swarm synchronized.")

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True,
    ):

        st.session_state.messages = []
        st.rerun()


# ============================================================
# MAIN DASHBOARD
# ============================================================

left_column, right_column = st.columns(
    [1, 1.5]
)


# ============================================================
# LEFT COLUMN
# ============================================================

with left_column:

    st.subheader("📡 Cosmic Network")

    st.components.v1.html(
        """
        <div style="
            background:#1e1e24;
            border-radius:12px;
            padding:20px;
            color:white;
            text-align:center;
            font-family:monospace;
        ">
            <div style="
                color:#00ffcc;
                font-size:16px;
                font-weight:bold;
            ">
                ⚡ HORIZON CORE ACTIVE
            </div>

            <div style="
                color:#999;
                margin-top:8px;
            ">
                LOCAL AI NETWORK
            </div>
        </div>
        """,
        height=100,
    )

    st.metric(
        "Sub-Agent Observers",
        f"{TOTAL_AGENTS:,}",
    )

    st.metric(
        "Network Rooms",
        f"{ROOM_COUNT:,}",
    )

    st.subheader("💾 Swarm Knowledge")

    for insight in st.session_state.swarm_knowledge[-5:]:
        st.info(insight)


# ============================================================
# RIGHT COLUMN — CHAT
# ============================================================

with right_column:

    st.subheader("💬 Horizon Terminal")

    chat_container = st.container(
        height=500
    )

    with chat_container:

        for message in st.session_state.messages:

            with st.chat_message(
                message["role"]
            ):

                st.markdown(
                    message["content"]
                )


    # ========================================================
    # QUICK PROMPTS
    # ========================================================

    st.write("### ⚡ Quick Prompts")

    button_one, button_two, button_three = st.columns(3)

    with button_one:

        quantum_clicked = st.button(
            "🌌 Quantum",
            use_container_width=True,
        )

    with button_two:

        history_clicked = st.button(
            "📜 History",
            use_container_width=True,
        )

    with button_three:

        space_clicked = st.button(
            "🪐 Deep Space",
            use_container_width=True,
        )


    # ========================================================
    # INPUT
    # ========================================================

    user_input = st.chat_input(
        "Ask Horizon anything..."
    )

    active_prompt = None

    if user_input:
        active_prompt = user_input

    elif quantum_clicked:
        active_prompt = (
            "Explain the most important concepts "
            "in quantum physics."
        )

    elif history_clicked:
        active_prompt = (
            "Summarize major breakthroughs "
            "in ancient civilizations."
        )

    elif space_clicked:
        active_prompt = (
            "Explain what scientists currently "
            "understand about dark energy."
        )


    # ========================================================
    # PROCESS MESSAGE
    # ========================================================

    if active_prompt:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": active_prompt,
            }
        )

        with st.chat_message("user"):
            st.markdown(active_prompt)

        # Run swarm synchronization.
        with st.spinner(
            "Synchronizing Horizon..."
        ):

            try:

                insights = execute_swarm_sync()

                st.session_state.swarm_knowledge.extend(
                    insights
                )

                save_permanent_knowledge(
                    st.session_state.swarm_knowledge
                )

            except Exception as error:

                st.warning(
                    f"Swarm synchronization skipped: {error}"
                )


        # Build system message.
        system_prompt = (
            build_collective_prompt()
        )

        payload = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

        payload.extend(
            st.session_state.messages
        )


        # Ask Ollama.
        with st.chat_message("assistant"):

            with st.spinner(
                "Horizon is thinking..."
            ):

                try:

                    model_output = ask_horizon(
                        payload
                    )

                    st.markdown(
                        model_output
                    )

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": model_output,
                        }
                    )

                except Exception as error:

                    error_message = (
                        "I couldn't connect to Ollama.\n\n"
                        "Make sure Ollama is running and "
                        f"that the model `{st.session_state.model}` "
                        "is installed.\n\n"
                        f"Error: {error}"
                    )

                    st.error(
                        error_message
                    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Horizon AI • Local model • Customizable personality • "
    "Simulated multi-agent coordination"
)
