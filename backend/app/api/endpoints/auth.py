from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import (
    UserCreate, LoginRequest, TokenResponse, UserResponse,
    MerchantRegisterRequest,
)
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """注册用户"""
    auth_service = AuthService(db)
    user = await auth_service.register(user_data, role="user")
    return user


@router.post("/merchant/register", status_code=status.HTTP_201_CREATED)
async def merchant_register(
    register_data: MerchantRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """注册商家"""
    auth_service = AuthService(db)

    from app.schemas.user import UserCreate
    user_data = UserCreate(
        username=register_data.username,
        phone=register_data.phone,
        password=register_data.password,
    )
    business_data = {
        "business_name": register_data.business_name,
        "contact_phone": register_data.contact_phone,
        "address": register_data.address,
        "description": register_data.description,
    }

    user, merchant = await auth_service.register_merchant(user_data, business_data)

    return {
        "user": UserResponse.model_validate(user),
        "merchant": {
            "id": merchant.id,
            "business_name": merchant.business_name,
            "status": merchant.status,
            "message": "商家注册申请已提交，等待管理员审核",
        }
    }


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """用户登录"""
    auth_service = AuthService(db)
    user, access_token = await auth_service.login(login_data)
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """刷新令牌"""
    auth_service = AuthService(db)
    access_token = await auth_service.create_token(current_user)
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """获取当前用户信息"""
    return current_user
