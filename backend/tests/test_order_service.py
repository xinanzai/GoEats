import pytest
import pytest_asyncio
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.order_service import OrderService
from app.schemas.order import OrderCreate, OrderItemCreate
from app.core.exceptions import NotFoundException, ValidationException, PermissionException
from tests.conftest import (
    _create_user,
    _create_merchant_user,
    _create_merchant,
    _create_category,
    _create_product,
    _create_address,
    _create_order,
    _create_order_item,
    db_session,
)


@pytest.mark.asyncio
class TestOrderCreate:
    """订单创建测试"""

    async def test_create_order_success(self, db_session: AsyncSession):
        """测试成功创建订单"""
        user = await _create_user(db_session, phone="13800007000")
        m_user = await _create_merchant_user(db_session, phone="13800007001")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        category = await _create_category(db_session, merchant=merchant)
        product = await _create_product(db_session, merchant=merchant, category=category, price=Decimal("39.90"), stock=50)
        address = await _create_address(db_session, user=user)

        service = OrderService(db_session)
        order_data = OrderCreate(
            merchant_id=merchant.id,
            address_id=address.id,
            items=[
                OrderItemCreate(product_id=product.id, quantity=2)
            ],
            remark="请注意包装",
        )
        order = await service.create(user.id, order_data)

        assert order.id is not None
        assert order.user_id == user.id
        assert order.merchant_id == merchant.id
        assert order.address_id == address.id
        assert order.total_price == Decimal("79.80")
        assert order.status == "pending"
        assert order.remark == "请注意包装"
        assert order.receiver == address.receiver
        assert order.receiver_phone == address.phone

    async def test_create_order_items_created(self, db_session: AsyncSession):
        """测试创建订单时订单项被正确创建"""
        user = await _create_user(db_session, phone="13800007100")
        m_user = await _create_merchant_user(db_session, phone="13800007101")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        category = await _create_category(db_session, merchant=merchant)
        product = await _create_product(db_session, merchant=merchant, category=category, price=Decimal("25.00"), stock=100)
        address = await _create_address(db_session, user=user)

        service = OrderService(db_session)
        order_data = OrderCreate(
            merchant_id=merchant.id,
            address_id=address.id,
            items=[
                OrderItemCreate(product_id=product.id, quantity=3)
            ],
        )
        order = await service.create(user.id, order_data)

        items = await service.get_order_items(order.id)
        assert len(items) == 1
        assert items[0].product_id == product.id
        assert items[0].quantity == 3
        assert items[0].price == Decimal("25.00")
        assert items[0].subtotal == Decimal("75.00")

    async def test_create_order_stock_decreased(self, db_session: AsyncSession):
        """测试创建订单后商品库存减少"""
        user = await _create_user(db_session, phone="13800007200")
        m_user = await _create_merchant_user(db_session, phone="13800007201")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        category = await _create_category(db_session, merchant=merchant)
        product = await _create_product(db_session, merchant=merchant, category=category, stock=50)
        address = await _create_address(db_session, user=user)

        service = OrderService(db_session)
        order_data = OrderCreate(
            merchant_id=merchant.id,
            address_id=address.id,
            items=[
                OrderItemCreate(product_id=product.id, quantity=5)
            ],
        )
        await service.create(user.id, order_data)

        from app.services.product_service import ProductService
        p_service = ProductService(db_session)
        updated_product = await p_service.get_by_id(product.id)
        assert updated_product.stock == 45

    async def test_create_order_merchant_not_found(self, db_session: AsyncSession):
        """测试商家不存在时创建订单失败"""
        user = await _create_user(db_session, phone="13800007300")
        address = await _create_address(db_session, user=user)
        service = OrderService(db_session)
        order_data = OrderCreate(
            merchant_id=99999,
            address_id=address.id,
            items=[OrderItemCreate(product_id=1, quantity=1)],
        )

        with pytest.raises(NotFoundException) as exc_info:
            await service.create(user.id, order_data)
        assert "商家" in str(exc_info.value.detail)

    async def test_create_order_merchant_not_approved(self, db_session: AsyncSession):
        """测试商家未通过审核时创建订单失败"""
        user = await _create_user(db_session, phone="13800007400")
        m_user = await _create_merchant_user(db_session, phone="13800007401")
        merchant = await _create_merchant(db_session, user=m_user, status="pending")
        address = await _create_address(db_session, user=user)
        service = OrderService(db_session)
        order_data = OrderCreate(
            merchant_id=merchant.id,
            address_id=address.id,
            items=[OrderItemCreate(product_id=1, quantity=1)],
        )

        with pytest.raises(ValidationException) as exc_info:
            await service.create(user.id, order_data)
        assert "尚未通过审核" in str(exc_info.value.detail)

    async def test_create_order_address_not_found(self, db_session: AsyncSession):
        """测试地址不存在时创建订单失败"""
        user = await _create_user(db_session, phone="13800007500")
        m_user = await _create_merchant_user(db_session, phone="13800007501")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        service = OrderService(db_session)
        order_data = OrderCreate(
            merchant_id=merchant.id,
            address_id=99999,
            items=[OrderItemCreate(product_id=1, quantity=1)],
        )

        with pytest.raises(NotFoundException) as exc_info:
            await service.create(user.id, order_data)
        assert "地址" in str(exc_info.value.detail)

    async def test_create_order_address_not_belong_to_user(self, db_session: AsyncSession):
        """测试地址不属于该用户时创建订单失败"""
        user1 = await _create_user(db_session, username="user_order_addr1", phone="13800007600")
        user2 = await _create_user(db_session, username="user_order_addr2", phone="13800007601")
        m_user = await _create_merchant_user(db_session, username="merchant_order_addr", phone="13800007602")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        address = await _create_address(db_session, user=user2)
        service = OrderService(db_session)
        order_data = OrderCreate(
            merchant_id=merchant.id,
            address_id=address.id,
            items=[OrderItemCreate(product_id=1, quantity=1)],
        )

        with pytest.raises(NotFoundException) as exc_info:
            await service.create(user1.id, order_data)
        assert "地址" in str(exc_info.value.detail)

    async def test_create_order_product_not_found(self, db_session: AsyncSession):
        """测试商品不存在时创建订单失败"""
        user = await _create_user(db_session, phone="13800007700")
        m_user = await _create_merchant_user(db_session, phone="13800007701")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        address = await _create_address(db_session, user=user)
        service = OrderService(db_session)
        order_data = OrderCreate(
            merchant_id=merchant.id,
            address_id=address.id,
            items=[OrderItemCreate(product_id=99999, quantity=1)],
        )

        with pytest.raises(NotFoundException) as exc_info:
            await service.create(user.id, order_data)
        assert "商品" in str(exc_info.value.detail)

    async def test_create_order_product_not_belong_to_merchant(self, db_session: AsyncSession):
        """测试商品不属于该商家时创建订单失败"""
        user = await _create_user(db_session, username="user_order_prod1", phone="13800007800")
        m_user1 = await _create_merchant_user(db_session, username="merchant_order_prod1", phone="13800007801")
        merchant1 = await _create_merchant(db_session, user=m_user1, status="approved")
        m_user2 = await _create_merchant_user(db_session, username="merchant_order_prod2", phone="13800007802")
        merchant2 = await _create_merchant(db_session, user=m_user2, status="approved")
        category = await _create_category(db_session, merchant=merchant2)
        product = await _create_product(db_session, merchant=merchant2, category=category)
        address = await _create_address(db_session, user=user)
        service = OrderService(db_session)
        order_data = OrderCreate(
            merchant_id=merchant1.id,
            address_id=address.id,
            items=[OrderItemCreate(product_id=product.id, quantity=1)],
        )

        with pytest.raises(ValidationException) as exc_info:
            await service.create(user.id, order_data)
        assert "不属于该商家" in str(exc_info.value.detail)

    async def test_create_order_product_unavailable(self, db_session: AsyncSession):
        """测试商品已下架时创建订单失败"""
        user = await _create_user(db_session, phone="13800007900")
        m_user = await _create_merchant_user(db_session, phone="13800007901")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        category = await _create_category(db_session, merchant=merchant)
        product = await _create_product(db_session, merchant=merchant, category=category, is_available=False)
        address = await _create_address(db_session, user=user)
        service = OrderService(db_session)
        order_data = OrderCreate(
            merchant_id=merchant.id,
            address_id=address.id,
            items=[OrderItemCreate(product_id=product.id, quantity=1)],
        )

        with pytest.raises(ValidationException) as exc_info:
            await service.create(user.id, order_data)
        assert "已下架" in str(exc_info.value.detail)

    async def test_create_order_stock_insufficient(self, db_session: AsyncSession):
        """测试库存不足时创建订单失败"""
        user = await _create_user(db_session, phone="13800008000")
        m_user = await _create_merchant_user(db_session, phone="13800008001")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        category = await _create_category(db_session, merchant=merchant)
        product = await _create_product(db_session, merchant=merchant, category=category, stock=5, name="库存不足商品")
        address = await _create_address(db_session, user=user)
        service = OrderService(db_session)
        order_data = OrderCreate(
            merchant_id=merchant.id,
            address_id=address.id,
            items=[OrderItemCreate(product_id=product.id, quantity=10)],
        )

        with pytest.raises(ValidationException) as exc_info:
            await service.create(user.id, order_data)
        assert "库存不足" in str(exc_info.value.detail)

    async def test_create_order_multiple_items(self, db_session: AsyncSession):
        """测试创建包含多个商品的订单"""
        user = await _create_user(db_session, phone="13800008100")
        m_user = await _create_merchant_user(db_session, phone="13800008101")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        category = await _create_category(db_session, merchant=merchant)
        product1 = await _create_product(db_session, merchant=merchant, category=category, price=Decimal("30.00"), stock=100)
        product2 = await _create_product(db_session, merchant=merchant, category=category, price=Decimal("20.00"), stock=100)
        address = await _create_address(db_session, user=user)

        service = OrderService(db_session)
        order_data = OrderCreate(
            merchant_id=merchant.id,
            address_id=address.id,
            items=[
                OrderItemCreate(product_id=product1.id, quantity=2),
                OrderItemCreate(product_id=product2.id, quantity=3),
            ],
        )
        order = await service.create(user.id, order_data)

        assert order.total_price == Decimal("120.00")
        items = await service.get_order_items(order.id)
        assert len(items) == 2


