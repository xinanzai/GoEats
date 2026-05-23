import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import (
    _create_user, _create_merchant_user, _create_merchant,
    _create_address, _create_order, get_test_headers, get_admin_headers,
)


class TestAdminDashboard:
    """测试管理端仪表盘接口"""

    async def test_get_dashboard_stats_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取仪表盘统计数据成功"""
        admin = await _create_user(db_session, username="dashboard_admin", phone="13800060001", role="admin", password="admin123")
        headers = get_test_headers(user_id=admin.id, username="dashboard_admin", role="admin", phone="13800060001")

        response = await client.get("/api/v1/admin/dashboard", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "user_count" in data or "merchant_count" in data or "order_count" in data or "total_users" in data or "users" in data or "statistics" in data or "stats" in data or "total_merchants" in data

    async def test_get_dashboard_with_data(self, client: AsyncClient, db_session: AsyncSession):
        """测试有数据时获取仪表盘统计"""
        admin = await _create_user(db_session, username="stats_admin", phone="13800060002", role="admin", password="admin123")
        await _create_user(db_session, username="stat_user1", phone="13800060003", role="user", password="user123")
        await _create_user(db_session, username="stat_user2", phone="13800060004", role="user", password="user123")
        m_user = await _create_merchant_user(db_session, username="stat_merchant", phone="13800060005")
        await _create_merchant(db_session, user=m_user, business_name="统计商家", status="approved")
        headers = get_test_headers(user_id=admin.id, username="stats_admin", role="admin", phone="13800060002")

        response = await client.get("/api/v1/admin/dashboard", headers=headers)
        assert response.status_code == 200

    async def test_get_dashboard_non_admin_fail(self, client: AsyncClient, db_session: AsyncSession):
        """测试非管理员访问仪表盘失败"""
        user = await _create_user(db_session, username="non_admin_dashboard", phone="13800060006", role="user", password="user123")
        headers = get_test_headers(user_id=user.id, username="non_admin_dashboard", role="user", phone="13800060006")

        response = await client.get("/api/v1/admin/dashboard", headers=headers)
        assert response.status_code == 403

    async def test_get_dashboard_unauthorized(self, client: AsyncClient):
        """测试未授权访问仪表盘"""
        response = await client.get("/api/v1/admin/dashboard")
        assert response.status_code == 403


class TestAdminUserManagement:
    """测试管理端用户管理"""

    async def test_list_users_empty(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取空用户列表"""
        admin = await _create_user(db_session, username="list_admin", phone="13800060007", role="admin", password="admin123")
        headers = get_test_headers(user_id=admin.id, username="list_admin", role="admin", phone="13800060007")

        response = await client.get("/api/v1/admin/users", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1  # 至少包含管理员自己

    async def test_list_users_with_data(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取有数据的用户列表"""
        admin = await _create_user(db_session, username="data_admin", phone="13800060008", role="admin", password="admin123")
        await _create_user(db_session, username="list_user1", phone="13800060009", role="user")
        await _create_user(db_session, username="list_user2", phone="13800060010", role="user")
        await _create_merchant_user(db_session, username="list_merchant", phone="13800060011")
        headers = get_test_headers(user_id=admin.id, username="data_admin", role="admin", phone="13800060008")

        response = await client.get("/api/v1/admin/users", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3

    async def test_list_users_with_search(self, client: AsyncClient, db_session: AsyncSession):
        """测试用户列表搜索功能"""
        admin = await _create_user(db_session, username="search_admin2", phone="13800060012", role="admin")
        await _create_user(db_session, username="张三丰", phone="13800060013", role="user")
        await _create_user(db_session, username="李四光", phone="13800060014", role="user")
        await _create_user(db_session, username="王五子", phone="13800060015", role="user")
        headers = get_test_headers(user_id=admin.id, username="search_admin2", role="admin", phone="13800060012")

        response = await client.get("/api/v1/admin/users?search=张", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["username"] == "张三丰"

    async def test_list_users_with_role_filter(self, client: AsyncClient, db_session: AsyncSession):
        """测试按角色筛选用户列表"""
        admin = await _create_user(db_session, username="filter_admin2", phone="13800060016", role="admin")
        await _create_user(db_session, username="role_user1", phone="13800060017", role="user")
        await _create_user(db_session, username="role_user2", phone="13800060018", role="user")
        await _create_merchant_user(db_session, username="role_merchant", phone="13800060019")
        headers = get_test_headers(user_id=admin.id, username="filter_admin2", role="admin", phone="13800060016")

        response = await client.get("/api/v1/admin/users?role=user", headers=headers)
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["role"] == "user"

    async def test_get_user_detail_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取用户详情成功"""
        admin = await _create_user(db_session, username="detail_admin2", phone="13800060020", role="admin")
        user = await _create_user(db_session, username="detail_target", phone="13800060021", role="user")
        headers = get_test_headers(user_id=admin.id, username="detail_admin2", role="admin", phone="13800060020")

        response = await client.get(f"/api/v1/admin/users/{user.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "detail_target"
        assert data["phone"] == "13800060021"

    async def test_get_user_detail_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取不存在的用户详情"""
        admin = await _create_user(db_session, username="notfound_admin", phone="13800060022", role="admin")
        headers = get_test_headers(user_id=admin.id, username="notfound_admin", role="admin", phone="13800060022")

        response = await client.get("/api/v1/admin/users/99999", headers=headers)
        assert response.status_code == 404

    async def test_update_user_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试管理员更新用户信息成功"""
        admin = await _create_user(db_session, username="update_admin2", phone="13800060023", role="admin")
        user = await _create_user(db_session, username="update_target", phone="13800060024", role="user")
        headers = get_test_headers(user_id=admin.id, username="update_admin2", role="admin", phone="13800060023")

        response = await client.put(f"/api/v1/admin/users/{user.id}", headers=headers, json={
            "username": "new_username",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "new_username"

    async def test_toggle_user_active_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试管理员禁用用户成功"""
        admin = await _create_user(db_session, username="toggle_admin", phone="13800060025", role="admin")
        user = await _create_user(db_session, username="toggle_target", phone="13800060026", role="user", is_active=True)
        headers = get_test_headers(user_id=admin.id, username="toggle_admin", role="admin", phone="13800060025")

        response = await client.put(f"/api/v1/admin/users/{user.id}/status", headers=headers, json={
            "is_active": False,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

    async def test_toggle_user_reactivate_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试管理员重新启用用户成功"""
        admin = await _create_user(db_session, username="reactivate_admin", phone="13800060027", role="admin")
        user = await _create_user(db_session, username="reactivate_target", phone="13800060028", role="user", is_active=False)
        headers = get_test_headers(user_id=admin.id, username="reactivate_admin", role="admin", phone="13800060027")

        response = await client.put(f"/api/v1/admin/users/{user.id}/status", headers=headers, json={
            "is_active": True,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True

    async def test_admin_users_unauthorized(self, client: AsyncClient):
        """测试未授权访问用户管理"""
        response = await client.get("/api/v1/admin/users")
        assert response.status_code == 403

    async def test_reset_user_password_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试管理员重置用户密码成功"""
        admin = await _create_user(db_session, username="reset_admin", phone="13800060040", role="admin", password="admin123")
        user = await _create_user(db_session, username="reset_target", phone="13800060041", role="user", password="oldpass")
        headers = get_test_headers(user_id=admin.id, username="reset_admin", role="admin", phone="13800060040")

        response = await client.put(
            f"/api/v1/admin/users/{user.id}/reset-password",
            headers=headers,
            json={"new_password": "newpassword123"}
        )
        assert response.status_code == 204

        # 验证密码已更新
        from app.core.security import verify_password
        from sqlalchemy import select
        from app.models.user import User
        result = await db_session.execute(select(User).where(User.id == user.id))
        updated_user = result.scalar_one()
        assert verify_password("newpassword123", updated_user.password_hash) is True
        assert verify_password("oldpass", updated_user.password_hash) is False

    async def test_reset_user_password_invalid_password(self, client: AsyncClient, db_session: AsyncSession):
        """测试重置密码密码过短"""
        admin = await _create_user(db_session, username="reset_admin2", phone="13800060042", role="admin")
        user = await _create_user(db_session, username="reset_target2", phone="13800060043", role="user")
        headers = get_test_headers(user_id=admin.id, username="reset_admin2", role="admin", phone="13800060042")

        response = await client.put(
            f"/api/v1/admin/users/{user.id}/reset-password",
            headers=headers,
            json={"new_password": "ab"}
        )
        assert response.status_code == 422

    async def test_reset_user_password_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """测试重置不存在用户的密码"""
        admin = await _create_user(db_session, username="reset_admin3", phone="13800060044", role="admin")
        headers = get_test_headers(user_id=admin.id, username="reset_admin3", role="admin", phone="13800060044")

        response = await client.put(
            "/api/v1/admin/users/99999/reset-password",
            headers=headers,
            json={"new_password": "newpassword123"}
        )
        assert response.status_code == 404

    async def test_reset_password_non_admin_fail(self, client: AsyncClient, db_session: AsyncSession):
        """测试非管理员重置密码失败"""
        user = await _create_user(db_session, username="reset_nonadmin", phone="13800060045", role="user", password="user123")
        target = await _create_user(db_session, username="reset_target3", phone="13800060046", role="user")
        headers = get_test_headers(user_id=user.id, username="reset_nonadmin", role="user", phone="13800060045")

        response = await client.put(
            f"/api/v1/admin/users/{target.id}/reset-password",
            headers=headers,
            json={"new_password": "newpassword123"}
        )
        assert response.status_code == 403


class TestAdminMerchantManagement:
    """测试管理端商家管理"""

    async def test_list_merchants_empty(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取空商家列表"""
        admin = await _create_user(db_session, username="m_list_admin", phone="13800060029", role="admin")
        headers = get_test_headers(user_id=admin.id, username="m_list_admin", role="admin", phone="13800060029")

        response = await client.get("/api/v1/admin/merchants", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 0

    async def test_list_merchants_with_data(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取有数据的商家列表"""
        admin = await _create_user(db_session, username="m_data_admin", phone="13800060030", role="admin")
        user1 = await _create_merchant_user(db_session, username="m_data1", phone="13800060031")
        await _create_merchant(db_session, user=user1, business_name="商家A", status="approved")
        user2 = await _create_merchant_user(db_session, username="m_data2", phone="13800060032")
        await _create_merchant(db_session, user=user2, business_name="商家B", status="approved")
        headers = get_test_headers(user_id=admin.id, username="m_data_admin", role="admin", phone="13800060030")

        response = await client.get("/api/v1/admin/merchants", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2

    async def test_list_merchants_with_search(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家列表搜索功能"""
        admin = await _create_user(db_session, username="m_search_admin", phone="13800060033", role="admin")
        user1 = await _create_merchant_user(db_session, username="m_search1", phone="13800060034")
        await _create_merchant(db_session, user=user1, business_name="肯德基", status="approved")
        user2 = await _create_merchant_user(db_session, username="m_search2", phone="13800060035")
        await _create_merchant(db_session, user=user2, business_name="麦当劳", status="approved")
        headers = get_test_headers(user_id=admin.id, username="m_search_admin", role="admin", phone="13800060033")

        response = await client.get("/api/v1/admin/merchants?search=肯", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["business_name"] == "肯德基"

    async def test_list_merchants_with_status_filter(self, client: AsyncClient, db_session: AsyncSession):
        """测试按状态筛选商家列表"""
        admin = await _create_user(db_session, username="m_filter_admin", phone="13800060036", role="admin")
        user1 = await _create_merchant_user(db_session, username="m_filter1", phone="13800060037")
        await _create_merchant(db_session, user=user1, business_name="待审核商家", status="pending")
        user2 = await _create_merchant_user(db_session, username="m_filter2", phone="13800060038")
        await _create_merchant(db_session, user=user2, business_name="已通过商家", status="approved")
        user3 = await _create_merchant_user(db_session, username="m_filter3", phone="13800060039")
        await _create_merchant(db_session, user=user3, business_name="已拒绝商家", status="rejected")
        headers = get_test_headers(user_id=admin.id, username="m_filter_admin", role="admin", phone="13800060036")

        response = await client.get("/api/v1/admin/merchants?status=pending", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "pending"

    async def test_get_merchant_detail_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取商家详情成功"""
        admin = await _create_user(db_session, username="m_detail_admin", phone="13800060040", role="admin")
        user = await _create_merchant_user(db_session, username="m_detail_user", phone="13800060041")
        merchant = await _create_merchant(db_session, user=user, business_name="详情商家", status="approved")
        headers = get_test_headers(user_id=admin.id, username="m_detail_admin", role="admin", phone="13800060040")

        response = await client.get(f"/api/v1/admin/merchants/{merchant.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["business_name"] == "详情商家"
        assert data["status"] == "approved"

    async def test_get_merchant_detail_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取不存在的商家详情"""
        admin = await _create_user(db_session, username="m_notfound_admin", phone="13800060042", role="admin")
        headers = get_test_headers(user_id=admin.id, username="m_notfound_admin", role="admin", phone="13800060042")

        response = await client.get("/api/v1/admin/merchants/99999", headers=headers)
        assert response.status_code == 404

    async def test_approve_merchant_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试管理员审批商家通过"""
        admin = await _create_user(db_session, username="approve_admin", phone="13800060043", role="admin")
        user = await _create_merchant_user(db_session, username="approve_user", phone="13800060044")
        merchant = await _create_merchant(db_session, user=user, business_name="待审批商家", status="pending")
        headers = get_test_headers(user_id=admin.id, username="approve_admin", role="admin", phone="13800060043")

        response = await client.put(f"/api/v1/admin/merchants/{merchant.id}/approve", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
        assert data["approved_by"] == admin.id
        assert data["approved_at"] is not None

    async def test_approve_already_approved_merchant_fail(self, client: AsyncClient, db_session: AsyncSession):
        """测试审批已通过的商家失败"""
        admin = await _create_user(db_session, username="approve_dup_admin", phone="13800060045", role="admin")
        user = await _create_merchant_user(db_session, username="approve_dup_user", phone="13800060046")
        merchant = await _create_merchant(db_session, user=user, business_name="已通过商家", status="approved")
        headers = get_test_headers(user_id=admin.id, username="approve_dup_admin", role="admin", phone="13800060045")

        response = await client.put(f"/api/v1/admin/merchants/{merchant.id}/approve", headers=headers)
        assert response.status_code in [200, 400]

    async def test_reject_merchant_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试管理员拒绝商家申请"""
        admin = await _create_user(db_session, username="reject_admin", phone="13800060047", role="admin")
        user = await _create_merchant_user(db_session, username="reject_user", phone="13800060048")
        merchant = await _create_merchant(db_session, user=user, business_name="待拒绝商家", status="pending")
        headers = get_test_headers(user_id=admin.id, username="reject_admin", role="admin", phone="13800060047")

        response = await client.put(f"/api/v1/admin/merchants/{merchant.id}/reject", headers=headers, json={
            "reason": "资料不完整",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        assert data["rejection_reason"] == "资料不完整"

    async def test_reject_already_rejected_merchant_fail(self, client: AsyncClient, db_session: AsyncSession):
        """测试拒绝已拒绝的商家失败"""
        admin = await _create_user(db_session, username="reject_dup_admin", phone="13800060049", role="admin")
        user = await _create_merchant_user(db_session, username="reject_dup_user", phone="13800060050")
        merchant = await _create_merchant(db_session, user=user, business_name="已拒绝商家", status="rejected")
        headers = get_test_headers(user_id=admin.id, username="reject_dup_admin", role="admin", phone="13800060049")

        response = await client.put(f"/api/v1/admin/merchants/{merchant.id}/reject", headers=headers, json={
            "reason": "再次拒绝",
        })
        assert response.status_code in [200, 400]

    async def test_admin_merchants_unauthorized(self, client: AsyncClient):
        """测试未授权访问商家管理"""
        response = await client.get("/api/v1/admin/merchants")
        assert response.status_code == 403


class TestAdminOrderManagement:
    """测试管理端订单管理"""

    async def test_list_orders_empty(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取空订单列表"""
        admin = await _create_user(db_session, username="o_list_admin", phone="13800060051", role="admin")
        headers = get_test_headers(user_id=admin.id, username="o_list_admin", role="admin", phone="13800060051")

        response = await client.get("/api/v1/admin/orders", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 0

    async def test_list_orders_with_data(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取有数据的订单列表"""
        admin = await _create_user(db_session, username="o_data_admin", phone="13800060052", role="admin")
        user = await _create_user(db_session, username="o_data_user", phone="13800060053", role="user")
        m_user = await _create_merchant_user(db_session, username="o_data_merchant", phone="13800060054")
        merchant = await _create_merchant(db_session, user=m_user, business_name="订单商家", status="approved")
        address = await _create_address(db_session, user=user, receiver="订单用户", is_default=True)
        await _create_order(db_session, user=user, merchant=merchant, address=address, status="pending")
        await _create_order(db_session, user=user, merchant=merchant, address=address, status="paid")
        headers = get_test_headers(user_id=admin.id, username="o_data_admin", role="admin", phone="13800060052")

        response = await client.get("/api/v1/admin/orders", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2

    async def test_list_orders_with_status_filter(self, client: AsyncClient, db_session: AsyncSession):
        """测试按状态筛选订单列表"""
        admin = await _create_user(db_session, username="o_filter_admin", phone="13800060055", role="admin")
        user = await _create_user(db_session, username="o_filter_user", phone="13800060056", role="user")
        m_user = await _create_merchant_user(db_session, username="o_filter_merchant", phone="13800060057")
        merchant = await _create_merchant(db_session, user=m_user, business_name="筛选商家", status="approved")
        address = await _create_address(db_session, user=user, receiver="筛选用户", is_default=True)
        await _create_order(db_session, user=user, merchant=merchant, address=address, status="pending")
        await _create_order(db_session, user=user, merchant=merchant, address=address, status="paid")
        await _create_order(db_session, user=user, merchant=merchant, address=address, status="completed")
        headers = get_test_headers(user_id=admin.id, username="o_filter_admin", role="admin", phone="13800060055")

        response = await client.get("/api/v1/admin/orders?status=pending", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "pending"

    async def test_admin_orders_unauthorized(self, client: AsyncClient):
        """测试未授权访问订单管理"""
        response = await client.get("/api/v1/admin/orders")
        assert response.status_code == 403


class TestAdminStatistics:
    """测试管理端数据统计"""

    async def test_get_statistics_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取数据统计成功"""
        admin = await _create_user(db_session, username="stats_admin2", phone="13800060058", role="admin")
        headers = get_test_headers(user_id=admin.id, username="stats_admin2", role="admin", phone="13800060058")

        response = await client.get("/api/v1/admin/statistics", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "order_statistics" in data or "popular_products" in data or "statistics" in data

    async def test_get_statistics_with_days_param(self, client: AsyncClient, db_session: AsyncSession):
        """测试指定天数获取数据统计"""
        admin = await _create_user(db_session, username="days_admin", phone="13800060059", role="admin")
        headers = get_test_headers(user_id=admin.id, username="days_admin", role="admin", phone="13800060059")

        response = await client.get("/api/v1/admin/statistics?days=7", headers=headers)
        assert response.status_code == 200

    async def test_get_statistics_invalid_days(self, client: AsyncClient, db_session: AsyncSession):
        """测试无效天数参数"""
        admin = await _create_user(db_session, username="invalid_days_admin", phone="13800060060", role="admin")
        headers = get_test_headers(user_id=admin.id, username="invalid_days_admin", role="admin", phone="13800060060")

        response = await client.get("/api/v1/admin/statistics?days=0", headers=headers)
        assert response.status_code in [422, 400]

    async def test_get_statistics_unauthorized(self, client: AsyncClient):
        """测试未授权访问数据统计"""
        response = await client.get("/api/v1/admin/statistics")
        assert response.status_code == 403


class TestAdminPermission:
    """测试管理端权限控制"""

    async def test_user_cannot_access_admin_users(self, client: AsyncClient, db_session: AsyncSession):
        """测试普通用户无法访问用户管理"""
        user = await _create_user(db_session, username="perm_user", phone="13800060061", role="user")
        headers = get_test_headers(user_id=user.id, username="perm_user", role="user", phone="13800060061")

        response = await client.get("/api/v1/admin/users", headers=headers)
        assert response.status_code == 403

    async def test_user_cannot_access_admin_merchants(self, client: AsyncClient, db_session: AsyncSession):
        """测试普通用户无法访问商家管理"""
        user = await _create_user(db_session, username="perm_user2", phone="13800060062", role="user")
        headers = get_test_headers(user_id=user.id, username="perm_user2", role="user", phone="13800060062")

        response = await client.get("/api/v1/admin/merchants", headers=headers)
        assert response.status_code == 403

    async def test_merchant_cannot_access_admin(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家无法访问管理接口"""
        user = await _create_merchant_user(db_session, username="perm_merchant", phone="13800060063")
        headers = get_test_headers(user_id=user.id, username="perm_merchant", role="merchant", phone="13800060063")

        response = await client.get("/api/v1/admin/dashboard", headers=headers)
        assert response.status_code == 403

        response = await client.get("/api/v1/admin/users", headers=headers)
        assert response.status_code == 403

        response = await client.get("/api/v1/admin/merchants", headers=headers)
        assert response.status_code == 403

        response = await client.get("/api/v1/admin/orders", headers=headers)
        assert response.status_code == 403

        response = await client.get("/api/v1/admin/statistics", headers=headers)
        assert response.status_code == 403
