from storage.profile import follow, unfollow, get_user

def dispatch(cmd, args, state):
    args = args.strip().split()
    
    if not state.user:
        print(f"[{cmd.upper()}] You must log in first")
        return
    
    if not args:
        print(f"[{cmd.upper()}] Usage: {cmd} <username>")
        return
    
    target_user = args[0].lower()
    
    # Prevent self-follow/unfollow
    if target_user == state.user:
        print(f"[{cmd.upper()}] You cannot {cmd} yourself")
        return
    
    # Check if target exists
    if not get_user(target_user):
        print(f"[{cmd.upper()}] User '{target_user}' does not exist")
        return
    
    # Map command to function
    action = follow if cmd == "follow" else unfollow
    
    try:
        action(state.user, target_user)
        profile = get_user(state.user)
        verb = "now following" if cmd == "follow" else "unfollowed"
        print(f"[{cmd.upper()}] You {verb} {target_user}")
        print(f"[{cmd.upper()}] You now follow {len(profile['following'])} users")
    except ValueError as e:
        print(f"[{cmd.upper()}] Error: {e}")
