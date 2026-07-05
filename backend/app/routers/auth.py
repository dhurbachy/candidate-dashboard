from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User,Role
from app.schemas import UserRegister, Token,UserOut,UserLogin,TokenResponse
from app.auth import get_password_hash, verify_password, create_access_token,get_current_user,create_refresh_token,verify_refresh_token,revoke_refresh_token,revoke_all_refresh_tokens_for_user
from app.logging import logger
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import REFRESH_COOKIE_NAME, COOKIE_SETTINGS, settings

router = APIRouter(prefix="/auth", tags=["Authentication Gateway Suite"])
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
        password=get_password_hash(payload.password),
        role=Role.reviewer
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"Successfully provisioned baseline reviewer account: {new_user.email}")
    return {"message": "Account created successfully with reviewer baseline privileges."}

@router.post("/login", response_model=Token)
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.email == payload.email).first()
    
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credential pairing. Verification failed."
        )
    
    token_claims = {"sub": user.email, "role": user.role, "id": user.id}
    access_token = create_access_token(data=token_claims)
    refresh_token = create_refresh_token(db, user_id=user.id)

    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        **COOKIE_SETTINGS,
    )

    
    logger.info(f"Successful session login token created for account ID: {user.id}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me",response_model=UserOut)
def me(current_user:User=Depends(get_current_user)):
    return current_user

@router.post("/refresh", response_model=TokenResponse)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    incoming_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not incoming_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token provided.")

    db_token = verify_refresh_token(db, incoming_token)
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid, expired, or revoked."
        )

    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists.")

    revoke_refresh_token(db, incoming_token)
    new_refresh_token = create_refresh_token(db, user_id=user.id)

    token_claims = {"sub": user.email, "role": user.role, "id": user.id}
    new_access_token = create_access_token(data=token_claims)

    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=new_refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        **COOKIE_SETTINGS,
    )

    logger.info(f"Refresh token rotated for account ID: {user.id}")
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incoming_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if incoming_token:
        revoke_refresh_token(db, incoming_token)

    response.delete_cookie(key=REFRESH_COOKIE_NAME, path=COOKIE_SETTINGS["path"])

    logger.info(f"User logged out, refresh token revoked for account ID: {current_user.id}")
    return {"message": "Logged out successfully."}