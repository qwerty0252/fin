from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.config import Settings, get_settings
from app.core.security import TokenResponse, create_access_token, hash_password, verify_password

router = APIRouter()

# ─── In-memory user store (replace with DB in Phase 2) ───────────────────────
_DEMO_USERS: dict[str, dict] = {
    "admin": {
        "hashed_password": hash_password("admin-secret"),
        "tenant_id": "bankops-internal",
        "scopes": ["transactions:read", "transactions:write", "admin"],
    },
    "partner": {
        "hashed_password": hash_password("partner-secret"),
        "tenant_id": "partner-001",
        "scopes": ["transactions:read", "transactions:write"],
    },
}


class APIKeyRequest(BaseModel):
    name: str
    tenant_id: str


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    user = _DEMO_USERS.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(
        data={
            "sub": form_data.username,
            "tenant_id": user["tenant_id"],
            "scopes": user["scopes"],
        },
        settings=settings,
    )
    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )
