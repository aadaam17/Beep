def dispatch(cmd, args, state):
    if cmd == "mute":
        print(f"[MOD] Muted user: {args}")
    elif cmd == "kick":
        print(f"[MOD] Kicked user: {args}")
