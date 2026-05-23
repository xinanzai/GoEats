from typing import Optional, Tuple
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.core.exceptions import NotFoundException, ConflictException, ValidationException


class UserService:
    """用户服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User:
        """根据 ID 获取用户。

        Args:
            user_id: 用户 ID。

        Returns:
            用户对象。

        Raises:
            NotFoundException: 当用户不存在时。
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException("用户", user_id)
        return user

    async def get_by_phone(self, phone: str) -> Optional[User]:
        """根据手机号获取用户。

        Args:
            phone: 手机号。

        Returns:
            用户对象或 None。
        """
        result = await self.db.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户。

        Args:
            username: 用户名。

        Returns:
            用户对象或 None。
        """
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create(self, user_data: UserCreate) -> User:
        """创建用户。

        Args:
            user_data: 用户创建数据。

        Returns:
            创建的用户对象。

        Raises:
            ConflictException: 当用户名或手机号已存在时。
        """
        # 检查用户名是否已存在
        existing_user = await self.get_by_username(user_data.username)
        if existing_user:
            raise ConflictException(f"用户名 {user_data.username} 已存在")

        # 检查手机号是否已存在
        existing_phone = await self.get_by_phone(user_data.phone)
        if existing_phone:
            raise ConflictException(f"手机号 {user_data.phone} 已注册")

        user = User(
            username=user_data.username,
            phone=user_data.phone,
            password_hash=get_password_hash(user_data.password),
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: int, update_data: UserUpdate) -> User:
        """更新用户信息。

        Args:
            user_id: 用户 ID。
            update_data: 更新数据。

        Returns:
            更新后的用户对象。

        Raises:
            NotFoundException: 当用户不存在时。
            ConflictException: 当用户名或手机号被其他用户使用时。
        """
        user = await self.get_by_id(user_id)

        # 如果更新用户名，检查是否已被其他用户使用
        if update_data.username and update_data.username != user.username:
            existing = await self.get_by_username(update_data.username)
            if existing and existing.id != user_id:
                raise ConflictException(f"用户名 {update_data.username} 已存在")
            user.username = update_data.username

        # 如果更新手机号，检查是否已被其他用户使用
        if update_data.phone and update_data.phone != user.phone:
            existing = await self.get_by_phone(update_data.phone)
            if existing and existing.id != user_id:
                raise ConflictException(f"手机号 {update_data.phone} 已注册")
            user.phone = update_data.phone

        # 更新头像
        if update_data.avatar is not None:
            user.avatar = update_data.avatar

        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        role: Optional[str] = None,
    ) -> Tuple[list[User], int]:
        """获取用户列表（分页）。

        Args:
            page: 页码，从 1 开始。
            page_size: 每页大小。
            search: 搜索关键词（用户名或手机号）。
            role: 角色筛选。

        Returns:
            用户列表和总数的元组。
        """
        # 构建查询条件
        conditions = []
        if search:
            conditions.append(
                or_(
                    User.username.contains(search),
                    User.phone.contains(search),
                )
            )
        if role:
            conditions.append(User.role == role)

        # 查询总数
        count_query = select(func.count(User.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # 查询数据
        query = select(User)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(User.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        users = result.scalars().all()

        return list(users), total

    async def toggle_active(self, user_id: int, is_active: bool) -> User:
        """启用/禁用用户。

        Args:
            user_id: 用户 ID。
            is_active: 是否激活。

        Returns:
            更新后的用户对象。

        Raises:
            NotFoundException: 当用户不存在时。
        """
        user = await self.get_by_id(user_id)
        user.is_active = is_active
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update_password(self, user_id: int, old_password: str, new_password: str) -> User:
        """修改密码。

        Args:
            user_id: 用户 ID。
            old_password: 旧密码。
            new_password: 新密码。

        Returns:
            更新后的用户对象。

        Raises:
            NotFoundException: 当用户不存在时。
            ValidationException: 当旧密码错误时。
        """
        from app.core.security import verify_password

        user = await self.get_by_id(user_id)

        # 验证旧密码
        if not verify_password(old_password, user.password_hash):
            raise ValidationException("旧密码错误")

        user.password_hash = get_password_hash(new_password)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def reset_password(self, user_id: int, new_password: str) -> None:
        """重置密码（管理员操作，无需验证旧密码）。

        Args:
            user_id: 用户 ID。
            new_password: 新密码。

        Raises:
            NotFoundException: 当用户不存在时。
        """
        user = await self.get_by_id(user_id)

        user.password_hash = get_password_hash(new_password)
        await self.db.flush()
