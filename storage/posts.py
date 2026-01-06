from .fs import BeepFS
fs = BeepFS()

def list_posts():
    return fs.list_posts()

def get_post(post_id):
    return fs.read_post(post_id)
