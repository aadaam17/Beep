# commands/feed.py

from storage.fs import BeepFS
from datetime import datetime

fs = BeepFS()
POSTS_PER_PAGE = 15


def relative_time(iso_ts):
    """Return relative time like '3h ago'."""
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
    months = days // 30
    if months < 12:
        return f"{months}mo ago"
    years = days // 365
    return f"{years}y ago"


def _get_comments(post_id):
    """Return post_ids that are comments of the given post."""
    all_posts = fs.list_posts()
    comments = []
    for pid in all_posts:
        post = fs.read_post(pid)
        # Only include comments where type=="comment" and parent_id matches
        if post.get("type") == "comment" and post.get("parent_id") == post_id:
            comments.append(pid)
    return comments


def _print_posts(posts, state):
    """Print posts nicely with shared, quoted, comments, deleted."""
    for post_id in posts:
        data = fs.read_post(post_id)

        # ---------------- DELETED POSTS ----------------
        if data.get("revoked"):
            print(f":: [deleted post] - {post_id}")
            comments = _get_comments(post_id)
            for c in comments:
                c_data = fs.read_post(c)
                c_ts = c_data.get("timestamp")
                rel = relative_time(c_ts) if c_ts else ""
                print(f"    : [{rel}] [{c_data.get('creator')}] - {c}: {c_data.get('content', '')}")
            print()
            continue

        # ---------------- SHARED / QUOTED POSTS ----------------
        if data.get("shared_from"):
            original_id = data["shared_from"]
            original = fs.read_post(original_id)
            t = datetime.fromisoformat(data["timestamp"]).strftime("%d.%m.%Y")
            rel = relative_time(data["timestamp"])
            label = "Quoted" if data.get("quote", False) else "Shared"
            content_display = f": {data.get('content')}" if data.get("quote", False) else ""
            print(f":: {label} [{t} · {rel}] [{data.get('creator')}] - {post_id} {content_display}")
            if original:
                ot = datetime.fromisoformat(original["timestamp"]).strftime("%d.%m.%Y")
                orel = relative_time(original["timestamp"])
                print(f"      ↳ [{ot} · {orel}] [{original.get('creator')}] - {original_id}: {original.get('content')}")
            comments = _get_comments(post_id)
            for c in comments:
                c_data = fs.read_post(c)
                c_ts = c_data.get("timestamp")
                rel = relative_time(c_ts) if c_ts else ""
                print(f"      : [{rel}] [{c_data.get('creator')}] - {c}: {c_data.get('content', '')}")
            print()
            continue

        # ---------------- NORMAL POSTS ----------------
        t = datetime.fromisoformat(data["timestamp"]).strftime("%d.%m.%Y")
        rel = relative_time(data["timestamp"])
        print(f":: [{t} · {rel}] [{data.get('creator')}] - {post_id}: {data.get('content', '')}")

        # ---------------- COMMENTS ----------------
        comments = _get_comments(post_id)
        for c in comments:
            c_data = fs.read_post(c)
            c_ts = c_data.get("timestamp")
            rel = relative_time(c_ts) if c_ts else ""
            print(f"    : [{rel}] [{c_data.get('creator')}] - {c}: {c_data.get('content', '')}")

        print()  # Blank line between posts


def dispatch(cmd, args, state):
    """Dispatch FYP commands: fyp, next, hold, resume."""
    if not hasattr(state, "fyp_index"):
        state.fyp_index = 0

    if cmd == "fyp":
        fyp_type = args or "global"
        state.switch_fyp(fyp_type)
        state.fyp_index = 0
        posts = _get_current_feed(state)
        _print_posts(posts, state)

    elif cmd == "next":
        if getattr(state, "hold", False):
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
        if not getattr(state, "hold", False):
            print("[FYP] Feed is not on hold.")
            return
        state.toggle_hold()
        print(f"[FYP] Feed resumed: {not state.hold}")


def _get_current_feed(state):
    """Return posts for current FYP mode."""
    start = getattr(state, "fyp_index", 0)
    end = start + POSTS_PER_PAGE

    if getattr(state, "fyp_type", "global") == "followed":
        if not state.user:
            print("[FYP] You must be logged in to view followed feed. Showing global feed.")
            posts = fs.list_posts()
        else:
            posts = fs.list_followed_posts(state.user)
    else:
        posts = fs.list_posts()

    return posts[start:end]
