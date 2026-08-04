class NotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UserNotFoundError(NotFoundError):
    pass


class CardNotFoundError(NotFoundError):
    pass
