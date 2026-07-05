from  datetime import datetime,timedelta,timezone
from typing import Optional
from fastapi import Depends,HTTPException,status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_db
from sqlalchemy.orm import Session
from app.models import User,RefreshToken
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError,jwt
from passlib.context import CryptContext
from app.config import settings
import secrets

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

# ---------- Refresh token (opaque, DB-backed) ----------

def create_refresh_token(db: Session, user_id: int) -> str:
    raw_token = secrets.token_urlsafe(64)
    db_token = RefreshToken(
        token=raw_token,
        user_id=user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return raw_token

def verify_refresh_token(db: Session, token: str) -> RefreshToken | None:
    db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    
    current_time = datetime.now(timezone.utc).replace(tzinfo=None) 
    
    if not db_token or db_token.revoked or db_token.expires_at < current_time:
        return None
    return db_token

def revoke_refresh_token(db: Session, token: str) -> bool:
    db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if db_token:
        db_token.revoked = True
        db.commit()
        return True
    return False

def revoke_all_refresh_tokens_for_user(db: Session, user_id: int) -> None:
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id, RefreshToken.revoked == False
    ).update({"revoked": True})
    db.commit()