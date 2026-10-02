import streamlit as st

from ollama_client import generate_response
from chat_store import (
    load_chats,
    create_chat,
    create_title,
    update_chat,
    delete_chat,
)

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Local AI Chat",
    page_icon="🤖",
    layout="wide",
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "chats" not in st.session_state:
    st.session_state.chats = load_chats()

if "active_chat_id" not in st.session_state:
    if st.session_state.chats:
        st.session_state.active_chat_id = st.session_state.chats[-1]["id"]
    else:
        new_chat = create_chat()
        st.session_state.chats.append(new_chat)
        st.session_state.active_chat_id = new_chat["id"]

# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def get_active_chat():
    for chat in st.session_state.chats:
        if chat["id"] == st.session_state.active_chat_id:
            return chat
    return None


def start_new_chat():
    new_chat = create_chat()
    st.session_state.chats.append(new_chat)
    st.session_state.active_chat_id = new_chat["id"]


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.title("🤖 Local AI")
    st.caption("Qwen • Ollama")

    st.divider()

    if st.button(
        "➕ New Chat",
        use_container_width=True,
    ):
        start_new_chat()
        st.rerun()

    st.divider()

    st.subheader("Conversation History")

    if not st.session_state.chats:
        st.caption("No conversations yet.")

    else:
        # Show newest chats first
        for chat in reversed(st.session_state.chats):

            title = chat.get("title", "New Chat")

            if len(title) > 30:
                title = title[:30] + "..."

            is_active = (
                chat["id"]
                == st.session_state.active_chat_id
            )

            button_text = (
                f"💬 {title}"
                if not is_active
                else f"🔵 {title}"
            )

            if st.button(
                button_text,
                key=f"chat_{chat['id']}",
                use_container_width=True,
            ):
                st.session_state.active_chat_id = chat["id"]
                st.rerun()

    st.divider()

    if st.button(
        "🗑️ Delete Current Chat",
        use_container_width=True,
    ):
        if len(st.session_state.chats) > 1:

            delete_chat(
                st.session_state.chats,
                st.session_state.active_chat_id,
            )

            st.session_state.active_chat_id = (
                st.session_state.chats[-1]["id"]
            )

            st.rerun()

        else:
            # Keep one empty chat
            chat = get_active_chat()

            if chat:
                chat["messages"] = []
                chat["title"] = "New Chat"

                update_chat(
                    st.session_state.chats,
                    chat,
                )

            st.rerun()

    st.divider()

    st.info(
        "Model: qwenllama:latest\n\n"
        "Running locally through Ollama."
    )


# --------------------------------------------------
# MAIN AREA
# --------------------------------------------------

active_chat = get_active_chat()

if active_chat is None:

    start_new_chat()
    active_chat = get_active_chat()


st.title("Local AI Chat")

st.caption(
    "Chat with Qwen running locally through Ollama."
)

# --------------------------------------------------
# EMPTY STATE
# --------------------------------------------------

if not active_chat["messages"]:

    st.success("🟢 Ollama connected locally")

    st.subheader("Start a conversation")

    st.write(
        "Type a question below and Qwen will "
        "generate a response using your local Ollama server."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(
            "💡 **Ask Questions**\n\n"
            "Ask questions and get answers "
            "from your local AI."
        )

    with col2:
        st.info(
            "🔒 **Private**\n\n"
            "Your conversation is processed "
            "locally through Ollama."
        )

    with col3:
        st.info(
            "⚡ **Lightweight**\n\n"
            "Powered by the lightweight "
            "Qwen model."
        )


# --------------------------------------------------
# DISPLAY CHAT HISTORY
# --------------------------------------------------

for message in active_chat["messages"]:

    role = message["role"]
    content = message["content"]

    if role == "user":
        with st.chat_message("user"):
            st.write(content)

    else:
        with st.chat_message("assistant"):
            st.write(content)


# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

user_prompt = st.chat_input(
    "Type your message..."
)


if user_prompt:

    # ----------------------------------------------
    # USER MESSAGE
    # ----------------------------------------------

    active_chat["messages"].append(
        {
            "role": "user",
            "content": user_prompt,
        }
    )

    # First message becomes chat title
    if active_chat["title"] == "New Chat":

        active_chat["title"] = create_title(
            user_prompt
        )

    update_chat(
        st.session_state.chats,
        active_chat,
    )

    # Show user message immediately
    with st.chat_message("user"):
        st.write(user_prompt)

    # ----------------------------------------------
    # MODEL RESPONSE
    # ----------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Qwen is thinking..."):

            response = generate_response(
                active_chat["messages"]
            )

        st.write(response)

    # ----------------------------------------------
    # SAVE ASSISTANT RESPONSE
    # ----------------------------------------------

    active_chat["messages"].append(
        {
            "role": "assistant",
            "content": response,
        }
    )

    update_chat(
        st.session_state.chats,
        active_chat,
    )

    st.rerun()