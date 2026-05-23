import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import (
    _create_user, _create_address,
    get_test_headers,
)


class TestUserProfile:
    """测试用户信息获取与更新"""

    async def test_get_profile_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取用户信息成功"""
        user = await _create_user(db_session, username="profile_user", phone="13800020001")
        headers = get_test_headers(user_id=user.id, username="profile_user", phone="13800020001")
        response = await client.get("/api/v1/users/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "profile_user"
        assert data["phone"] == "13800020001"
        assert data["role"] == "user"

    async def test_update_profile_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试更新用户信息成功"""
        user = await _create_user(db_session, username="old_name", phone="13800020002")
        headers = get_test_headers(user_id=user.id, username="old_name", phone="13800020002")
        response = await client.put("/api/v1/users/profile", headers=headers, json={
            "username": "new_name",
            "avatar": "https://example.com/avatar.jpg",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "new_name"
        assert data["avatar"] == "https://example.com/avatar.jpg"

    async def test_update_profile_partial(self, client: AsyncClient, db_session: AsyncSession):
        """测试部分更新用户信息"""
        user = await _create_user(db_session, username="partial_user", phone="13800020003")
        headers = get_test_headers(user_id=user.id, username="partial_user", phone="13800020003")
        response = await client.put("/api/v1/users/profile", headers=headers, json={
            "avatar": "https://example.com/new-avatar.jpg",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "partial_user"
        assert data["avatar"] == "https://example.com/new-avatar.jpg"

    async def test_update_profile_invalid_username(self, client: AsyncClient, db_session: AsyncSession):
        """测试更新用户名为无效长度"""
        user = await _create_user(db_session, username="valid_user", phone="13800020004")
        headers = get_test_headers(user_id=user.id, username="valid_user", phone="13800020004")
        response = await client.put("/api/v1/users/profile", headers=headers, json={
            "username": "a",
        })
        assert response.status_code == 422

    async def test_get_profile_unauthorized(self, client: AsyncClient):
        """测试未授权访问用户信息"""
        response = await client.get("/api/v1/users/profile")
        assert response.status_code == 403


class TestChangePassword:
    """测试密码修改"""

    async def test_change_password_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试修改密码成功"""
        user = await _create_user(db_session, username="password_user", phone="13800020005", password="old_password123")
        headers = get_test_headers(user_id=user.id, username="password_user", phone="13800020005")
        response = await client.put("/api/v1/users/password", headers=headers, json={
            "old_password": "old_password123",
            "new_password": "new_password123",
        })
        assert response.status_code == 204

    async def test_change_password_wrong_old_password(self, client: AsyncClient, db_session: AsyncSession):
        """测试旧密码错误修改失败"""
        user = await _create_user(db_session, username="wrong_pwd_user", phone="13800020006", password="correct_old")
        headers = get_test_headers(user_id=user.id, username="wrong_pwd_user", phone="13800020006")
        response = await client.put("/api/v1/users/password", headers=headers, json={
            "old_password": "wrong_old",
            "new_password": "new_password123",
        })
        assert response.status_code == 400

    async def test_change_password_weak_new_password(self, client: AsyncClient, db_session: AsyncSession):
        """测试新密码过短修改失败"""
        user = await _create_user(db_session, username="weak_pwd_user", phone="13800020007", password="strong_password")
        headers = get_test_headers(user_id=user.id, username="weak_pwd_user", phone="13800020007")
        response = await client.put("/api/v1/users/password", headers=headers, json={
            "old_password": "strong_password",
            "new_password": "12345",
        })
        assert response.status_code == 422

    async def test_change_password_unauthorized(self, client: AsyncClient):
        """测试未授权修改密码"""
        response = await client.put("/api/v1/users/password", json={
            "old_password": "old",
            "new_password": "new",
        })
        assert response.status_code == 403


class TestAddressManagement:
    """测试地址管理"""

    async def test_get_addresses_empty(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取空地址列表"""
        user = await _create_user(db_session, username="addr_user1", phone="13800020008")
        headers = get_test_headers(user_id=user.id, username="addr_user1", phone="13800020008")
        response = await client.get("/api/v1/users/addresses", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    async def test_create_address_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试创建地址成功"""
        user = await _create_user(db_session, username="addr_user2", phone="13800020009")
        headers = get_test_headers(user_id=user.id, username="addr_user2", phone="13800020009")
        response = await client.post("/api/v1/users/addresses", headers=headers, json={
            "receiver": "张三",
            "phone": "13700000001",
            "province": "北京市",
            "city": "北京市",
            "district": "朝阳区",
            "detail_address": "测试街道123号",
            "is_default": True,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["receiver"] == "张三"
        assert data["phone"] == "13700000001"
        assert data["is_default"] is True
        assert "id" in data

    async def test_get_addresses_with_data(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取有数据的地址列表"""
        user = await _create_user(db_session, username="addr_user3", phone="13800020010")
        await _create_address(db_session, user=user, receiver="张三", is_default=True)
        await _create_address(db_session, user=user, receiver="李四", is_default=False)
        headers = get_test_headers(user_id=user.id, username="addr_user3", phone="13800020010")
        response = await client.get("/api/v1/users/addresses", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    async def test_update_address_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试更新地址成功"""
        user = await _create_user(db_session, username="addr_user4", phone="13800020011")
        address = await _create_address(db_session, user=user, receiver="原姓名", is_default=True)
        headers = get_test_headers(user_id=user.id, username="addr_user4", phone="13800020011")
        response = await client.put(f"/api/v1/users/addresses/{address.id}", headers=headers, json={
            "receiver": "新姓名",
            "detail_address": "新地址456号",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["receiver"] == "新姓名"
        assert data["detail_address"] == "新地址456号"

    async def test_update_other_user_address_fail(self, client: AsyncClient, db_session: AsyncSession):
        """测试更新其他用户地址失败"""
        user1 = await _create_user(db_session, username="owner_user", phone="13800020012")
        user2 = await _create_user(db_session, username="other_user", phone="13800020013")
        address = await _create_address(db_session, user=user1, receiver="owner", is_default=True)
        headers = get_test_headers(user_id=user2.id, username="other_user", phone="13800020013")
        response = await client.put(f"/api/v1/users/addresses/{address.id}", headers=headers, json={
            "receiver": "hacker",
        })
        assert response.status_code == 403

    async def test_delete_address_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试删除地址成功"""
        user = await _create_user(db_session, username="delete_user", phone="13800020014")
        address = await _create_address(db_session, user=user, receiver="to_delete", is_default=True)
        headers = get_test_headers(user_id=user.id, username="delete_user", phone="13800020014")
        response = await client.delete(f"/api/v1/users/addresses/{address.id}", headers=headers)
        assert response.status_code == 204

    async def test_delete_other_user_address_fail(self, client: AsyncClient, db_session: AsyncSession):
        """测试删除其他用户地址失败"""
        user1 = await _create_user(db_session, username="del_owner", phone="13800020015")
        user2 = await _create_user(db_session, username="del_other", phone="13800020016")
        address = await _create_address(db_session, user=user1, receiver="safe", is_default=True)
        headers = get_test_headers(user_id=user2.id, username="del_other", phone="13800020016")
        response = await client.delete(f"/api/v1/users/addresses/{address.id}", headers=headers)
        assert response.status_code == 403

    async def test_set_default_address_success(self, client: AsyncClient, db_session: AsyncSession):
        """测试设置默认地址成功"""
        user = await _create_user(db_session, username="default_user", phone="13800020017")
        addr1 = await _create_address(db_session, user=user, receiver="addr1", is_default=True)
        addr2 = await _create_address(db_session, user=user, receiver="addr2", is_default=False)
        headers = get_test_headers(user_id=user.id, username="default_user", phone="13800020017")
        response = await client.put(f"/api/v1/users/addresses/{addr2.id}/set-default", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == addr2.id
        assert data["is_default"] is True

    async def test_set_default_other_user_address_fail(self, client: AsyncClient, db_session: AsyncSession):
        """测试设置其他用户地址为默认失败"""
        user1 = await _create_user(db_session, username="set_owner", phone="13800020018")
        user2 = await _create_user(db_session, username="set_other", phone="13800020019")
        address = await _create_address(db_session, user=user1, receiver="safe", is_default=False)
        headers = get_test_headers(user_id=user2.id, username="set_other", phone="13800020019")
        response = await client.put(f"/api/v1/users/addresses/{address.id}/set-default", headers=headers)
        assert response.status_code == 403

    async def test_create_address_missing_fields(self, client: AsyncClient, db_session: AsyncSession):
        """测试创建地址缺少必填字段"""
        user = await _create_user(db_session, username="missing_addr", phone="13800020020")
        headers = get_test_headers(user_id=user.id, username="missing_addr", phone="13800020020")
        response = await client.post("/api/v1/users/addresses", headers=headers, json={
            "receiver": "张三",
        })
        assert response.status_code == 422

    async def test_get_addresses_unauthorized(self, client: AsyncClient):
        """测试未授权访问地址列表"""
        response = await client.get("/api/v1/users/addresses")
        assert response.status_code == 403
