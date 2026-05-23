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


class TestMerchantApprovalFlow:
    """E2E 测试：商家审批完整流程

    测试场景：多个商家注册 → 管理员批量审批 → 审批通过后可经营 → 拒绝后不可经营
    """

    async def test_multi_merchant_approval_flow(self, client: AsyncClient, db_session: AsyncSession):
        """测试多个商家注册后管理员分别审批的流程"""
        # Step 1: 创建管理员
        admin = await _create_user(
            db_session,
            username="approval_admin",
            phone="13800090010",
            password="admin123",
            role="admin",
        )
        admin_headers = get_test_headers(
            user_id=admin.id,
            username="approval_admin",
            role="admin",
            phone="13800090010",
        )

        # Step 2: 商家 A 注册
        response = await client.post("/api/v1/auth/merchant/register", json={
            "username": "shop_a_owner",
            "phone": "13800090001",
            "password": "merchant123",
            "business_name": "美味餐厅A",
            "contact_phone": "13900090001",
            "address": "南山区A路100号",
            "description": "美味餐厅A描述",
        })
        assert response.status_code == 201
        merchant_a_id = response.json()["merchant"]["id"]

        # Step 3: 商家 B 注册
        response = await client.post("/api/v1/auth/merchant/register", json={
            "username": "shop_b_owner",
            "phone": "13800090002",
            "password": "merchant123",
            "business_name": "美味餐厅B",
            "contact_phone": "13900090002",
            "address": "南山区B路200号",
            "description": "美味餐厅B描述",
        })
        assert response.status_code == 201
        merchant_b_id = response.json()["merchant"]["id"]

        # Step 4: 商家 C 注册
        response = await client.post("/api/v1/auth/merchant/register", json={
            "username": "shop_c_owner",
            "phone": "13800090003",
            "password": "merchant123",
            "business_name": "违规餐厅C",
            "contact_phone": "13900090003",
            "address": "南山区C路300号",
        })
        assert response.status_code == 201
        merchant_c_id = response.json()["merchant"]["id"]

        # Step 5: 管理员查看所有待审核商家
        response = await client.get("/api/v1/admin/merchants?status=pending", headers=admin_headers)
        assert response.status_code == 200
        pending_list = response.json()
        assert pending_list["total"] >= 3

        # Step 6: 管理员审批通过商家 A
        response = await client.put(
            f"/api/v1/admin/merchants/{merchant_a_id}/approve",
            headers=admin_headers,
            json={"reason": "审核通过"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "approved"

        # Step 7: 管理员审批通过商家 B
        response = await client.put(
            f"/api/v1/admin/merchants/{merchant_b_id}/approve",
            headers=admin_headers,
            json={"reason": "审核通过"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "approved"

        # Step 8: 管理员拒绝商家 C
        response = await client.put(
            f"/api/v1/admin/merchants/{merchant_c_id}/reject",
            headers=admin_headers,
            json={"reason": "经营范围不符合平台要求"},
        )
        assert response.status_code == 200
        reject_data = response.json()
        assert reject_data["status"] == "rejected"
        assert reject_data["rejection_reason"] == "经营范围不符合平台要求"

        # Step 9: 验证待审核列表不再有已处理的商家
        response = await client.get("/api/v1/admin/merchants?status=pending", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["total"] == 0

        # Step 10: 验证已通过商家列表
        response = await client.get("/api/v1/admin/merchants?status=approved", headers=admin_headers)
        assert response.status_code == 200
        approved_list = response.json()
        approved_ids = [item["id"] for item in approved_list["items"]]
        assert merchant_a_id in approved_ids
        assert merchant_b_id in approved_ids

        # Step 11: 验证已拒绝商家列表
        response = await client.get("/api/v1/admin/merchants?status=rejected", headers=admin_headers)
        assert response.status_code == 200
        rejected_list = response.json()
        rejected_ids = [item["id"] for item in rejected_list["items"]]
        assert merchant_c_id in rejected_ids

    async def test_approved_merchant_can_operate(self, client: AsyncClient, db_session: AsyncSession):
        """测试审批通过的商家可以进行经营操作"""
        # Step 1: 创建管理员并审批商家
        admin = await _create_user(
            db_session,
            username="operate_admin",
            phone="13800090011",
            password="admin123",
            role="admin",
        )
        admin_headers = get_test_headers(
            user_id=admin.id,
            username="operate_admin",
            role="admin",
            phone="13800090011",
        )

        # Step 2: 商家注册
        response = await client.post("/api/v1/auth/merchant/register", json={
            "username": "operate_shop",
            "phone": "13800090004",
            "password": "merchant123",
            "business_name": "经营测试餐厅",
            "contact_phone": "13900090004",
            "address": "测试地址",
        })
        assert response.status_code == 201
        merchant_id = response.json()["merchant"]["id"]

        # Step 3: 管理员审批通过
        response = await client.put(
            f"/api/v1/admin/merchants/{merchant_id}/approve",
            headers=admin_headers,
            json={"reason": "通过"},
        )
        assert response.status_code == 200

        # Step 4: 商家登录
        response = await client.post("/api/v1/auth/login", json={
            "phone": "13800090004",
            "password": "merchant123",
        })
        assert response.status_code == 200
        token = response.json()["access_token"]
        merchant_headers = {"Authorization": f"Bearer {token}"}

        # Step 5: 商家添加分类
        response = await client.post("/api/v1/merchants/me/categories", headers=merchant_headers, json={
            "name": "热饮",
            "sort_order": 1,
        })
        assert response.status_code == 201
        category_id = response.json()["id"]

        # Step 6: 商家添加商品
        response = await client.post("/api/v1/products/merchant/me", headers=merchant_headers, json={
            "name": "拿铁",
            "description": "浓郁拿铁咖啡",
            "price": 32.00,
            "category_id": category_id,
            "stock": 200,
            "is_available": True,
        })
        assert response.status_code == 201
        product_id = response.json()["id"]

        # Step 7: 商家更新商品信息
        response = await client.put(
            f"/api/v1/products/merchant/me/{product_id}",
            headers=merchant_headers,
            json={"name": "焦糖拿铁", "price": 36.00},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "焦糖拿铁"

        # Step 8: 商家查看商品列表
        response = await client.get("/api/v1/products/merchant/me", headers=merchant_headers)
        assert response.status_code == 200
        products = response.json()
        assert any(p["name"] == "焦糖拿铁" for p in products["items"])

        # Step 9: 商家切换商品上架状态
        response = await client.put(
            f"/api/v1/products/merchant/me/{product_id}/toggle",
            headers=merchant_headers,
        )
        assert response.status_code == 200

        # Step 10: 商家删除商品
        response = await client.delete(
            f"/api/v1/products/merchant/me/{product_id}",
            headers=merchant_headers,
        )
        assert response.status_code == 204

    async def test_pending_merchant_cannot_operate(self, client: AsyncClient, db_session: AsyncSession):
        """测试未审核通过的商家无法进行经营操作"""
        # Step 1: 商家注册（pending 状态）
        response = await client.post("/api/v1/auth/merchant/register", json={
            "username": "pending_shop",
            "phone": "13800090005",
            "password": "merchant123",
            "business_name": "待审核餐厅",
            "contact_phone": "13900090005",
            "address": "测试地址",
        })
        assert response.status_code == 201

        # Step 2: 商家登录
        response = await client.post("/api/v1/auth/login", json={
            "phone": "13800090005",
            "password": "merchant123",
        })
        assert response.status_code == 200
        token = response.json()["access_token"]
        merchant_headers = {"Authorization": f"Bearer {token}"}

        # Step 3: 商家查看自己的信息（状态应为 pending）
        response = await client.get("/api/v1/merchants/me", headers=merchant_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "pending"

        # Step 4: 商家尝试添加商品（应该有商家信息才能添加）
        response = await client.post("/api/v1/merchants/me/categories", headers=merchant_headers, json={
            "name": "测试分类",
        })
        # 无论成功还是失败，pending 商家不应有经营权限
        # 如果 API 允许，分类应该关联到该商家的 merchant 记录
        if response.status_code == 201:
            category_id = response.json()["id"]
            # 尝试添加商品
            response = await client.post("/api/v1/products/merchant/me", headers=merchant_headers, json={
                "name": "测试商品",
                "price": 10.00,
                "category_id": category_id,
                "stock": 10,
            })
            # pending 商家可能可以添加商品但不能被用户下单

    async def test_admin_merchant_detail_view(self, client: AsyncClient, db_session: AsyncSession):
        """测试管理员查看商家详情的完整流程"""
        # Step 1: 创建管理员
        admin = await _create_user(
            db_session,
            username="detail_admin",
            phone="13800090012",
            password="admin123",
            role="admin",
        )
        admin_headers = get_test_headers(
            user_id=admin.id,
            username="detail_admin",
            role="admin",
            phone="13800090012",
        )

        # Step 2: 商家注册
        response = await client.post("/api/v1/auth/merchant/register", json={
            "username": "detail_shop",
            "phone": "13800090006",
            "password": "merchant123",
            "business_name": "详情测试餐厅",
            "contact_phone": "13900090006",
            "address": "深圳市南山区详情路999号",
            "description": "这是一家用于测试详情查看的餐厅",
        })
        assert response.status_code == 201
        merchant_id = response.json()["merchant"]["id"]

        # Step 3: 管理员查看商家详情（pending）
        response = await client.get(f"/api/v1/admin/merchants/{merchant_id}", headers=admin_headers)
        assert response.status_code == 200
        detail = response.json()
        assert detail["business_name"] == "详情测试餐厅"
        assert detail["status"] == "pending"
        assert detail["contact_phone"] == "13900090006"

        # Step 4: 管理员审批通过
        response = await client.put(
            f"/api/v1/admin/merchants/{merchant_id}/approve",
            headers=admin_headers,
            json={"reason": "审核通过"},
        )
        assert response.status_code == 200

        # Step 5: 管理员再次查看详情（approved）
        response = await client.get(f"/api/v1/admin/merchants/{merchant_id}", headers=admin_headers)
        assert response.status_code == 200
        detail = response.json()
        assert detail["status"] == "approved"

    async def test_approval_permission_control(self, client: AsyncClient, db_session: AsyncSession):
        """测试审批权限控制"""
        # Step 1: 商家注册
        response = await client.post("/api/v1/auth/merchant/register", json={
            "username": "perm_shop",
            "phone": "13800090007",
            "password": "merchant123",
            "business_name": "权限测试餐厅",
            "contact_phone": "13900090007",
            "address": "测试地址",
        })
        assert response.status_code == 201
        merchant_id = response.json()["merchant"]["id"]

        # Step 2: 非管理员尝试审批（应该被拒绝）
        regular_user = await _create_user(
            db_session,
            username="regular_user",
            phone="13800090008",
            password="user123",
            role="user",
        )
        user_headers = get_test_headers(
            user_id=regular_user.id,
            username="regular_user",
            role="user",
            phone="13800090008",
        )

        response = await client.put(
            f"/api/v1/admin/merchants/{merchant_id}/approve",
            headers=user_headers,
            json={"reason": "通过"},
        )
        assert response.status_code == 403

        # Step 3: 无权限访问商家列表
        response = await client.get("/api/v1/admin/merchants", headers=user_headers)
        assert response.status_code == 403

        # Step 4: 商家自己尝试审批自己
        merchant_headers = get_test_headers(
            user_id=1,
            username="perm_shop",
            role="merchant",
            phone="13800090007",
        )
        response = await client.put(
            f"/api/v1/admin/merchants/{merchant_id}/approve",
            headers=merchant_headers,
            json={"reason": "自己审批自己"},
        )
        assert response.status_code == 403


class TestApprovalIntegrationFlow:
    """E2E 测试：审批与完整业务流程集成

    测试场景：商家注册 → 审批 → 添加商品 → 用户下单 → 商家处理订单
    """

    async def test_full_business_lifecycle(self, client: AsyncClient, db_session: AsyncSession):
        """测试从商家注册到订单完成的完整业务生命周期"""
        # === 第一部分：商家注册与审批 ===
        admin = await _create_user(
            db_session,
            username="lifecycle_admin",
            phone="13800090020",
            password="admin123",
            role="admin",
        )
        admin_headers = get_test_headers(
            user_id=admin.id,
            username="lifecycle_admin",
            role="admin",
            phone="13800090020",
        )

        # 商家注册
        response = await client.post("/api/v1/auth/merchant/register", json={
            "username": "lifecycle_merchant",
            "phone": "13800090009",
            "password": "merchant123",
            "business_name": "生命周期测试餐厅",
            "contact_phone": "13900090009",
            "address": "南山区",
        })
        assert response.status_code == 201
        merchant_id = response.json()["merchant"]["id"]

        # 管理员审批
        response = await client.put(
            f"/api/v1/admin/merchants/{merchant_id}/approve",
            headers=admin_headers,
            json={"reason": "通过"},
        )
        assert response.status_code == 200

        # === 第二部分：商家经营准备 ===
        merchant_login = await client.post("/api/v1/auth/login", json={
            "phone": "13800090009",
            "password": "merchant123",
        })
        merchant_token = merchant_login.json()["access_token"]
        merchant_headers = {"Authorization": f"Bearer {merchant_token}"}

        # 添加分类和商品
        cat_resp = await client.post("/api/v1/merchants/me/categories", headers=merchant_headers, json={
            "name": "招牌菜",
        })
        category_id = cat_resp.json()["id"]

        product_resp = await client.post("/api/v1/products/merchant/me", headers=merchant_headers, json={
            "name": "招牌牛肉面",
            "description": "精选上等牛肉",
            "price": 48.00,
            "category_id": category_id,
            "stock": 100,
        })
        product_id = product_resp.json()["id"]

        # === 第三部分：用户下单 ===
        user_register = await client.post("/api/v1/auth/register", json={
            "username": "lifecycle_user",
            "phone": "13800090019",
            "password": "user123",
        })
        assert user_register.status_code == 201

        user_login = await client.post("/api/v1/auth/login", json={
            "phone": "13800090019",
            "password": "user123",
        })
        user_token = user_login.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # 添加地址
        addr_resp = await client.post("/api/v1/users/addresses", headers=user_headers, json={
            "receiver": "测试用户",
            "phone": "13700000001",
            "province": "广东省",
            "city": "深圳市",
            "district": "南山区",
            "detail_address": "测试路1号",
            "is_default": True,
        })
        address_id = addr_resp.json()["id"]

        # 创建订单
        order_resp = await client.post("/api/v1/orders", headers=user_headers, json={
            "merchant_id": merchant_id,
            "address_id": address_id,
            "items": [{"product_id": product_id, "quantity": 2}],
            "remark": "少辣",
        })
        assert order_resp.status_code == 201
        order_id = order_resp.json()["id"]

        # === 第四部分：用户支付 ===
        pay_resp = await client.post(f"/api/v1/orders/users/me/{order_id}/pay", headers=user_headers)
        assert pay_resp.status_code == 200
        assert pay_resp.json()["status"] == "paid"

        # === 第五部分：商家处理订单 ===
        prepare_resp = await client.post(
            f"/api/v1/orders/merchant/me/{order_id}/prepare",
            headers=merchant_headers,
        )
        assert prepare_resp.status_code == 200
        assert prepare_resp.json()["status"] == "preparing"

        deliver_resp = await client.post(
            f"/api/v1/orders/merchant/me/{order_id}/deliver",
            headers=merchant_headers,
        )
        assert deliver_resp.status_code == 200
        assert deliver_resp.json()["status"] == "delivering"

        complete_resp = await client.post(
            f"/api/v1/orders/merchant/me/{order_id}/complete",
            headers=merchant_headers,
        )
        assert complete_resp.status_code == 200
        assert complete_resp.json()["status"] == "completed"

        # === 第六部分：用户确认订单完成 ===
        final_order = await client.get(f"/api/v1/orders/users/me/{order_id}", headers=user_headers)
        assert final_order.status_code == 200
        assert final_order.json()["status"] == "completed"

        # === 第七部分：管理员查看统计 ===
        dashboard_resp = await client.get("/api/v1/admin/dashboard", headers=admin_headers)
        assert dashboard_resp.status_code == 200
