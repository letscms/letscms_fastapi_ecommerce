import jwt
from datetime import datetime, timedelta
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM

def create_token(data: dict, expires_minutes: int = 30):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=expires_minutes)})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(token: str):
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
