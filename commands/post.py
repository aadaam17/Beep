# commands/post.py

from storage.fs import BeepFS
fs = BeepFS()


def dispatch(cmd, args, state):
    user = state.user or "demo"
    parts = args.split() if args else []

    if cmd == "post":
        content = args.strip()
        if not content:
            print("[POST] Cannot create empty post")
            return
        post_id = fs.create_post(user, content)
        print(f"[POST] Post created: {post_id}")

    elif cmd == "comment":
        if len(parts) < 2:
            print("[COMMENT] Usage: comment <post_id> <content>")
            return
        post_id, content = parts[0], " ".join(parts[1:])
        # Check if post exists
        parent = fs.read_post(post_id)
        if not parent or parent.get("revoked", False):
            print(f"[COMMENT] Error: Post {post_id} does not exist or was deleted")
            return
        comment_id = fs.create_post(user, content, shared_from=post_id)
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
        # Create a shared post linked to original post
        shared_id = fs.create_post(user, parent["content"], shared_from=pid)
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
        quote_id = fs.create_post(user, content, shared_from=pid)
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
