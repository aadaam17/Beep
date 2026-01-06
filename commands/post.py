from storage.fs import BeepFS
fs = BeepFS()

def dispatch(cmd, args, state):
    user = state.user or "demo"
    parts = args.split()
    if cmd == "post":
        fs.write_post(f"post{user}{len(fs.list_posts())}", {"author": user, "content": args})
        print(f"Post created: {args}")
    elif cmd == "comment":
        post_id, content = parts[0], " ".join(parts[1:])
        fs.append_comment(post_id, {"author": user, "content": content})
        print(f"Comment added to {post_id}")
    elif cmd == "share":
        pid = args.strip()
        fs.share_post(pid, "~/.beep")
        print(f"Shared post: {pid}")
    elif cmd == "quote":
        pid, content = parts[0], " ".join(parts[1:])
        fs.append_comment(pid, {"author": user, "type": "quote", "content": content})
        print(f"Quote created: {content}")
    elif cmd == "delete":
        fs.delete_post(args.strip())
        print(f"Deleted post: {args.strip()}")
