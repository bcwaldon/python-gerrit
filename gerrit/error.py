
class AuthenticationError(Exception):
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message

class GerritError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class NotSignedInError(GerritError):
    pass

class UnknownAuthenticationMethodError(Exception):
    pass

