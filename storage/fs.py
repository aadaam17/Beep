import time
import json
import uuid
from pathlib import Path
from datetime import datetime
from storage.crypto import load_or_create_keys
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

# ---------------- PATHS ----------------

STORAGE_DIR = Path.home() / ".beep_storage"
POSTS_DIR = STORAGE_DIR / "posts"
PROFILES_DIR = STORAGE_DIR / "profiles"
ROOMS_DIR = STORAGE_DIR / "rooms"
USER_DIR = STORAGE_DIR / "users"

for path in (STORAGE_DIR, POSTS_DIR, PROFILES_DIR, ROOMS_DIR, USER_DIR):
    path.mkdir(exist_ok=True)

PAGE = 10

# ================= FILESYSTEM =================

class BeepFS:
    # ------------ GENERIC HELPERS ------------

    @staticmethod
    def _read_json(path, default=None):
        if not path.exists():
            return default
        with open(path, "r") as f:
            return json.load(f)

    @staticmethod
    def _write_json(path, data):
        with open(path, "w") as f:
            json.dump(data, f, indent=4)

    # ---------------- POSTS ----------------

    def list_posts(self):
        return sorted((p.stem for p in POSTS_DIR.glob("*.json")), reverse=True)

    def list_followed_posts(self, username):
        from storage.profile import get_user
        user = get_user(username)
        if not user:
            return []
        followed = set(user.get("following", []))
        return [
            post_id
            for post_id in self.list_posts()
            if self.read_post(post_id).get("creator") in followed
        ]

    def post_path(self, post_id):
        return POSTS_DIR / f"{post_id}.json"

    def read_post(self, post_id):
        return self._read_json(
            self.post_path(post_id),
            default={"creator": None, "content": "[missing]", "revoked": True, "shared_from": None},
        )

    def save_post(self, post_id, data):
        self._write_json(self.post_path(post_id), data)

    def create_post(self, creator, content, shared_from=None):
        post_id = f"post{uuid.uuid4().hex[:8]}"
        post_data = {
            "creator": creator,
            "content": content,
            "revoked": False,
            "shared_from": shared_from,
            "timestamp": datetime.now().isoformat()
        }
        self.save_post(post_id, post_data)

        from storage.profile import get_user, update_user
        user = get_user(creator) or {"username": creator, "followers": [], "following": [], "posts": [], "shared": []}
        target = "shared" if shared_from else "posts"
        user[target].append(post_id)
        update_user(creator, user)

        return post_id

    def delete_post(self, post_id, username):
        post = self.read_post(post_id)
        if post.get("creator") != username:
            raise PermissionError("Cannot delete another user's post")
        post["revoked"] = True
        self.save_post(post_id, post)

    # ---------------- PROFILES ----------------

    def profile_path(self, username):
        return PROFILES_DIR / f"{username}.json"

    def read_profile(self, username):
        return self._read_json(
            self.profile_path(username),
            default={"username": username, "followers": [], "following": [], "posts": [], "shared": []},
        )

    def save_profile(self, username, data):
        self._write_json(self.profile_path(username), data)

    # ---------------- USER VIEWS ----------------

    def list_user_posts(self, username):
        profile = self.read_profile(username)
        return [pid for pid in profile.get("posts", []) if not self.read_post(pid).get("revoked")]

    def list_user_shared(self, username):
        profile = self.read_profile(username)
        return [pid for pid in profile.get("shared", []) if not self.read_post(pid).get("revoked")]

    # ---------- ROOMS ----------

    def room_path(self, name):
        return ROOMS_DIR / f"{name}.json"

    def _write_room(self, room):
        self.room_path(room["name"]).write_text(json.dumps(room, indent=4))

    def _read_room(self, name):
        path = self.room_path(name)
        if not path.exists():
            return None
        room = json.loads(path.read_text())

        # auto-expire
        if room.get("ephemeral") and time.time() > room["expires_at"]:
            path.unlink(missing_ok=True)
            return None
        return room

    def create_room(self, name, creator, private=False, ttl=None):
        if self.room_path(name).exists():
            raise ValueError("Room exists")
        room = {
            "name": name,
            "type": "private" if private else "public",
            "members": [creator],
            "invites": [],
            "messages": [],
            "ephemeral": bool(ttl),
            "expires_at": time.time() + ttl if ttl else None,
        }
        self._write_room(room)

    def join_room(self, name, user, re_encrypt_old=False):
        room = self._read_room(name)
        if not room:
            raise ValueError("Room not found")
        if room["type"] == "private" and user not in room["invites"]:
            raise PermissionError("Invite required")
        if user not in room["members"]:
            room["members"].append(user)
            if re_encrypt_old:
                self._encrypt_old_messages_for_new_user(room, user)
        self._write_room(room)

    def invite(self, room_name, user):
        room = self._read_room(room_name)
        if user not in room["invites"]:
            room["invites"].append(user)
        self._write_room(room)

    # ---------------- MESSAGE ENCRYPTION ----------------

    def say(self, room_name, sender, message):
        room = self._read_room(room_name)
        if not room or sender not in room["members"]:
            raise PermissionError("Cannot send message to a room you are not a member of")

        msg_bytes = message.encode()
        encrypted = {}
        for member in room["members"]:
            _, pub_key = load_or_create_keys(member)
            encrypted_blob = pub_key.encrypt(
                msg_bytes,
                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                             algorithm=hashes.SHA256(), label=None)
            )
            encrypted[member] = encrypted_blob.hex()

        room["messages"].append({
            "sender": sender,
            "timestamp": int(time.time()),
            "encrypted": encrypted
        })
        self._write_room(room)

    def read_messages(self, room_name, username, start=0, limit=10):
        room = self._read_room(room_name)
        if not room or username not in room["members"]:
            return [], 0

        private_key, _ = load_or_create_keys(username)
        visible_msgs = []

        for msg in room.get("messages", []):
            if username not in msg["encrypted"]:
                continue
            encrypted_blob = bytes.fromhex(msg["encrypted"][username])
            try:
                decrypted = private_key.decrypt(
                    encrypted_blob,
                    padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                 algorithm=hashes.SHA256(), label=None)
                )
                visible_msgs.append({
                    "sender": msg["sender"],
                    "timestamp": msg["timestamp"],
                    "content": decrypted.decode()
                })
            except:
                continue

        total = len(visible_msgs)
        return visible_msgs[start:start+limit], total

    # --- OPTIONAL: Re-encrypt old messages for new users ---
    def _encrypt_old_messages_for_new_user(self, room, new_user):
        _, pub_key = load_or_create_keys(new_user)
        for msg in room.get("messages", []):
            if new_user not in msg["encrypted"]:
                sender = msg["sender"]
                priv_key, _ = load_or_create_keys(sender)
                decrypted = priv_key.decrypt(
                    bytes.fromhex(msg["encrypted"][sender]),
                    padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                 algorithm=hashes.SHA256(), label=None)
                )
                encrypted_blob = pub_key.encrypt(
                    decrypted,
                    padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                 algorithm=hashes.SHA256(), label=None)
                )
                msg["encrypted"][new_user] = encrypted_blob.hex()
