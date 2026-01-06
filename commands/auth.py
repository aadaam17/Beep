import shlex
import getpass
from storage import profile

def dispatch(cmd, args, state):
    parts = shlex.split(args)
    username = None
    password = None

    # Parse flags
    i = 0
    while i < len(parts):
        if parts[i] in ("-u", "--username"):
            i += 1
            if i < len(parts):
                username = parts[i]
        elif parts[i] in ("-p", "--password"):
            i += 1
            if i < len(parts):
                password = parts[i]
        i += 1

    # Interactive password if not supplied
    if password is None and cmd in ("register", "login"):
        password = getpass.getpass("Enter password: ")

    try:
        if cmd == "register":
            if not username:
                print("[AUTH] Error: Username required! Use -u <username>")
                return
            user = profile.create_user(username, password)
            state.user = user["username"]
            print(f"[AUTH] User '{username}' registered successfully!")

        elif cmd == "login":
            if not username:
                print("[AUTH] Error: Username required! Use -u <username>")
                return
            user = profile.authenticate(username, password)
            state.user = user["username"]
            print(f"[AUTH] User '{username}' logged in successfully!")

        elif cmd == "logout":
            if state.user:
                print(f"[AUTH] User '{state.user}' logged out.")
                state.user = None
            else:
                print("[AUTH] No user currently logged in.")

    except ValueError as e:
        print(f"[AUTH] Error: {e}")
