def get_prompt(state):
    if state.mode.name == "CHAT" and state.current_chat:
        return f"[chat:@{state.current_chat}] > "
    elif state.mode.name == "ROOM" and state.current_room:
        return f"[forum:{state.current_room}] > "
    elif state.mode.name == "PROFILE":
        return "[profile] > "
    else:
        return f"[fyp:{state.fyp_type}] > "
