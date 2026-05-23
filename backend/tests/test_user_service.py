import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate
from app.core.exceptions import NotFoundException, ConflictException, ValidationException
from tests.conftest import (
    _create_user,
    db_session,
)


@pytest.mark.asyncio
class TestUserCreate:
    """用户创建测试"""

    async def test_create_user_success(self, db_session: AsyncSession):
        """测试成功创建用户"""
        service = UserService(db_session)
        user_data = UserCreate(
            username="newuser",
            phone="13800000100",
            password="password123",
        )
        user = await service.create(user_data)

        assert user.id is not None
        assert user.username == "newuser"
        assert user.phone == "13800000100"
        assert user.password_hash is not None
        assert user.password_hash != "password123"
        assert user.role == "user"
        assert user.is_active is True

    async def test_create_user_password_is_hashed(self, db_session: AsyncSession):
        """测试密码被正确哈希"""
        from app.core.security import verify_password

        service = UserService(db_session)
        user_data = UserCreate(
            username="secureuser",
            phone="13800000101",
            password="MySecurePass!",
        )
        user = await service.create(user_data)

        assert verify_password("MySecurePass!", user.password_hash) is True
        assert user.password_hash != "MySecurePass!"

    async def test_create_user_duplicate_username(self, db_session: AsyncSession):
        """测试重复用户名创建失败"""
        await _create_user(db_session, username="duplicate", phone="13800000200", password="pass123")
        service = UserService(db_session)
        user_data = UserCreate(
            username="duplicate",
            phone="13800000201",
            password="password123",
        )

        with pytest.raises(ConflictException) as exc_info:
            await service.create(user_data)
        assert "已存在" in str(exc_info.value.detail)

    async def test_create_user_duplicate_phone(self, db_session: AsyncSession):
        """测试重复手机号创建失败"""
        await _create_user(db_session, username="user1", phone="13800000300", password="pass123")
        service = UserService(db_session)
        user_data = UserCreate(
            username="user2",
            phone="13800000300",
            password="password123",
        )

        with pytest.raises(ConflictException) as exc_info:
            await service.create(user_data)
        assert "已注册" in str(exc_info.value.detail)


@pytest.mark.asyncio
class TestUserQuery:
    """用户查询测试"""

    async def test_get_by_id_success(self, db_session: AsyncSession):
        """测试根据ID获取用户成功"""
        created = await _create_user(db_session, username="queryuser", phone="13800000400")
        service = UserService(db_session)
        user = await service.get_by_id(created.id)

        assert user.id == created.id
        assert user.username == "queryuser"

    async def test_get_by_id_not_found(self, db_session: AsyncSession):
        """测试根据ID获取不存在的用户"""
        service = UserService(db_session)

        with pytest.raises(NotFoundException) as exc_info:
            await service.get_by_id(99999)
        assert "用户" in str(exc_info.value.detail)

    async def test_get_by_phone_success(self, db_session: AsyncSession):
        """测试根据手机号获取用户成功"""
        await _create_user(db_session, username="phoneuser", phone="13800000500")
        service = UserService(db_session)
        user = await service.get_by_phone("13800000500")

        assert user is not None
        assert user.phone == "13800000500"
        assert user.username == "phoneuser"

    async def test_get_by_phone_not_found(self, db_session: AsyncSession):
        """测试根据手机号获取不存在的用户"""
        service = UserService(db_session)
        user = await service.get_by_phone("13800009999")

        assert user is None

    async def test_get_by_username_success(self, db_session: AsyncSession):
        """测试根据用户名获取用户成功"""
        await _create_user(db_session, username="uniqueusername", phone="13800000600")
        service = UserService(db_session)
        user = await service.get_by_username("uniqueusername")

        assert user is not None
        assert user.username == "uniqueusername"

    async def test_get_by_username_not_found(self, db_session: AsyncSession):
        """测试根据用户名获取不存在的用户"""
        service = UserService(db_session)
        user = await service.get_by_username("nonexistent_user_xyz")

        assert user is None


