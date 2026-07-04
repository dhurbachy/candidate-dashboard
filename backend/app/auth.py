from  datetime import datetime,timedelta
from typing import Optional
from fastapi import Depends,HTTPException,status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_db
from sqlalchemy.orm import Session
from app.models import User
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError,jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

bearer_scheme = HTTPBearer()

def verify_password(plain_password:str, hashed_password:str)->bool:

    return pwd_context.verify(plain_password,hashed_password)

def get_password_hash(password:str)->str:
   return pwd_context.hash(password)


def create_access_token(data:dict,expire_delta:Optional[timedelta]=None)->str:
    to_encode=data.copy()
    expire=datetime.utcnow()+(expire_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,settings.JWT_SECRET,algorithm=settings.JWT_ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),db: Session = Depends(get_db),)->dict:
    token = credentials.credentials

    credentials_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate":"Bearer"},
    )

    try:
        payload=jwt.decode(token,settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

        email:str=payload.get("sub")

        if not email:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user
    
def require_admin(current_user:dict=Depends(get_current_user))->dict:
    if current_user.get("role")!="admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return current_user