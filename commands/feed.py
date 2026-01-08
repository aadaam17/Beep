from storage.fs import BeepFS
from datetime import datetime

fs = BeepFS()

POSTS_PER_PAGE = 15  # number of posts to show per page


# ---------- TIME HELPERS ----------

def relative_time(iso_ts):
    """
    Convert ISO timestamp to relative time (e.g. 3m ago, 2h ago)
    """
    try:
        past = datetime.fromisoformat(iso_ts)
    except Exception:
        return ""

    now = datetime.now()
    diff = now - past
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return f"{seconds}s ago"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    if days < 7:
        return f"{days}d ago"
    weeks = days // 7
    if weeks < 4:
        return f"{weeks}w ago"
    months = days // 30
    if months < 12:
        return f"{months}mo ago"
    years = days // 365
    return f"{years}y ago"


# ---------- COMMAND DISPATCH ----------

def dispatch(cmd, args, state):
    # Initialize pagination if it doesn't exist
    if not hasattr(state, "fyp_index"):
        state.fyp_index = 0

    if cmd == "fyp":
        fyp_type = args or "global"
        state.switch_fyp(fyp_type)
        state.fyp_index = 0  # reset pagination

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
            state.fyp_index -= POSTS_PER_PAGE
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


# ---------- FEED LOGIC ----------

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


# ---------- OUTPUT ----------

def _print_posts(posts, state):
    """
    Prints posts nicely in CLI
    """
    start = getattr(state, "fyp_index", 0) + 1
    end = getattr(state, "fyp_index", 0) + len(posts)

    print(f"[FYP] ({state.fyp_type}) Posts {start} - {end}")

    for post_id in posts:
        data = fs.read_post(post_id)

        status = "[deleted]" if data.get("revoked") else ""
        creator = data.get("creator", "unknown")
        content = data.get("content", "")[:50]

        ts = data.get("timestamp")
        if ts:
            date_str = datetime.fromisoformat(ts).strftime("%d.%m.%Y")
            rel = relative_time(ts)
            time_display = f"[{date_str} · {rel}] "
        else:
            time_display = ""

        print(f"{time_display}[{creator}] - {post_id} {status}: {content}")
