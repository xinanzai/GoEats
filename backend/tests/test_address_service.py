import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.address_service import AddressService
from app.schemas.address import AddressCreate, AddressUpdate
from app.core.exceptions import NotFoundException, PermissionException
from tests.conftest import (
    _create_user,
    _create_address,
    db_session,
)


@pytest.mark.asyncio
class TestAddressCreate:
    """地址创建测试"""

    async def test_create_address_success(self, db_session: AsyncSession):
        """测试成功创建地址"""
        user = await _create_user(db_session, phone="13800011000")
        service = AddressService(db_session)
        address_data = AddressCreate(
            receiver="张三",
            phone="13700001001",
            province="北京市",
            city="北京市",
            district="朝阳区",
            detail_address="建国路123号",
            is_default=False,
        )
        address = await service.create(user.id, address_data)

        assert address.id is not None
        assert address.user_id == user.id
        assert address.receiver == "张三"
        assert address.phone == "13700001001"
        assert address.province == "北京市"
        assert address.city == "北京市"
        assert address.district == "朝阳区"
        assert address.detail_address == "建国路123号"
        assert address.is_default is False

    async def test_create_default_address(self, db_session: AsyncSession):
        """测试创建默认地址"""
        user = await _create_user(db_session, phone="13800011100")
        service = AddressService(db_session)
        address_data = AddressCreate(
            receiver="李四",
            phone="13700001101",
            province="上海市",
            city="上海市",
            district="浦东新区",
            detail_address="陆家嘴环路456号",
            is_default=True,
        )
        address = await service.create(user.id, address_data)

        assert address.is_default is True

    async def test_create_default_address_clears_old_default(self, db_session: AsyncSession):
        """测试创建新默认地址时取消旧默认地址"""
        user = await _create_user(db_session, phone="13800011200")
        await _create_address(db_session, user=user, receiver="旧默认", is_default=True)
        service = AddressService(db_session)
        address_data = AddressCreate(
            receiver="新默认",
            phone="13700001202",
            province="广东省",
            city="深圳市",
            district="南山区",
            detail_address="科技园888号",
            is_default=True,
        )
        new_address = await service.create(user.id, address_data)

        assert new_address.is_default is True

        addresses = await service.list_by_user(user.id)
        old_default = [a for a in addresses if a.receiver == "旧默认"]
        assert len(old_default) == 1
        assert old_default[0].is_default is False

    async def test_create_multiple_addresses(self, db_session: AsyncSession):
        """测试创建多个地址"""
        user = await _create_user(db_session, phone="13800011300")
        service = AddressService(db_session)
        address_data1 = AddressCreate(
            receiver="地址1",
            phone="13700001301",
            province="北京市",
            city="北京市",
            district="朝阳区",
            detail_address="地址1详情",
        )
        address_data2 = AddressCreate(
            receiver="地址2",
            phone="13700001302",
            province="上海市",
            city="上海市",
            district="黄浦区",
            detail_address="地址2详情",
        )
        addr1 = await service.create(user.id, address_data1)
        addr2 = await service.create(user.id, address_data2)

        assert addr1.id != addr2.id
        addresses = await service.list_by_user(user.id)
        assert len(addresses) == 2


