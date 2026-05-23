import pytest
import pytest_asyncio
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.product_service import ProductService
from app.schemas.product import ProductCreate, ProductUpdate
from app.core.exceptions import NotFoundException, ValidationException, PermissionException
from tests.conftest import (
    _create_merchant_user,
    _create_merchant,
    _create_category,
    _create_product,
    _create_user,
    db_session,
)


@pytest.mark.asyncio
class TestProductCreate:
    """商品创建测试"""

    async def test_create_product_success(self, db_session: AsyncSession):
        """测试成功创建商品"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user)
        category = await _create_category(db_session, merchant=merchant)
        service = ProductService(db_session)
        product_data = ProductCreate(
            merchant_id=merchant.id,
            category_id=category.id,
            name="测试菜品",
            description="美味的菜品",
            price=Decimal("39.90"),
            stock=100,
            is_available=True,
        )
        product = await service.create(user.id, product_data)

        assert product.id is not None
        assert product.merchant_id == merchant.id
        assert product.category_id == category.id
        assert product.name == "测试菜品"
        assert product.description == "美味的菜品"
        assert product.price == Decimal("39.90")
        assert product.stock == 100
        assert product.is_available is True

    async def test_create_product_with_original_price(self, db_session: AsyncSession):
        """测试创建带原价的商品（折扣）"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user)
        category = await _create_category(db_session, merchant=merchant)
        service = ProductService(db_session)
        product_data = ProductCreate(
            merchant_id=merchant.id,
            category_id=category.id,
            name="打折菜品",
            price=Decimal("29.90"),
            original_price=Decimal("49.90"),
            stock=0,
        )
        product = await service.create(user.id, product_data)

        assert product.original_price == Decimal("49.90")
        assert product.stock == 0

    async def test_create_product_merchant_not_found(self, db_session: AsyncSession):
        """测试商家不存在时创建商品失败"""
        service = ProductService(db_session)
        product_data = ProductCreate(
            merchant_id=999,
            category_id=1,
            name="测试菜品",
            price=Decimal("29.90"),
        )

        with pytest.raises(NotFoundException) as exc_info:
            await service.create(99999, product_data)
        assert "商家" in str(exc_info.value.detail)

    async def test_create_product_category_not_found(self, db_session: AsyncSession):
        """测试分类不存在时创建商品失败"""
        user = await _create_merchant_user(db_session)
        await _create_merchant(db_session, user=user)
        service = ProductService(db_session)
        product_data = ProductCreate(
            merchant_id=1,
            category_id=99999,
            name="测试菜品",
            price=Decimal("29.90"),
        )

        with pytest.raises(PermissionException) as exc_info:
            await service.create(user.id, product_data)
        assert "分类不存在" in str(exc_info.value.detail)

    async def test_create_product_category_not_belong_to_merchant(self, db_session: AsyncSession):
        """测试分类不属于该商家时创建商品失败"""
        owner = await _create_merchant_user(db_session, username="owner", phone="13800003000")
        merchant = await _create_merchant(db_session, user=owner)
        category = await _create_category(db_session, merchant=merchant)

        other_user = await _create_merchant_user(db_session, username="other", phone="13800003001")
        await _create_merchant(db_session, user=other_user)
        service = ProductService(db_session)
        product_data = ProductCreate(
            merchant_id=merchant.id,
            category_id=category.id,
            name="测试菜品",
            price=Decimal("29.90"),
        )

        with pytest.raises(PermissionException) as exc_info:
            await service.create(other_user.id, product_data)
        assert "分类不存在或不属于" in str(exc_info.value.detail)


