"""Dependency-light HS256 JWT authentication with tenant claims.

Author: Karthikeya
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer = HTTPBearer(auto_error=False)


class AuthConfigurationError(RuntimeError):
    """Raised when production authentication is not configured safely."""


def _is_production() -> bool:
    """Return whether production hardening rules should apply."""
    return os.getenv("APP_ENV", "development").lower() in {"prod", "production"}


def _b64(value: bytes) -> str:
    """Encode bytes as unpadded URL-safe base64."""
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _unb64(value: str) -> bytes:
    """Decode unpadded URL-safe base64."""
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _secret() -> bytes:
    """Read the JWT secret and reject unsafe production configuration."""
    secret = os.getenv("JWT_SECRET")
    if not secret:
        if _is_production():
            raise AuthConfigurationError("JWT_SECRET must be configured in production")
        return b"dev-only-change-me"
    if _is_production() and len(secret) < 32:
        raise AuthConfigurationError("JWT_SECRET must contain at least 32 characters in production")
    return secret.encode()


def create_token(
    subject: str, tenant_id: str, scopes: list[str] | None = None, expires_in: int = 3600
) -> str:
    """Create a signed token with an expiry and tenant claim."""
    if expires_in <= 0:
        raise ValueError("expires_in must be positive")
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": subject,
        "tenant_id": tenant_id,
        "scopes": scopes or ["routing:read", "forecast:read"],
        "exp": int(time.time()) + expires_in,
    }
    encoded = f"{_b64(json.dumps(header, separators=(',', ':')).encode())}.{_b64(json.dumps(payload, separators=(',', ':')).encode())}"
    signature = _b64(hmac.new(_secret(), encoded.encode(), hashlib.sha256).digest())
    return f"{encoded}.{signature}"


def decode_token(token: str) -> dict:
    """Verify signature, expiry, and required claims, returning the token payload."""
    try:
        encoded, signature = token.rsplit(".", 1)
        expected = _b64(hmac.new(_secret(), encoded.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError("invalid signature")
        payload = json.loads(_unb64(encoded.split(".")[1]))
        if payload.get("exp", 0) < time.time():
            raise ValueError("expired token")
        if not payload.get("sub") or not payload.get("tenant_id"):
            raise ValueError("missing claims")
        return payload
    except AuthConfigurationError as exc:
        raise HTTPException(status_code=503, detail="authentication is not configured") from exc
    except (ValueError, KeyError, IndexError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid JWT") from exc


@dataclass(frozen=True)
class TenantPrincipal:
    """Authenticated identity and tenant-scoped authorization claims."""

    subject: str
    tenant_id: str
    scopes: tuple[str, ...]


def get_current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> TenantPrincipal:
    """Resolve the current bearer token into a tenant principal."""
    if credentials is None:
        if os.getenv("AUTH_REQUIRED", "false").lower() != "true":
            return TenantPrincipal("development", "development", ("*",))
        raise HTTPException(status_code=401, detail="Bearer token required")
    claims = decode_token(credentials.credentials)
    return TenantPrincipal(claims["sub"], claims["tenant_id"], tuple(claims.get("scopes", [])))