@pytest.mark.asyncio
class TestAddressQuery:
    """地址查询测试"""

    async def test_get_by_id_success(self, db_session: AsyncSession):
        """测试根据ID获取地址成功"""
        user = await _create_user(db_session, phone="13800011400")
        address = await _create_address(db_session, user=user)
        service = AddressService(db_session)
        result = await service.get_by_id(address.id)

        assert result.id == address.id
        assert result.user_id == user.id

    async def test_get_by_id_not_found(self, db_session: AsyncSession):
        """测试根据ID获取不存在的地址"""
        service = AddressService(db_session)

        with pytest.raises(NotFoundException) as exc_info:
            await service.get_by_id(99999)
        assert "地址" in str(exc_info.value.detail)

    async def test_get_by_id_permission_denied(self, db_session: AsyncSession):
        """测试无权限获取其他用户的地址"""
        user1 = await _create_user(db_session, username="user_addr_perm1", phone="13800011500")
        user2 = await _create_user(db_session, username="user_addr_perm2", phone="13800011501")
        address = await _create_address(db_session, user=user1)
        service = AddressService(db_session)

        with pytest.raises(PermissionException) as exc_info:
            await service.get_by_id(address.id, user2.id)
        assert "没有权限" in str(exc_info.value.detail)

    async def test_get_by_id_no_user_check(self, db_session: AsyncSession):
        """测试不传user_id时不校验权限"""
        user1 = await _create_user(db_session, phone="13800011600")
        address = await _create_address(db_session, user=user1)
        service = AddressService(db_session)

        result = await service.get_by_id(address.id)
        assert result.id == address.id

    async def test_list_by_user_success(self, db_session: AsyncSession):
        """测试获取用户地址列表"""
        user = await _create_user(db_session, phone="13800011700")
        await _create_address(db_session, user=user, receiver="地址A", is_default=False)
        await _create_address(db_session, user=user, receiver="地址B", is_default=True)
        await _create_address(db_session, user=user, receiver="地址C", is_default=False)

        service = AddressService(db_session)
        addresses = await service.list_by_user(user.id)

        assert len(addresses) == 3
        assert addresses[0].is_default is True
        assert addresses[0].receiver == "地址B"

    async def test_list_by_user_empty(self, db_session: AsyncSession):
        """测试用户无地址时返回空列表"""
        user = await _create_user(db_session, phone="13800011800")
        service = AddressService(db_session)
        addresses = await service.list_by_user(user.id)

        assert len(addresses) == 0

    async def test_list_by_user_only_shows_own_addresses(self, db_session: AsyncSession):
        """测试地址列表只显示当前用户的地址"""
        user1 = await _create_user(db_session, username="user_addr_list1", phone="13800011900")
        user2 = await _create_user(db_session, username="user_addr_list2", phone="13800011901")
        await _create_address(db_session, user=user1, receiver="用户1地址")
        await _create_address(db_session, user=user2, receiver="用户2地址")

        service = AddressService(db_session)
        addresses = await service.list_by_user(user1.id)

        assert len(addresses) == 1
        assert addresses[0].receiver == "用户1地址"

    async def test_get_default_address_success(self, db_session: AsyncSession):
        """测试获取默认地址成功"""
        user = await _create_user(db_session, phone="13800012000")
        await _create_address(db_session, user=user, receiver="非默认", is_default=False)
        default_addr = await _create_address(db_session, user=user, receiver="默认地址", is_default=True)

        service = AddressService(db_session)
        result = await service.get_default_address(user.id)

        assert result is not None
        assert result.id == default_addr.id
        assert result.receiver == "默认地址"

    async def test_get_default_address_not_found(self, db_session: AsyncSession):
        """测试无默认地址时返回None"""
        user = await _create_user(db_session, phone="13800012100")
        await _create_address(db_session, user=user, receiver="非默认", is_default=False)

        service = AddressService(db_session)
        result = await service.get_default_address(user.id)

        assert result is None

    async def test_get_default_address_no_addresses(self, db_session: AsyncSession):
        """测试无地址时获取默认地址返回None"""
        user = await _create_user(db_session, phone="13800012200")
        service = AddressService(db_session)
        result = await service.get_default_address(user.id)

        assert result is None


