class ServiceException(Exception):
    default_message: str = "An error occurred"

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class NotFoundException(ServiceException):
    default_message = "Not found"


class UnauthorizedException(ServiceException):
    default_message = "Unauthorized"


class NoFamilyException(ServiceException):
    default_message = "User must be part of a family to perform this action"


class DuplicateException(ServiceException):
    default_message = "Duplicate"
