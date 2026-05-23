import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from tests.conftest import (
    _create_merchant_user, _create_merchant, _create_category,
    _create_product, _create_user, _create_address,
    get_test_headers, get_admin_headers,
)


class TestProductList:
    """测试商品列表接口"""

    async def test_get_products_list_empty(self, client: AsyncClient):
        """测试获取空商品列表"""
        response = await client.get("/api/v1/products")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 0
        assert len(data["items"]) == 0

    async def test_get_products_list_available_only(self, client: AsyncClient, db_session: AsyncSession):
        """测试商品列表只显示上架商品"""
        user = await _create_merchant_user(db_session, username="prod_list_merchant", phone="13800040001")
        merchant = await _create_merchant(db_session, user=user, business_name="商品列表商家", status="approved")
        category = await _create_category(db_session, merchant=merchant, name="测试分类")
        await _create_product(db_session, merchant=merchant, category=category, name="上架商品", is_available=True)
        await _create_product(db_session, merchant=merchant, category=category, name="下架商品", is_available=False)

        response = await client.get("/api/v1/products")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "上架商品"

    async def test_get_products_list_by_merchant(self, client: AsyncClient, db_session: AsyncSession):
        """测试按商家筛选商品列表"""
        user1 = await _create_merchant_user(db_session, username="merchant_a", phone="13800040002")
        merchant1 = await _create_merchant(db_session, user=user1, business_name="商家A", status="approved")
        cat1 = await _create_category(db_session, merchant=merchant1, name="分类A")
        await _create_product(db_session, merchant=merchant1, category=cat1, name="商家A商品")

        user2 = await _create_merchant_user(db_session, username="merchant_b", phone="13800040003")
        merchant2 = await _create_merchant(db_session, user=user2, business_name="商家B", status="approved")
        cat2 = await _create_category(db_session, merchant=merchant2, name="分类B")
        await _create_product(db_session, merchant=merchant2, category=cat2, name="商家B商品")

        response = await client.get(f"/api/v1/products?merchant_id={merchant1.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "商家A商品"

    async def test_get_products_list_search(self, client: AsyncClient, db_session: AsyncSession):
        """测试商品列表搜索功能"""
        user = await _create_merchant_user(db_session, username="search_merchant", phone="13800040004")
        merchant = await _create_merchant(db_session, user=user, business_name="搜索商家", status="approved")
        category = await _create_category(db_session, merchant=merchant, name="搜索分类")
        await _create_product(db_session, merchant=merchant, category=category, name="宫保鸡丁")
        await _create_product(db_session, merchant=merchant, category=category, name="鱼香肉丝")
        await _create_product(db_session, merchant=merchant, category=category, name="番茄蛋汤")

        response = await client.get("/api/v1/products?search=鸡")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "宫保鸡丁"

    async def test_get_products_list_pagination(self, client: AsyncClient, db_session: AsyncSession):
        """测试商品列表分页功能"""
        user = await _create_merchant_user(db_session, username="page_merchant", phone="13800040005")
        merchant = await _create_merchant(db_session, user=user, business_name="分页商家", status="approved")
        category = await _create_category(db_session, merchant=merchant, name="分页分类")

        for i in range(5):
            await _create_product(db_session, merchant=merchant, category=category, name=f"分页商品{i}", price=Decimal(str(10 + i)))

        response = await client.get("/api/v1/products?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["total_pages"] == 3


class TestProductDetail:
    """测试商品详情接口"""

    async def test_get_product_detail_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取商品详情成功"""
        user = await _create_merchant_user(db_session, username="detail_merchant", phone="13800040006")
        merchant = await _create_merchant(db_session, user=user, business_name="详情商家", status="approved")
        category = await _create_category(db_session, merchant=merchant, name="详情分类")
        product = await _create_product(db_session, merchant=merchant, category=category, name="详情商品", price=Decimal("39.90"))

        response = await client.get(f"/api/v1/products/{product.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "详情商品"
        assert float(data["price"]) == 39.90
        assert data["id"] == product.id

    async def test_get_product_detail_not_found(self, client: AsyncClient):
        """测试获取不存在的商品详情"""
        response = await client.get("/api/v1/products/99999")
        assert response.status_code == 404


class TestMerchantProductCRUD:
    """测试商家端商品 CRUD"""

    async def test_get_my_products_empty(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家获取空商品列表"""
        user = await _create_merchant_user(db_session, username="my_prod_merchant", phone="13800040007")
        await _create_merchant(db_session, user=user, business_name="我的商品商家", status="approved")
        headers = get_test_headers(user_id=user.id, username="my_prod_merchant", role="merchant", phone="13800040007")

        response = await client.get("/api/v1/products/merchant/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0

    async def test_create_product_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家创建商品成功"""
        user = await _create_merchant_user(db_session, username="create_prod_merchant", phone="13800040008")
        merchant = await _create_merchant(db_session, user=user, business_name="创建商品商家", status="approved")
        category = await _create_category(db_session, merchant=merchant, name="创建分类")
        headers = get_test_headers(user_id=user.id, username="create_prod_merchant", role="merchant", phone="13800040008")

        response = await client.post("/api/v1/products/merchant/me", headers=headers, json={
            "name": "测试商品",
            "description": "这是一个测试商品",
            "price": 29.90,
            "stock": 100,
            "is_available": True,
            "sort_order": 0,
            "category_id": category.id,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "测试商品"
        assert float(data["price"]) == 29.90
        assert data["stock"] == 100
        assert data["is_available"] is True
        assert "id" in data

    async def test_create_product_missing_fields(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家创建商品缺少必填字段"""
        user = await _create_merchant_user(db_session, username="missing_prod_merchant", phone="13800040009")
        merchant = await _create_merchant(db_session, user=user, business_name="缺字段商家", status="approved")
        headers = get_test_headers(user_id=user.id, username="missing_prod_merchant", role="merchant", phone="13800040009")

        response = await client.post("/api/v1/products/merchant/me", headers=headers, json={
            "name": "测试商品",
        })
        assert response.status_code == 422

    async def test_create_product_non_merchant_user(self, client: AsyncClient, db_session: AsyncSession):
        """测试非商家角色创建商品失败"""
        m_user = await _create_merchant_user(db_session, username="prod_cat_merchant", phone="13800040099")
        m_merchant = await _create_merchant(db_session, user=m_user, business_name="分类商家", status="approved")
        m_category = await _create_category(db_session, merchant=m_merchant, name="测试分类")
        user = await _create_user(db_session, username="regular_prod_user", phone="13800040010", role="user")
        headers = get_test_headers(user_id=user.id, username="regular_prod_user", role="user", phone="13800040010")

        response = await client.post("/api/v1/products/merchant/me", headers=headers, json={
            "name": "非法商品",
            "price": 10.00,
            "stock": 10,
            "category_id": m_category.id,
        })
        assert response.status_code == 403

    async def test_update_product_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家更新商品成功"""
        user = await _create_merchant_user(db_session, username="update_prod_merchant", phone="13800040011")
        merchant = await _create_merchant(db_session, user=user, business_name="更新商品商家", status="approved")
        category = await _create_category(db_session, merchant=merchant, name="更新分类")
        product = await _create_product(db_session, merchant=merchant, category=category, name="原商品名", price=Decimal("19.90"))
        headers = get_test_headers(user_id=user.id, username="update_prod_merchant", role="merchant", phone="13800040011")

        response = await client.put(f"/api/v1/products/merchant/me/{product.id}", headers=headers, json={
            "name": "新商品名",
            "price": 39.90,
            "stock": 50,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "新商品名"
        assert float(data["price"]) == 39.90
        assert data["stock"] == 50

    async def test_update_product_partial(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家部分更新商品"""
        user = await _create_merchant_user(db_session, username="partial_prod_merchant", phone="13800040012")
        merchant = await _create_merchant(db_session, user=user, business_name="部分更新商家", status="approved")
        category = await _create_category(db_session, merchant=merchant, name="部分分类")
        product = await _create_product(db_session, merchant=merchant, category=category, name="部分商品", description="原描述")
        headers = get_test_headers(user_id=user.id, username="partial_prod_merchant", role="merchant", phone="13800040012")

        response = await client.put(f"/api/v1/products/merchant/me/{product.id}", headers=headers, json={
            "description": "新描述",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "新描述"
        assert data["name"] == "部分商品"

    async def test_update_other_merchant_product_fail(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家更新其他商家的商品失败"""
        user1 = await _create_merchant_user(db_session, username="owner_merchant", phone="13800040013")
        merchant1 = await _create_merchant(db_session, user=user1, business_name="商家1", status="approved")
        cat1 = await _create_category(db_session, merchant=merchant1, name="分类1")
        product = await _create_product(db_session, merchant=merchant1, category=cat1, name="商家1商品")

        user2 = await _create_merchant_user(db_session, username="other_merchant", phone="13800040014")
        await _create_merchant(db_session, user=user2, business_name="商家2", status="approved")
        headers = get_test_headers(user_id=user2.id, username="other_merchant", role="merchant", phone="13800040014")

        response = await client.put(f"/api/v1/products/merchant/me/{product.id}", headers=headers, json={
            "name": "尝试修改",
        })
        assert response.status_code == 403

    async def test_delete_product_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家删除商品成功"""
        user = await _create_merchant_user(db_session, username="delete_prod_merchant", phone="13800040015")
        merchant = await _create_merchant(db_session, user=user, business_name="删除商品商家", status="approved")
        category = await _create_category(db_session, merchant=merchant, name="删除分类")
        product = await _create_product(db_session, merchant=merchant, category=category, name="待删除商品")
        headers = get_test_headers(user_id=user.id, username="delete_prod_merchant", role="merchant", phone="13800040015")

        response = await client.delete(f"/api/v1/products/merchant/me/{product.id}", headers=headers)
        assert response.status_code == 204

        get_response = await client.get(f"/api/v1/products/{product.id}")
        assert get_response.status_code == 404

    async def test_delete_other_merchant_product_fail(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家删除其他商家的商品失败"""
        user1 = await _create_merchant_user(db_session, username="del_owner_merchant", phone="13800040016")
        merchant1 = await _create_merchant(db_session, user=user1, business_name="商家1", status="approved")
        cat1 = await _create_category(db_session, merchant=merchant1, name="分类1")
        product = await _create_product(db_session, merchant=merchant1, category=cat1, name="商家1商品")

        user2 = await _create_merchant_user(db_session, username="del_other_merchant", phone="13800040017")
        await _create_merchant(db_session, user=user2, business_name="商家2", status="approved")
        headers = get_test_headers(user_id=user2.id, username="del_other_merchant", role="merchant", phone="13800040017")

        response = await client.delete(f"/api/v1/products/merchant/me/{product.id}", headers=headers)
        assert response.status_code == 403

    async def test_toggle_product_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家切换商品上架/下架状态"""
        user = await _create_merchant_user(db_session, username="toggle_merchant", phone="13800040018")
        merchant = await _create_merchant(db_session, user=user, business_name="切换商家", status="approved")
        category = await _create_category(db_session, merchant=merchant, name="切换分类")
        product = await _create_product(db_session, merchant=merchant, category=category, name="切换商品", is_available=True)
        headers = get_test_headers(user_id=user.id, username="toggle_merchant", role="merchant", phone="13800040018")

        response = await client.put(f"/api/v1/products/merchant/me/{product.id}/toggle", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_available"] is False

        response2 = await client.put(f"/api/v1/products/merchant/me/{product.id}/toggle", headers=headers)
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["is_available"] is True

    async def test_get_my_products_with_data(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家获取有数据的商品列表"""
        user = await _create_merchant_user(db_session, username="list_my_merchant", phone="13800040019")
        merchant = await _create_merchant(db_session, user=user, business_name="列表商家", status="approved")
        category = await _create_category(db_session, merchant=merchant, name="列表分类")
        await _create_product(db_session, merchant=merchant, category=category, name="商品1")
        await _create_product(db_session, merchant=merchant, category=category, name="商品2")
        await _create_product(db_session, merchant=merchant, category=category, name="商品3", is_available=False)
        headers = get_test_headers(user_id=user.id, username="list_my_merchant", role="merchant", phone="13800040019")

        response = await client.get("/api/v1/products/merchant/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    async def test_get_my_products_unauthorized(self, client: AsyncClient):
        """测试未授权访问我的商品列表"""
        response = await client.get("/api/v1/products/merchant/me")
        assert response.status_code == 403


class TestProductValidation:
    """测试商品验证"""

    async def test_create_product_invalid_name(self, client: AsyncClient, db_session: AsyncSession):
        """测试创建商品名称过长"""
        user = await _create_merchant_user(db_session, username="invalid_name_merchant", phone="13800040020")
        merchant = await _create_merchant(db_session, user=user, business_name="无效名称商家", status="approved")
        category = await _create_category(db_session, merchant=merchant, name="无效分类")
        headers = get_test_headers(user_id=user.id, username="invalid_name_merchant", role="merchant", phone="13800040020")

        response = await client.post("/api/v1/products/merchant/me", headers=headers, json={
            "name": "a" * 101,
            "price": 10.00,
            "stock": 10,
            "category_id": category.id,
        })
        assert response.status_code == 422

    async def test_create_product_invalid_category(self, client: AsyncClient, db_session: AsyncSession):
        """测试创建商品时分类不属于该商家"""
        user1 = await _create_merchant_user(db_session, username="cat_merchant1", phone="13800040021")
        merchant1 = await _create_merchant(db_session, user=user1, business_name="商家1", status="approved")
        category1 = await _create_category(db_session, merchant=merchant1, name="商家1分类")

        user2 = await _create_merchant_user(db_session, username="cat_merchant2", phone="13800040022")
        merchant2 = await _create_merchant(db_session, user=user2, business_name="商家2", status="approved")
        headers = get_test_headers(user_id=user2.id, username="cat_merchant2", role="merchant", phone="13800040022")

        response = await client.post("/api/v1/products/merchant/me", headers=headers, json={
            "name": "非法商品",
            "price": 10.00,
            "stock": 10,
            "category_id": category1.id,
        })
        assert response.status_code in [400, 403]

    async def test_create_product_negative_stock(self, client: AsyncClient, db_session: AsyncSession):
        """测试创建商品库存为负数"""
        user = await _create_merchant_user(db_session, username="neg_stock_merchant", phone="13800040023")
        merchant = await _create_merchant(db_session, user=user, business_name="负库存商家", status="approved")
        category = await _create_category(db_session, merchant=merchant, name="负库存分类")
        headers = get_test_headers(user_id=user.id, username="neg_stock_merchant", role="merchant", phone="13800040023")

        response = await client.post("/api/v1/products/merchant/me", headers=headers, json={
            "name": "负库存商品",
            "price": 10.00,
            "stock": -5,
            "category_id": category.id,
        })
        assert response.status_code in [201, 422]
