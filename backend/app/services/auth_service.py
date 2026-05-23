from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.merchant import Merchant
from app.schemas.user import UserCreate, LoginRequest
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.exceptions import ValidationException, ConflictException, NotFoundException


class AuthService:
    """认证服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, user_data: UserCreate, role: str = "user") -> User:
        """注册用户。

        Args:
            user_data: 用户注册数据。
            role: 用户角色，默认为 user。

        Returns:
            创建的用户对象。

        Raises:
            ConflictException: 当用户名或手机号已存在时。
        """
        # 检查用户名是否已存在
        result = await self.db.execute(select(User).where(User.username == user_data.username))
        if result.scalar_one_or_none():
            raise ConflictException(f"用户名 {user_data.username} 已存在")

        # 检查手机号是否已存在
        result = await self.db.execute(select(User).where(User.phone == user_data.phone))
        if result.scalar_one_or_none():
            raise ConflictException(f"手机号 {user_data.phone} 已注册")

        # 创建用户
        user = User(
            username=user_data.username,
            phone=user_data.phone,
            password_hash=get_password_hash(user_data.password),
            role=role,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def register_merchant(self, user_data: UserCreate, business_data: dict) -> tuple[User, Merchant]:
        """注册商家。

        Args:
            user_data: 用户注册数据。
            business_data: 商家业务数据，包含 business_name, contact_phone, address, description。

        Returns:
            用户和商家对象的元组。

        Raises:
            ConflictException: 当用户名或手机号已存在时。
        """
        # 检查用户名是否已存在
        result = await self.db.execute(select(User).where(User.username == user_data.username))
        if result.scalar_one_or_none():
            raise ConflictException(f"用户名 {user_data.username} 已存在")

        # 检查手机号是否已存在
        result = await self.db.execute(select(User).where(User.phone == user_data.phone))
        if result.scalar_one_or_none():
            raise ConflictException(f"手机号 {user_data.phone} 已注册")

        # 创建用户
        user = User(
            username=user_data.username,
            phone=user_data.phone,
            password_hash=get_password_hash(user_data.password),
            role="merchant",
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        # 创建商家档案
        merchant = Merchant(
            user_id=user.id,
            business_name=business_data["business_name"],
            contact_phone=business_data.get("contact_phone", user_data.phone),
            address=business_data["address"],
            description=business_data.get("description"),
            status="pending",
        )
        self.db.add(merchant)
        await self.db.commit()
        await self.db.refresh(merchant)

        return user, merchant

    async def login(self, login_data: LoginRequest) -> tuple[User, str]:
        """用户登录。

        Args:
            login_data: 登录数据（手机号和密码）。

        Returns:
            用户对象和访问令牌的元组。

        Raises:
            NotFoundException: 当用户不存在时。
            ValidationException: 当密码错误时。
        """
        # 查找用户
        result = await self.db.execute(select(User).where(User.phone == login_data.phone))
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException("用户", login_data.phone)

        # 检查用户是否被禁用
        if not user.is_active:
            raise ValidationException("用户已被禁用，请联系管理员")

        # 验证密码
        if not verify_password(login_data.password, user.password_hash):
            raise ValidationException("密码错误")

        # 创建 Token
        access_token = create_access_token(data={"sub": user.id})

        return user, access_token

    async def change_password(
        self,
        user: User,
        old_password: str,
        new_password: str,
    ) -> User:
        """修改密码。

        Args:
            user: 当前用户。
            old_password: 旧密码。
            new_password: 新密码。

        Returns:
            更新后的用户对象。

        Raises:
            ValidationException: 当旧密码错误时。
        """
        # 验证旧密码
        if not verify_password(old_password, user.password_hash):
            raise ValidationException("旧密码错误")

        # 更新密码
        user.password_hash = get_password_hash(new_password)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def create_token(self, user: User) -> str:
        """创建访问令牌。

        Args:
            user: 用户对象。

        Returns:
            JWT 访问令牌。
        """
        return create_access_token(data={"sub": user.id})
