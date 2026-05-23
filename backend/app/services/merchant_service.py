from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.merchant import Merchant
from app.models.user import User
from app.schemas.merchant import MerchantCreate, MerchantUpdate
from app.core.exceptions import NotFoundException, ValidationException, PermissionException


class MerchantService:
    """商家服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, merchant_id: int) -> Merchant:
        """根据 ID 获取商家。

        Args:
            user_id: 商家 ID。

        Returns:
            商家对象。

        Raises:
            NotFoundException: 当商家不存在时。
        """
        result = await self.db.execute(select(Merchant).where(Merchant.id == merchant_id))
        merchant = result.scalar_one_or_none()
        if not merchant:
            raise NotFoundException("商家", merchant_id)
        return merchant

    async def get_by_user_id(self, user_id: int) -> Optional[Merchant]:
        """根据用户 ID 获取商家。

        Args:
            user_id: 用户 ID。

        Returns:
            商家对象或 None。
        """
        result = await self.db.execute(select(Merchant).where(Merchant.user_id == user_id))
        return result.scalar_one_or_none()

    async def create(self, user_id: int, merchant_data: MerchantCreate) -> Merchant:
        """创建商家。

        Args:
            user_id: 关联的用户 ID。
            merchant_data: 商家创建数据。

        Returns:
            创建的商家对象。
        """
        # 检查用户是否已有商家档案
        existing = await self.get_by_user_id(user_id)
        if existing:
            raise ValidationException("您已提交过商家申请")

        merchant = Merchant(
            user_id=user_id,
            business_name=merchant_data.business_name,
            contact_phone=merchant_data.contact_phone,
            address=merchant_data.address,
            description=merchant_data.description,
            status="pending",
        )
        self.db.add(merchant)
        await self.db.flush()
        await self.db.refresh(merchant)
        return merchant

    async def update(
        self,
        merchant_id: int,
        user_id: int,
        update_data: MerchantUpdate,
    ) -> Merchant:
        """更新商家信息。

        Args:
            merchant_id: 商家 ID。
            user_id: 当前用户 ID（用于权限验证）。
            update_data: 更新数据。

        Returns:
            更新后的商家对象。

        Raises:
            NotFoundException: 当商家不存在时。
            PermissionException: 当用户无权限时。
        """
        merchant = await self.get_by_id(merchant_id)

        # 验证权限：只有商家本人或管理员可以更新
        if merchant.user_id != user_id:
            raise PermissionException("没有权限修改此商家信息")

        # 更新字段
        if update_data.business_name is not None:
            merchant.business_name = update_data.business_name
        if update_data.contact_phone is not None:
            merchant.contact_phone = update_data.contact_phone
        if update_data.address is not None:
            merchant.address = update_data.address
        if update_data.description is not None:
            merchant.description = update_data.description
        if update_data.logo is not None:
            merchant.logo = update_data.logo

        await self.db.flush()
        await self.db.refresh(merchant)
        return merchant

    async def list_merchants(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None,
        approved_only: bool = False,
    ) -> Tuple[list[Merchant], int]:
        """获取商家列表（分页）。

        Args:
            page: 页码，从 1 开始。
            page_size: 每页大小。
            search: 搜索关键词（商家名称）。
            status: 状态筛选（pending/approved/rejected）。
            approved_only: 只显示已通过的商家。

        Returns:
            商家列表和总数的元组。
        """
        # 构建查询条件
        conditions = []
        if search:
            conditions.append(Merchant.business_name.contains(search))
        if status:
            conditions.append(Merchant.status == status)
        if approved_only:
            conditions.append(Merchant.status == "approved")

        # 查询总数
        count_query = select(func.count(Merchant.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # 查询数据
        query = select(Merchant)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(Merchant.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        merchants = result.scalars().all()

        return list(merchants), total

    async def approve(self, merchant_id: int, admin_user_id: int) -> Merchant:
        """审批商家（通过）。

        Args:
            merchant_id: 商家 ID。
            admin_user_id: 管理员用户 ID。

        Returns:
            更新后的商家对象。

        Raises:
            NotFoundException: 当商家不存在时。
            ValidationException: 当商家状态不允许审批时。
        """
        merchant = await self.get_by_id(merchant_id)

        if merchant.status != "pending":
            raise ValidationException("只能审批待审核的商家")

        merchant.status = "approved"
        merchant.approved_at = datetime.utcnow()
        merchant.approved_by = admin_user_id
        merchant.rejection_reason = None

        await self.db.flush()
        await self.db.refresh(merchant)
        return merchant

    async def reject(
        self,
        merchant_id: int,
        admin_user_id: int,
        reason: str,
    ) -> Merchant:
        """审批商家（拒绝）。

        Args:
            merchant_id: 商家 ID。
            admin_user_id: 管理员用户 ID。
            reason: 拒绝原因。

        Returns:
            更新后的商家对象。

        Raises:
            NotFoundException: 当商家不存在时。
            ValidationException: 当商家状态不允许审批时。
        """
        merchant = await self.get_by_id(merchant_id)

        if merchant.status != "pending":
            raise ValidationException("只能审批待审核的商家")

        merchant.status = "rejected"
        merchant.rejection_reason = reason
        merchant.approved_by = admin_user_id

        await self.db.flush()
        await self.db.refresh(merchant)
        return merchant

    async def get_pending_merchants(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[list[Merchant], int]:
        """获取待审核商家列表。

        Args:
            page: 页码。
            page_size: 每页大小。

        Returns:
            商家列表和总数的元组。
        """
        # 查询总数
        count_query = select(func.count(Merchant.id)).where(Merchant.status == "pending")
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # 查询数据
        query = (
            select(Merchant)
            .where(Merchant.status == "pending")
            .order_by(Merchant.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.db.execute(query)
        merchants = result.scalars().all()

        return list(merchants), total
