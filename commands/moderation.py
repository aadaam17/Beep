from storage.fs import BeepFS
from state import Mode
import time

fs = BeepFS()
MUTE_24H = 86400  # 24 hours in seconds

def dispatch(cmd, args, state):
    if state.mode != Mode.ROOM:
        print("Error: moderation commands only work in rooms")
        return

    room = fs._read_room(state.current_room)
    actor = state.user

    if not room:
        print("Error: room not found")
        return

    owner = room.get("owner")
    mods = room.get("moderators", [])
    room.setdefault("muted", {})
    room.setdefault("banned", [])
    room.setdefault("members", [])

    def is_mod():
        return actor == owner or actor in mods

    target = args.replace("--perma", "").strip()

    if cmd == "mod":
        if actor != owner:
            print("Error: only owner can assign moderators")
            return
        if target == owner:
            print("Error: owner is already supreme")
            return
        if target in mods:
            print(f"{target} is already a moderator")
            return
        room["moderators"].append(target)
        fs._write_room(room)
        print(f"{target} is now a moderator")

    elif cmd == "unmod":
        if actor != owner:
            print("Error: only owner can remove moderators")
            return
        if target not in mods:
            print(f"{target} is not a moderator")
            return
        room["moderators"].remove(target)
        fs._write_room(room)
        print(f"{target} removed from moderators")

    elif cmd == "mute":
        if not is_mod():
            print("Error: permission denied")
            return
        if target == owner:
            print("Error: cannot mute owner")
            return
        if "--perma" in args:
            room["muted"][target] = "perma"
        else:
            room["muted"][target] = {"until": time.time() + MUTE_24H}
        fs._write_room(room)
        print(f"{target} muted")

    elif cmd == "unmute":
        if not is_mod():
            print("Error: permission denied")
            return
        if target not in room["muted"]:
            print(f"{target} is not muted")
            return
        room["muted"].pop(target)
        fs._write_room(room)
        print(f"{target} unmuted")

    elif cmd == "kick":
        if not is_mod():
            print("Error: permission denied")
            return
        if target == owner:
            print("Error: cannot kick owner")
            return
        if target not in room["members"]:
            print(f"{target} is not in the room")
            return
        room["members"].remove(target)
        if target not in room["banned"]:
            room["banned"].append(target)
        fs._write_room(room)
        print(f"{target} kicked and banned")

    else:
        print("Unknown moderation command")
