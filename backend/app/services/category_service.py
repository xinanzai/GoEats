from typing import Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.merchant import Merchant
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.core.exceptions import NotFoundException, ValidationException, PermissionException


class CategoryService:
    """分类服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, category_id: int) -> Category:
        """根据 ID 获取分类。

        Args:
            category_id: 分类 ID。

        Returns:
            分类对象。

        Raises:
            NotFoundException: 当分类不存在时。
        """
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()
        if not category:
            raise NotFoundException("分类", category_id)
        return category

    async def create(self, merchant_user_id: int, category_data: CategoryCreate) -> Category:
        """创建分类。

        Args:
            merchant_user_id: 商家用户 ID（用于获取商家 ID）。
            category_data: 分类创建数据。

        Returns:
            创建的分类对象。

        Raises:
            NotFoundException: 当商家不存在时。
        """
        # 获取商家信息
        merchant_result = await self.db.execute(
            select(Merchant).where(Merchant.user_id == merchant_user_id)
        )
        merchant = merchant_result.scalar_one_or_none()
        if not merchant:
            raise NotFoundException("商家", merchant_user_id)

        category = Category(
            merchant_id=merchant.id,
            name=category_data.name,
            sort_order=category_data.sort_order,
        )
        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)
        return category

    async def update(
        self,
        category_id: int,
        merchant_user_id: int,
        update_data: CategoryUpdate,
    ) -> Category:
        """更新分类。

        Args:
            category_id: 分类 ID。
            merchant_user_id: 商家用户 ID（用于权限验证）。
            update_data: 更新数据。

        Returns:
            更新后的分类对象。

        Raises:
            NotFoundException: 当分类不存在时。
            PermissionException: 当用户无权限时。
        """
        category = await self.get_by_id(category_id)

        # 验证权限：获取商家信息
        merchant_result = await self.db.execute(
            select(Merchant).where(Merchant.user_id == merchant_user_id)
        )
        merchant = merchant_result.scalar_one_or_none()
        if not merchant or category.merchant_id != merchant.id:
            raise PermissionException("没有权限修改此分类")

        # 更新字段
        if update_data.name is not None:
            category.name = update_data.name
        if update_data.sort_order is not None:
            category.sort_order = update_data.sort_order

        await self.db.flush()
        await self.db.refresh(category)
        return category

    async def delete(self, category_id: int, merchant_user_id: int) -> bool:
        """删除分类。

        Args:
            category_id: 分类 ID。
            merchant_user_id: 商家用户 ID（用于权限验证）。

        Returns:
            是否删除成功。

        Raises:
            NotFoundException: 当分类不存在时。
            PermissionException: 当用户无权限时。
            ValidationException: 当分类下有商品时。
        """
        from app.models.product import Product

        category = await self.get_by_id(category_id)

        # 验证权限
        merchant_result = await self.db.execute(
            select(Merchant).where(Merchant.user_id == merchant_user_id)
        )
        merchant = merchant_result.scalar_one_or_none()
        if not merchant or category.merchant_id != merchant.id:
            raise PermissionException("没有权限删除此分类")

        # 检查是否有商品
        product_count_result = await self.db.execute(
            select(func.count(Product.id)).where(Product.category_id == category_id)
        )
        product_count = product_count_result.scalar()
        if product_count > 0:
            raise ValidationException("该分类下还有商品，无法删除")

        # 删除分类
        await self.db.delete(category)
        await self.db.flush()
        return True

    async def list_by_merchant(
        self,
        merchant_user_id: int,
    ) -> list[Category]:
        """获取商家的分类列表。

        Args:
            merchant_user_id: 商家用户 ID。

        Returns:
            分类列表。
        """
        # 获取商家信息
        merchant_result = await self.db.execute(
            select(Merchant).where(Merchant.user_id == merchant_user_id)
        )
        merchant = merchant_result.scalar_one_or_none()
        if not merchant:
            return []

        # 查询分类
        query = (
            select(Category)
            .where(Category.merchant_id == merchant.id)
            .order_by(Category.sort_order.asc(), Category.created_at.asc())
        )
        result = await self.db.execute(query)
        categories = result.scalars().all()

        return list(categories)

    async def list_by_merchant_public(
        self,
        merchant_id: int,
    ) -> list[Category]:
        """获取商家的分类列表（公开接口）。

        Args:
            merchant_id: 商家 ID。

        Returns:
            分类列表。
        """
        query = (
            select(Category)
            .where(Category.merchant_id == merchant_id)
            .order_by(Category.sort_order.asc(), Category.created_at.asc())
        )
        result = await self.db.execute(query)
        categories = result.scalars().all()

        return list(categories)
