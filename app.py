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
    "room": ["room", "join", "leave", "invite"],
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

# Flatten command-to-module mapping for quick lookup
COMMAND_TO_MODULE = {cmd: module for module, cmds in COMMAND_MODULES.items() for cmd in cmds}

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
    print("Welcome to Beep CLI v0.1")

    while True:
        try:
            line = input(get_prompt()).strip()
            if not line:
                continue

            parts = shlex.split(line)
            if not parts:
                continue

            # Enforce mandatory 'beep' prefix
            if parts[0] != "beep":
                print("All commands must start with 'beep'")
                continue

            parts = parts[1:]  # Remove the 'beep' prefix
            if not parts:
                print("No command provided after 'beep'")
                continue

            cmd_name = parts[0]
            args = " ".join(parts[1:]) if len(parts) > 1 else ""

            module_name = COMMAND_TO_MODULE.get(cmd_name)
            if module_name:
                MODULE_DISPATCH[module_name](cmd_name, args, state)
            else:
                print(f"Unknown command: {cmd_name}")

        except KeyboardInterrupt:
            print("\nExiting Beep CLI. Bye!")
            break
        except Exception as e:
            print(f"Error: {e}")