@pytest.mark.asyncio
class TestProductQuery:
    """商品查询测试"""

    async def test_get_by_id_success(self, db_session: AsyncSession):
        """测试根据ID获取商品成功"""
        product = await _create_product(db_session, name="查询测试商品")
        service = ProductService(db_session)
        result = await service.get_by_id(product.id)

        assert result.id == product.id
        assert result.name == "查询测试商品"

    async def test_get_by_id_not_found(self, db_session: AsyncSession):
        """测试根据ID获取不存在的商品"""
        service = ProductService(db_session)

        with pytest.raises(NotFoundException) as exc_info:
            await service.get_by_id(99999)
        assert "商品" in str(exc_info.value.detail)

    async def test_list_products_success(self, db_session: AsyncSession):
        """测试获取商品列表成功"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user)
        category = await _create_category(db_session, merchant=merchant)
        await _create_product(db_session, merchant=merchant, category=category, name="商品1")
        await _create_product(db_session, merchant=merchant, category=category, name="商品2")
        await _create_product(db_session, merchant=merchant, category=category, name="商品3")

        service = ProductService(db_session)
        products, total = await service.list_products(merchant_id=merchant.id)

        assert total == 3
        assert len(products) == 3

    async def test_list_products_pagination(self, db_session: AsyncSession):
        """测试商品列表分页"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user)
        category = await _create_category(db_session, merchant=merchant)
        for i in range(5):
            await _create_product(db_session, merchant=merchant, category=category, name=f"商品{i+1}")

        service = ProductService(db_session)
        products, total = await service.list_products(merchant_id=merchant.id, page=1, page_size=2)

        assert total == 5
        assert len(products) == 2

    async def test_list_products_search(self, db_session: AsyncSession):
        """测试商品列表搜索"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user)
        category = await _create_category(db_session, merchant=merchant)
        await _create_product(db_session, merchant=merchant, category=category, name="牛肉面")
        await _create_product(db_session, merchant=merchant, category=category, name="羊肉串")
        await _create_product(db_session, merchant=merchant, category=category, name="鱼香肉丝")

        service = ProductService(db_session)
        products, total = await service.list_products(merchant_id=merchant.id, search="牛肉")

        assert total == 1
        assert products[0].name == "牛肉面"

    async def test_list_products_available_only(self, db_session: AsyncSession):
        """测试只显示上架商品"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user)
        category = await _create_category(db_session, merchant=merchant)
        await _create_product(db_session, merchant=merchant, category=category, name="上架商品", is_available=True)
        await _create_product(db_session, merchant=merchant, category=category, name="下架商品", is_available=False)

        service = ProductService(db_session)
        products, total = await service.list_products(merchant_id=merchant.id, available_only=True)

        assert total == 1
        assert products[0].name == "上架商品"

    async def test_list_by_merchant_success(self, db_session: AsyncSession):
        """测试获取商家的商品列表"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user)
        category = await _create_category(db_session, merchant=merchant)
        await _create_product(db_session, merchant=merchant, category=category, name="商品A")
        await _create_product(db_session, merchant=merchant, category=category, name="商品B")

        service = ProductService(db_session)
        products, total = await service.list_by_merchant(user.id)

        assert total == 2
        assert len(products) == 2

    async def test_list_by_merchant_not_found(self, db_session: AsyncSession):
        """测试商家不存在时商品列表为空"""
        service = ProductService(db_session)
        products, total = await service.list_by_merchant(99999)

        assert total == 0
        assert len(products) == 0

    async def test_list_products_by_category(self, db_session: AsyncSession):
        """测试按分类筛选商品"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user)
        cat1 = await _create_category(db_session, merchant=merchant, name="主食")
        cat2 = await _create_category(db_session, merchant=merchant, name="饮料")
        await _create_product(db_session, merchant=merchant, category=cat1, name="米饭")
        await _create_product(db_session, merchant=merchant, category=cat1, name="面条")
        await _create_product(db_session, merchant=merchant, category=cat2, name="可乐")

        service = ProductService(db_session)
        products, total = await service.list_products(category_id=cat1.id)

        assert total == 2
        names = [p.name for p in products]
        assert "米饭" in names
        assert "面条" in names


