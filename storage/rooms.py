from .fs import BeepFS
fs = BeepFS()

def send_room_message(room, msg):
    fs.append_room(room, msg)

def read_room(room):
    path = fs.room_path(room)
    if path.exists():
        return [line.strip() for line in path.open()]
    return []