@pytest.mark.asyncio
class TestOrderQuery:
    """订单查询测试"""

    async def test_get_by_id_success(self, db_session: AsyncSession):
        """测试根据ID获取订单成功"""
        order = await _create_order(db_session)
        service = OrderService(db_session)
        result = await service.get_by_id(order.id)

        assert result.id == order.id
        assert result.order_no is not None

    async def test_get_by_id_not_found(self, db_session: AsyncSession):
        """测试根据ID获取不存在的订单"""
        service = OrderService(db_session)

        with pytest.raises(NotFoundException) as exc_info:
            await service.get_by_id(99999)
        assert "订单" in str(exc_info.value.detail)

    async def test_list_user_orders_success(self, db_session: AsyncSession):
        """测试获取用户订单列表"""
        user = await _create_user(db_session, phone="13800009000")
        m_user = await _create_merchant_user(db_session, phone="13800009001")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        address = await _create_address(db_session, user=user)
        await _create_order(db_session, user=user, merchant=merchant, address=address)
        await _create_order(db_session, user=user, merchant=merchant, address=address)
        await _create_order(db_session, user=user, merchant=merchant, address=address)

        service = OrderService(db_session)
        orders, total = await service.list_user_orders(user.id)

        assert total == 3
        assert len(orders) == 3

    async def test_list_user_orders_with_status_filter(self, db_session: AsyncSession):
        """测试按状态筛选用户订单"""
        user = await _create_user(db_session, phone="13800009100")
        m_user = await _create_merchant_user(db_session, phone="13800009101")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        address = await _create_address(db_session, user=user)
        await _create_order(db_session, user=user, merchant=merchant, address=address, status="pending")
        await _create_order(db_session, user=user, merchant=merchant, address=address, status="paid")
        await _create_order(db_session, user=user, merchant=merchant, address=address, status="completed")

        service = OrderService(db_session)
        orders, total = await service.list_user_orders(user.id, status="paid")

        assert total == 1
        assert orders[0].status == "paid"

    async def test_list_merchant_orders_success(self, db_session: AsyncSession):
        """测试获取商家订单列表"""
        user = await _create_user(db_session, phone="13800009200")
        m_user = await _create_merchant_user(db_session, phone="13800009201")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        address = await _create_address(db_session, user=user)
        await _create_order(db_session, user=user, merchant=merchant, address=address)
        await _create_order(db_session, user=user, merchant=merchant, address=address)

        service = OrderService(db_session)
        orders, total = await service.list_merchant_orders(m_user.id)

        assert total == 2
        assert len(orders) == 2

    async def test_list_merchant_not_found(self, db_session: AsyncSession):
        """测试商家不存在时订单列表为空"""
        service = OrderService(db_session)
        orders, total = await service.list_merchant_orders(99999)

        assert total == 0
        assert len(orders) == 0

    async def test_get_order_items_success(self, db_session: AsyncSession):
        """测试获取订单商品项"""
        user = await _create_user(db_session, phone="13800009300")
        m_user = await _create_merchant_user(db_session, phone="13800009301")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        category = await _create_category(db_session, merchant=merchant)
        product = await _create_product(db_session, merchant=merchant, category=category)
        address = await _create_address(db_session, user=user)

        service = OrderService(db_session)
        order_data = OrderCreate(
            merchant_id=merchant.id,
            address_id=address.id,
            items=[OrderItemCreate(product_id=product.id, quantity=2)],
        )
        order = await service.create(user.id, order_data)

        items = await service.get_order_items(order.id)
        assert len(items) == 1
        assert items[0].quantity == 2

    async def test_get_order_items_order_not_found(self, db_session: AsyncSession):
        """测试获取不存在订单的商品项"""
        service = OrderService(db_session)

        with pytest.raises(NotFoundException):
            await service.get_order_items(99999)


