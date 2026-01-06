from .fs import BeepFS
fs = BeepFS()

def send_message(user, msg):
    fs.append_chat(user, msg)

def read_chat(user):
    path = fs.chat_path(user)
    if path.exists():
        return [line.strip() for line in path.open()]
    return []
