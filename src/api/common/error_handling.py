from fastapi import HTTPException


def raise_http_exception(status_code: int, detail: str) -> None:
    """Raise an HTTP exception with the given status code and detail message."""
    raise HTTPException(status_code=status_code, detail=detail)