@pytest.mark.asyncio
class TestAddressUpdate:
    """地址更新测试"""

    async def test_update_address_success(self, db_session: AsyncSession):
        """测试成功更新地址"""
        user = await _create_user(db_session, phone="13800012300")
        address = await _create_address(db_session, user=user)
        service = AddressService(db_session)
        update_data = AddressUpdate(
            receiver="王五",
            phone="13700002301",
            detail_address="新街道666号",
        )
        result = await service.update(address.id, user.id, update_data)

        assert result.receiver == "王五"
        assert result.phone == "13700002301"
        assert result.detail_address == "新街道666号"

    async def test_update_address_province_city_district(self, db_session: AsyncSession):
        """测试更新省市区和详细地址"""
        user = await _create_user(db_session, phone="13800012400")
        address = await _create_address(db_session, user=user)
        service = AddressService(db_session)
        update_data = AddressUpdate(
            province="广东省",
            city="广州市",
            district="天河区",
            detail_address="天河路999号",
        )
        result = await service.update(address.id, user.id, update_data)

        assert result.province == "广东省"
        assert result.city == "广州市"
        assert result.district == "天河区"
        assert result.detail_address == "天河路999号"

    async def test_update_address_set_default(self, db_session: AsyncSession):
        """测试更新地址并设置为默认"""
        user = await _create_user(db_session, phone="13800012500")
        await _create_address(db_session, user=user, receiver="旧默认", is_default=True)
        address = await _create_address(db_session, user=user, receiver="非默认", is_default=False)
        service = AddressService(db_session)
        update_data = AddressUpdate(is_default=True)
        result = await service.update(address.id, user.id, update_data)

        assert result.is_default is True

        addresses = await service.list_by_user(user.id)
        old = [a for a in addresses if a.receiver == "旧默认"][0]
        assert old.is_default is False

    async def test_update_address_not_found(self, db_session: AsyncSession):
        """测试更新不存在的地址"""
        user = await _create_user(db_session, phone="13800012600")
        service = AddressService(db_session)
        update_data = AddressUpdate(receiver="新名称")

        with pytest.raises(NotFoundException):
            await service.update(99999, user.id, update_data)

    async def test_update_address_permission_denied(self, db_session: AsyncSession):
        """测试无权限更新其他用户的地址"""
        user1 = await _create_user(db_session, username="user_addr_upd1", phone="13800012700")
        user2 = await _create_user(db_session, username="user_addr_upd2", phone="13800012701")
        address = await _create_address(db_session, user=user1)
        service = AddressService(db_session)
        update_data = AddressUpdate(receiver="篡改")

        with pytest.raises(PermissionException) as exc_info:
            await service.update(address.id, user2.id, update_data)
        assert "没有权限" in str(exc_info.value.detail)

    async def test_update_address_partial(self, db_session: AsyncSession):
        """测试部分更新不影响其他字段"""
        user = await _create_user(db_session, phone="13800012800")
        address = await _create_address(db_session, user=user, receiver="原名称", phone="13700002801")
        service = AddressService(db_session)
        update_data = AddressUpdate(receiver="新名称")
        result = await service.update(address.id, user.id, update_data)

        assert result.receiver == "新名称"
        assert result.phone == "13700002801"


@pytest.mark.asyncio
class TestAddressDelete:
    """地址删除测试"""

    async def test_delete_address_success(self, db_session: AsyncSession):
        """测试成功删除地址"""
        user = await _create_user(db_session, phone="13800012900")
        address = await _create_address(db_session, user=user, is_default=False)
        service = AddressService(db_session)

        result = await service.delete(address.id, user.id)
        assert result is True

        with pytest.raises(NotFoundException):
            await service.get_by_id(address.id)

    async def test_delete_address_not_found(self, db_session: AsyncSession):
        """测试删除不存在的地址"""
        user = await _create_user(db_session, phone="13800013000")
        service = AddressService(db_session)

        with pytest.raises(NotFoundException):
            await service.delete(99999, user.id)

    async def test_delete_address_permission_denied(self, db_session: AsyncSession):
        """测试无权限删除其他用户的地址"""
        user1 = await _create_user(db_session, username="user_addr_del1", phone="13800013100")
        user2 = await _create_user(db_session, username="user_addr_del2", phone="13800013101")
        address = await _create_address(db_session, user=user1)
        service = AddressService(db_session)

        with pytest.raises(PermissionException) as exc_info:
            await service.delete(address.id, user2.id)
        assert "没有权限" in str(exc_info.value.detail)

    async def test_delete_one_address_keeps_others(self, db_session: AsyncSession):
        """测试删除一个地址不影响其他地址"""
        user = await _create_user(db_session, phone="13800013200")
        addr1 = await _create_address(db_session, user=user, receiver="地址1", is_default=False)
        addr2 = await _create_address(db_session, user=user, receiver="地址2", is_default=False)
        service = AddressService(db_session)

        await service.delete(addr1.id, user.id)

        addresses = await service.list_by_user(user.id)
        assert len(addresses) == 1
        assert addresses[0].receiver == "地址2"


