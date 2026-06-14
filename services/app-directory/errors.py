"""
Consistent error payload shape — platform contract.
Error shape: { "error": str, "code"?: int, "details"?: any }
Vendored from platform/builder-cli/templates/backend/errors.py.
"""
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Optional


class ErrorPayload(BaseModel):
    error: str
    code: Optional[int] = None
    details: Optional[Any] = None


def error_response(
    status_code: int,
    message: str,
    code: Optional[int] = None,
    details: Optional[Any] = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ErrorPayload(error=message, code=code, details=details).model_dump(
            exclude_none=True
        ),
    )


class NotFoundError(HTTPException):
    def __init__(self, resource: str, identifier: Any = None):
        detail = f"{resource} not found"
        if identifier is not None:
            detail = f"{resource} '{identifier}' not found"
        super().__init__(status_code=404, detail=detail)


class UnauthorizedError(HTTPException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(status_code=401, detail=message)
