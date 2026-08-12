from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.config import get_settings
from app.core.security import decode_token

_PUBLIC_PATHS = {"/health", "/metrics", "/docs", "/redoc", "/openapi.json", "/auth/token"}

settings = get_settings()


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in _PUBLIC_PATHS or request.url.path.startswith("/auth/"):
            return await call_next(request)

        # Check API key first
        api_key = request.headers.get(settings.api_key_header)
        if api_key:
            # TODO: validate API key against database in Phase 2
            request.state.auth_method = "api_key"
            return await call_next(request)

        # Fall back to JWT Bearer
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.removeprefix("Bearer ").strip()
        try:
            token_data = decode_token(token, settings)
            request.state.user = token_data
            request.state.auth_method = "jwt"
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

        return await call_next(request)
