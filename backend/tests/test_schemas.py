import pytest
from pydantic import ValidationError
from decimal import Decimal
from datetime import datetime

from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse,
    LoginRequest, TokenResponse, ChangePasswordRequest,
    MerchantRegisterRequest,
)
from app.schemas.merchant import (
    MerchantCreate, MerchantUpdate, MerchantResponse,
)
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse,
)
from app.schemas.order import (
    OrderCreate, OrderItemCreate, OrderItemResponse, OrderResponse,
)
from app.schemas.address import (
    AddressCreate, AddressUpdate, AddressResponse,
)


class TestUserSchemaValidation:
    """用户 Schema 验证测试"""

    def test_user_create_valid(self):
        """测试有效的用户创建数据"""
        data = {
            "username": "testuser",
            "phone": "13800000001",
            "password": "password123",
        }
        user = UserCreate(**data)
        assert user.username == "testuser"
        assert user.phone == "13800000001"
        assert user.password == "password123"

    def test_user_create_missing_username(self):
        """测试缺少用户名校验失败"""
        data = {"phone": "13800000001", "password": "password123"}
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        assert "username" in str(exc_info.value).lower()

    def test_user_create_missing_phone(self):
        """测试缺少手机号校验失败"""
        data = {"username": "testuser", "password": "password123"}
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_user_create_missing_password(self):
        """测试缺少密码校验失败"""
        data = {"username": "testuser", "phone": "13800000001"}
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_user_create_username_too_short(self):
        """测试用户名字段最短长度校验"""
        data = {
            "username": "a",
            "phone": "13800000001",
            "password": "password123",
        }
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_user_create_username_max_length(self):
        """测试用户名字段最大长度"""
        data = {
            "username": "a" * 50,
            "phone": "13800000001",
            "password": "password123",
        }
        user = UserCreate(**data)
        assert len(user.username) == 50

    def test_user_create_username_too_long(self):
        """测试用户名字段超长校验"""
        data = {
            "username": "a" * 51,
            "phone": "13800000001",
            "password": "password123",
        }
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_user_create_invalid_phone_format(self):
        """测试无效手机号格式校验"""
        invalid_phones = [
            "12345678901",
            "23800000001",
            "1380000000",
            "abcdefghijk",
            "138-0000-0001",
            "",
        ]
        for phone in invalid_phones:
            data = {"username": "testuser", "phone": phone, "password": "password123"}
            with pytest.raises(ValidationError):
                UserCreate(**data)

    def test_user_create_valid_phone_formats(self):
        """测试有效手机号格式"""
        valid_phones = [
            "13800000001",
            "13912345678",
            "15812345678",
            "18612345678",
            "19912345678",
        ]
        for phone in valid_phones:
            data = {"username": "testuser", "phone": phone, "password": "password123"}
            user = UserCreate(**data)
            assert user.phone == phone

    def test_user_create_password_too_short(self):
        """测试密码长度过短校验"""
        data = {
            "username": "testuser",
            "phone": "13800000001",
            "password": "12345",
        }
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_user_create_password_min_length(self):
        """测试密码最小长度边界"""
        data = {
            "username": "testuser",
            "phone": "13800000001",
            "password": "123456",
        }
        user = UserCreate(**data)
        assert len(user.password) == 6

    def test_user_update_optional_fields(self):
        """测试用户更新所有字段可选"""
        update = UserUpdate()
        assert update.username is None
        assert update.phone is None
        assert update.avatar is None

    def test_user_update_partial(self):
        """测试用户更新部分字段"""
        update = UserUpdate(username="newname")
        assert update.username == "newname"
        assert update.phone is None

    def test_user_update_username_validation(self):
        """测试用户更新时用户名长度校验"""
        with pytest.raises(ValidationError):
            UserUpdate(username="a")

    def test_user_response_from_dict(self):
        """测试 UserResponse 从字典创建"""
        data = {
            "id": 1,
            "username": "testuser",
            "phone": "13800000001",
            "avatar": "/avatars/1.jpg",
            "role": "user",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        resp = UserResponse(**data)
        assert resp.id == 1
        assert resp.username == "testuser"
        assert resp.role == "user"
        assert resp.is_active is True

    def test_login_request_valid(self):
        """测试有效的登录请求"""
        req = LoginRequest(phone="13800000001", password="password123")
        assert req.phone == "13800000001"

    def test_login_request_invalid_phone(self):
        """测试登录请求手机号校验"""
        with pytest.raises(ValidationError):
            LoginRequest(phone="invalid", password="password123")

    def test_token_response(self):
        """测试 Token 响应"""
        resp = TokenResponse(access_token="test_token_abc123")
        assert resp.access_token == "test_token_abc123"
        assert resp.token_type == "bearer"

    def test_change_password_request_valid(self):
        """测试有效的修改密码请求"""
        req = ChangePasswordRequest(old_password="old123", new_password="new123456")
        assert req.old_password == "old123"
        assert req.new_password == "new123456"

    def test_change_password_new_too_short(self):
        """测试新密码过短校验"""
        with pytest.raises(ValidationError):
            ChangePasswordRequest(old_password="old123", new_password="12345")

    def test_merchant_register_request_valid(self):
        """测试有效的商家注册请求"""
        data = {
            "username": "merchant1",
            "phone": "13800000001",
            "password": "password123",
            "business_name": "美味餐厅",
            "contact_phone": "13900000001",
            "address": "北京市朝阳区xxx路123号",
            "description": "好吃的餐厅",
        }
        req = MerchantRegisterRequest(**data)
        assert req.username == "merchant1"
        assert req.business_name == "美味餐厅"

    def test_merchant_register_invalid_phone(self):
        """测试商家注册手机号校验"""
        data = {
            "username": "merchant1",
            "phone": "invalid_phone",
            "password": "password123",
            "business_name": "美味餐厅",
            "contact_phone": "13900000001",
            "address": "北京市朝阳区xxx路123号",
        }
        with pytest.raises(ValidationError):
            MerchantRegisterRequest(**data)


class TestMerchantSchemaValidation:
    """商家 Schema 验证测试"""

    def test_merchant_create_valid(self):
        """测试有效的商家创建数据"""
        data = {
            "business_name": "测试商家",
            "contact_phone": "13900000001",
            "address": "测试地址",
        }
        merchant = MerchantCreate(**data)
        assert merchant.business_name == "测试商家"
        assert merchant.description is None

    def test_merchant_create_with_description(self):
        """测试带描述的商家创建"""
        data = {
            "business_name": "测试商家",
            "contact_phone": "13900000001",
            "address": "测试地址",
            "description": "这是一家好店",
        }
        merchant = MerchantCreate(**data)
        assert merchant.description == "这是一家好店"

    def test_merchant_create_business_name_too_short(self):
        """测试商家名称过短校验"""
        data = {
            "business_name": "a",
            "contact_phone": "13900000001",
            "address": "测试地址",
        }
        with pytest.raises(ValidationError):
            MerchantCreate(**data)

    def test_merchant_create_missing_fields(self):
        """测试缺少必填字段"""
        data = {"business_name": "测试商家"}
        with pytest.raises(ValidationError):
            MerchantCreate(**data)

    def test_merchant_update_optional(self):
        """测试商家更新所有字段可选"""
        update = MerchantUpdate()
        assert update.business_name is None
        assert update.logo is None

    def test_merchant_update_partial(self):
        """测试商家部分更新"""
        update = MerchantUpdate(logo="/logos/1.jpg")
        assert update.logo == "/logos/1.jpg"
        assert update.business_name is None

    def test_merchant_response_valid(self):
        """测试商家响应"""
        data = {
            "id": 1,
            "user_id": 10,
            "business_name": "测试商家",
            "contact_phone": "13900000001",
            "address": "测试地址",
            "description": "描述",
            "logo": "/logos/1.jpg",
            "status": "approved",
            "rejection_reason": None,
            "approved_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        resp = MerchantResponse(**data)
        assert resp.id == 1
        assert resp.status == "approved"


class TestProductSchemaValidation:
    """商品 Schema 验证测试"""

    def test_product_create_valid(self):
        """测试有效的商品创建数据"""
        data = {
            "name": "红烧牛肉面",
            "price": Decimal("25.90"),
            "merchant_id": 1,
            "category_id": 1,
        }
        product = ProductCreate(**data)
        assert product.name == "红烧牛肉面"
        assert product.price == Decimal("25.90")
        assert product.stock == 0
        assert product.is_available is True

    def test_product_create_with_all_fields(self):
        """测试带所有字段的创建"""
        data = {
            "name": "麻辣香锅",
            "description": "好吃的香锅",
            "price": Decimal("39.90"),
            "original_price": Decimal("49.90"),
            "stock": 50,
            "is_available": False,
            "sort_order": 10,
            "merchant_id": 1,
            "category_id": 2,
        }
        product = ProductCreate(**data)
        assert product.original_price == Decimal("49.90")
        assert product.stock == 50
        assert product.is_available is False

    def test_product_create_empty_name(self):
        """测试商品名称不能为空"""
        data = {
            "name": "",
            "price": Decimal("10.00"),
            "merchant_id": 1,
            "category_id": 1,
        }
        with pytest.raises(ValidationError):
            ProductCreate(**data)

    def test_product_create_missing_required(self):
        """测试缺少必填字段"""
        data = {"name": "测试商品", "price": Decimal("10.00")}
        with pytest.raises(ValidationError):
            ProductCreate(**data)

    def test_product_update_optional(self):
        """测试商品更新所有字段可选"""
        update = ProductUpdate()
        assert update.name is None
        assert update.price is None

    def test_product_update_partial(self):
        """测试商品部分更新"""
        update = ProductUpdate(stock=100, is_available=True)
        assert update.stock == 100
        assert update.is_available is True

    def test_product_response_valid(self):
        """测试商品响应"""
        data = {
            "id": 1,
            "name": "测试商品",
            "description": "描述",
            "price": Decimal("29.90"),
            "original_price": None,
            "stock": 100,
            "is_available": True,
            "sort_order": 0,
            "merchant_id": 1,
            "category_id": 1,
            "image_url": "/images/1.jpg",
            "images": '["/images/1.jpg"]',
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        resp = ProductResponse(**data)
        assert resp.id == 1
        assert resp.price == Decimal("29.90")


class TestOrderSchemaValidation:
    """订单 Schema 验证测试"""

    def test_order_item_create_valid(self):
        """测试有效的订单项创建"""
        item = OrderItemCreate(product_id=1, quantity=2)
        assert item.product_id == 1
        assert item.quantity == 2

    def test_order_item_create_quantity_zero(self):
        """测试订单项数量必须大于0"""
        with pytest.raises(ValidationError):
            OrderItemCreate(product_id=1, quantity=0)

    def test_order_item_create_negative_quantity(self):
        """测试订单项数量不能为负数"""
        with pytest.raises(ValidationError):
            OrderItemCreate(product_id=1, quantity=-1)

    def test_order_create_valid(self):
        """测试有效的订单创建"""
        data = {
            "merchant_id": 1,
            "address_id": 1,
            "items": [
                {"product_id": 1, "quantity": 2},
                {"product_id": 2, "quantity": 1},
            ],
            "remark": "不要辣",
        }
        order = OrderCreate(**data)
        assert order.merchant_id == 1
        assert len(order.items) == 2
        assert order.remark == "不要辣"

    def test_order_create_min_items(self):
        """测试订单项列表至少需要一个项"""
        data = {
            "merchant_id": 1,
            "address_id": 1,
            "items": [{"product_id": 1, "quantity": 1}],
        }
        order = OrderCreate(**data)
        assert len(order.items) == 1

    def test_order_create_missing_fields(self):
        """测试缺少必填字段"""
        data = {"merchant_id": 1}
        with pytest.raises(ValidationError):
            OrderCreate(**data)

    def test_order_create_remark_max_length(self):
        """测试备注最大长度"""
        data = {
            "merchant_id": 1,
            "address_id": 1,
            "items": [{"product_id": 1, "quantity": 1}],
            "remark": "a" * 500,
        }
        order = OrderCreate(**data)
        assert len(order.remark) == 500

    def test_order_create_remark_too_long(self):
        """测试备注超长校验"""
        data = {
            "merchant_id": 1,
            "address_id": 1,
            "items": [{"product_id": 1, "quantity": 1}],
            "remark": "a" * 501,
        }
        with pytest.raises(ValidationError):
            OrderCreate(**data)

    def test_order_item_response_valid(self):
        """测试订单项响应"""
        data = {
            "id": 1,
            "product_id": 1,
            "product_name": "测试商品",
            "product_image": "/images/1.jpg",
            "price": Decimal("25.90"),
            "quantity": 2,
            "subtotal": Decimal("51.80"),
        }
        resp = OrderItemResponse(**data)
        assert resp.id == 1
        assert resp.subtotal == Decimal("51.80")

    def test_order_response_valid(self):
        """测试订单响应"""
        data = {
            "id": 1,
            "order_no": "ORD2026052300001",
            "user_id": 1,
            "merchant_id": 1,
            "address_id": 1,
            "receiver": "张三",
            "receiver_phone": "13800000001",
            "receiver_address": "北京市朝阳区xxx",
            "total_price": Decimal("99.90"),
            "discount_amount": Decimal("5.00"),
            "delivery_fee": Decimal("5.00"),
            "pay_amount": Decimal("99.90"),
            "status": "pending",
            "paid_at": None,
            "completed_at": None,
            "cancel_reason": None,
            "remark": "测试",
            "items": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        resp = OrderResponse(**data)
        assert resp.order_no == "ORD2026052300001"
        assert resp.status == "pending"
        assert resp.pay_amount == Decimal("99.90")


class TestAddressSchemaValidation:
    """地址 Schema 验证测试"""

    def test_address_create_valid(self):
        """测试有效的地址创建"""
        data = {
            "receiver": "张三",
            "phone": "13800000001",
            "province": "北京市",
            "city": "北京市",
            "district": "朝阳区",
            "detail_address": "建国路123号",
        }
        addr = AddressCreate(**data)
        assert addr.receiver == "张三"
        assert addr.is_default is False

    def test_address_create_with_default(self):
        """测试设置为默认地址"""
        data = {
            "receiver": "张三",
            "phone": "13800000001",
            "province": "北京市",
            "city": "北京市",
            "district": "朝阳区",
            "detail_address": "建国路123号",
            "is_default": True,
        }
        addr = AddressCreate(**data)
        assert addr.is_default is True

    def test_address_create_missing_fields(self):
        """测试缺少必填字段"""
        data = {"receiver": "张三", "phone": "13800000001"}
        with pytest.raises(ValidationError):
            AddressCreate(**data)

    def test_address_create_empty_receiver(self):
        """测试收货人不能为空"""
        data = {
            "receiver": "",
            "phone": "13800000001",
            "province": "北京市",
            "city": "北京市",
            "district": "朝阳区",
            "detail_address": "测试地址",
        }
        with pytest.raises(ValidationError):
            AddressCreate(**data)

    def test_address_create_receiver_max_length(self):
        """测试收货人最大长度"""
        data = {
            "receiver": "a" * 50,
            "phone": "13800000001",
            "province": "北京市",
            "city": "北京市",
            "district": "朝阳区",
            "detail_address": "测试地址",
        }
        addr = AddressCreate(**data)
        assert len(addr.receiver) == 50

    def test_address_create_receiver_too_long(self):
        """测试收货人超长校验"""
        data = {
            "receiver": "a" * 51,
            "phone": "13800000001",
            "province": "北京市",
            "city": "北京市",
            "district": "朝阳区",
            "detail_address": "测试地址",
        }
        with pytest.raises(ValidationError):
            AddressCreate(**data)

    def test_address_update_optional(self):
        """测试地址更新所有字段可选"""
        update = AddressUpdate()
        assert update.receiver is None
        assert update.is_default is None

    def test_address_update_partial(self):
        """测试地址部分更新"""
        update = AddressUpdate(is_default=True, detail_address="新地址")
        assert update.is_default is True
        assert update.detail_address == "新地址"

    def test_address_response_valid(self):
        """测试地址响应"""
        data = {
            "id": 1,
            "user_id": 1,
            "receiver": "张三",
            "phone": "13800000001",
            "province": "北京市",
            "city": "北京市",
            "district": "朝阳区",
            "detail_address": "建国路123号",
            "is_default": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        resp = AddressResponse(**data)
        assert resp.id == 1
        assert resp.is_default is True
        assert resp.receiver == "张三"
