import json
from pathlib import Path
import hashlib
import uuid

# Path to local user storage
USER_STORAGE_FILE = Path.home() / ".beep_users.json"

# Load all users from storage
def load_users():
    if USER_STORAGE_FILE.exists():
        with open(USER_STORAGE_FILE, "r") as f:
            return json.load(f)
    return {}

# Save users back to storage
def save_users(users):
    with open(USER_STORAGE_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Hash a password (SHA256 for now)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Create a new user
def create_user(username, password):
    users = load_users()
    if username in users:
        raise ValueError(f"Username '{username}' already exists")

    users[username] = {
        "id": str(uuid.uuid4()),       # unique user ID
        "username": username,
        "password": hash_password(password),
        "followers": [],
        "following": [],
        "posts": [],
        "shared": []
    }
    save_users(users)
    return users[username]

# Authenticate user
def authenticate(username, password):
    users = load_users()
    if username not in users:
        raise ValueError(f"Username '{username}' not found")
    if users[username]["password"] != hash_password(password):
        raise ValueError("Incorrect password")
    return users[username]

# Get user by username
def get_user(username):
    users = load_users()
    return users.get(username)

# Update user data (posts, shared, followers)
def update_user(username, data):
    users = load_users()
    if username not in users:
        raise ValueError(f"Username '{username}' not found")
    users[username].update(data)
    save_users(users)
    return users[username]

# Follow another user
def follow(user_a, user_b):
    ua = get_user(user_a)
    ub = get_user(user_b)
    if not ua or not ub:
        raise ValueError("One of the users does not exist")
    if user_b not in ua["following"]:
        ua["following"].append(user_b)
    if user_a not in ub["followers"]:
        ub["followers"].append(user_a)
    update_user(user_a, ua)
    update_user(user_b, ub)

# Unfollow another user
def unfollow(user_a, user_b):
    ua = get_user(user_a)
    ub = get_user(user_b)
    if user_b in ua.get("following", []):
        ua["following"].remove(user_b)
    if user_a in ub.get("followers", []):
        ub["followers"].remove(user_a)
    update_user(user_a, ua)
    update_user(user_b, ub)
