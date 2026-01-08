import shlex
from state import AppState, Mode
from commands import auth, feed, post, profile, follow, chat, room, moderation, help

state = AppState()

# Mapping commands to their dispatch modules
COMMAND_MODULES = {
    "auth": ["register", "login", "logout"],
    "post": ["post", "comment", "share", "quote", "delete"],
    "profile": ["profile"],
    "follow": ["follow", "unfollow"],
    "chat": ["chat", "message", "exit"],
    "room": ["room", "join", "leave", "invite", "say", "late"],
    "feed": ["fyp", "next", "hold", "resume"],
    "moderation": ["mute", "kick"],
    "help": ["help"],
}

MODULE_DISPATCH = {
    "auth": auth.dispatch,
    "post": post.dispatch,
    "profile": profile.dispatch,
    "follow": follow.dispatch,
    "chat": chat.dispatch,
    "room": room.dispatch,
    "feed": feed.dispatch,
    "moderation": moderation.dispatch,
    "help": help.dispatch,
}

COMMAND_TO_MODULE = {cmd: module for module, cmds in COMMAND_MODULES.items() for cmd in cmds}

# Room-only commands
ROOM_ONLY = {"say", "late", "invite"}

def get_prompt():
    if state.mode == Mode.CHAT and state.current_chat:
        return f"[chat:@{state.current_chat}] > "
    elif state.mode == Mode.ROOM and state.current_room:
        return f"[forum:{state.current_room}] > "
    elif state.mode == Mode.PROFILE:
        return "[profile] > "
    else:
        return "[fyp:global] > "

def main_loop():
    print("Welcome to Beep CLI v0.2")

    while True:
        try:
            line = input(get_prompt()).strip()
            if not line:
                continue

            # Allow plain messages inside a room
            if state.mode == Mode.ROOM and not line.startswith("beep"):
                from commands import room
                room.dispatch("say", line, state)
                continue

            parts = shlex.split(line)
            if not parts or parts[0] != "beep":
                print("All commands must start with 'beep'")
                continue

            parts = parts[1:]  # remove 'beep'
            if not parts:
                print("No command provided after 'beep'")
                continue

            cmd_name = parts[0]
            args = " ".join(parts[1:]) if len(parts) > 1 else ""

            module_name = COMMAND_TO_MODULE.get(cmd_name)
            if not module_name:
                print(f"Unknown command: {cmd_name}")
                continue

            # --- Enforce room-only commands ---
            if cmd_name in ROOM_ONLY:
                if state.mode != Mode.ROOM:
                    print(f"Error: '{cmd_name}' can only be used inside a room")
                    continue
                from commands import room
                room.dispatch(cmd_name, args, state)
                continue

            # --- Enforce global-only commands ---
            if state.mode == Mode.ROOM and cmd_name not in ROOM_ONLY and cmd_name != "leave":
                print(f"Error: '{cmd_name}' cannot be used inside a room")
                continue

            # --- Dispatch normally ---
            MODULE_DISPATCH[module_name](cmd_name, args, state)

        except KeyboardInterrupt:
            print("\nExiting Beep CLI. Bye!")
            break
        except Exception as e:
            print(f"Error: {e}")
