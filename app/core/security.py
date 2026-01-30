from passlib.context import CryptContext
from app.config import ACCESS_TOKEN_EXPIRE_MIN, JWT_SECRET,  JWT_ALG
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_access_token(sub: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MIN)
    payload = {"sub": sub, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
