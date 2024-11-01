from fastapi import HTTPException, status


def raise_http_exception(status_code: int, detail: str) -> None:
    """Raise an HTTP exception with the given status code and detail message."""
    raise HTTPException(status_code=status_code, detail=detail)


class AuthenticationError(HTTPException):
    """Custom authentication exception."""

    def __init__(self, detail: str = "Authentication failed") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class AuthorizationError(HTTPException):
    """Custom authorization exception."""

    def __init__(self, detail: str = "Unauthorized access") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
