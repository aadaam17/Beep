from storage.profile import follow, unfollow, get_user

def dispatch(cmd, args, state):
    args = args.strip().split()
    if cmd == "follow":
        if not state.user:
            print("[FOLLOW] You must log in first")
            return
        if not args:
            print("[FOLLOW] Usage: follow <username>")
            return
        target_user = args[0]
        try:
            follow(state.user, target_user)
            print(f"[FOLLOW] You are now following {target_user}")
        except ValueError as e:
            print(f"[FOLLOW] Error: {e}")

    elif cmd == "unfollow":
        if not state.user:
            print("[FOLLOW] You must log in first")
            return
        if not args:
            print("[UNFOLLOW] Usage: unfollow <username>")
            return
        target_user = args[0]
        try:
            unfollow(state.user, target_user)
            print(f"[UNFOLLOW] You unfollowed {target_user}")
        except ValueError as e:
            print(f"[UNFOLLOW] Error: {e}")
