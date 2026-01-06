from storage.fs import BeepFS
fs = BeepFS()

def dispatch(cmd, args, state):
    parts = args.split()
    uname = None
    show_posts = "--posts" in parts
    show_shared = "--shared" in parts
    for p in parts:
        if not p.startswith("--"):
            uname = p
    uname = uname or state.user or "demo"
    print(f"Profile: {uname}")
    if show_posts:
        posts = fs.list_posts()
        print("Posts:")
        for p in posts:
            data = fs.read_post(p)
            print(f"- {p}: {data['content'][:50]}")
    if show_shared:
        print("Shared posts not implemented")
