import os
import json
import uuid


CHAT_DIR = "chat_history"

os.makedirs(CHAT_DIR, exist_ok=True)


# -----------------------------
# CREATE NEW CHAT
# -----------------------------

def create_chat():

    chat_id = str(uuid.uuid4())

    filepath = os.path.join(CHAT_DIR, f"{chat_id}.json")

    with open(filepath, "w") as f:
        json.dump([], f)

    return chat_id


# -----------------------------
# LOAD CHAT
# -----------------------------

def load_chat(chat_id):

    filepath = os.path.join(CHAT_DIR, f"{chat_id}.json")

    if not os.path.exists(filepath):
        return []

    with open(filepath, "r") as f:
        messages = json.load(f)

    return messages


# -----------------------------
# SAVE MESSAGE
# -----------------------------

def save_message(chat_id, role, content):

    messages = load_chat(chat_id)

    messages.append({
        "role": role,
        "content": content
    })

    filepath = os.path.join(CHAT_DIR, f"{chat_id}.json")

    with open(filepath, "w") as f:
        json.dump(messages, f, indent=4)


# -----------------------------
# GET ALL CHATS
# -----------------------------

def get_all_chats():

    chats = []

    for file in os.listdir(CHAT_DIR):

        if file.endswith(".json"):

            chats.append(file.replace(".json", ""))

    return chats