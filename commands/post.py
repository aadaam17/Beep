# commands/post.py

from storage.fs import BeepFS
from storage.profile import get_user

fs = BeepFS()


def dispatch(cmd, args, state):
    user = state.user
    if not user:
        print("[POST] You must be logged in to post")
        return

    parts = args.split() if args else []

    # Make sure the user exists
    if not get_user(user):
        print(f"[POST] Error: user '{user}' does not exist")
        return

    if cmd == "post":
        content = args.strip()
        if not content:
            print("[POST] Cannot create empty post")
            return
        post_id = fs.create_post(user, content, post_type="post")
        print(f"[POST] Post created: {post_id}")

    elif cmd == "comment":
        if len(parts) < 2:
            print("[COMMENT] Usage: comment <post_id> <content>")
            return
        post_id, content = parts[0], " ".join(parts[1:])
        parent = fs.read_post(post_id)
        if not parent or parent.get("revoked", False):
            print(f"[COMMENT] Error: Post {post_id} does not exist or was deleted")
            return
        # Comment uses parent_id instead of shared_from
        comment_id = fs.create_post(user, content, post_type="comment", parent_id=post_id)
        print(f"[COMMENT] Comment added: {comment_id} (to {post_id})")

    elif cmd == "share":
        if not parts:
            print("[SHARE] Usage: share <post_id>")
            return
        pid = parts[0]
        parent = fs.read_post(pid)
        if not parent or parent.get("revoked", False):
            print(f"[SHARE] Error: Post {pid} does not exist or was deleted")
            return
        # Shared post has type "share" and points to shared_from
        shared_id = fs.create_post(user, parent["content"], shared_from=pid, post_type="share")
        print(f"[SHARE] Shared post: {shared_id}")

    elif cmd == "quote":
        if len(parts) < 2:
            print("[QUOTE] Usage: quote <post_id> <content>")
            return
        pid, content = parts[0], " ".join(parts[1:])
        parent = fs.read_post(pid)
        if not parent or parent.get("revoked", False):
            print(f"[QUOTE] Error: Post {pid} does not exist or was deleted")
            return
        # Quoted post has new content, type "quote", and shared_from points to original
        quote_id = fs.create_post(user, content, shared_from=pid, quote=True, post_type="quote")
        print(f"[QUOTE] Quote created: {quote_id} (from {pid})")

    elif cmd == "delete":
        pid = args.strip()
        if not pid:
            print("[DELETE] Usage: delete <post_id>")
            return
        try:
            fs.delete_post(pid, user)
            print(f"[DELETE] Deleted post: {pid}")
        except PermissionError as e:
            print(f"[DELETE] Error: {e}")
