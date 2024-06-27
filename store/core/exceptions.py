class BaseException(Exception):
    message: str = "Internal Server Error"

    def __init__(self, message: str | None = None) -> None:
        if message:
            self.message = message


class NotFoundException(BaseException):
    message = "Not Found"

class DatabaseInsertError(Exception):
    def __init__(self, message="Error occurred during database insertion.") -> None:
        self.message = message
        super().__init__(self.message)