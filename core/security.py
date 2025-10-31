from fastapi import HTTPException, Header
from typing import Optional
import os
import jwt
from datetime import datetime, timedelta

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = "HS256"
API_KEYS = os.getenv("API_KEYS", "").split(",")

def create_jwt_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def verify_api_key(api_key: Optional[str] = Header(None, alias="X-API-Key")):
    if not API_KEYS or not API_KEYS[0]:
        return True  # No API keys configured
    
    if not api_key or api_key not in API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )
    return api_key

def get_password_hash(password: str):
    # In a real application, use proper password hashing
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()