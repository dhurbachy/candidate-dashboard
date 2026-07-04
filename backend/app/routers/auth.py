from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User,Role
from app.schemas import UserRegister, Token,UserOut,UserLogin
from app.auth import get_password_hash, verify_password, create_access_token,get_current_user
from app.logging import logger
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/api/auth", tags=["Authentication Gateway Suite"])
bearer_scheme = HTTPBearer()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
   
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account registration username is already taken."
        )
    
   
    new_user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        role=Role.reviewer
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"Successfully provisioned baseline reviewer account: {new_user.email}")
    return {"message": "Account created successfully with reviewer baseline privileges."}

@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.email == payload.email).first()
    
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credential pairing. Verification failed."
        )
    
    token_claims = {"sub": user.email, "role": user.role, "id": user.id}
    access_token = create_access_token(data=token_claims)
    
    logger.info(f"Successful session login token created for account ID: {user.id}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me",response_model=UserOut)
def me(current_user:User=Depends(get_current_user)):
    return current_user
