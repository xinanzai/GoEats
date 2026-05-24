import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import (
    _create_user, _create_merchant_user, _create_merchant,
    generate_test_token, get_test_headers,
)


class TestRegister:
    """测试用户注册流程"""

    async def test_register_success(self, client: AsyncClient):
        """测试用户注册成功"""
        response = await client.post("/api/v1/auth/register", json={
            "username": "newuser",
            "phone": "13800001111",
            "password": "password123",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["phone"] == "13800001111"
        assert data["role"] == "user"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_register_duplicate_phone(self, client: AsyncClient, db_session: AsyncSession):
        """测试手机号重复时注册失败"""
        await _create_user(db_session, phone="13800002222", username="existing")
        response = await client.post("/api/v1/auth/register", json={
            "username": "newuser2",
            "phone": "13800002222",
            "password": "password123",
        })
        assert response.status_code == 409

    async def test_register_duplicate_username(self, client: AsyncClient, db_session: AsyncSession):
        """测试用户名重复时注册失败"""
        await _create_user(db_session, username="duplicate_user", phone="13800003333")
        response = await client.post("/api/v1/auth/register", json={
            "username": "duplicate_user",
            "phone": "13800004444",
            "password": "password123",
        })
        assert response.status_code == 409

    async def test_register_invalid_phone(self, client: AsyncClient):
        """测试无效手机号格式注册失败"""
        response = await client.post("/api/v1/auth/register", json={
            "username": "testuser",
            "phone": "123456",
            "password": "password123",
        })
        assert response.status_code == 422

    async def test_register_weak_password(self, client: AsyncClient):
        """测试密码过短注册失败"""
        response = await client.post("/api/v1/auth/register", json={
            "username": "testuser",
            "phone": "13800005555",
            "password": "12345",
        })
        assert response.status_code == 422

    async def test_register_missing_fields(self, client: AsyncClient):
        """测试缺少必填字段注册失败"""
        response = await client.post("/api/v1/auth/register", json={
            "username": "testuser",
        })
        assert response.status_code == 422


class TestLogin:
    """测试用户登录流程"""

    async def test_login_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试登录成功"""
        await _create_user(db_session, phone="13800006666", password="mypassword123")
        response = await client.post("/api/v1/auth/login", json={
            "phone": "13800006666",
            "password": "mypassword123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient, db_session: AsyncSession):
        """测试密码错误登录失败"""
        await _create_user(db_session, phone="13800007777", password="correct_password")
        response = await client.post("/api/v1/auth/login", json={
            "phone": "13800007777",
            "password": "wrong_password",
        })
        assert response.status_code == 400

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """测试不存在的手机号登录失败"""
        response = await client.post("/api/v1/auth/login", json={
            "phone": "13800008888",
            "password": "password123",
        })
        assert response.status_code == 404

    async def test_login_by_username(self, client: AsyncClient, db_session: AsyncSession):
        """测试使用用户名登录成功"""
        await _create_user(db_session, phone="13800006667", username="usernamelogin", password="mypassword123")
        response = await client.post("/api/v1/auth/login", json={
            "phone": "usernamelogin",
            "password": "mypassword123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_account_format(self, client: AsyncClient):
        """测试无效账号格式登录失败（既不是合法手机号也不是合法用户名长度）"""
        # 空字符串无法通过校验
        response = await client.post("/api/v1/auth/login", json={
            "phone": "",
            "password": "password123",
        })
        assert response.status_code == 422

    async def test_login_inactive_user(self, client: AsyncClient, db_session: AsyncSession):
        """测试被禁用的用户登录失败"""
        await _create_user(db_session, phone="13800009999", password="password123", is_active=False)
        response = await client.post("/api/v1/auth/login", json={
            "phone": "13800009999",
            "password": "password123",
        })
        assert response.status_code == 400


class TestMerchantRegister:
    """测试商家注册流程"""

    async def test_merchant_register_success(self, client: AsyncClient):
        """测试商家注册成功"""
        response = await client.post("/api/v1/auth/merchant/register", json={
            "username": "merchant_test",
            "phone": "13800001010",
            "password": "merchant123",
            "business_name": "测试餐厅",
            "contact_phone": "13900001010",
            "address": "测试地址123号",
            "description": "这是一家测试餐厅",
        })
        assert response.status_code == 201
        data = response.json()
        assert "user" in data
        assert "merchant" in data
        assert data["user"]["username"] == "merchant_test"
        assert data["user"]["role"] == "merchant"
        assert data["merchant"]["business_name"] == "测试餐厅"
        assert data["merchant"]["status"] == "pending"

    async def test_merchant_register_duplicate_phone(self, client: AsyncClient, db_session: AsyncSession):
        """测试商家注册时手机号重复"""
        await _create_user(db_session, phone="13800001212", username="existing")
        response = await client.post("/api/v1/auth/merchant/register", json={
            "username": "merchant_new",
            "phone": "13800001212",
            "password": "merchant123",
            "business_name": "新商家",
            "contact_phone": "13900001212",
            "address": "测试地址",
        })
        assert response.status_code == 409

    async def test_merchant_register_missing_fields(self, client: AsyncClient):
        """测试商家注册缺少必填字段"""
        response = await client.post("/api/v1/auth/merchant/register", json={
            "username": "merchant_test",
            "phone": "13800001313",
            "password": "merchant123",
        })
        assert response.status_code == 422


class TestTokenValidation:
    """测试 Token 验证"""

    async def test_get_current_user_with_valid_token(self, client: AsyncClient, db_session: AsyncSession):
        """测试使用有效 Token 获取当前用户信息"""
        user = await _create_user(db_session, username="token_user", phone="13800001414")
        headers = get_test_headers(user_id=user.id, username="token_user", phone="13800001414")
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "token_user"
        assert data["phone"] == "13800001414"

    async def test_get_current_user_with_invalid_token(self, client: AsyncClient):
        """测试使用无效 Token 获取用户信息失败"""
        headers = {"Authorization": "Bearer invalid_token_string"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

    async def test_get_current_user_without_token(self, client: AsyncClient):
        """测试无 Token 访问受保护接口"""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 403

    async def test_refresh_token_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试 Token 刷新成功"""
        user = await _create_user(db_session, username="refresh_user", phone="13800001515")
        headers = get_test_headers(user_id=user.id, username="refresh_user", phone="13800001515")
        response = await client.post("/api/v1/auth/refresh", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


class TestUnauthorizedAccess:
    """测试未授权访问"""

    async def test_unauthorized_access_to_protected_endpoint(self, client: AsyncClient):
        """测试未授权访问受保护端点"""
        response = await client.get("/api/v1/users/profile")
        assert response.status_code == 403

    async def test_unauthorized_access_to_merchant_endpoints(self, client: AsyncClient):
        """测试未授权访问商家端点"""
        response = await client.get("/api/v1/merchants/me")
        assert response.status_code == 403
