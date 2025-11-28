"""
Authentication Endpoints for Trivya Backend

This module provides API endpoints for user authentication, including
signup, login, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Any, Dict
import uuid
from datetime import datetime

from backend.app.models.user import User, UserCreate, Token, UserInDB
from shared.core_functions.security import get_security, TrivyaSecurity
from shared.core_functions.logger import get_logger

router = APIRouter()
security = get_security()
logger = get_logger(None).get_logger("AuthAPI")

# In-memory user store for MVP (Replace with DB in production)
# Format: {email: UserInDB}
fake_users_db: Dict[str, UserInDB] = {}


@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    if user_in.email in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    
    # Hash password
    hashed_password = security.hash_password(user_in.password)
    
    # Create user
    db_user = UserInDB(
        **user_in.dict(exclude={"password"}),
        hashed_password=hashed_password
    )
    
    fake_users_db[user_in.email] = db_user
    
    logger.info(f"User created: {user_in.email}")
    return db_user


@router.post("/login/access-token", response_model=Token)
async def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = fake_users_db.get(form_data.username)
    
    if not user:
        # Timing attack mitigation handled by verify_password usually, 
        # but here we just fail. In prod, use constant time lookup or dummy verify.
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = security.jwt_access_token_expire_minutes
    
    access_token = security.generate_jwt_token(
        user_id=user.id,
        roles=user.roles,
        permissions=user.permissions,
        token_type="access"
    )
    
    # Update last login
    user.last_login = datetime.utcnow()
    
    logger.info(f"User logged in: {user.email}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": access_token_expires * 60
    }


@router.post("/login/test-token", response_model=User)
async def test_token(current_user: User = Depends(get_current_user)) -> Any:
    """
    Test access token.
    """
    return current_user


# Dependency for getting current user
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/access-token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Validate token and return current user.
    """
    is_valid, payload, error = security.validate_jwt_token(token)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error or "Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_id = payload.get("user_id")
    
    # In a real DB, we would fetch by ID. Here we search the dict.
    user = None
    for u in fake_users_db.values():
        if u.id == user_id:
            user = u
            break
            
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return user