@pytest.mark.asyncio
class TestProductUpdate:
    """商品更新测试"""

    async def test_update_product_success(self, db_session: AsyncSession):
        """测试成功更新商品信息"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user)
        category = await _create_category(db_session, merchant=merchant)
        product = await _create_product(db_session, merchant=merchant, category=category)
        service = ProductService(db_session)
        update_data = ProductUpdate(
            name="新商品名称",
            description="新的描述",
            price=Decimal("49.90"),
        )
        result = await service.update(product.id, user.id, update_data)

        assert result.name == "新商品名称"
        assert result.description == "新的描述"
        assert result.price == Decimal("49.90")

    async def test_update_product_stock(self, db_session: AsyncSession):
        """测试更新商品库存"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user)
        category = await _create_category(db_session, merchant=merchant)
        product = await _create_product(db_session, merchant=merchant, category=category, stock=100)
        service = ProductService(db_session)
        update_data = ProductUpdate(stock=200)
        result = await service.update(product.id, user.id, update_data)

        assert result.stock == 200

    async def test_update_product_not_found(self, db_session: AsyncSession):
        """测试更新不存在的商品"""
        user = await _create_merchant_user(db_session)
        service = ProductService(db_session)
        update_data = ProductUpdate(name="新名称")

        with pytest.raises(NotFoundException):
            await service.update(99999, user.id, update_data)

    async def test_update_product_permission_denied(self, db_session: AsyncSession):
        """测试无权限更新其他商家的商品"""
        owner = await _create_merchant_user(db_session, username="owner", phone="13800004000")
        merchant = await _create_merchant(db_session, user=owner)
        category = await _create_category(db_session, merchant=merchant)
        product = await _create_product(db_session, merchant=merchant, category=category)

        other_user = await _create_merchant_user(db_session, username="other", phone="13800004001")
        service = ProductService(db_session)
        update_data = ProductUpdate(name="篡改名称")

        with pytest.raises(PermissionException) as exc_info:
            await service.update(product.id, other_user.id, update_data)
        assert "没有权限" in str(exc_info.value.detail)

    async def test_update_product_partial(self, db_session: AsyncSession):
        """测试部分更新不影响其他字段"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user)
        category = await _create_category(db_session, merchant=merchant)
        product = await _create_product(
            db_session,
            merchant=merchant,
            category=category,
            name="原名称",
            price=Decimal("29.90"),
            stock=50,
        )
        service = ProductService(db_session)
        update_data = ProductUpdate(description="仅更新描述")
        result = await service.update(product.id, user.id, update_data)

        assert result.name == "原名称"
        assert result.price == Decimal("29.90")
        assert result.stock == 50
        assert result.description == "仅更新描述"

    async def test_update_product_image_url(self, db_session: AsyncSession):
        """测试更新商品图片URL"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user)
        category = await _create_category(db_session, merchant=merchant)
        product = await _create_product(db_session, merchant=merchant, category=category)
        service = ProductService(db_session)
        update_data = ProductUpdate(image_url="/images/new_image.jpg")
        result = await service.update(product.id, user.id, update_data)

        assert result.image_url == "/images/new_image.jpg"


