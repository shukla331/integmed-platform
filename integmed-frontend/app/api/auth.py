"""
Authentication API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import httpx
import jwt
from uuid import UUID

from app.core.database import get_db
from app.core.config import settings
from app.models.database import User, AuditLog
from app.schemas.api import HPRAuthInit, HPRAuthVerify, TokenResponse, UserResponse

router = APIRouter()


# =============== HPR Authentication ===============

@router.post("/doctor/init", response_model=dict)
async def init_doctor_auth(
    auth_data: HPRAuthInit,
    db: Session = Depends(get_db)
):
    """
    Initialize doctor authentication via HPR
    Sends OTP to registered mobile number
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.HPR_API_URL}/v1/auth/init",
                json={
                    "authMethod": "MOBILE_OTP",
                    "healthId": auth_data.mobile
                },
                headers={"Content-Type": "application/json"},
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to send OTP. Please verify mobile number."
                )
            
            data = response.json()
            return {
                "txn_id": data.get("txnId"),
                "message": "OTP sent to registered mobile number"
            }
    
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="HPR service unavailable"
        )


@router.post("/doctor/verify", response_model=TokenResponse)
async def verify_doctor_auth(
    auth_data: HPRAuthVerify,
    db: Session = Depends(get_db)
):
    """
    Verify OTP and complete authentication
    Returns JWT token and user profile
    """
    try:
        # Verify OTP with HPR
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.HPR_API_URL}/v1/auth/confirmWithMobileOTP",
                json={
                    "txnId": auth_data.txn_id,
                    "otp": auth_data.otp
                },
                headers={"Content-Type": "application/json"},
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid OTP"
                )
            
            hpr_data = response.json()
        
        # Fetch doctor profile from HPR
        hpr_id = hpr_data.get("hprId")
        
        async with httpx.AsyncClient() as client:
            profile_response = await client.get(
                f"{settings.HPR_API_URL}/v1/search/searchByHealthId",
                params={"healthId": hpr_id},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {hpr_data.get('token')}"
                },
                timeout=10.0
            )
            
            profile = profile_response.json()
        
        # Find or create user in database
        user = db.query(User).filter(User.hpr_id == hpr_id).first()
        
        if not user:
            # Create new user from HPR profile
            user = User(
                hpr_id=hpr_id,
                name=profile.get("name"),
                mobile=profile.get("mobile"),
                email=profile.get("email"),
                system=_map_system_type(profile.get("system")),
                qualification=", ".join(profile.get("qualifications", [])),
                registration_number=profile.get("registrationNumber"),
                registration_council=profile.get("councilName"),
                specialization=profile.get("specialization"),
                role="doctor",
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Generate JWT tokens
        access_token = _create_access_token(user.id)
        refresh_token = _create_refresh_token(user.id)
        
        # Log authentication
        audit = AuditLog(
            user_id=user.id,
            action="login",
            resource_type="user",
            resource_id=user.id,
            response_status=200
        )
        db.add(audit)
        db.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.from_orm(user)
        )
    
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="HPR service unavailable"
        )


# =============== Helper Functions ===============

def _map_system_type(hpr_system: str) -> str:
    """
    Map HPR system type to internal system enum
    """
    mapping = {
        "MODERN_MEDICINE": "allopathy",
        "AYURVEDA": "ayurveda",
        "HOMEOPATHY": "homeopathy",
        "UNANI": "unani"
    }
    return mapping.get(hpr_system, "allopathy")


def _create_access_token(user_id: UUID) -> str:
    """
    Create JWT access token
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _create_refresh_token(user_id: UUID) -> str:
    """
    Create JWT refresh token
    """
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.id == UUID(user_id)).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Inactive user")
        
        return user
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


from fastapi.security import OAuth2PasswordBearer
