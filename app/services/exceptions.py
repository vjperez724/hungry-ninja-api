class NotFoundException(Exception):
    message: str

    def __init__(self, message: str):
        self.message = message


class UnauthorizedException(Exception):
    message: str

    def __init__(self, message: str):
        self.message = message


class NoFamilyException(Exception):
    message: str = "User must be part of a family to perform this action"


class DuplicateException(Exception):
    message: str

    def __init__(self, message: str):
        self.message = message
