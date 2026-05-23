from typing import Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.merchant import Merchant
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductUpdate
from app.core.exceptions import NotFoundException, ValidationException, PermissionException


class ProductService:
    """商品服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, product_id: int) -> Product:
        """根据 ID 获取商品。

        Args:
            product_id: 商品 ID。

        Returns:
            商品对象。

        Raises:
            NotFoundException: 当商品不存在时。
        """
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if not product:
            raise NotFoundException("商品", product_id)
        return product

    async def create(self, merchant_user_id: int, product_data: ProductCreate) -> Product:
        """创建商品。

        Args:
            merchant_user_id: 商家用户 ID。
            product_data: 商品创建数据。

        Returns:
            创建的商品对象。

        Raises:
            NotFoundException: 当商家或分类不存在时。
            PermissionException: 当分类不属于该商家时。
        """
        # 获取商家信息
        merchant_result = await self.db.execute(
            select(Merchant).where(Merchant.user_id == merchant_user_id)
        )
        merchant = merchant_result.scalar_one_or_none()
        if not merchant:
            raise NotFoundException("商家", merchant_user_id)

        # 验证分类是否属于该商家
        category_result = await self.db.execute(
            select(Category).where(
                Category.id == product_data.category_id,
                Category.merchant_id == merchant.id,
            )
        )
        category = category_result.scalar_one_or_none()
        if not category:
            raise PermissionException("分类不存在或不属于该商家")

        product = Product(
            merchant_id=merchant.id,
            category_id=product_data.category_id,
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            original_price=product_data.original_price,
            stock=product_data.stock,
            is_available=product_data.is_available,
            sort_order=product_data.sort_order,
        )
        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def update(
        self,
        product_id: int,
        merchant_user_id: int,
        update_data: ProductUpdate,
    ) -> Product:
        """更新商品。

        Args:
            product_id: 商品 ID。
            merchant_user_id: 商家用户 ID。
            update_data: 更新数据。

        Returns:
            更新后的商品对象。

        Raises:
            NotFoundException: 当商品不存在时。
            PermissionException: 当商品不属于该商家时。
        """
        product = await self.get_by_id(product_id)

        # 验证权限
        merchant_result = await self.db.execute(
            select(Merchant).where(Merchant.user_id == merchant_user_id)
        )
        merchant = merchant_result.scalar_one_or_none()
        if not merchant or product.merchant_id != merchant.id:
            raise PermissionException("没有权限修改此商品")

        # 更新字段
        if update_data.name is not None:
            product.name = update_data.name
        if update_data.description is not None:
            product.description = update_data.description
        if update_data.price is not None:
            product.price = update_data.price
        if update_data.original_price is not None:
            product.original_price = update_data.original_price
        if update_data.image_url is not None:
            product.image_url = update_data.image_url
        if update_data.images is not None:
            product.images = update_data.images
        if update_data.stock is not None:
            product.stock = update_data.stock
        if update_data.is_available is not None:
            product.is_available = update_data.is_available
        if update_data.sort_order is not None:
            product.sort_order = update_data.sort_order

        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def delete(self, product_id: int, merchant_user_id: int) -> bool:
        """删除商品。

        Args:
            product_id: 商品 ID。
            merchant_user_id: 商家用户 ID。

        Returns:
            是否删除成功。

        Raises:
            NotFoundException: 当商品不存在时。
            PermissionException: 当商品不属于该商家时。
        """
        product = await self.get_by_id(product_id)

        # 验证权限
        merchant_result = await self.db.execute(
            select(Merchant).where(Merchant.user_id == merchant_user_id)
        )
        merchant = merchant_result.scalar_one_or_none()
        if not merchant or product.merchant_id != merchant.id:
            raise PermissionException("没有权限删除此商品")

        await self.db.delete(product)
        await self.db.flush()
        return True

    async def toggle_available(
        self,
        product_id: int,
        merchant_user_id: int,
    ) -> Product:
        """切换商品上架/下架状态。

        Args:
            product_id: 商品 ID。
            merchant_user_id: 商家用户 ID。

        Returns:
            更新后的商品对象。

        Raises:
            NotFoundException: 当商品不存在时。
            PermissionException: 当商品不属于该商家时。
        """
        product = await self.get_by_id(product_id)

        # 验证权限
        merchant_result = await self.db.execute(
            select(Merchant).where(Merchant.user_id == merchant_user_id)
        )
        merchant = merchant_result.scalar_one_or_none()
        if not merchant or product.merchant_id != merchant.id:
            raise PermissionException("没有权限操作此商品")

        product.is_available = not product.is_available
        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def list_products(
        self,
        page: int = 1,
        page_size: int = 20,
        merchant_id: Optional[int] = None,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        available_only: bool = True,
    ) -> Tuple[list[Product], int]:
        """获取商品列表（分页）。

        Args:
            page: 页码。
            page_size: 每页大小。
            merchant_id: 商家 ID 筛选。
            category_id: 分类 ID 筛选。
            search: 搜索关键词。
            available_only: 只显示上架商品。

        Returns:
            商品列表和总数的元组。
        """
        # 构建查询条件
        conditions = []
        if merchant_id:
            conditions.append(Product.merchant_id == merchant_id)
        if category_id:
            conditions.append(Product.category_id == category_id)
        if search:
            conditions.append(Product.name.contains(search))
        if available_only:
            conditions.append(Product.is_available == True)

        # 查询总数
        count_query = select(func.count(Product.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # 查询数据
        query = select(Product)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(Product.sort_order.asc(), Product.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        products = result.scalars().all()

        return list(products), total

    async def list_by_merchant(
        self,
        merchant_user_id: int,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        category_id: Optional[int] = None,
        is_available: Optional[bool] = None,
    ) -> Tuple[list[Product], int]:
        """获取商家的商品列表。

        Args:
            merchant_user_id: 商家用户 ID。
            page: 页码。
            page_size: 每页大小。
            keyword: 搜索关键词（商品名称）。
            category_id: 分类 ID 筛选。
            is_available: 上架状态筛选。

        Returns:
            商品列表和总数的元组。
        """
        # 获取商家信息
        merchant_result = await self.db.execute(
            select(Merchant).where(Merchant.user_id == merchant_user_id)
        )
        merchant = merchant_result.scalar_one_or_none()
        if not merchant:
            return [], 0

        # 构建查询条件
        conditions = [Product.merchant_id == merchant.id]
        if keyword:
            conditions.append(Product.name.contains(keyword))
        if category_id:
            conditions.append(Product.category_id == category_id)
        if is_available is not None:
            conditions.append(Product.is_available == is_available)

        # 查询总数
        count_query = select(func.count(Product.id)).where(*conditions)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # 查询数据
        query = (
            select(Product)
            .where(*conditions)
            .order_by(Product.sort_order.asc(), Product.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.db.execute(query)
        products = result.scalars().all()

        return list(products), total

    async def decrease_stock(self, product_id: int, quantity: int) -> bool:
        """减少商品库存。

        Args:
            product_id: 商品 ID。
            quantity: 减少的数量。

        Returns:
            是否成功。

        Raises:
            NotFoundException: 当商品不存在时。
            ValidationException: 当库存不足时。
        """
        product = await self.get_by_id(product_id)

        # 0 表示不限库存
        if product.stock > 0 and product.stock < quantity:
            raise ValidationException(f"商品 {product.name} 库存不足")

        if product.stock > 0:
            product.stock -= quantity
        await self.db.flush()
        return True
