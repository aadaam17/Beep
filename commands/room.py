from storage.fs import BeepFS
from datetime import datetime
from state import Mode
import time

fs = BeepFS()
DEFAULT_LATEST = 5  # default number of messages for 'beep late'

def dispatch(cmd, args, state):
    """
    Room commands:
      room   -> create a room (login required)
      join   -> join a room (login required)
      leave  -> leave current room
      say    -> send a message (room-only, login required)
      late   -> show latest messages (room-only)
      invite -> invite user to room (room-only, login required)
    """

    ROOM_ONLY = {"say", "late", "invite"}
    LOGIN_REQUIRED = {"room", "join", "say", "invite"}

    parts = args.split() if args else []
    user = state.user

    # --- ROOM-ONLY CHECK ---
    if cmd in ROOM_ONLY and state.mode != Mode.ROOM:
        print(f"Error: '{cmd}' can only be used inside a room")
        return

    # --- LOGIN CHECK ---
    if cmd in LOGIN_REQUIRED and not user:
        print(f"Error: You must be logged in to use '{cmd}'")
        return

    # --- COMMAND HANDLERS ---

    # CREATE ROOM
    if cmd == "room":
        if state.mode == Mode.ROOM:
            print("Error: Cannot create a new room while inside another room")
            return
        if not parts:
            print("Error: room name required")
            return

        name = parts[0]
        private = "--private" in parts
        ttl = 86400 if "--ephemeral" in parts else None

        fs.create_room(name, user, private, ttl)
        state.enter_room(name)  # creator automatically enters the room
        print(f"Room created and joined: {name}")

    # JOIN ROOM
    elif cmd == "join":
        if state.mode == Mode.ROOM:
            print("Error: Already inside a room")
            return
        if not parts:
            print("Error: room name required")
            return

        room_name = parts[0]
        try:
            fs.join_room(room_name, user)
            state.enter_room(room_name)
            print(f"Joined {room_name}")
        except PermissionError as e:
            print(f"Error: {e}")
        except ValueError as e:
            print(f"Error: {e}")

    # LEAVE ROOM
    elif cmd == "leave":
        if state.mode != Mode.ROOM:
            print("Error: Not in a room")
            return
        print(f"Leaving room {state.current_room}")
        state.exit_room()

    # SEND MESSAGE
    elif cmd == "say":
        if not args:
            print("Error: message required")
            return
        fs.say(state.current_room, user, args)
        print("✓ sent")

    # SHOW LATEST MESSAGES
    elif cmd == "late":
        # Determine number of messages to show
        show_all = False
        num = DEFAULT_LATEST
        if parts:
            if parts[0] == "--all":
                show_all = True
            elif parts[0].isdigit():
                num = int(parts[0])

        msgs, total = fs.read_messages(state.current_room, user)
        if not msgs:
            print("No messages in this room yet.")
            return

        # Slice messages to show latest
        if show_all:
            display = msgs
        else:
            display = msgs[-num:]

        # Ensure chronological order
        display.sort(key=lambda m: m["timestamp"])

        # Print messages
        for m in display:
            t = datetime.fromtimestamp(m["timestamp"]).strftime("%H:%M")
            print(f"[{t}] {m['sender']}: {m['content']}")

    # INVITE USER
    elif cmd == "invite":
        if not parts:
            print("Error: username required to invite")
            return
        fs.invite(state.current_room, parts[0])
        print(f"Invited {parts[0]}")
