from storage.fs import BeepFS
fs = BeepFS()

def dispatch(cmd, args, state):
    user = state.user or "demo"
    if cmd == "chat":
        state.enter_chat(args.strip())
        print(f"Entering chat with {args}")
    elif cmd == "message":
        fs.append_chat(state.current_chat, {"from": user, "msg": args})
        print(f"Sent message to {state.current_chat}: {args}")
    elif cmd == "exit":
        state.exit_chat()
        print("Exited chat")
