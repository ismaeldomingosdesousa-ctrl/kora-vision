"""Authentication and JWT utilities."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, NamedTuple
from uuid import UUID
import logging

from .config import settings
from .schemas.user import CurrentUser

logger = logging.getLogger(__name__)


# Define HTTPAuthCredentials locally since it's not in fastapi.security
class HTTPAuthCredentials(NamedTuple):
    scheme: str
    credentials: str


security = HTTPBearer()


def create_access_token(
    tenant_id: UUID,
    user_id: UUID,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""

    if expires_delta is None:
        expires_delta = timedelta(hours=settings.JWT_EXPIRATION_HOURS)

    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify and decode JWT token."""

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
) -> CurrentUser:
    """Get current authenticated user from JWT token."""

    token = credentials.credentials

    try:
        payload = verify_token(token)
        user_id: str = payload.get("sub")
        tenant_id: str = payload.get("tenant_id")

        if user_id is None or tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        return CurrentUser(
            id=UUID(user_id),
            tenant_id=UUID(tenant_id),
            email="",  # Would be populated from database
            role="member",  # Would be populated from database
            is_active=True,
        )

    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthCredentials] = Depends(security),
) -> Optional[CurrentUser]:
    """Get current user if authenticated, otherwise None."""

    if credentials is None:
        return None

    return await get_current_user(credentials)
