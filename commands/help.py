def dispatch(cmd, args, state):
    print("""
Beep — Anonymous CLI Social Network
==================================

Note:
  • Always prefix commands with `beep`
  • Example: beep post "hello world"

-- Identity & Session --
  register -u <username> -p <password>   Create local identity (generates keys)
  login  -u <username> -p <password>   Unlock identity
  logout                               Lock identity

-- Feed (FYP) --
  fyp global                            Switch to global feed (default)
  fyp followed                          Switch to followed feed
  next                                  Load next posts
  hold                                  Pause auto-loading
  resume                                Resume auto-loading

-- Posts --
  post "content"                        Create a post
  comment <post_id> "comment"           Comment on a post
  share <post_id>                       Share a post (reference)
  quote <post_id> "text"                Quote a post (new post)
  delete <post_id>                      Delete your post

-- Profile --
  profile                               View your profile
  profile <username>                    View another profile
  profile --followers                   Show list of followers
  profile --following                   Show list of following
  profile --posts                       Show posts only
  profile --shared                      Show shared posts only

-- Follow --
  follow <username>                     Follow a user
  unfollow <username>                   Unfollow a user

-- Chat --
  chat                                  List chats
  chat <username>                       Enter direct chat or room
  say "message"                         Send message (chat mode)
  read [--all | <number>]               Read messages
  exit                                  Leave chat / return to feed

-- Rooms --
  room                                  List rooms
  room <name> [--private] [--ephemeral] Create a room
  say "message"                         Send message (room mode)
  late [--all | <number>]               Read room messages
  join <name>                           Join a room
  invite <username>                     Invite user to private room
  leave                                 Leave chat / return to fe
  ed

-- Moderation (Room Owner and Moderators) --
  mute <username>                       Mute a user
  unmute <username>                     Unmute a user
  kick <username>                       Remove user from room

-- Mod (Exclusive to Room Owner)--
  mod <username>                        Make a member a moderator
  unmod <username>                      Remove a member from moderator

-- Help --
  help                                  Show this help
""")