@pytest.mark.asyncio
class TestAddressSetDefault:
    """设置默认地址测试"""

    async def test_set_default_success(self, db_session: AsyncSession):
        """测试成功设置默认地址"""
        user = await _create_user(db_session, phone="13800013300")
        address = await _create_address(db_session, user=user, is_default=False)
        service = AddressService(db_session)

        result = await service.set_default(address.id, user.id)
        assert result.is_default is True

    async def test_set_default_clears_old_default(self, db_session: AsyncSession):
        """测试设置默认地址时取消旧默认地址"""
        user = await _create_user(db_session, phone="13800013400")
        old_default = await _create_address(db_session, user=user, receiver="旧默认", is_default=True)
        new_default = await _create_address(db_session, user=user, receiver="新默认", is_default=False)
        service = AddressService(db_session)

        result = await service.set_default(new_default.id, user.id)
        assert result.is_default is True

        addresses = await service.list_by_user(user.id)
        old = [a for a in addresses if a.id == old_default.id][0]
        assert old.is_default is False

    async def test_set_default_not_found(self, db_session: AsyncSession):
        """测试设置不存在的地址为默认"""
        user = await _create_user(db_session, phone="13800013500")
        service = AddressService(db_session)

        with pytest.raises(NotFoundException):
            await service.set_default(99999, user.id)

    async def test_set_default_permission_denied(self, db_session: AsyncSession):
        """测试无权限设置其他用户的地址为默认"""
        user1 = await _create_user(db_session, username="user_addr_setdef1", phone="13800013600")
        user2 = await _create_user(db_session, username="user_addr_setdef2", phone="13800013601")
        address = await _create_address(db_session, user=user1)
        service = AddressService(db_session)

        with pytest.raises(PermissionException) as exc_info:
            await service.set_default(address.id, user2.id)
        assert "没有权限" in str(exc_info.value.detail)

    async def test_set_default_already_default(self, db_session: AsyncSession):
        """测试将已经是默认的地址再次设置为默认"""
        user = await _create_user(db_session, phone="13800013700")
        address = await _create_address(db_session, user=user, is_default=True)
        service = AddressService(db_session)

        result = await service.set_default(address.id, user.id)
        assert result.is_default is True


@pytest.mark.asyncio
class TestAddressEdgeCases:
    """地址服务边界情况测试"""

    async def test_list_by_user_ordering(self, db_session: AsyncSession):
        """测试地址列表默认地址优先排序"""
        user = await _create_user(db_session, phone="13800013800")
        await _create_address(db_session, user=user, receiver="普通1", is_default=False)
        await _create_address(db_session, user=user, receiver="默认地址", is_default=True)
        await _create_address(db_session, user=user, receiver="普通2", is_default=False)

        service = AddressService(db_session)
        addresses = await service.list_by_user(user.id)

        assert addresses[0].is_default is True
        assert addresses[0].receiver == "默认地址"

    async def test_create_address_non_default_not_affect_others(self, db_session: AsyncSession):
        """测试创建非默认地址不影响已有默认地址"""
        user = await _create_user(db_session, phone="13800013900")
        default_addr = await _create_address(db_session, user=user, receiver="默认", is_default=True)
        service = AddressService(db_session)
        address_data = AddressCreate(
            receiver="新增非默认",
            phone="13700003901",
            province="浙江省",
            city="杭州市",
            district="西湖区",
            detail_address="西湖边",
            is_default=False,
        )
        await service.create(user.id, address_data)

        updated_default = await service.get_by_id(default_addr.id)
        assert updated_default.is_default is True

    async def test_clear_default_addresses(self, db_session: AsyncSession):
        """测试清除默认地址功能"""
        user = await _create_user(db_session, phone="13800014000")
        default_addr = await _create_address(db_session, user=user, receiver="默认", is_default=True)
        service = AddressService(db_session)

        await service.clear_default_addresses(user.id)

        updated = await service.get_by_id(default_addr.id)
        assert updated.is_default is False

    async def test_clear_default_addresses_exclude_id(self, db_session: AsyncSession):
        """测试清除默认地址时排除指定ID"""
        user = await _create_user(db_session, phone="13800014100")
        addr1 = await _create_address(db_session, user=user, receiver="默认1", is_default=True)
        # 注意：_create_address 会自动取消旧默认地址，所以我们需要手动设置两个都为默认
        addr2 = await _create_address(db_session, user=user, receiver="默认2", is_default=False)
        addr2.is_default = True
        await db_session.flush()
        service = AddressService(db_session)

        await service.clear_default_addresses(user.id, exclude_id=addr1.id)
        await db_session.flush()

        updated1 = await service.get_by_id(addr1.id)
        updated2 = await service.get_by_id(addr2.id)
        assert updated1.is_default is True
        assert updated2.is_default is False