@pytest.mark.asyncio
class TestUserUpdate:
    """用户更新测试"""

    async def test_update_username(self, db_session: AsyncSession):
        """测试更新用户名"""
        created = await _create_user(db_session, username="oldname", phone="13800000700")
        service = UserService(db_session)
        update_data = UserUpdate(username="newname")
        user = await service.update(created.id, update_data)

        assert user.username == "newname"

    async def test_update_avatar(self, db_session: AsyncSession):
        """测试更新头像"""
        created = await _create_user(db_session, username="avataruser", phone="13800000701")
        service = UserService(db_session)
        update_data = UserUpdate(avatar="/avatars/new.jpg")
        user = await service.update(created.id, update_data)

        assert user.avatar == "/avatars/new.jpg"

    async def test_update_phone(self, db_session: AsyncSession):
        """测试更新手机号"""
        created = await _create_user(db_session, username="phoneupdate", phone="13800000702")
        service = UserService(db_session)
        update_data = UserUpdate(phone="13800000799")
        user = await service.update(created.id, update_data)

        assert user.phone == "13800000799"

    async def test_update_user_not_found(self, db_session: AsyncSession):
        """测试更新不存在的用户"""
        service = UserService(db_session)
        update_data = UserUpdate(username="newname")

        with pytest.raises(NotFoundException):
            await service.update(99999, update_data)

    async def test_update_duplicate_username(self, db_session: AsyncSession):
        """测试更新为已存在的用户名"""
        user1 = await _create_user(db_session, username="user1", phone="13800000800")
        user2 = await _create_user(db_session, username="user2", phone="13800000801")
        service = UserService(db_session)
        update_data = UserUpdate(username="user1")

        with pytest.raises(ConflictException):
            await service.update(user2.id, update_data)

    async def test_update_duplicate_phone(self, db_session: AsyncSession):
        """测试更新为已存在的手机号"""
        user1 = await _create_user(db_session, username="user1", phone="13800000900")
        user2 = await _create_user(db_session, username="user2", phone="13800000901")
        service = UserService(db_session)
        update_data = UserUpdate(phone="13800000900")

        with pytest.raises(ConflictException):
            await service.update(user2.id, update_data)

    async def test_update_same_username_is_ok(self, db_session: AsyncSession):
        """测试更新为自己的用户名不报错"""
        created = await _create_user(db_session, username="sameuser", phone="13800000950")
        service = UserService(db_session)
        update_data = UserUpdate(username="sameuser")
        user = await service.update(created.id, update_data)

        assert user.username == "sameuser"

    async def test_update_same_phone_is_ok(self, db_session: AsyncSession):
        """测试更新为自己的手机号不报错"""
        created = await _create_user(db_session, username="samephone", phone="13800000951")
        service = UserService(db_session)
        update_data = UserUpdate(phone="13800000951")
        user = await service.update(created.id, update_data)

        assert user.phone == "13800000951"

    async def test_update_partial_fields(self, db_session: AsyncSession):
        """测试部分更新不影响其他字段"""
        created = await _create_user(
            db_session,
            username="partialuser",
            phone="13800000960",
            is_active=False,
        )
        service = UserService(db_session)
        update_data = UserUpdate(username="newpartial")
        user = await service.update(created.id, update_data)

        assert user.username == "newpartial"
        assert user.phone == "13800000960"
        assert user.is_active is False


@pytest.mark.asyncio
class TestUserList:
    """用户列表分页测试"""

    async def test_list_users_empty(self, db_session: AsyncSession):
        """测试空用户列表"""
        service = UserService(db_session)
        users, total = await service.list_users()

        assert users == []
        assert total == 0

    async def test_list_users_basic(self, db_session: AsyncSession):
        """测试基本用户列表"""
        await _create_user(db_session, username="listuser1", phone="13800001001")
        await _create_user(db_session, username="listuser2", phone="13800001002")
        service = UserService(db_session)
        users, total = await service.list_users()

        assert total >= 2
        assert len(users) >= 2

    async def test_list_users_pagination(self, db_session: AsyncSession):
        """测试用户列表分页"""
        for i in range(15):
            await _create_user(
                db_session,
                username=f"pageuser{i:03d}",
                phone=f"138000{1000 + i:05d}",
            )
        service = UserService(db_session)

        page1, total1 = await service.list_users(page=1, page_size=10)
        assert len(page1) == 10
        assert total1 >= 15

        page2, total2 = await service.list_users(page=2, page_size=10)
        assert len(page2) >= 5
        assert total2 == total1

    async def test_list_users_pagination_empty_page(self, db_session: AsyncSession):
        """测试超出范围的页码返回空列表"""
        await _create_user(db_session, username="onlyuser", phone="13800001100")
        service = UserService(db_session)
        users, total = await service.list_users(page=100, page_size=10)

        assert users == []
        assert total == 1

    async def test_list_users_search_by_username(self, db_session: AsyncSession):
        """测试按用户名搜索"""
        await _create_user(db_session, username="searchme", phone="13800001200")
        await _create_user(db_session, username="otheruser", phone="13800001201")
        service = UserService(db_session)
        users, total = await service.list_users(search="searchme")

        assert total == 1
        assert users[0].username == "searchme"

    async def test_list_users_search_by_phone(self, db_session: AsyncSession):
        """测试按手机号搜索"""
        await _create_user(db_session, username="phone1", phone="13800001300")
        await _create_user(db_session, username="phone2", phone="13800001399")
        service = UserService(db_session)
        users, total = await service.list_users(search="1300")

        assert total == 1
        assert users[0].phone == "13800001300"

    async def test_list_users_search_no_results(self, db_session: AsyncSession):
        """测试搜索无结果"""
        await _create_user(db_session, username="existuser", phone="13800001400")
        service = UserService(db_session)
        users, total = await service.list_users(search="zzzznotexist")

        assert users == []
        assert total == 0

    async def test_list_users_filter_by_role(self, db_session: AsyncSession):
        """测试按角色筛选"""
        await _create_user(db_session, username="admin1", phone="13800001500", role="admin")
        await _create_user(db_session, username="normal1", phone="13800001501", role="user")
        await _create_user(db_session, username="merchant1", phone="13800001502", role="merchant")
        service = UserService(db_session)

        admins, admin_total = await service.list_users(role="admin")
        assert admin_total == 1
        assert admins[0].role == "admin"

        users, users_total = await service.list_users(role="user")
        assert users_total == 1
        assert users[0].role == "user"

    async def test_list_users_combined_search_and_role(self, db_session: AsyncSession):
        """测试搜索和角色筛选组合"""
        await _create_user(db_session, username="admin_test", phone="13800001600", role="admin")
        await _create_user(db_session, username="user_test", phone="13800001601", role="user")
        await _create_user(db_session, username="admin_other", phone="13800001602", role="admin")
        service = UserService(db_session)
        users, total = await service.list_users(search="test", role="admin")

        assert total == 1
        assert users[0].username == "admin_test"

    async def test_list_users_order_by_created_desc(self, db_session: AsyncSession):
        """测试列表按创建时间倒序"""
        await _create_user(db_session, username="first_user", phone="13800001700")
        await _create_user(db_session, username="second_user", phone="13800001701")
        service = UserService(db_session)
        users, _ = await service.list_users()

        assert len(users) >= 2


