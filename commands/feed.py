from storage.fs import BeepFS
fs = BeepFS()

POSTS_PER_PAGE = 10  # number of posts to show per page

def dispatch(cmd, args, state):
    # Initialize pagination if it doesn't exist
    if not hasattr(state, "fyp_index"):
        state.fyp_index = 0

    if cmd == "fyp":
        fyp_type = args or "global"
        state.switch_fyp(fyp_type)
        state.fyp_index = 0  # reset pagination when switching feed

        posts = _get_current_feed(state)
        _print_posts(posts, state)

    elif cmd == "next":
        if state.hold:
            print("[FYP] Feed is on hold. Use 'resume' to continue.")
            return

        state.fyp_index += POSTS_PER_PAGE
        posts = _get_current_feed(state)
        if not posts:
            print("[FYP] No more posts.")
            state.fyp_index -= POSTS_PER_PAGE  # revert index
            return

        _print_posts(posts, state)

    elif cmd == "hold":
        state.toggle_hold()
        print(f"[FYP] Feed hold: {state.hold}")

    elif cmd == "resume":
        if not state.hold:
            print("[FYP] Feed is not on hold.")
            return
        state.toggle_hold()
        print(f"[FYP] Feed resumed: {not state.hold}")


def _get_current_feed(state):
    """
    Returns a list of posts based on the current FYP mode and pagination.
    """
    start = getattr(state, "fyp_index", 0)
    end = start + POSTS_PER_PAGE

    if state.fyp_type == "followed":
        if not state.user:
            print("[FYP] You must be logged in to view followed feed. Showing global feed.")
            posts = fs.list_posts()
        else:
            posts = fs.list_followed_posts(state.user)
    else:
        posts = fs.list_posts()

    return posts[start:end]


def _print_posts(posts, state):
    """
    Prints posts nicely in CLI
    """
    print(f"[FYP] ({state.fyp_type}) Posts {getattr(state, 'fyp_index', 0)+1} - "
          f"{getattr(state, 'fyp_index', 0)+len(posts)}")
    for post_id in posts:
        data = fs.read_post(post_id)
        status = "[deleted]" if data.get("revoked") else ""
        print(f"- {post_id} {status}: {data['content'][:50]}")
