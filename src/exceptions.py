class InvalidVersionError(Exception):
    def __init__(self, version: int) -> None:
        super().__init__(f"Version not supported: {version}")


class InvalidRequestError(Exception):
    def __init__(self, request: bytes | int) -> None:
        super().__init__(f"Invalid request: {request}")
