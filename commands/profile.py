# commands/profile.py

from storage.fs import BeepFS
from storage.profile import get_user

fs = BeepFS()

def dispatch(cmd, args, state):
    """
    Handles profile command.

    Usage:
      beep profile                 -> shows your profile
      beep profile <username>      -> shows another user's profile
      beep profile --posts         -> shows your posts (with nested comments/quotes)
      beep profile <username> --shared -> shows their shared posts
    """
    parts = args.split() if args else []

    show_posts = "--posts" in parts
    show_shared = "--shared" in parts

    # Determine the username
    uname = None
    for p in parts:
        if not p.startswith("--"):
            uname = p
    uname = uname or state.user or "demo"

    # Load profile
    profile_data = get_user(uname)

    # Print basic profile info
    print(f"\nProfile: {uname}")
    print(f"Followers: {len(profile_data.get('followers', []))}")
    print(f"Following: {len(profile_data.get('following', []))}")
    print(f"Posts: {len(profile_data.get('posts', []))}")
    print(f"Shared: {len(profile_data.get('shared', []))}\n")

    # --- Recursive display for nested comments/quotes ---
    def display_post(post_id, indent=0):
        data = fs.read_post(post_id)
        status = "[deleted]" if data.get("revoked") else ""
        prefix = "    " * indent
        print(f"{prefix}- {post_id} {status}: {data['content'][:50]}")

        # Children: all posts where shared_from == post_id
        all_posts = fs.list_posts()  # global list of all posts
        children = [p for p in all_posts if fs.read_post(p).get("shared_from") == post_id]
        for child_id in children:
            display_post(child_id, indent=indent+1)

    # --- Show user posts if requested ---
    if show_posts:
        posts = fs.list_user_posts(uname)
        print("Posts:")
        if not posts:
            print("  No posts yet.")
        else:
            top_posts = [p for p in posts if fs.read_post(p).get("shared_from") is None]
            for post_id in top_posts:
                display_post(post_id)

    # --- Show shared posts if requested ---
    if show_shared:
        shared = fs.list_user_shared(uname)
        print("\nShared posts:")
        if not shared:
            print("  No shared posts yet.")
        else:
            for post_id in shared:
                display_post(post_id)

    print("")  # extra newline for readability
