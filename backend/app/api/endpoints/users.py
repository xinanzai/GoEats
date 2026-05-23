from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import UserUpdate, UserResponse, ChangePasswordRequest
from app.schemas.address import AddressCreate, AddressUpdate, AddressResponse
from app.services.user_service import UserService
from app.services.address_service import AddressService
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    """获取当前用户信息"""
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新当前用户信息"""
    user_service = UserService(db)
    user = await user_service.update(current_user.id, update_data)
    return user


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """修改密码"""
    from app.services.auth_service import AuthService
    auth_service = AuthService(db)
    await auth_service.change_password(
        current_user,
        password_data.old_password,
        password_data.new_password,
    )


@router.get("/addresses", response_model=list[AddressResponse])
async def get_addresses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取用户地址列表"""
    address_service = AddressService(db)
    addresses = await address_service.list_by_user(current_user.id)
    return addresses


@router.post("/addresses", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(
    address_data: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加用户地址"""
    address_service = AddressService(db)
    address = await address_service.create(current_user.id, address_data)
    return address


@router.put("/addresses/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: int,
    address_data: AddressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新用户地址"""
    address_service = AddressService(db)
    address = await address_service.update(address_id, current_user.id, address_data)
    return address


@router.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除用户地址"""
    address_service = AddressService(db)
    await address_service.delete(address_id, current_user.id)


@router.put("/addresses/{address_id}/set-default", response_model=AddressResponse)
async def set_default_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """设置默认地址"""
    address_service = AddressService(db)
    address = await address_service.set_default(address_id, current_user.id)
    return address
