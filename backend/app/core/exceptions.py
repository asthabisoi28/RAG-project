from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code = 400
    code = "app_error"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class InvalidFileError(AppError):
    status_code = 422
    code = "invalid_file"


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class LLMConfigurationError(AppError):
    status_code = 500
    code = "llm_configuration_error"


class LLMProviderError(AppError):
    status_code = 502
    code = "llm_provider_error"


class LLMQuotaError(LLMProviderError):
    status_code = 429
    code = "llm_quota_error"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "internal_server_error", "message": str(exc)}},
        )