@pytest.mark.asyncio
class TestProductDelete:
    """商品删除测试"""

    async def test_delete_product_success(self, db_session: AsyncSession):
        """测试成功删除商品"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user)
        category = await _create_category(db_session, merchant=merchant)
        product = await _create_product(db_session, merchant=merchant, category=category)
        service = ProductService(db_session)

        result = await service.delete(product.id, user.id)
        assert result is True

        with pytest.raises(NotFoundException):
            await service.get_by_id(product.id)

    async def test_delete_product_not_found(self, db_session: AsyncSession):
        """测试删除不存在的商品"""
        user = await _create_merchant_user(db_session)
        service = ProductService(db_session)

        with pytest.raises(NotFoundException):
            await service.delete(99999, user.id)

    async def test_delete_product_permission_denied(self, db_session: AsyncSession):
        """测试无权限删除其他商家的商品"""
        owner = await _create_merchant_user(db_session, username="owner", phone="13800005000")
        merchant = await _create_merchant(db_session, user=owner)
        category = await _create_category(db_session, merchant=merchant)
        product = await _create_product(db_session, merchant=merchant, category=category)

        other_user = await _create_merchant_user(db_session, username="other", phone="13800005001")
        service = ProductService(db_session)

        with pytest.raises(PermissionException) as exc_info:
            await service.delete(product.id, other_user.id)
        assert "没有权限" in str(exc_info.value.detail)


@pytest.mark.asyncio
class TestProductToggle:
    """商品上架/下架测试"""

    async def test_toggle_product_available_to_unavailable(self, db_session: AsyncSession):
        """测试将上架商品切换为下架"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user)
        category = await _create_category(db_session, merchant=merchant)
        product = await _create_product(db_session, merchant=merchant, category=category, is_available=True)
        service = ProductService(db_session)

        result = await service.toggle_available(product.id, user.id)
        assert result.is_available is False

    async def test_toggle_product_unavailable_to_available(self, db_session: AsyncSession):
        """测试将下架商品切换为上架"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user)
        category = await _create_category(db_session, merchant=merchant)
        product = await _create_product(db_session, merchant=merchant, category=category, is_available=False)
        service = ProductService(db_session)

        result = await service.toggle_available(product.id, user.id)
        assert result.is_available is True

    async def test_toggle_product_not_found(self, db_session: AsyncSession):
        """测试切换不存在的商品"""
        user = await _create_merchant_user(db_session)
        service = ProductService(db_session)

        with pytest.raises(NotFoundException):
            await service.toggle_available(99999, user.id)

    async def test_toggle_product_permission_denied(self, db_session: AsyncSession):
        """测试无权限切换其他商家的商品"""
        owner = await _create_merchant_user(db_session, username="owner", phone="13800006000")
        merchant = await _create_merchant(db_session, user=owner)
        category = await _create_category(db_session, merchant=merchant)
        product = await _create_product(db_session, merchant=merchant, category=category)

        other_user = await _create_merchant_user(db_session, username="other", phone="13800006001")
        service = ProductService(db_session)

        with pytest.raises(PermissionException) as exc_info:
            await service.toggle_available(product.id, other_user.id)
        assert "没有权限" in str(exc_info.value.detail)


@pytest.mark.asyncio
class TestProductStock:
    """商品库存管理测试"""

    async def test_decrease_stock_success(self, db_session: AsyncSession):
        """测试成功减少库存"""
        product = await _create_product(db_session, stock=100)
        service = ProductService(db_session)

        result = await service.decrease_stock(product.id, 30)
        assert result is True

        updated = await service.get_by_id(product.id)
        assert updated.stock == 70

    async def test_decrease_stock_unlimited(self, db_session: AsyncSession):
        """测试不限库存的商品扣减"""
        product = await _create_product(db_session, stock=0)
        service = ProductService(db_session)

        result = await service.decrease_stock(product.id, 50)
        assert result is True

        updated = await service.get_by_id(product.id)
        assert updated.stock == 0

    async def test_decrease_stock_insufficient(self, db_session: AsyncSession):
        """测试库存不足时减少库存失败"""
        product = await _create_product(db_session, stock=10)
        service = ProductService(db_session)

        with pytest.raises(ValidationException) as exc_info:
            await service.decrease_stock(product.id, 20)
        assert "库存不足" in str(exc_info.value.detail)

    async def test_decrease_stock_not_found(self, db_session: AsyncSession):
        """测试减少不存在商品的库存"""
        service = ProductService(db_session)

        with pytest.raises(NotFoundException):
            await service.decrease_stock(99999, 1)
