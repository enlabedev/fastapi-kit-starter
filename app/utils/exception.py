from fastapi import Request
from fastapi.responses import JSONResponse


class AppBaseException(Exception):
    def __init__(self, status_code: int, message: str, code: str = "000"):
        self.status_code = status_code
        self.code = code
        self.message = message


async def base_exception_handler(request: Request, exc: AppBaseException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "success": False, "message": exc.message},
    )
