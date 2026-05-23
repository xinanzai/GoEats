from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.address import Address
from app.schemas.address import AddressCreate, AddressUpdate
from app.core.exceptions import NotFoundException, PermissionException


class AddressService:
    """地址服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, address_id: int, user_id: Optional[int] = None) -> Address:
        """根据 ID 获取地址。

        Args:
            address_id: 地址 ID。
            user_id: 用户 ID（可选，用于权限验证）。

        Returns:
            地址对象。

        Raises:
            NotFoundException: 当地址不存在时。
            PermissionException: 当地址不属于该用户时。
        """
        result = await self.db.execute(select(Address).where(Address.id == address_id))
        address = result.scalar_one_or_none()
        if not address:
            raise NotFoundException("地址", address_id)

        # 如果提供了 user_id，验证权限
        if user_id and address.user_id != user_id:
            raise PermissionException("没有权限访问此地址")

        return address

    async def create(self, user_id: int, address_data: AddressCreate) -> Address:
        """创建地址。

        Args:
            user_id: 用户 ID。
            address_data: 地址创建数据。

        Returns:
            创建的地址对象。
        """
        # 如果设置为默认地址，先取消其他默认地址
        if address_data.is_default:
            await self.clear_default_addresses(user_id)

        address = Address(
            user_id=user_id,
            receiver=address_data.receiver,
            phone=address_data.phone,
            province=address_data.province,
            city=address_data.city,
            district=address_data.district,
            detail_address=address_data.detail_address,
            is_default=address_data.is_default,
        )
        self.db.add(address)
        await self.db.flush()
        await self.db.refresh(address)
        return address

    async def update(
        self,
        address_id: int,
        user_id: int,
        update_data: AddressUpdate,
    ) -> Address:
        """更新地址。

        Args:
            address_id: 地址 ID。
            user_id: 用户 ID。
            update_data: 更新数据。

        Returns:
            更新后的地址对象。

        Raises:
            NotFoundException: 当地址不存在时。
            PermissionException: 当地址不属于该用户时。
        """
        address = await self.get_by_id(address_id, user_id)

        # 更新字段
        if update_data.receiver is not None:
            address.receiver = update_data.receiver
        if update_data.phone is not None:
            address.phone = update_data.phone
        if update_data.province is not None:
            address.province = update_data.province
        if update_data.city is not None:
            address.city = update_data.city
        if update_data.district is not None:
            address.district = update_data.district
        if update_data.detail_address is not None:
            address.detail_address = update_data.detail_address

        # 如果设置为默认地址，先取消其他默认地址
        if update_data.is_default and update_data.is_default != address.is_default:
            await self.clear_default_addresses(user_id, exclude_id=address_id)
            address.is_default = True

        await self.db.flush()
        await self.db.refresh(address)
        return address

    async def delete(self, address_id: int, user_id: int) -> bool:
        """删除地址。

        Args:
            address_id: 地址 ID。
            user_id: 用户 ID。

        Returns:
            是否删除成功。

        Raises:
            NotFoundException: 当地址不存在时。
            PermissionException: 当地址不属于该用户时。
        """
        address = await self.get_by_id(address_id, user_id)

        await self.db.delete(address)
        await self.db.flush()
        return True

    async def set_default(self, address_id: int, user_id: int) -> Address:
        """设置默认地址。

        Args:
            address_id: 地址 ID。
            user_id: 用户 ID。

        Returns:
            更新后的地址对象。

        Raises:
            NotFoundException: 当地址不存在时。
            PermissionException: 当地址不属于该用户时。
        """
        address = await self.get_by_id(address_id, user_id)

        # 取消其他默认地址
        await self.clear_default_addresses(user_id, exclude_id=address_id)

        # 设置当前地址为默认
        address.is_default = True
        await self.db.flush()
        await self.db.refresh(address)
        return address

    async def list_by_user(self, user_id: int) -> list[Address]:
        """获取用户的地址列表。

        Args:
            user_id: 用户 ID。

        Returns:
            地址列表。
        """
        query = (
            select(Address)
            .where(Address.user_id == user_id)
            .order_by(Address.is_default.desc(), Address.created_at.desc())
        )
        result = await self.db.execute(query)
        addresses = result.scalars().all()

        return list(addresses)

    async def get_default_address(self, user_id: int) -> Optional[Address]:
        """获取用户的默认地址。

        Args:
            user_id: 用户 ID。

        Returns:
            默认地址对象或 None。
        """
        result = await self.db.execute(
            select(Address).where(
                Address.user_id == user_id,
                Address.is_default == True,
            )
        )
        return result.scalar_one_or_none()

    async def clear_default_addresses(
        self,
        user_id: int,
        exclude_id: Optional[int] = None,
    ) -> None:
        """取消用户的所有默认地址。

        Args:
            user_id: 用户 ID。
            exclude_id: 要排除的地址 ID（可选）。
        """
        query = select(Address).where(
            Address.user_id == user_id,
            Address.is_default == True,
        )
        if exclude_id:
            query = query.where(Address.id != exclude_id)

        result = await self.db.execute(query)
        addresses = result.scalars().all()

        for address in addresses:
            address.is_default = False
