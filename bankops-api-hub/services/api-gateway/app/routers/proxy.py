from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
import httpx

from app.config import Settings, get_settings
from app.core.security import TokenData, get_current_user

router = APIRouter()


async def _forward(
    request: Request,
    target_url: str,
) -> JSONResponse:
    """Forward a request to a downstream service and return its response."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
                content=await request.body(),
                params=dict(request.query_params),
            )
            return JSONResponse(
                content=response.json() if response.content else None,
                status_code=response.status_code,
                headers=dict(response.headers),
            )
        except httpx.ConnectError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Downstream service unavailable: {exc}",
            ) from exc
        except httpx.TimeoutException as exc:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Downstream service timed out",
            ) from exc


@router.api_route(
    "/transactions/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy_transactions(
    path: str,
    request: Request,
    settings: Settings = Depends(get_settings),
    _user: TokenData = Depends(get_current_user),
) -> JSONResponse:
    target = f"{settings.transaction_service_url}/api/v1/{path}"
    return await _forward(request, target)


@router.api_route(
    "/workflows/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy_orchestration(
    path: str,
    request: Request,
    settings: Settings = Depends(get_settings),
    _user: TokenData = Depends(get_current_user),
) -> JSONResponse:
    target = f"{settings.orchestration_service_url}/api/v1/{path}"
    return await _forward(request, target)
