from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.security.auth import create_token
router = APIRouter(prefix='/auth', tags=['auth'])
class LoginRequest(BaseModel): username: str; password: str; tenant_id: str
@router.post('/token')
def token(request: LoginRequest):
    if not request.username or not request.password or not request.tenant_id: raise HTTPException(400, 'username, password, and tenant_id are required')
    return {'access_token': create_token(request.username, request.tenant_id), 'token_type': 'bearer', 'expires_in': 3600}
