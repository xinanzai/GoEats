import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from decimal import Decimal

from tests.conftest import (
    _create_user, _create_merchant_user, _create_merchant,
    _create_category, _create_product, _create_address,
    _create_order, _create_order_item,
    generate_test_token, get_test_headers, get_admin_headers,
)


class TestOrderCreateFlow:
    """E2E 测试：用户完整下单流程

    测试场景：用户注册 → 登录 → 添加地址 → 浏览商家和商品 → 下单 → 支付
    """

    async def test_full_order_creation_flow(self, client: AsyncClient, db_session: AsyncSession):
        """测试用户从注册到下单的完整流程"""
        # Step 1: 创建已审核的商家和商品
        m_user = await _create_merchant_user(
            db_session,
            username="order_flow_merchant",
            phone="13800080011",
        )
        merchant = await _create_merchant(
            db_session, user=m_user, business_name="下单流程商家", status="approved"
        )
        category = await _create_category(
            db_session, merchant=merchant, name="主食"
        )
        product1 = await _create_product(
            db_session, merchant=merchant, category=category,
            name="牛肉面", price=Decimal("35.00"), stock=50,
        )
        product2 = await _create_product(
            db_session, merchant=merchant, category=category,
            name="炒饭", price=Decimal("18.00"), stock=100,
        )

        # Step 2: 用户注册
        register_data = {
            "username": "order_flow_user",
            "phone": "13800080001",
            "password": "password123",
        }
        response = await client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201

        # Step 3: 用户登录
        response = await client.post("/api/v1/auth/login", json={
            "phone": "13800080001",
            "password": "password123",
        })
        assert response.status_code == 200
        token = response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {token}"}

        # Step 4: 添加收货地址
        response = await client.post("/api/v1/users/addresses", headers=user_headers, json={
            "receiver": "李明",
            "phone": "13700000001",
            "province": "北京市",
            "city": "北京市",
            "district": "海淀区",
            "detail_address": "中关村大街1号",
            "is_default": True,
        })
        assert response.status_code == 201
        address_id = response.json()["id"]

        # Step 5: 浏览商品列表
        response = await client.get(f"/api/v1/products?merchant_id={merchant.id}")
        assert response.status_code == 200
        products = response.json()
        assert products["total"] >= 2

        # Step 6: 创建订单
        response = await client.post("/api/v1/orders", headers=user_headers, json={
            "merchant_id": merchant.id,
            "address_id": address_id,
            "items": [
                {"product_id": product1.id, "quantity": 2},
                {"product_id": product2.id, "quantity": 3},
            ],
            "remark": "请不要放辣",
        })
        assert response.status_code == 201
        order_data = response.json()
        assert order_data["status"] == "pending"
        assert len(order_data["items"]) == 2
        assert order_data["remark"] == "请不要放辣"
        assert "order_no" in order_data
        order_id = order_data["id"]

        # Step 7: 验证订单金额
        expected_total = float(Decimal("35.00") * 2 + Decimal("18.00") * 3)
        assert float(order_data["total_price"]) == expected_total

        # Step 8: 用户查看自己的订单列表
        response = await client.get("/api/v1/orders/users/me", headers=user_headers)
        assert response.status_code == 200
        orders_list = response.json()
        assert orders_list["total"] >= 1

        # Step 9: 用户查看订单详情
        response = await client.get(f"/api/v1/orders/users/me/{order_id}", headers=user_headers)
        assert response.status_code == 200
        detail = response.json()
        assert detail["order_no"] == order_data["order_no"]

        # Step 10: 用户支付订单
        response = await client.post(f"/api/v1/orders/users/me/{order_id}/pay", headers=user_headers)
        assert response.status_code == 200
        pay_data = response.json()
        assert pay_data["status"] == "paid"

        # Step 11: 验证支付后状态
        response = await client.get(f"/api/v1/orders/users/me/{order_id}", headers=user_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "paid"

    async def test_order_stock_deduction_flow(self, client: AsyncClient, db_session: AsyncSession):
        """测试下单后库存扣减流程"""
        m_user = await _create_merchant_user(db_session, phone="13800080012")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        category = await _create_category(db_session, merchant=merchant, name="饮品")
        product = await _create_product(
            db_session, merchant=merchant, category=category,
            name="奶茶", price=Decimal("15.00"), stock=5,
        )

        user = await _create_user(db_session, username="stock_test_user", phone="13800080002")
        address = await _create_address(db_session, user=user, receiver="王五", is_default=True)
        user_headers = get_test_headers(user_id=user.id, username="stock_test_user", role="user", phone="13800080002")

        # Step 1: 下单购买 3 份
        response = await client.post("/api/v1/orders", headers=user_headers, json={
            "merchant_id": merchant.id,
            "address_id": address.id,
            "items": [{"product_id": product.id, "quantity": 3}],
        })
        assert response.status_code == 201

        # Step 2: 验证库存减少
        response = await client.get(f"/api/v1/products/{product.id}")
        assert response.status_code == 200
        assert response.json()["stock"] == 2

        # Step 3: 再尝试购买 3 份，应该失败（库存不足）
        response = await client.post("/api/v1/orders", headers=user_headers, json={
            "merchant_id": merchant.id,
            "address_id": address.id,
            "items": [{"product_id": product.id, "quantity": 3}],
        })
        assert response.status_code == 400

        # Step 4: 购买剩余的 2 份应该成功
        response = await client.post("/api/v1/orders", headers=user_headers, json={
            "merchant_id": merchant.id,
            "address_id": address.id,
            "items": [{"product_id": product.id, "quantity": 2}],
        })
        assert response.status_code == 201


class TestOrderProcessingFlow:
    """E2E 测试：订单处理流程

    测试场景：商家接单 → 制作 → 配送 → 完成
    """

    async def test_full_order_processing_flow(self, client: AsyncClient, db_session: AsyncSession):
        """测试从商家接单到完成的完整流程"""
        # 创建用户和商家
        user = await _create_user(db_session, username="process_user", phone="13800080003")
        m_user = await _create_merchant_user(db_session, phone="13800080013")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        category = await _create_category(db_session, merchant=merchant, name="套餐")
        product = await _create_product(
            db_session, merchant=merchant, category=category,
            name="超值套餐", price=Decimal("58.00"), stock=200,
        )
        address = await _create_address(db_session, user=user, receiver="赵六", is_default=True)

        user_headers = get_test_headers(user_id=user.id, username="process_user", role="user", phone="13800080003")
        merchant_headers = get_test_headers(
            user_id=m_user.id, username="process_merchant", role="merchant", phone="13800080013"
        )

        # Step 1: 用户创建订单
        response = await client.post("/api/v1/orders", headers=user_headers, json={
            "merchant_id": merchant.id,
            "address_id": address.id,
            "items": [{"product_id": product.id, "quantity": 1}],
        })
        assert response.status_code == 201
        order_id = response.json()["id"]

        # Step 2: 用户支付订单
        response = await client.post(f"/api/v1/orders/users/me/{order_id}/pay", headers=user_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "paid"

        # Step 3: 商家查看待处理订单
        response = await client.get("/api/v1/orders/merchant/me", headers=merchant_headers)
        assert response.status_code == 200
        orders = response.json()
        assert orders["total"] >= 1

        # Step 4: 商家开始制作
        response = await client.post(
            f"/api/v1/orders/merchant/me/{order_id}/prepare",
            headers=merchant_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "preparing"

        # Step 5: 商家开始配送
        response = await client.post(
            f"/api/v1/orders/merchant/me/{order_id}/deliver",
            headers=merchant_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "delivering"

        # Step 6: 商家完成订单
        response = await client.post(
            f"/api/v1/orders/merchant/me/{order_id}/complete",
            headers=merchant_headers,
        )
        assert response.status_code == 200
        complete_data = response.json()
        assert complete_data["status"] == "completed"

        # Step 7: 用户查看最终订单状态
        response = await client.get(f"/api/v1/orders/users/me/{order_id}", headers=user_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    async def test_order_cancel_flow(self, client: AsyncClient, db_session: AsyncSession):
        """测试订单取消流程"""
        user = await _create_user(db_session, username="cancel_user", phone="13800080004")
        m_user = await _create_merchant_user(db_session, phone="13800080014")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        category = await _create_category(db_session, merchant=merchant, name="小吃")
        product = await _create_product(
            db_session, merchant=merchant, category=category,
            name="鸡翅", price=Decimal("25.00"), stock=50,
        )
        address = await _create_address(db_session, user=user, receiver="孙七", is_default=True)
        user_headers = get_test_headers(user_id=user.id, username="cancel_user", role="user", phone="13800080004")

        # Step 1: 创建订单
        response = await client.post("/api/v1/orders", headers=user_headers, json={
            "merchant_id": merchant.id,
            "address_id": address.id,
            "items": [{"product_id": product.id, "quantity": 2}],
        })
        assert response.status_code == 201
        order_id = response.json()["id"]

        # Step 2: 用户取消订单
        response = await client.post(
            f"/api/v1/orders/users/me/{order_id}/cancel",
            headers=user_headers,
            json={"reason": "改变主意了"},
        )
        assert response.status_code == 200
        cancel_data = response.json()
        assert cancel_data["status"] == "cancelled"

        # Step 3: 验证取消后状态
        response = await client.get(f"/api/v1/orders/users/me/{order_id}", headers=user_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"

        # Step 4: 验证库存恢复
        response = await client.get(f"/api/v1/products/{product.id}")
        assert response.status_code == 200
        assert response.json()["stock"] == 50

    async def test_order_status_filter_flow(self, client: AsyncClient, db_session: AsyncSession):
        """测试用户按状态筛选订单"""
        user = await _create_user(db_session, username="filter_user", phone="13800080005")
        m_user = await _create_merchant_user(db_session, phone="13800080015")
        merchant = await _create_merchant(db_session, user=m_user, status="approved")
        address = await _create_address(db_session, user=user, receiver="周八", is_default=True)

        await _create_order(db_session, user=user, merchant=merchant, address=address, status="pending")
        await _create_order(db_session, user=user, merchant=merchant, address=address, status="paid")
        await _create_order(db_session, user=user, merchant=merchant, address=address, status="completed")
        await _create_order(db_session, user=user, merchant=merchant, address=address, status="pending")

        user_headers = get_test_headers(user_id=user.id, username="filter_user", role="user", phone="13800080005")

        # Step 1: 获取所有订单
        response = await client.get("/api/v1/orders/users/me", headers=user_headers)
        assert response.status_code == 200
        assert response.json()["total"] == 4

        # Step 2: 筛选 pending 状态
        response = await client.get("/api/v1/orders/users/me?status=pending", headers=user_headers)
        assert response.status_code == 200
        assert response.json()["total"] == 2

        # Step 3: 筛选 completed 状态
        response = await client.get("/api/v1/orders/users/me?status=completed", headers=user_headers)
        assert response.status_code == 200
        assert response.json()["total"] == 1