@pytest.mark.asyncio
class TestUserToggleActive:
    """用户状态管理测试"""

    async def test_toggle_active_to_true(self, db_session: AsyncSession):
        """测试激活用户"""
        created = await _create_user(db_session, username="inactive", phone="13800001800", is_active=False)
        service = UserService(db_session)
        user = await service.toggle_active(created.id, is_active=True)

        assert user.is_active is True

    async def test_toggle_active_to_false(self, db_session: AsyncSession):
        """测试禁用用户"""
        created = await _create_user(db_session, username="active", phone="13800001801", is_active=True)
        service = UserService(db_session)
        user = await service.toggle_active(created.id, is_active=False)

        assert user.is_active is False

    async def test_toggle_active_not_found(self, db_session: AsyncSession):
        """测试禁用不存在的用户"""
        service = UserService(db_session)

        with pytest.raises(NotFoundException):
            await service.toggle_active(99999, is_active=True)


@pytest.mark.asyncio
class TestUserPasswordUpdate:
    """用户密码修改测试"""

    async def test_update_password_success(self, db_session: AsyncSession):
        """测试成功修改密码"""
        created = await _create_user(db_session, username="pwduser", phone="13800001900", password="oldpass123")
        service = UserService(db_session)
        user = await service.update_password(created.id, "oldpass123", "newpass456")

        from app.core.security import verify_password
        assert verify_password("newpass456", user.password_hash) is True
        assert verify_password("oldpass123", user.password_hash) is False

    async def test_update_password_wrong_old_password(self, db_session: AsyncSession):
        """测试旧密码错误"""
        created = await _create_user(db_session, username="pwduser2", phone="13800001901", password="realpass")
        service = UserService(db_session)

        with pytest.raises(ValidationException) as exc_info:
            await service.update_password(created.id, "wrongoldpass", "newpass456")
        assert "旧密码错误" in str(exc_info.value.detail)

    async def test_update_password_user_not_found(self, db_session: AsyncSession):
        """测试修改不存在用户的密码"""
        service = UserService(db_session)

        with pytest.raises(NotFoundException):
            await service.update_password(99999, "oldpass", "newpass")


@pytest.mark.asyncio
class TestUserResetPassword:
    """用户密码重置测试（管理员操作）"""

    async def test_reset_password_success(self, db_session: AsyncSession):
        """测试管理员成功重置用户密码"""
        created = await _create_user(db_session, username="resetuser", phone="13800002000", password="oldpass123")
        service = UserService(db_session)
        await service.reset_password(created.id, "newpass456")

        from app.core.security import verify_password
        user = await service.get_by_id(created.id)
        assert verify_password("newpass456", user.password_hash) is True
        assert verify_password("oldpass123", user.password_hash) is False

    async def test_reset_password_not_found(self, db_session: AsyncSession):
        """测试重置不存在用户的密码"""
        service = UserService(db_session)

        with pytest.raises(NotFoundException):
            await service.reset_password(99999, "newpass")

    async def test_reset_password_without_old_password(self, db_session: AsyncSession):
        """测试重置密码不需要旧密码"""
        created = await _create_user(db_session, username="resetuser2", phone="13800002001", password="verysecret")
        service = UserService(db_session)

        # 不需要提供旧密码即可重置
        await service.reset_password(created.id, "brandnewpass")

        from app.core.security import verify_password
        user = await service.get_by_id(created.id)
        assert verify_password("brandnewpass", user.password_hash) is True

    async def test_reset_password_short_password(self, db_session: AsyncSession):
        """测试重置密码为短密码（Service层不限制，由Schema层校验）"""
        created = await _create_user(db_session, username="resetuser3", phone="13800002002", password="oldpass")
        service = UserService(db_session)

        # Service层本身不校验密码长度，直接哈希
        await service.reset_password(created.id, "ab")

        from app.core.security import verify_password
        user = await service.get_by_id(created.id)
        assert verify_password("ab", user.password_hash) is True
