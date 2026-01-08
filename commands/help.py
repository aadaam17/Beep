def dispatch(cmd, args, state):
    print("""
  Beep CLI Help

  Disclaimer: Use "beep" prefix on all commands to work
  i.e beep register <username>

  -- Authentication --
  register <username>
  login <username>
  logout

  -- Posts --
  post "content"
  comment <post_id> "comment"
  share <post_id>
  quote <post_id> "quote"
  delete <post_id>

  -- Profile --
  profile [username] [--posts] [--shared]

  -- Follow --
  follow <username>
  unfollow <username>

  -- Chat --
  chat <username>
  message "your message"
  exit

  -- Rooms --
  beep room <name> [--private] [--ephemeral]
  beep join <name>
  beep leave
  beep say <message>
  beep late [--all | <number>]
  beep invite <username>

  -- Feed --
  fyp [global|followed]
  next
  hold
  resume

  -- Moderation --
  mute <username>
  kick <username>

  -- Help --
  help
""")
