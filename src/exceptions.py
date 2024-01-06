class InvalidVersionError(Exception):
    """Exception raised when an invalid SOCKS version is encountered."""

    def __init__(self, version: int) -> None:
        super().__init__(f"Version not supported: {version}")


class InvalidRequestError(Exception):
    """Exception raised for invalid requests.

    Attributes:
        request (bytes | int): The invalid request that caused the error.
    """

    def __init__(self, request: bytes | int) -> None:
        super().__init__(f"Invalid request: {request}")
