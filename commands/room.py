from storage.fs import BeepFS
fs = BeepFS()

def dispatch(cmd, args, state):
    if cmd == "room":
        parts = args.split()
        room_name = parts[0]
        rtype = "public"
        if "--private" in parts:
            rtype = "private"
        fs.append_room(room_name, {"type": rtype, "msg": "Room created"})
        print(f"Room created: {room_name} ({rtype})")
    elif cmd == "join":
        state.enter_room(args.strip())
        print(f"Joined room {args.strip()}")
    elif cmd == "leave":
        state.exit_room()
        print(f"Left room {args.strip()}")
    elif cmd == "invite":
        print(f"Invite {args.strip()} to room (not implemented)")
