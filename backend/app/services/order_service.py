from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple
import random
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.merchant import Merchant
from app.models.address import Address
from app.schemas.order import OrderCreate, OrderItemCreate, OrderItemResponse
from app.core.exceptions import NotFoundException, ValidationException, PermissionException


class OrderService:
    """订单服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, order_id: int) -> Order:
        """根据 ID 获取订单。

        Args:
            order_id: 订单 ID。

        Returns:
            订单对象。

        Raises:
            NotFoundException: 当订单不存在时。
        """
        result = await self.db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise NotFoundException("订单", order_id)
        return order

    async def get_by_order_no(self, order_no: str) -> Optional[Order]:
        """根据订单编号获取订单。

        Args:
            order_no: 订单编号。

        Returns:
            订单对象或 None。
        """
        result = await self.db.execute(select(Order).where(Order.order_no == order_no))
        return result.scalar_one_or_none()

    async def create(self, user_id: int, order_data: OrderCreate) -> Order:
        """创建订单。

        Args:
            user_id: 用户 ID。
            order_data: 订单创建数据。

        Returns:
            创建的订单对象。

        Raises:
            NotFoundException: 当商家、地址或商品不存在时。
            PermissionException: 当地址不属于该用户时。
            ValidationException: 当库存不足时。
        """
        # 验证商家是否存在
        merchant_result = await self.db.execute(
            select(Merchant).where(Merchant.id == order_data.merchant_id)
        )
        merchant = merchant_result.scalar_one_or_none()
        if not merchant:
            raise NotFoundException("商家", order_data.merchant_id)

        # 验证商家状态
        if merchant.status != "approved":
            raise ValidationException("该商家尚未通过审核")

        # 验证地址
        address_result = await self.db.execute(
            select(Address).where(
                Address.id == order_data.address_id,
                Address.user_id == user_id,
            )
        )
        address = address_result.scalar_one_or_none()
        if not address:
            raise NotFoundException("地址", order_data.address_id)

        # 验证商品并计算总价
        items_data = []
        total_price = Decimal("0")

        for item in order_data.items:
            # 验证商品
            product_result = await self.db.execute(
                select(Product).where(Product.id == item.product_id)
            )
            product = product_result.scalar_one_or_none()
            if not product:
                raise NotFoundException("商品", item.product_id)

            # 验证商品属于该商家
            if product.merchant_id != order_data.merchant_id:
                raise ValidationException("商品不属于该商家")

            # 验证商品是否上架
            if not product.is_available:
                raise ValidationException(f"商品 {product.name} 已下架")

            # 验证库存
            if product.stock > 0 and product.stock < item.quantity:
                raise ValidationException(f"商品 {product.name} 库存不足")

            # 计算小计
            subtotal = product.price * item.quantity
            total_price += subtotal

            items_data.append({
                "product": product,
                "quantity": item.quantity,
                "subtotal": subtotal,
            })

        # 扣减库存
        for item_data in items_data:
            product = item_data["product"]
            if product.stock > 0:
                product.stock -= item_data["quantity"]

        # 计算实付金额
        discount_amount = Decimal("0")
        delivery_fee = Decimal("0")
        pay_amount = total_price - discount_amount + delivery_fee

        # 生成订单编号
        order_no = self._generate_order_no()

        # 创建订单
        order = Order(
            order_no=order_no,
            user_id=user_id,
            merchant_id=order_data.merchant_id,
            address_id=order_data.address_id,
            receiver=address.receiver,
            receiver_phone=address.phone,
            receiver_address=f"{address.province}{address.city}{address.district}{address.detail_address}",
            total_price=total_price,
            discount_amount=discount_amount,
            delivery_fee=delivery_fee,
            pay_amount=pay_amount,
            remark=order_data.remark,
            status="pending",
        )
        self.db.add(order)
        await self.db.flush()
        await self.db.refresh(order)

        # 创建订单项
        for item_data in items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data["product"].id,
                product_name=item_data["product"].name,
                product_image=item_data["product"].image_url,
                price=item_data["product"].price,
                quantity=item_data["quantity"],
                subtotal=item_data["subtotal"],
            )
            self.db.add(order_item)

        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def cancel(
        self,
        order_id: int,
        user_id: int,
        reason: Optional[str] = None,
    ) -> Order:
        """取消订单。

        Args:
            order_id: 订单 ID。
            user_id: 用户 ID。
            reason: 取消原因。

        Returns:
            更新后的订单对象。

        Raises:
            NotFoundException: 当订单不存在时。
            PermissionException: 当订单不属于该用户时。
            ValidationException: 当订单状态不允许取消时。
        """
        order = await self.get_by_id(order_id)

        # 验证权限
        if order.user_id != user_id:
            raise PermissionException("没有权限操作此订单")

        # 验证状态
        if order.status not in ["pending", "paid"]:
            raise ValidationException("当前状态不允许取消订单")

        # 恢复库存
        await self._restore_stock(order_id)

        order.status = "cancelled"
        order.cancel_reason = reason
        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def pay(self, order_id: int, user_id: int) -> Order:
        """支付订单（模拟支付）。

        Args:
            order_id: 订单 ID。
            user_id: 用户 ID。

        Returns:
            更新后的订单对象。

        Raises:
            NotFoundException: 当订单不存在时。
            PermissionException: 当订单不属于该用户时。
            ValidationException: 当订单状态不允许支付时。
        """
        order = await self.get_by_id(order_id)

        # 验证权限
        if order.user_id != user_id:
            raise PermissionException("没有权限操作此订单")

        # 验证状态
        if order.status != "pending":
            raise ValidationException("只有待付款订单可以支付")

        order.status = "paid"
        order.paid_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def update_status(
        self,
        order_id: int,
        merchant_user_id: int,
        new_status: str,
    ) -> Order:
        """更新订单状态（商家端）。

        Args:
            order_id: 订单 ID。
            merchant_user_id: 商家用户 ID。
            new_status: 新状态。

        Returns:
            更新后的订单对象。

        Raises:
            NotFoundException: 当订单不存在时。
            PermissionException: 当订单不属于该商家时。
            ValidationException: 当状态流转不合法时。
        """
        order = await self.get_by_id(order_id)

        # 验证权限
        merchant_result = await self.db.execute(
            select(Merchant).where(Merchant.user_id == merchant_user_id)
        )
        merchant = merchant_result.scalar_one_or_none()
        if not merchant or order.merchant_id != merchant.id:
            raise PermissionException("没有权限操作此订单")

        # 验证状态流转
        valid_transitions = {
            "paid": ["preparing", "cancelled"],
            "preparing": ["delivering"],
            "delivering": ["completed"],
        }

        allowed_statuses = valid_transitions.get(order.status, [])
        if new_status not in allowed_statuses:
            raise ValidationException(
                f"订单当前状态为 {order.status}，不能转换为 {new_status}"
            )

        order.status = new_status

        # 如果完成订单，记录完成时间
        if new_status == "completed":
            order.completed_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def prepare(self, order_id: int, merchant_user_id: int) -> Order:
        """开始制作订单。

        Args:
            order_id: 订单 ID。
            merchant_user_id: 商家用户 ID。

        Returns:
            更新后的订单对象。
        """
        return await self.update_status(order_id, merchant_user_id, "preparing")

    async def deliver(self, order_id: int, merchant_user_id: int) -> Order:
        """开始配送订单。

        Args:
            order_id: 订单 ID。
            merchant_user_id: 商家用户 ID。

        Returns:
            更新后的订单对象。
        """
        return await self.update_status(order_id, merchant_user_id, "delivering")

    async def complete(self, order_id: int, merchant_user_id: int) -> Order:
        """完成订单。

        Args:
            order_id: 订单 ID。
            merchant_user_id: 商家用户 ID。

        Returns:
            更新后的订单对象。
        """
        return await self.update_status(order_id, merchant_user_id, "completed")

    async def list_user_orders(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
    ) -> Tuple[list[Order], int]:
        """获取用户的订单列表。

        Args:
            user_id: 用户 ID。
            page: 页码。
            page_size: 每页大小。
            status: 状态筛选。

        Returns:
            订单列表和总数的元组。
        """
        conditions = [Order.user_id == user_id]
        if status:
            conditions.append(Order.status == status)

        # 查询总数
        count_query = select(func.count(Order.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # 查询数据
        query = select(Order)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(Order.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        orders = result.scalars().all()

        return list(orders), total

    async def list_merchant_orders(
        self,
        merchant_user_id: int,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
    ) -> Tuple[list[Order], int]:
        """获取商家的订单列表。

        Args:
            merchant_user_id: 商家用户 ID。
            page: 页码。
            page_size: 每页大小。
            status: 状态筛选。

        Returns:
            订单列表和总数的元组。
        """
        # 获取商家 ID
        merchant_result = await self.db.execute(
            select(Merchant).where(Merchant.user_id == merchant_user_id)
        )
        merchant = merchant_result.scalar_one_or_none()
        if not merchant:
            return [], 0

        conditions = [Order.merchant_id == merchant.id]
        if status:
            conditions.append(Order.status == status)

        # 查询总数
        count_query = select(func.count(Order.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # 查询数据
        query = select(Order)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(Order.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        orders = result.scalars().all()

        return list(orders), total

    async def get_order_items(self, order_id: int) -> list[OrderItem]:
        """获取订单商品项列表。

        Args:
            order_id: 订单 ID。

        Returns:
            订单商品项列表。
        """
        # 验证订单存在
        await self.get_by_id(order_id)

        query = (
            select(OrderItem)
            .where(OrderItem.order_id == order_id)
            .order_by(OrderItem.id.asc())
        )
        result = await self.db.execute(query)
        items = result.scalars().all()

        return list(items)

    async def _restore_stock(self, order_id: int) -> None:
        """恢复订单商品库存。

        Args:
            order_id: 订单 ID。
        """
        items_result = await self.db.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        items = items_result.scalars().all()

        for item in items:
            product_result = await self.db.execute(
                select(Product).where(Product.id == item.product_id)
            )
            product = product_result.scalar_one_or_none()
            if product and product.stock >= 0:
                product.stock += item.quantity

    def _generate_order_no(self) -> str:
        """生成订单编号。

        Returns:
            订单编号字符串。
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_part = random.randint(1000, 9999)
        return f"OD{timestamp}{random_part}"