@pytest.mark.asyncio
class TestOrderCancel:
    """订单取消测试"""

    async def test_cancel_order_when_pending(self, db_session: AsyncSession):
        """测试取消待付款订单"""
        user = await _create_user(db_session, phone="13800009400")
        m_user = await _create_merchant_user(db_session, phone="13800009401")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        address = await _create_address(db_session, user=user)
        order = await _create_order(db_session, user=user, merchant=merchant, address=address, status="pending")

        service = OrderService(db_session)
        result = await service.cancel(order.id, user.id, reason="不想买了")

        assert result.status == "cancelled"
        assert result.cancel_reason == "不想买了"

    async def test_cancel_order_when_paid(self, db_session: AsyncSession):
        """测试取消已付款订单"""
        user = await _create_user(db_session, phone="13800009500")
        m_user = await _create_merchant_user(db_session, phone="13800009501")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        address = await _create_address(db_session, user=user)
        order = await _create_order(db_session, user=user, merchant=merchant, address=address, status="paid")

        service = OrderService(db_session)
        result = await service.cancel(order.id, user.id)

        assert result.status == "cancelled"

    async def test_cancel_order_stock_restored(self, db_session: AsyncSession):
        """测试取消订单后库存恢复"""
        user = await _create_user(db_session, phone="13800009600")
        m_user = await _create_merchant_user(db_session, phone="13800009601")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        category = await _create_category(db_session, merchant=merchant)
        product = await _create_product(db_session, merchant=merchant, category=category, stock=10)
        address = await _create_address(db_session, user=user)

        service = OrderService(db_session)
        order_data = OrderCreate(
            merchant_id=merchant.id,
            address_id=address.id,
            items=[OrderItemCreate(product_id=product.id, quantity=3)],
        )
        order = await service.create(user.id, order_data)

        from app.services.product_service import ProductService
        p_service = ProductService(db_session)
        p1 = await p_service.get_by_id(product.id)
        assert p1.stock == 7

        await service.cancel(order.id, user.id)
        p2 = await p_service.get_by_id(product.id)
        assert p2.stock == 10

    async def test_cancel_order_not_found(self, db_session: AsyncSession):
        """测试取消不存在的订单"""
        service = OrderService(db_session)

        with pytest.raises(NotFoundException):
            await service.cancel(99999, 1)

    async def test_cancel_order_permission_denied(self, db_session: AsyncSession):
        """测试无权限取消他人订单"""
        user1 = await _create_user(db_session, username="user_cancel1", phone="13800009700")
        user2 = await _create_user(db_session, username="user_cancel2", phone="13800009701")
        m_user = await _create_merchant_user(db_session, username="merchant_cancel", phone="13800009702")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        address = await _create_address(db_session, user=user1)
        order = await _create_order(db_session, user=user1, merchant=merchant, address=address, status="pending")

        service = OrderService(db_session)

        with pytest.raises(PermissionException) as exc_info:
            await service.cancel(order.id, user2.id)
        assert "没有权限" in str(exc_info.value.detail)

    async def test_cancel_order_invalid_status(self, db_session: AsyncSession):
        """测试不允许取消的订单状态"""
        user = await _create_user(db_session, phone="13800009800")
        m_user = await _create_merchant_user(db_session, phone="13800009801")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        address = await _create_address(db_session, user=user)
        order = await _create_order(db_session, user=user, merchant=merchant, address=address, status="preparing")

        service = OrderService(db_session)

        with pytest.raises(ValidationException) as exc_info:
            await service.cancel(order.id, user.id)
        assert "不允许取消" in str(exc_info.value.detail)


