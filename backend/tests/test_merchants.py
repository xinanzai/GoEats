import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import (
    _create_merchant_user, _create_merchant, _create_admin,
    get_merchant_headers, get_test_headers,
)


class TestMerchantList:
    """测试商家列表接口"""

    async def test_get_merchants_list_empty(self, client: AsyncClient):
        """测试获取空商家列表"""
        response = await client.get("/api/v1/merchants")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 0
        assert len(data["items"]) == 0

    async def test_get_merchants_list_approved_only(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家列表只显示已通过的商家"""
        user1 = await _create_merchant_user(db_session, username="merchant1", phone="13800030001")
        await _create_merchant(db_session, user=user1, business_name="通过的商家", status="approved")
        user2 = await _create_merchant_user(db_session, username="merchant2", phone="13800030002")
        await _create_merchant(db_session, user=user2, business_name="待审核商家", status="pending")
        user3 = await _create_merchant_user(db_session, username="merchant3", phone="13800030003")
        await _create_merchant(db_session, user=user3, business_name="拒绝的商家", status="rejected")

        response = await client.get("/api/v1/merchants")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["business_name"] == "通过的商家"

    async def test_get_merchants_list_with_search(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家列表搜索功能"""
        user1 = await _create_merchant_user(db_session, username="m1", phone="13800030004")
        await _create_merchant(db_session, user=user1, business_name="肯德基", status="approved")
        user2 = await _create_merchant_user(db_session, username="m2", phone="13800030005")
        await _create_merchant(db_session, user=user2, business_name="麦当劳", status="approved")
        user3 = await _create_merchant_user(db_session, username="m3", phone="13800030006")
        await _create_merchant(db_session, user=user3, business_name="汉堡王", status="approved")

        response = await client.get("/api/v1/merchants?search=肯")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["business_name"] == "肯德基"

    async def test_get_merchants_list_pagination(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家列表分页功能"""
        for i in range(5):
            user = await _create_merchant_user(db_session, username=f"page_m{i}", phone=f"138000310{i}")
            await _create_merchant(db_session, user=user, business_name=f"分页商家{i}", status="approved")

        response = await client.get("/api/v1/merchants?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["total_pages"] == 3


class TestMerchantDetail:
    """测试商家详情接口"""

    async def test_get_merchant_detail_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取商家详情成功"""
        user = await _create_merchant_user(db_session, username="detail_merchant", phone="13800030007")
        merchant = await _create_merchant(db_session, user=user, business_name="详情商家", status="approved")

        response = await client.get(f"/api/v1/merchants/{merchant.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["business_name"] == "详情商家"
        assert data["status"] == "approved"
        assert data["id"] == merchant.id

    async def test_get_merchant_detail_not_found(self, client: AsyncClient):
        """测试获取不存在的商家详情"""
        response = await client.get("/api/v1/merchants/99999")
        assert response.status_code == 404


class TestMyMerchant:
    """测试当前商家信息接口"""

    async def test_get_my_merchant_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家获取自己的信息成功"""
        user = await _create_merchant_user(db_session, username="my_merchant", phone="13800030008")
        merchant = await _create_merchant(db_session, user=user, business_name="我的商家", status="approved")
        headers = get_test_headers(user_id=user.id, username="my_merchant", role="merchant", phone="13800030008")

        response = await client.get("/api/v1/merchants/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["business_name"] == "我的商家"

    async def test_get_my_merchant_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家用户无商家信息时获取失败"""
        user = await _create_merchant_user(db_session, username="no_merchant", phone="13800030009")
        headers = get_test_headers(user_id=user.id, username="no_merchant", role="merchant", phone="13800030009")

        response = await client.get("/api/v1/merchants/me", headers=headers)
        assert response.status_code == 404

    async def test_get_my_merchant_non_merchant_user(self, client: AsyncClient, db_session: AsyncSession):
        """测试非商家角色访问商家信息失败"""
        from tests.conftest import _create_user
        user = await _create_user(db_session, username="regular_user", phone="13800030010", role="user")
        headers = get_test_headers(user_id=user.id, username="regular_user", role="user", phone="13800030010")

        response = await client.get("/api/v1/merchants/me", headers=headers)
        assert response.status_code == 403

    async def test_update_my_merchant_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家更新自己的信息成功"""
        user = await _create_merchant_user(db_session, username="update_merchant", phone="13800030011")
        merchant = await _create_merchant(db_session, user=user, business_name="原商家名", status="approved")
        headers = get_test_headers(user_id=user.id, username="update_merchant", role="merchant", phone="13800030011")

        response = await client.put("/api/v1/merchants/me", headers=headers, json={
            "business_name": "新商家名",
            "contact_phone": "13900000011",
            "address": "新地址",
            "description": "新的商家描述",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["business_name"] == "新商家名"
        assert data["contact_phone"] == "13900000011"
        assert data["address"] == "新地址"
        assert data["description"] == "新的商家描述"

    async def test_update_my_merchant_partial(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家部分更新信息"""
        user = await _create_merchant_user(db_session, username="partial_update", phone="13800030012")
        await _create_merchant(db_session, user=user, business_name="原商家名", status="approved")
        headers = get_test_headers(user_id=user.id, username="partial_update", role="merchant", phone="13800030012")

        response = await client.put("/api/v1/merchants/me", headers=headers, json={
            "description": "只更新描述",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "只更新描述"

    async def test_update_my_merchant_invalid_name(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家更新无效名称"""
        user = await _create_merchant_user(db_session, username="invalid_name", phone="13800030013")
        await _create_merchant(db_session, user=user, business_name="原商家名", status="approved")
        headers = get_test_headers(user_id=user.id, username="invalid_name", role="merchant", phone="13800030013")

        response = await client.put("/api/v1/merchants/me", headers=headers, json={
            "business_name": "a",
        })
        assert response.status_code == 422

    async def test_update_my_merchant_non_merchant_user(self, client: AsyncClient, db_session: AsyncSession):
        """测试非商家角色更新商家信息失败"""
        from tests.conftest import _create_user
        user = await _create_user(db_session, username="regular_updater", phone="13800030014", role="user")
        headers = get_test_headers(user_id=user.id, username="regular_updater", role="user", phone="13800030014")

        response = await client.put("/api/v1/merchants/me", headers=headers, json={
            "business_name": "尝试修改",
        })
        assert response.status_code == 403

    async def test_get_my_merchant_unauthorized(self, client: AsyncClient):
        """测试未授权访问当前商家信息"""
        response = await client.get("/api/v1/merchants/me")
        assert response.status_code == 403


class TestCategoryManagement:
    """测试商家分类管理"""

    async def test_get_categories_empty(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取空分类列表"""
        user = await _create_merchant_user(db_session, username="cat_merchant", phone="13800030015")
        await _create_merchant(db_session, user=user, business_name="分类商家", status="approved")
        headers = get_test_headers(user_id=user.id, username="cat_merchant", role="merchant", phone="13800030015")

        response = await client.get("/api/v1/merchants/me/categories", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    async def test_create_category_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试创建分类成功"""
        user = await _create_merchant_user(db_session, username="create_cat", phone="13800030016")
        await _create_merchant(db_session, user=user, business_name="创建分类商家", status="approved")
        headers = get_test_headers(user_id=user.id, username="create_cat", role="merchant", phone="13800030016")

        response = await client.post("/api/v1/merchants/me/categories", headers=headers, json={
            "name": "热销菜品",
            "sort_order": 1,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "热销菜品"
        assert data["sort_order"] == 1
        assert "id" in data

    async def test_get_categories_with_data(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取有数据的分类列表"""
        user = await _create_merchant_user(db_session, username="list_cat", phone="13800030017")
        merchant = await _create_merchant(db_session, user=user, business_name="列表分类商家", status="approved")
        headers = get_test_headers(user_id=user.id, username="list_cat", role="merchant", phone="13800030017")

        await client.post("/api/v1/merchants/me/categories", headers=headers, json={"name": "分类A"})
        await client.post("/api/v1/merchants/me/categories", headers=headers, json={"name": "分类B"})

        response = await client.get("/api/v1/merchants/me/categories", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_update_category_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试更新分类成功"""
        user = await _create_merchant_user(db_session, username="update_cat", phone="13800030018")
        await _create_merchant(db_session, user=user, business_name="更新分类商家", status="approved")
        headers = get_test_headers(user_id=user.id, username="update_cat", role="merchant", phone="13800030018")

        create_response = await client.post("/api/v1/merchants/me/categories", headers=headers, json={"name": "原分类"})
        category_id = create_response.json()["id"]

        response = await client.put(f"/api/v1/merchants/me/categories/{category_id}", headers=headers, json={
            "name": "新分类",
            "sort_order": 5,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "新分类"
        assert data["sort_order"] == 5

    async def test_delete_category_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试删除分类成功"""
        user = await _create_merchant_user(db_session, username="delete_cat", phone="13800030019")
        await _create_merchant(db_session, user=user, business_name="删除分类商家", status="approved")
        headers = get_test_headers(user_id=user.id, username="delete_cat", role="merchant", phone="13800030019")

        create_response = await client.post("/api/v1/merchants/me/categories", headers=headers, json={"name": "待删除"})
        category_id = create_response.json()["id"]

        response = await client.delete(f"/api/v1/merchants/me/categories/{category_id}", headers=headers)
        assert response.status_code == 204

    async def test_create_category_non_merchant_user(self, client: AsyncClient, db_session: AsyncSession):
        """测试非商家角色创建分类失败"""
        from tests.conftest import _create_user
        user = await _create_user(db_session, username="regular_cat", phone="13800030020", role="user")
        headers = get_test_headers(user_id=user.id, username="regular_cat", role="user", phone="13800030020")

        response = await client.post("/api/v1/merchants/me/categories", headers=headers, json={"name": "非法分类"})
        assert response.status_code == 403

    async def test_create_category_missing_name(self, client: AsyncClient, db_session: AsyncSession):
        """测试创建分类缺少名称"""
        user = await _create_merchant_user(db_session, username="missing_name", phone="13800030021")
        await _create_merchant(db_session, user=user, business_name="缺名称商家", status="approved")
        headers = get_test_headers(user_id=user.id, username="missing_name", role="merchant", phone="13800030021")

        response = await client.post("/api/v1/merchants/me/categories", headers=headers, json={})
        assert response.status_code == 422

    async def test_get_categories_unauthorized(self, client: AsyncClient):
        """测试未授权访问分类列表"""
        response = await client.get("/api/v1/merchants/me/categories")
        assert response.status_code == 403
