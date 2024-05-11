from jose import jwt
from datetime import datetime, timedelta

RESET_TOKEN_SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
RESET_TOKEN_EXPIRE_TIME = timedelta(hours=1)  # Token expires in 1 hour

def generate_reset_token(email: str) -> str:
    payload = {
        "email": email,
        "exp": datetime.utcnow() + RESET_TOKEN_EXPIRE_TIME
    }
    token = jwt.encode(payload, RESET_TOKEN_SECRET_KEY, algorithm="HS256")
    return token
