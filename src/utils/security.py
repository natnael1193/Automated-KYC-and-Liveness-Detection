# security.py
from sqlmodel import SQLModel # type: ignore
from passlib.context import CryptContext # type: ignore
from datetime import datetime, timedelta
from jose import JWTError, jwt # type: ignore
from fastapi import Depends, HTTPException, status # type: ignore
from fastapi.security import OAuth2PasswordBearer # type: ignore
from sqlmodel import select # type: ignore
from src.config.db_config import sessions


# Secret key
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Create a CryptContext for bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Hash a plain password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verify a password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(model: SQLModel, email: str, password: str):
    with sessions as session:
        user = session.exec(select(model).where(model.email == email)).first()
        if user:
            if not verify_password(password, user.password):
                return False
            return user
        else:
            return False

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    print("Token:", token)
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("Payload:", payload)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return {"username": username}
    except JWTError:
        raise credentials_exception