@pytest.mark.asyncio
class TestOrderPay:
    """订单支付测试"""

    async def test_pay_order_success(self, db_session: AsyncSession):
        """测试成功支付订单"""
        user = await _create_user(db_session, phone="13800009900")
        m_user = await _create_merchant_user(db_session, phone="13800009901")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        address = await _create_address(db_session, user=user)
        order = await _create_order(db_session, user=user, merchant=merchant, address=address, status="pending")

        service = OrderService(db_session)
        result = await service.pay(order.id, user.id)

        assert result.status == "paid"
        assert result.paid_at is not None

    async def test_pay_order_not_found(self, db_session: AsyncSession):
        """测试支付不存在的订单"""
        service = OrderService(db_session)

        with pytest.raises(NotFoundException):
            await service.pay(99999, 1)

    async def test_pay_order_permission_denied(self, db_session: AsyncSession):
        """测试无权限支付他人订单"""
        user1 = await _create_user(db_session, username="user_pay1", phone="13800010000")
        user2 = await _create_user(db_session, username="user_pay2", phone="13800010001")
        m_user = await _create_merchant_user(db_session, username="merchant_pay", phone="13800010002")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        address = await _create_address(db_session, user=user1)
        order = await _create_order(db_session, user=user1, merchant=merchant, address=address, status="pending")

        service = OrderService(db_session)

        with pytest.raises(PermissionException) as exc_info:
            await service.pay(order.id, user2.id)
        assert "没有权限" in str(exc_info.value.detail)

    async def test_pay_order_invalid_status(self, db_session: AsyncSession):
        """测试支付非待付款状态订单"""
        user = await _create_user(db_session, phone="13800010100")
        m_user = await _create_merchant_user(db_session, phone="13800010101")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        address = await _create_address(db_session, user=user)
        order = await _create_order(db_session, user=user, merchant=merchant, address=address, status="paid")

        service = OrderService(db_session)

        with pytest.raises(ValidationException) as exc_info:
            await service.pay(order.id, user.id)
        assert "只有待付款订单可以支付" in str(exc_info.value.detail)


