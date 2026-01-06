import json
from pathlib import Path

STORAGE_DIR = Path.home() / ".beep_storage"
POSTS_DIR = STORAGE_DIR / "posts"
PROFILES_DIR = STORAGE_DIR / "profiles"

# Ensure directories exist
STORAGE_DIR.mkdir(exist_ok=True)
POSTS_DIR.mkdir(exist_ok=True)
PROFILES_DIR.mkdir(exist_ok=True)


class BeepFS:
    def __init__(self):
        POSTS_DIR.mkdir(exist_ok=True)
        PROFILES_DIR.mkdir(exist_ok=True)

    # ---------------- POSTS ----------------

    def list_posts(self):
        """
        Return a list of all post IDs in the system (global feed)
        """
        return sorted([p.stem for p in POSTS_DIR.glob("*.json")], reverse=True)

    def list_followed_posts(self, username):
        """
        Return posts only from users that `username` follows.
        """
        from storage.profile import get_user
        user = get_user(username)
        if not user:
            return []

        followed_users = set(user.get("following", []))
        all_posts = self.list_posts()
        filtered_posts = []

        for post_id in all_posts:
            post_data = self.read_post(post_id)
            if post_data.get("creator") in followed_users:
                filtered_posts.append(post_id)

        return filtered_posts

    def read_post(self, post_id):
        """
        Read a single post.
        """
        post_file = POSTS_DIR / f"{post_id}.json"
        if not post_file.exists():
            return {
                "creator": None,
                "content": "[missing]",
                "revoked": True,
                "shared_from": None
            }

        with open(post_file, "r") as f:
            return json.load(f)

    def save_post(self, post_id, data):
        """
        Save a post dict to file
        """
        post_file = POSTS_DIR / f"{post_id}.json"
        with open(post_file, "w") as f:
            json.dump(data, f, indent=4)

    def create_post(self, creator, content, shared_from=None):
        """
        Create a new post or derived post (comment/share/quote)
        """
        import uuid
        post_id = f"post{uuid.uuid4().hex[:8]}"

        post_data = {
            "creator": creator,
            "content": content,
            "revoked": False,
            "shared_from": shared_from
        }

        self.save_post(post_id, post_data)

        # ---- CRITICAL FIX: always update profile ----
        from storage.profile import get_user, update_user

        user = get_user(creator)
        if not user:
            user = {
                "username": creator,
                "followers": [],
                "following": [],
                "posts": [],
                "shared": []
            }

        if shared_from:
            user["shared"].append(post_id)
        else:
            user["posts"].append(post_id)

        update_user(creator, user)

        return post_id

    def delete_post(self, post_id, username):
        """
        Mark a post as revoked
        """
        post_data = self.read_post(post_id)
        if post_data.get("creator") != username:
            raise PermissionError("Cannot delete another user's post")

        post_data["revoked"] = True
        self.save_post(post_id, post_data)

    # ---------------- PROFILE ----------------

    def profile_path(self, username):
        return PROFILES_DIR / f"{username}.json"

    def read_profile(self, username):
        path = self.profile_path(username)
        if not path.exists():
            return {
                "username": username,
                "followers": [],
                "following": [],
                "posts": [],
                "shared": []
            }

        with open(path, "r") as f:
            return json.load(f)

    def save_profile(self, username, data):
        path = self.profile_path(username)
        with open(path, "w") as f:
            json.dump(data, f, indent=4)

    # ---------------- USER VIEWS ----------------

    def list_user_posts(self, username):
        """
        Return non-revoked posts created by user
        """
        profile = self.read_profile(username)
        posts = []

        for post_id in profile.get("posts", []):
            data = self.read_post(post_id)
            if data.get("creator") == username and not data.get("revoked"):
                posts.append(post_id)

        return posts

    def list_user_shared(self, username):
        """
        Return non-revoked shared/quoted posts
        """
        profile = self.read_profile(username)
        shared = []

        for post_id in profile.get("shared", []):
            data = self.read_post(post_id)
            if data and not data.get("revoked"):
                shared.append(post_id)

        return shared
