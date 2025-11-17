from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta,timezone
from ..database import get_db
from ..crud.user_crud import get_user_by_id
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from ..enum import RoleEnum
import bcrypt
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session 

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
security_scheme = HTTPBearer()

class TokenPayLoad(BaseModel):
    sub: str
    user_id: Optional[int] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[RoleEnum] = None
    exp: Optional[datetime] = None

class CurrentUser(BaseModel):
    user_id: int
    email: str
    full_name: str
    role: str
   


def verify_password(plain_password: str, hashed_password: str) -> bool:
    
    return bcrypt.checkpw(
        password=plain_password.encode('utf-8'),
        hashed_password=hashed_password.encode('utf-8')
    )
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type" : "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type" : "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(db: Session = Depends(get_db), creds : HTTPAuthorizationCredentials = Depends(security_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"Authentication": "Bearer"}
    )
    
    token = creds.credentials
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("user_id"))
        email: str = payload.get("email")
        full_name: str = payload.get("full_name")
        role: str = payload.get("role")
       
        if user_id is None:
            raise credentials_exception
        db_user = get_user_by_id(db=db, user_id=user_id)

        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nguoi dung nay khong ton tai")
        token_type = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    return CurrentUser(
        user_id=user_id,
        email=email,
        full_name=full_name,
        role=role
    )

def verify_refresh_token(token: str) -> dict:
    """
    Verify refresh token và trả về payload
    """
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        
        # Kiểm tra loại token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        return payload
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )