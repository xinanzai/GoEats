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


class TestUserRegisterFlow:
    """E2E 测试：用户注册完整流程

    测试场景：用户注册 → 登录 → 获取个人信息 → 修改个人信息
    """

    async def test_user_register_and_login_flow(self, client: AsyncClient):
        """测试用户注册并登录的完整流程"""
        register_data = {
            "username": "e2e_newuser",
            "phone": "13800070001",
            "password": "password123",
        }

        # Step 1: 用户注册
        response = await client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201
        reg_data = response.json()
        assert reg_data["username"] == "e2e_newuser"
        assert reg_data["phone"] == "13800070001"
        assert reg_data["role"] == "user"
        assert reg_data["is_active"] is True
        assert "id" in reg_data

        # Step 2: 使用注册的账号登录
        login_data = {
            "phone": "13800070001",
            "password": "password123",
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        login_resp = response.json()
        assert "access_token" in login_resp
        assert login_resp["token_type"] == "bearer"

        # Step 3: 使用 Token 获取个人信息
        headers = {"Authorization": f"Bearer {login_resp['access_token']}"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        me_data = response.json()
        assert me_data["username"] == "e2e_newuser"
        assert me_data["phone"] == "13800070001"

        # Step 4: 修改个人信息
        response = await client.put("/api/v1/users/profile", headers=headers, json={
            "username": "e2e_updated_user",
        })
        assert response.status_code == 200
        update_data = response.json()
        assert update_data["username"] == "e2e_updated_user"

        # Step 5: 验证修改后的信息
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["username"] == "e2e_updated_user"

    async def test_user_register_add_address_flow(self, client: AsyncClient):
        """测试用户注册后添加收货地址的流程"""
        register_data = {
            "username": "addr_user",
            "phone": "13800070002",
            "password": "password123",
        }

        # Step 1: 注册
        response = await client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201

        # Step 2: 登录获取 Token
        response = await client.post("/api/v1/auth/login", json={
            "phone": "13800070002",
            "password": "password123",
        })
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 3: 添加收货地址
        response = await client.post("/api/v1/users/addresses", headers=headers, json={
            "receiver": "张三",
            "phone": "13700000001",
            "province": "广东省",
            "city": "深圳市",
            "district": "南山区",
            "detail_address": "科技园123号",
            "is_default": True,
        })
        assert response.status_code == 201
        addr_data = response.json()
        assert addr_data["receiver"] == "张三"
        assert addr_data["is_default"] is True
        assert "id" in addr_data

        # Step 4: 获取地址列表
        response = await client.get("/api/v1/users/addresses", headers=headers)
        assert response.status_code == 200
        addr_list = response.json()
        assert len(addr_list) == 1
        assert addr_list[0]["receiver"] == "张三"


class TestMerchantRegisterFlow:
    """E2E 测试：商家注册审批流程

    测试场景：商家注册 → 管理员审核 → 商家登录 → 添加分类和商品
    """

    async def test_merchant_register_and_approval_flow(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家注册后经管理员审批的完整流程"""
        # Step 1: 创建管理员账号
        admin = await _create_user(
            db_session,
            username="e2e_admin",
            phone="13800070010",
            password="admin123",
            role="admin",
        )
        admin_headers = get_test_headers(
            user_id=admin.id,
            username="e2e_admin",
            role="admin",
            phone="13800070010",
        )

        # Step 2: 商家注册（状态为 pending）
        merchant_reg_data = {
            "username": "e2e_merchant_shop",
            "phone": "13800070003",
            "password": "merchant123",
            "business_name": "E2E 测试餐厅",
            "contact_phone": "13900070003",
            "address": "深圳市南山区测试路100号",
            "description": "这是一家E2E测试餐厅",
        }
        response = await client.post("/api/v1/auth/merchant/register", json=merchant_reg_data)
        assert response.status_code == 201
        reg_data = response.json()
        assert reg_data["user"]["username"] == "e2e_merchant_shop"
        assert reg_data["user"]["role"] == "merchant"
        assert reg_data["merchant"]["status"] == "pending"
        merchant_id = reg_data["merchant"]["id"]

        # Step 3: 管理员查看待审核商家列表
        response = await client.get("/api/v1/admin/merchants?status=pending", headers=admin_headers)
        assert response.status_code == 200
        pending_data = response.json()
        assert pending_data["total"] >= 1
        merchant_found = False
        for item in pending_data["items"]:
            if item["id"] == merchant_id:
                merchant_found = True
                assert item["business_name"] == "E2E 测试餐厅"
                assert item["status"] == "pending"
        assert merchant_found, "商家未在待审核列表中找到"

        # Step 4: 管理员审批通过
        response = await client.put(
            f"/api/v1/admin/merchants/{merchant_id}/approve",
            headers=admin_headers,
            json={"reason": "审核通过"},
        )
        assert response.status_code == 200
        approve_data = response.json()
        assert approve_data["status"] == "approved"

        # Step 5: 商家登录
        response = await client.post("/api/v1/auth/login", json={
            "phone": "13800070003",
            "password": "merchant123",
        })
        assert response.status_code == 200
        token = response.json()["access_token"]
        merchant_headers = {"Authorization": f"Bearer {token}"}

        # Step 6: 商家查看自己的信息
        response = await client.get("/api/v1/merchants/me", headers=merchant_headers)
        assert response.status_code == 200
        me_merchant = response.json()
        assert me_merchant["business_name"] == "E2E 测试餐厅"
        assert me_merchant["status"] == "approved"

        # Step 7: 商家添加分类
        response = await client.post("/api/v1/merchants/me/categories", headers=merchant_headers, json={
            "name": "特色菜",
            "sort_order": 1,
        })
        assert response.status_code == 201
        category_data = response.json()
        assert category_data["name"] == "特色菜"
        category_id = category_data["id"]

        # Step 8: 商家添加商品
        response = await client.post("/api/v1/products/merchant/me", headers=merchant_headers, json={
            "name": "宫保鸡丁",
            "description": "经典川菜",
            "price": 38.00,
            "category_id": category_id,
            "stock": 100,
            "is_available": True,
        })
        assert response.status_code == 201
        product_data = response.json()
        assert product_data["name"] == "宫保鸡丁"
        assert float(product_data["price"]) == 38.00

        # Step 9: 验证商品列表
        response = await client.get("/api/v1/products/merchant/me", headers=merchant_headers)
        assert response.status_code == 200
        products_resp = response.json()
        assert any(p["name"] == "宫保鸡丁" for p in products_resp["items"])

    async def test_merchant_register_rejection_flow(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家注册后被拒绝的流程"""
        # Step 1: 创建管理员
        admin = await _create_user(
            db_session,
            username="reject_admin",
            phone="13800070011",
            password="admin123",
            role="admin",
        )
        admin_headers = get_test_headers(
            user_id=admin.id,
            username="reject_admin",
            role="admin",
            phone="13800070011",
        )

        # Step 2: 商家注册
        response = await client.post("/api/v1/auth/merchant/register", json={
            "username": "rejected_shop",
            "phone": "13800070004",
            "password": "merchant123",
            "business_name": "被拒绝的餐厅",
            "contact_phone": "13900070004",
            "address": "测试地址",
        })
        assert response.status_code == 201
        merchant_id = response.json()["merchant"]["id"]

        # Step 3: 管理员拒绝
        response = await client.put(
            f"/api/v1/admin/merchants/{merchant_id}/reject",
            headers=admin_headers,
            json={"reason": "资料不完整"},
        )
        assert response.status_code == 200
        reject_data = response.json()
        assert reject_data["status"] == "rejected"
        assert reject_data["rejection_reason"] == "资料不完整"

        # Step 4: 验证商家状态为已拒绝
        response = await client.get(f"/api/v1/admin/merchants/{merchant_id}", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "rejected"
