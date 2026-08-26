"""Dependency-light HS256 JWT authentication with tenant claims."""

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


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _secret() -> bytes:
    return os.getenv("JWT_SECRET", "dev-only-change-me").encode()


def create_token(
    subject: str, tenant_id: str, scopes: list[str] | None = None, expires_in: int = 3600
) -> str:
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
    except (ValueError, KeyError, IndexError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid JWT") from exc


@dataclass(frozen=True)
class TenantPrincipal:
    subject: str
    tenant_id: str
    scopes: tuple[str, ...]


def get_current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> TenantPrincipal:
    if credentials is None:
        if os.getenv("AUTH_REQUIRED", "false").lower() != "true":
            return TenantPrincipal("development", "development", ("*",))
        raise HTTPException(status_code=401, detail="Bearer token required")
    claims = decode_token(credentials.credentials)
    return TenantPrincipal(claims["sub"], claims["tenant_id"], tuple(claims.get("scopes", [])))
