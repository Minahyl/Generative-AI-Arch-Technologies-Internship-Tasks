import json
import uuid
from pathlib import Path
from datetime import datetime


DATA_FOLDER = Path("data")
CHAT_FILE = DATA_FOLDER / "chats.json"


def initialize_storage():
    """Create the data folder and chat file if they don't exist."""

    DATA_FOLDER.mkdir(exist_ok=True)

    if not CHAT_FILE.exists():
        CHAT_FILE.write_text(
            "[]",
            encoding="utf-8"
        )


def load_chats():
    """Load all saved conversations from JSON."""

    initialize_storage()

    try:
        with open(
            CHAT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (json.JSONDecodeError, FileNotFoundError):

        return []


def save_chats(chats):
    """Save conversations to JSON."""

    initialize_storage()

    with open(
        CHAT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chats,
            file,
            indent=4,
            ensure_ascii=False
        )


def create_chat():
    """Create a new empty conversation."""

    return {
        "id": str(uuid.uuid4()),

        "title": "New Chat",

        "created_at": datetime.now().isoformat(),

        "updated_at": datetime.now().isoformat(),

        "messages": []
    }


def create_title(message):
    """Create a short title from the first user message."""

    title = message.strip()

    if len(title) > 35:
        title = title[:35].rstrip() + "..."

    return title


def update_chat(chats, chat):
    """Update an existing conversation."""

    chat["updated_at"] = datetime.now().isoformat()

    for index, existing_chat in enumerate(chats):

        if existing_chat["id"] == chat["id"]:

            chats[index] = chat

            break

    save_chats(chats)


def delete_chat(chats, chat_id):
    """Delete a conversation."""

    chats[:] = [
        chat
        for chat in chats
        if chat["id"] != chat_id
    ]

    save_chats(chats)