class BeepError(Exception):
    pass

class AuthError(BeepError):
    pass

class CommandError(BeepError):
    pass
