import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from tests.conftest import (
    _create_user, _create_merchant_user, _create_merchant,
    _create_category, _create_product, _create_address,
    _create_order, _create_order_item,
    get_test_headers,
)


class TestOrderCreate:
    """测试订单创建"""

    async def test_create_order_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试创建订单成功"""
        user = await _create_user(db_session, username="order_user1", phone="13800050001", password="password123")
        m_user = await _create_merchant_user(db_session, username="order_merchant1", phone="13800050011")
        merchant = await _create_merchant(db_session, user=m_user, business_name="订单商家1", status="approved")
        category = await _create_category(db_session, merchant=merchant, name="订单分类")
        product = await _create_product(db_session, merchant=merchant, category=category, name="订单商品", price=Decimal("29.90"), stock=100)
        address = await _create_address(db_session, user=user, receiver="张三", is_default=True)
        headers = get_test_headers(user_id=user.id, username="order_user1", role="user", phone="13800050001")

        response = await client.post("/api/v1/orders", headers=headers, json={
            "merchant_id": merchant.id,
            "address_id": address.id,
            "items": [
                {"product_id": product.id, "quantity": 2},
            ],
            "remark": "请尽快配送",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"
        assert len(data["items"]) == 1
        assert data["items"][0]["product_name"] == "订单商品"
        assert data["items"][0]["quantity"] == 2
        assert data["remark"] == "请尽快配送"
        assert "order_no" in data

    async def test_create_order_multiple_items(self, client: AsyncClient, db_session: AsyncSession):
        """测试创建多商品订单"""
        user = await _create_user(db_session, username="multi_order_user", phone="13800050002", password="password123")
        m_user = await _create_merchant_user(db_session, username="multi_merchant", phone="13800050012")
        merchant = await _create_merchant(db_session, user=m_user, business_name="多商品商家", status="approved")
        category = await _create_category(db_session, merchant=merchant, name="多商品分类")
        product1 = await _create_product(db_session, merchant=merchant, category=category, name="商品1", price=Decimal("10.00"), stock=50)
        product2 = await _create_product(db_session, merchant=merchant, category=category, name="商品2", price=Decimal("20.00"), stock=50)
        address = await _create_address(db_session, user=user, receiver="李四", is_default=True)
        headers = get_test_headers(user_id=user.id, username="multi_order_user", role="user", phone="13800050002")

        response = await client.post("/api/v1/orders", headers=headers, json={
            "merchant_id": merchant.id,
            "address_id": address.id,
            "items": [
                {"product_id": product1.id, "quantity": 1},
                {"product_id": product2.id, "quantity": 3},
            ],
        })
        assert response.status_code == 201
        data = response.json()
        assert len(data["items"]) == 2
        total_expected = float(Decimal("10.00") * 1 + Decimal("20.00") * 3)
        assert float(data["total_price"]) == total_expected

    async def test_create_order_unapproved_merchant(self, client: AsyncClient, db_session: AsyncSession):
        """测试向未审核通过的商家下单失败"""
        user = await _create_user(db_session, username="unapproved_user", phone="13800050003", password="password123")
        m_user = await _create_merchant_user(db_session, username="unapproved_merchant", phone="13800050013")
        merchant = await _create_merchant(db_session, user=m_user, business_name="未审核商家", status="pending")
        address = await _create_address(db_session, user=user, receiver="王五", is_default=True)
        headers = get_test_headers(user_id=user.id, username="unapproved_user", role="user", phone="13800050003")

        response = await client.post("/api/v1/orders", headers=headers, json={
            "merchant_id": merchant.id,
            "address_id": address.id,
            "items": [
                {"product_id": 1, "quantity": 1},
            ],
        })
        assert response.status_code == 400

    async def test_create_order_insufficient_stock(self, client: AsyncClient, db_session: AsyncSession):
        """测试库存不足时下单失败"""
        user = await _create_user(db_session, username="stock_user", phone="13800050004", password="password123")
        m_user = await _create_merchant_user(db_session, username="stock_merchant", phone="13800050014")
        merchant = await _create_merchant(db_session, user=m_user, business_name="库存商家", status="approved")
        category = await _create_category(db_session, merchant=merchant, name="库存分类")
        product = await _create_product(db_session, merchant=merchant, category=category, name="库存商品", price=Decimal("10.00"), stock=2)
        address = await _create_address(db_session, user=user, receiver="赵六", is_default=True)
        headers = get_test_headers(user_id=user.id, username="stock_user", role="user", phone="13800050004")

        response = await client.post("/api/v1/orders", headers=headers, json={
            "merchant_id": merchant.id,
            "address_id": address.id,
            "items": [
                {"product_id": product.id, "quantity": 5},
            ],
        })
        assert response.status_code == 400

    async def test_create_order_unavailable_product(self, client: AsyncClient, db_session: AsyncSession):
        """测试购买下架商品失败"""
        user = await _create_user(db_session, username="unavail_user", phone="13800050005", password="password123")
        m_user = await _create_merchant_user(db_session, username="unavail_merchant", phone="13800050015")
        merchant = await _create_merchant(db_session, user=m_user, business_name="下架商家", status="approved")
        category = await _create_category(db_session, merchant=merchant, name="下架分类")
        product = await _create_product(db_session, merchant=merchant, category=category, name="下架商品", price=Decimal("10.00"), stock=100, is_available=False)
        address = await _create_address(db_session, user=user, receiver="钱七", is_default=True)
        headers = get_test_headers(user_id=user.id, username="unavail_user", role="user", phone="13800050005")

        response = await client.post("/api/v1/orders", headers=headers, json={
            "merchant_id": merchant.id,
            "address_id": address.id,
            "items": [
                {"product_id": product.id, "quantity": 1},
            ],
        })
        assert response.status_code == 400

    async def test_create_order_unauthorized(self, client: AsyncClient):
        """测试未授权创建订单"""
        response = await client.post("/api/v1/orders", json={
            "merchant_id": 1,
            "address_id": 1,
            "items": [{"product_id": 1, "quantity": 1}],
        })
        assert response.status_code == 403

    async def test_create_order_invalid_address(self, client: AsyncClient, db_session: AsyncSession):
        """测试使用无效地址创建订单"""
        user = await _create_user(db_session, username="invalid_addr_user", phone="13800050006", password="password123")
        headers = get_test_headers(user_id=user.id, username="invalid_addr_user", role="user", phone="13800050006")

        response = await client.post("/api/v1/orders", headers=headers, json={
            "merchant_id": 1,
            "address_id": 99999,
            "items": [{"product_id": 1, "quantity": 1}],
        })
        assert response.status_code == 404

    async def test_create_order_missing_fields(self, client: AsyncClient, db_session: AsyncSession):
        """测试创建订单缺少必填字段"""
        user = await _create_user(db_session, username="missing_field_user", phone="13800050007", password="password123")
        headers = get_test_headers(user_id=user.id, username="missing_field_user", role="user", phone="13800050007")

        response = await client.post("/api/v1/orders", headers=headers, json={
            "merchant_id": 1,
        })
        assert response.status_code == 422


class TestUserOrderList:
    """测试用户端订单列表"""

    async def test_get_my_orders_empty(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取空订单列表"""
        user = await _create_user(db_session, username="empty_order_user", phone="13800050008", password="password123")
        headers = get_test_headers(user_id=user.id, username="empty_order_user", role="user", phone="13800050008")

        response = await client.get("/api/v1/orders/users/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0

    async def test_get_my_orders_with_data(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取有数据的订单列表"""
        user = await _create_user(db_session, username="list_order_user", phone="13800050009", password="password123")
        m_user = await _create_merchant_user(db_session, username="list_merchant", phone="13800050016")
        merchant = await _create_merchant(db_session, user=m_user, business_name="列表商家", status="approved")
        address = await _create_address(db_session, user=user, receiver="列表用户", is_default=True)
        await _create_order(db_session, user=user, merchant=merchant, address=address, status="pending")
        await _create_order(db_session, user=user, merchant=merchant, address=address, status="paid")
        await _create_order(db_session, user=user, merchant=merchant, address=address, status="completed")
        headers = get_test_headers(user_id=user.id, username="list_order_user", role="user", phone="13800050009")

        response = await client.get("/api/v1/orders/users/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    async def test_get_my_orders_with_status_filter(self, client: AsyncClient, db_session: AsyncSession):
        """测试按状态筛选订单列表"""
        user = await _create_user(db_session, username="filter_order_user", phone="13800050010", password="password123")
        m_user = await _create_merchant_user(db_session, username="filter_merchant", phone="13800050017")
        merchant = await _create_merchant(db_session, user=m_user, business_name="筛选商家", status="approved")
        address = await _create_address(db_session, user=user, receiver="筛选用户", is_default=True)
        await _create_order(db_session, user=user, merchant=merchant, address=address, status="pending")
        await _create_order(db_session, user=user, merchant=merchant, address=address, status="paid")
        await _create_order(db_session, user=user, merchant=merchant, address=address, status="pending")
        headers = get_test_headers(user_id=user.id, username="filter_order_user", role="user", phone="13800050010")

        response = await client.get("/api/v1/orders/users/me?status=pending", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        for item in data["items"]:
            assert item["status"] == "pending"


class TestUserOrderDetail:
    """测试用户端订单详情"""

    async def test_get_my_order_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取订单详情成功"""
        user = await _create_user(db_session, username="detail_order_user", phone="13800050011", password="password123")
        m_user = await _create_merchant_user(db_session, username="detail_merchant", phone="13800050018")
        merchant = await _create_merchant(db_session, user=m_user, business_name="详情商家", status="approved")
        address = await _create_address(db_session, user=user, receiver="详情用户", is_default=True)
        order = await _create_order(db_session, user=user, merchant=merchant, address=address, status="paid")
        headers = get_test_headers(user_id=user.id, username="detail_order_user", role="user", phone="13800050011")

        response = await client.get(f"/api/v1/orders/users/me/{order.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order.id
        assert data["status"] == "paid"
        assert data["receiver"] == "详情用户"

    async def test_get_other_user_order_fail(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取其他用户订单失败"""
        user1 = await _create_user(db_session, username="owner_order_user", phone="13800050012", password="password123")
        user2 = await _create_user(db_session, username="other_order_user", phone="13800050013", password="password123")
        m_user = await _create_merchant_user(db_session, username="other_merchant", phone="13800050019")
        merchant = await _create_merchant(db_session, user=m_user, business_name="其他商家", status="approved")
        address = await _create_address(db_session, user=user1, receiver="所有者", is_default=True)
        order = await _create_order(db_session, user=user1, merchant=merchant, address=address, status="pending")
        headers = get_test_headers(user_id=user2.id, username="other_order_user", role="user", phone="13800050013")

        response = await client.get(f"/api/v1/orders/users/me/{order.id}", headers=headers)
        assert response.status_code == 403

    async def test_get_my_order_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取不存在的订单"""
        user = await _create_user(db_session, username="notfound_order_user", phone="13800050014", password="password123")
        headers = get_test_headers(user_id=user.id, username="notfound_order_user", role="user", phone="13800050014")

        response = await client.get("/api/v1/orders/users/me/99999", headers=headers)
        assert response.status_code == 404

    async def test_get_my_order_unauthorized(self, client: AsyncClient):
        """测试未授权访问订单详情"""
        response = await client.get("/api/v1/orders/users/me/1")
        assert response.status_code == 403


class TestOrderCancel:
    """测试订单取消"""

    async def test_cancel_order_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试取消订单成功"""
        user = await _create_user(db_session, username="cancel_user", phone="13800050015", password="password123")
        m_user = await _create_merchant_user(db_session, username="cancel_merchant", phone="13800050020")
        merchant = await _create_merchant(db_session, user=m_user, business_name="取消商家", status="approved")
        address = await _create_address(db_session, user=user, receiver="取消用户", is_default=True)
        order = await _create_order(db_session, user=user, merchant=merchant, address=address, status="pending")
        headers = get_test_headers(user_id=user.id, username="cancel_user", role="user", phone="13800050015")

        response = await client.post(f"/api/v1/orders/users/me/{order.id}/cancel", headers=headers, json={
            "reason": "不想要了",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"
        assert data["cancel_reason"] == "不想要了"

    async def test_cancel_paid_order(self, client: AsyncClient, db_session: AsyncSession):
        """测试取消已支付的订单"""
        user = await _create_user(db_session, username="cancel_paid_user", phone="13800050016", password="password123")
        m_user = await _create_merchant_user(db_session, username="cancel_paid_merchant", phone="13800050021")
        merchant = await _create_merchant(db_session, user=m_user, business_name="已支付商家", status="approved")
        address = await _create_address(db_session, user=user, receiver="已支付用户", is_default=True)
        order = await _create_order(db_session, user=user, merchant=merchant, address=address, status="paid")
        headers = get_test_headers(user_id=user.id, username="cancel_paid_user", role="user", phone="13800050016")

        response = await client.post(f"/api/v1/orders/users/me/{order.id}/cancel", headers=headers, json={
            "reason": "改变主意了",
        })
        assert response.status_code in [200, 400]

    async def test_cancel_completed_order_fail(self, client: AsyncClient, db_session: AsyncSession):
        """测试取消已完成订单失败"""
        user = await _create_user(db_session, username="cancel_completed_user", phone="13800050017", password="password123")
        m_user = await _create_merchant_user(db_session, username="cancel_completed_merchant", phone="13800050022")
        merchant = await _create_merchant(db_session, user=m_user, business_name="已完成商家", status="approved")
        address = await _create_address(db_session, user=user, receiver="已完成用户", is_default=True)
        order = await _create_order(db_session, user=user, merchant=merchant, address=address, status="completed")
        headers = get_test_headers(user_id=user.id, username="cancel_completed_user", role="user", phone="13800050017")

        response = await client.post(f"/api/v1/orders/users/me/{order.id}/cancel", headers=headers, json={
            "reason": "尝试取消",
        })
        assert response.status_code == 400


class TestOrderPay:
    """测试订单支付"""

    async def test_pay_order_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试支付订单成功"""
        user = await _create_user(db_session, username="pay_user", phone="13800050018", password="password123")
        m_user = await _create_merchant_user(db_session, username="pay_merchant", phone="13800050023")
        merchant = await _create_merchant(db_session, user=m_user, business_name="支付商家", status="approved")
        address = await _create_address(db_session, user=user, receiver="支付用户", is_default=True)
        order = await _create_order(db_session, user=user, merchant=merchant, address=address, status="pending")
        headers = get_test_headers(user_id=user.id, username="pay_user", role="user", phone="13800050018")

        response = await client.post(f"/api/v1/orders/users/me/{order.id}/pay", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "paid"
        assert data["paid_at"] is not None

    async def test_pay_already_paid_order_fail(self, client: AsyncClient, db_session: AsyncSession):
        """测试重复支付订单失败"""
        user = await _create_user(db_session, username="pay_dup_user", phone="13800050019", password="password123")
        m_user = await _create_merchant_user(db_session, username="pay_dup_merchant", phone="13800050024")
        merchant = await _create_merchant(db_session, user=m_user, business_name="重复支付商家", status="approved")
        address = await _create_address(db_session, user=user, receiver="重复支付用户", is_default=True)
        order = await _create_order(db_session, user=user, merchant=merchant, address=address, status="paid")
        headers = get_test_headers(user_id=user.id, username="pay_dup_user", role="user", phone="13800050019")

        response = await client.post(f"/api/v1/orders/users/me/{order.id}/pay", headers=headers)
        assert response.status_code == 400


class TestMerchantOrderOperations:
    """测试商家端订单操作"""

    async def test_get_merchant_orders_empty(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家获取空订单列表"""
        m_user = await _create_merchant_user(db_session, username="empty_merchant_orders", phone="13800050025")
        await _create_merchant(db_session, user=m_user, business_name="空订单商家", status="approved")
        headers = get_test_headers(user_id=m_user.id, username="empty_merchant_orders", role="merchant", phone="13800050025")

        response = await client.get("/api/v1/orders/merchant/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    async def test_get_merchant_orders_with_data(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家获取有数据的订单列表"""
        user = await _create_user(db_session, username="merchant_list_user", phone="13800050026", password="password123")
        m_user = await _create_merchant_user(db_session, username="merchant_list", phone="13800050027")
        merchant = await _create_merchant(db_session, user=m_user, business_name="商家列表", status="approved")
        address = await _create_address(db_session, user=user, receiver="商家列表用户", is_default=True)
        await _create_order(db_session, user=user, merchant=merchant, address=address, status="pending")
        await _create_order(db_session, user=user, merchant=merchant, address=address, status="paid")
        headers = get_test_headers(user_id=m_user.id, username="merchant_list", role="merchant", phone="13800050027")

        response = await client.get("/api/v1/orders/merchant/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    async def test_prepare_order_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家开始制作订单"""
        user = await _create_user(db_session, username="prepare_user", phone="13800050028", password="password123")
        m_user = await _create_merchant_user(db_session, username="prepare_merchant", phone="13800050029")
        merchant = await _create_merchant(db_session, user=m_user, business_name="制作商家", status="approved")
        address = await _create_address(db_session, user=user, receiver="制作用户", is_default=True)
        order = await _create_order(db_session, user=user, merchant=merchant, address=address, status="paid")
        headers = get_test_headers(user_id=m_user.id, username="prepare_merchant", role="merchant", phone="13800050029")

        response = await client.post(f"/api/v1/orders/merchant/me/{order.id}/prepare", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "preparing"

    async def test_deliver_order_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家开始配送订单"""
        user = await _create_user(db_session, username="deliver_user", phone="13800050030", password="password123")
        m_user = await _create_merchant_user(db_session, username="deliver_merchant", phone="13800050031")
        merchant = await _create_merchant(db_session, user=m_user, business_name="配送商家", status="approved")
        address = await _create_address(db_session, user=user, receiver="配送用户", is_default=True)
        order = await _create_order(db_session, user=user, merchant=merchant, address=address, status="preparing")
        headers = get_test_headers(user_id=m_user.id, username="deliver_merchant", role="merchant", phone="13800050031")

        response = await client.post(f"/api/v1/orders/merchant/me/{order.id}/deliver", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "delivering"

    async def test_complete_order_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家完成订单"""
        user = await _create_user(db_session, username="complete_user", phone="13800050032", password="password123")
        m_user = await _create_merchant_user(db_session, username="complete_merchant", phone="13800050033")
        merchant = await _create_merchant(db_session, user=m_user, business_name="完成商家", status="approved")
        address = await _create_address(db_session, user=user, receiver="完成用户", is_default=True)
        order = await _create_order(db_session, user=user, merchant=merchant, address=address, status="delivering")
        headers = get_test_headers(user_id=m_user.id, username="complete_merchant", role="merchant", phone="13800050033")

        response = await client.post(f"/api/v1/orders/merchant/me/{order.id}/complete", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None

    async def test_merchant_update_order_status(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家更新订单状态"""
        user = await _create_user(db_session, username="status_user", phone="13800050034", password="password123")
        m_user = await _create_merchant_user(db_session, username="status_merchant", phone="13800050035")
        merchant = await _create_merchant(db_session, user=m_user, business_name="状态商家", status="approved")
        address = await _create_address(db_session, user=user, receiver="状态用户", is_default=True)
        order = await _create_order(db_session, user=user, merchant=merchant, address=address, status="paid")
        headers = get_test_headers(user_id=m_user.id, username="status_merchant", role="merchant", phone="13800050035")

        response = await client.put(f"/api/v1/orders/merchant/me/{order.id}/status", headers=headers, json={
            "new_status": "preparing",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "preparing"

    async def test_merchant_operate_other_merchant_order_fail(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家操作其他商家订单失败"""
        user = await _create_user(db_session, username="other_op_user", phone="13800050036", password="password123")
        m_user1 = await _create_merchant_user(db_session, username="other_op_merchant1", phone="13800050037")
        merchant1 = await _create_merchant(db_session, user=m_user1, business_name="商家1", status="approved")
        m_user2 = await _create_merchant_user(db_session, username="other_op_merchant2", phone="13800050038")
        await _create_merchant(db_session, user=m_user2, business_name="商家2", status="approved")
        address = await _create_address(db_session, user=user, receiver="操作用户", is_default=True)
        order = await _create_order(db_session, user=user, merchant=merchant1, address=address, status="paid")
        headers = get_test_headers(user_id=m_user2.id, username="other_op_merchant2", role="merchant", phone="13800050038")

        response = await client.post(f"/api/v1/orders/merchant/me/{order.id}/prepare", headers=headers)
        assert response.status_code == 403

    async def test_non_merchant_access_merchant_orders(self, client: AsyncClient, db_session: AsyncSession):
        """测试非商家角色访问商家订单接口失败"""
        user = await _create_user(db_session, username="non_merchant_order", phone="13800050039", role="user", password="password123")
        headers = get_test_headers(user_id=user.id, username="non_merchant_order", role="user", phone="13800050039")

        response = await client.get("/api/v1/orders/merchant/me", headers=headers)
        assert response.status_code == 403

    async def test_get_merchant_orders_unauthorized(self, client: AsyncClient):
        """测试未授权访问商家订单列表"""
        response = await client.get("/api/v1/orders/merchant/me")
        assert response.status_code == 403


class TestOrderFullFlow:
    """测试完整订单流程"""

    async def test_full_order_flow(self, client: AsyncClient, db_session: AsyncSession):
        """测试完整订单流程：创建->支付->制作->配送->完成"""
        # 创建用户
        user = await _create_user(db_session, username="flow_user", phone="13800050040", password="password123")
        # 创建商家和商品
        m_user = await _create_merchant_user(db_session, username="flow_merchant", phone="13800050041")
        merchant = await _create_merchant(db_session, user=m_user, business_name="流程商家", status="approved")
        category = await _create_category(db_session, merchant=merchant, name="流程分类")
        product = await _create_product(db_session, merchant=merchant, category=category, name="流程商品", price=Decimal("50.00"), stock=100)
        # 创建地址
        address = await _create_address(db_session, user=user, receiver="流程用户", is_default=True)

        user_headers = get_test_headers(user_id=user.id, username="flow_user", role="user", phone="13800050040")
        merchant_headers = get_test_headers(user_id=m_user.id, username="flow_merchant", role="merchant", phone="13800050041")

        # 1. 创建订单
        response = await client.post("/api/v1/orders", headers=user_headers, json={
            "merchant_id": merchant.id,
            "address_id": address.id,
            "items": [{"product_id": product.id, "quantity": 2}],
        })
        assert response.status_code == 201
        order_data = response.json()
        order_id = order_data["id"]
        assert order_data["status"] == "pending"

        # 2. 支付订单
        response = await client.post(f"/api/v1/orders/users/me/{order_id}/pay", headers=user_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "paid"

        # 3. 商家开始制作
        response = await client.post(f"/api/v1/orders/merchant/me/{order_id}/prepare", headers=merchant_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "preparing"

        # 4. 商家开始配送
        response = await client.post(f"/api/v1/orders/merchant/me/{order_id}/deliver", headers=merchant_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "delivering"

        # 5. 商家完成订单
        response = await client.post(f"/api/v1/orders/merchant/me/{order_id}/complete", headers=merchant_headers)
        assert response.status_code == 200
        final_data = response.json()
        assert final_data["status"] == "completed"
        assert final_data["completed_at"] is not None

        # 6. 用户查看订单
        response = await client.get(f"/api/v1/orders/users/me/{order_id}", headers=user_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