@pytest.mark.asyncio
class TestOrderStatusUpdate:
    """订单状态流转测试"""

    async def test_prepare_order_success(self, db_session: AsyncSession):
        """测试商家开始制作订单"""
        user = await _create_user(db_session, phone="13800010200")
        m_user = await _create_merchant_user(db_session, phone="13800010201")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        address = await _create_address(db_session, user=user)
        order = await _create_order(db_session, user=user, merchant=merchant, address=address, status="paid")

        service = OrderService(db_session)
        result = await service.prepare(order.id, m_user.id)

        assert result.status == "preparing"

    async def test_deliver_order_success(self, db_session: AsyncSession):
        """测试商家开始配送订单"""
        user = await _create_user(db_session, phone="13800010300")
        m_user = await _create_merchant_user(db_session, phone="13800010301")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        address = await _create_address(db_session, user=user)
        order = await _create_order(db_session, user=user, merchant=merchant, address=address, status="preparing")

        service = OrderService(db_session)
        result = await service.deliver(order.id, m_user.id)

        assert result.status == "delivering"

    async def test_complete_order_success(self, db_session: AsyncSession):
        """测试商家完成订单"""
        user = await _create_user(db_session, phone="13800010400")
        m_user = await _create_merchant_user(db_session, phone="13800010401")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        address = await _create_address(db_session, user=user)
        order = await _create_order(db_session, user=user, merchant=merchant, address=address, status="delivering")

        service = OrderService(db_session)
        result = await service.complete(order.id, m_user.id)

        assert result.status == "completed"
        assert result.completed_at is not None

    async def test_update_status_permission_denied(self, db_session: AsyncSession):
        """测试无权限更新他人商家订单状态"""
        user = await _create_user(db_session, username="user_status", phone="13800010500")
        m_user1 = await _create_merchant_user(db_session, username="merchant_status1", phone="13800010501")
        merchant1 = await _create_merchant(db_session, user=m_user1, status="approved")
        m_user2 = await _create_merchant_user(db_session, username="merchant_status2", phone="13800010502")
        address = await _create_address(db_session, user=user)
        order = await _create_order(db_session, user=user, merchant=merchant1, address=address, status="paid")

        service = OrderService(db_session)

        with pytest.raises(PermissionException) as exc_info:
            await service.update_status(order.id, m_user2.id, "preparing")
        assert "没有权限" in str(exc_info.value.detail)

    async def test_update_status_invalid_transition(self, db_session: AsyncSession):
        """测试非法的状态流转"""
        user = await _create_user(db_session, phone="13800010600")
        m_user = await _create_merchant_user(db_session, phone="13800010601")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        address = await _create_address(db_session, user=user)
        order = await _create_order(db_session, user=user, merchant=merchant, address=address, status="paid")

        service = OrderService(db_session)

        with pytest.raises(ValidationException) as exc_info:
            await service.update_status(order.id, m_user.id, "completed")
        assert "不能转换" in str(exc_info.value.detail)

    async def test_full_order_flow(self, db_session: AsyncSession):
        """测试完整订单状态流转：pending -> paid -> preparing -> delivering -> completed"""
        user = await _create_user(db_session, phone="13800010700")
        m_user = await _create_merchant_user(db_session, phone="13800010701")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        category = await _create_category(db_session, merchant=merchant)
        product = await _create_product(db_session, merchant=merchant, category=category, stock=100)
        address = await _create_address(db_session, user=user)

        service = OrderService(db_session)

        order_data = OrderCreate(
            merchant_id=merchant.id,
            address_id=address.id,
            items=[OrderItemCreate(product_id=product.id, quantity=1)],
        )
        order = await service.create(user.id, order_data)
        assert order.status == "pending"

        order = await service.pay(order.id, user.id)
        assert order.status == "paid"

        order = await service.prepare(order.id, m_user.id)
        assert order.status == "preparing"

        order = await service.deliver(order.id, m_user.id)
        assert order.status == "delivering"

        order = await service.complete(order.id, m_user.id)
        assert order.status == "completed"
        assert order.completed_at is not None
