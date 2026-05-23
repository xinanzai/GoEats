import pytest
import pytest_asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.merchant_service import MerchantService
from app.schemas.merchant import MerchantCreate, MerchantUpdate
from app.core.exceptions import NotFoundException, ValidationException, PermissionException
from tests.conftest import (
    _create_user,
    _create_merchant_user,
    _create_merchant,
)


@pytest.mark.asyncio
class TestMerchantCreate:
    """商家创建测试"""

    async def test_create_merchant_success(self, db_session: AsyncSession):
        """测试成功创建商家"""
        user = await _create_merchant_user(db_session)
        service = MerchantService(db_session)
        merchant_data = MerchantCreate(
            business_name="美味餐厅",
            contact_phone="13900000001",
            address="北京市朝阳区建国路123号",
            description="好吃的餐厅",
        )
        merchant = await service.create(user.id, merchant_data)

        assert merchant.id is not None
        assert merchant.user_id == user.id
        assert merchant.business_name == "美味餐厅"
        assert merchant.contact_phone == "13900000001"
        assert merchant.address == "北京市朝阳区建国路123号"
        assert merchant.description == "好吃的餐厅"
        assert merchant.status == "pending"

    async def test_create_merchant_default_status_pending(self, db_session: AsyncSession):
        """测试创建商家默认状态为待审核"""
        user = await _create_merchant_user(db_session)
        service = MerchantService(db_session)
        merchant_data = MerchantCreate(
            business_name="测试商家",
            contact_phone="13900000002",
            address="测试地址",
        )
        merchant = await service.create(user.id, merchant_data)

        assert merchant.status == "pending"
        assert merchant.rejection_reason is None
        assert merchant.approved_at is None

    async def test_create_merchant_duplicate_user(self, db_session: AsyncSession):
        """测试同一用户重复创建商家失败"""
        user = await _create_merchant_user(db_session)
        service = MerchantService(db_session)
        merchant_data = MerchantCreate(
            business_name="第一家",
            contact_phone="13900000003",
            address="地址一",
        )
        await service.create(user.id, merchant_data)

        merchant_data2 = MerchantCreate(
            business_name="第二家",
            contact_phone="13900000004",
            address="地址二",
        )
        with pytest.raises(ValidationException) as exc_info:
            await service.create(user.id, merchant_data2)
        assert "已提交" in str(exc_info.value.detail)

    async def test_create_merchant_no_description(self, db_session: AsyncSession):
        """测试创建商家不需要描述"""
        user = await _create_merchant_user(db_session)
        service = MerchantService(db_session)
        merchant_data = MerchantCreate(
            business_name="简单商家",
            contact_phone="13900000005",
            address="简单地址",
        )
        merchant = await service.create(user.id, merchant_data)

        assert merchant.id is not None
        assert merchant.description is None


@pytest.mark.asyncio
class TestMerchantQuery:
    """商家查询测试"""

    async def test_get_by_id_success(self, db_session: AsyncSession):
        """测试根据ID获取商家成功"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user, business_name="查询测试商家")
        service = MerchantService(db_session)
        result = await service.get_by_id(merchant.id)

        assert result.id == merchant.id
        assert result.business_name == "查询测试商家"

    async def test_get_by_id_not_found(self, db_session: AsyncSession):
        """测试根据ID获取不存在的商家"""
        service = MerchantService(db_session)

        with pytest.raises(NotFoundException) as exc_info:
            await service.get_by_id(99999)
        assert "商家" in str(exc_info.value.detail)

    async def test_get_by_user_id_success(self, db_session: AsyncSession):
        """测试根据用户ID获取商家成功"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user)
        service = MerchantService(db_session)
        result = await service.get_by_user_id(user.id)

        assert result is not None
        assert result.user_id == user.id

    async def test_get_by_user_id_not_found(self, db_session: AsyncSession):
        """测试根据用户ID获取不存在的商家"""
        user = await _create_user(db_session, username="normal_user", phone="13800002000", role="user")
        service = MerchantService(db_session)
        result = await service.get_by_user_id(user.id)

        assert result is None


@pytest.mark.asyncio
class TestMerchantUpdate:
    """商家更新测试"""

    async def test_update_merchant_success(self, db_session: AsyncSession):
        """测试成功更新商家信息"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user)
        service = MerchantService(db_session)
        update_data = MerchantUpdate(
            business_name="新名称",
            contact_phone="13900000100",
            description="新的描述",
        )
        result = await service.update(merchant.id, user.id, update_data)

        assert result.business_name == "新名称"
        assert result.contact_phone == "13900000100"
        assert result.description == "新的描述"

    async def test_update_merchant_logo(self, db_session: AsyncSession):
        """测试更新商家Logo"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user)
        service = MerchantService(db_session)
        update_data = MerchantUpdate(logo="/logos/new_logo.jpg")
        result = await service.update(merchant.id, user.id, update_data)

        assert result.logo == "/logos/new_logo.jpg"

    async def test_update_merchant_not_found(self, db_session: AsyncSession):
        """测试更新不存在的商家"""
        user = await _create_merchant_user(db_session)
        service = MerchantService(db_session)
        update_data = MerchantUpdate(business_name="新名称")

        with pytest.raises(NotFoundException):
            await service.update(99999, user.id, update_data)

    async def test_update_merchant_permission_denied(self, db_session: AsyncSession):
        """测试无权限更新其他商家"""
        owner = await _create_merchant_user(db_session, username="owner", phone="13800002100")
        merchant = await _create_merchant(db_session, user=owner)
        other_user = await _create_merchant_user(db_session, username="other", phone="13800002101")
        service = MerchantService(db_session)
        update_data = MerchantUpdate(business_name="篡改名称")

        with pytest.raises(PermissionException) as exc_info:
            await service.update(merchant.id, other_user.id, update_data)
        assert "没有权限" in str(exc_info.value.detail)

    async def test_update_merchant_partial(self, db_session: AsyncSession):
        """测试部分更新不影响其他字段"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(
            db_session,
            user=user,
            business_name="原名称",
            status="approved",
        )
        service = MerchantService(db_session)
        update_data = MerchantUpdate(description="仅更新描述")
        result = await service.update(merchant.id, user.id, update_data)

        assert result.business_name == "原名称"
        assert result.description == "仅更新描述"
        assert result.status == "approved"


@pytest.mark.asyncio
class TestMerchantList:
    """商家列表查询测试"""

    async def test_list_merchants_empty(self, db_session: AsyncSession):
        """测试空商家列表"""
        service = MerchantService(db_session)
        merchants, total = await service.list_merchants()

        assert merchants == []
        assert total == 0

    async def test_list_merchants_basic(self, db_session: AsyncSession):
        """测试基本商家列表"""
        user1 = await _create_merchant_user(db_session, username="m1", phone="13800002200")
        user2 = await _create_merchant_user(db_session, username="m2", phone="13800002201")
        await _create_merchant(db_session, user=user1, business_name="商家A")
        await _create_merchant(db_session, user=user2, business_name="商家B")
        service = MerchantService(db_session)
        merchants, total = await service.list_merchants()

        assert total == 2
        assert len(merchants) == 2

    async def test_list_merchants_pagination(self, db_session: AsyncSession):
        """测试商家列表分页"""
        for i in range(8):
            user = await _create_merchant_user(
                db_session,
                username=f"page_m_{i}",
                phone=f"138000{2300 + i:05d}",
            )
            await _create_merchant(db_session, user=user, business_name=f"分页商家{i}")
        service = MerchantService(db_session)

        page1, total1 = await service.list_merchants(page=1, page_size=5)
        assert len(page1) == 5
        assert total1 == 8

        page2, total2 = await service.list_merchants(page=2, page_size=5)
        assert len(page2) == 3
        assert total2 == 8

    async def test_list_merchants_search(self, db_session: AsyncSession):
        """测试商家列表搜索"""
        user1 = await _create_merchant_user(db_session, username="m1", phone="13800002400")
        user2 = await _create_merchant_user(db_session, username="m2", phone="13800002401")
        await _create_merchant(db_session, user=user1, business_name="肯德基")
        await _create_merchant(db_session, user=user2, business_name="麦当劳")
        service = MerchantService(db_session)

        merchants, total = await service.list_merchants(search="肯德基")
        assert total == 1
        assert merchants[0].business_name == "肯德基"

    async def test_list_merchants_filter_by_status(self, db_session: AsyncSession):
        """测试按状态筛选商家"""
        user1 = await _create_merchant_user(db_session, username="m1", phone="13800002500")
        user2 = await _create_merchant_user(db_session, username="m2", phone="13800002501")
        user3 = await _create_merchant_user(db_session, username="m3", phone="13800002502")
        await _create_merchant(db_session, user=user1, status="approved")
        await _create_merchant(db_session, user=user2, status="pending")
        await _create_merchant(db_session, user=user3, status="rejected")
        service = MerchantService(db_session)

        approved, approved_total = await service.list_merchants(status="approved")
        assert approved_total == 1
        assert approved[0].status == "approved"

        pending, pending_total = await service.list_merchants(status="pending")
        assert pending_total == 1

    async def test_list_merchants_approved_only(self, db_session: AsyncSession):
        """测试只显示已通过的商家"""
        user1 = await _create_merchant_user(db_session, username="m1", phone="13800002600")
        user2 = await _create_merchant_user(db_session, username="m2", phone="13800002601")
        await _create_merchant(db_session, user=user1, status="approved")
        await _create_merchant(db_session, user=user2, status="pending")
        service = MerchantService(db_session)
        merchants, total = await service.list_merchants(approved_only=True)

        assert total == 1
        assert merchants[0].status == "approved"


@pytest.mark.asyncio
class TestMerchantApproval:
    """商家审批测试"""

    async def test_approve_merchant_success(self, db_session: AsyncSession):
        """测试成功审批商家"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user, status="pending")
        admin = await _create_user(db_session, username="admin", phone="13800002700", role="admin")
        service = MerchantService(db_session)
        result = await service.approve(merchant.id, admin.id)

        assert result.status == "approved"
        assert result.approved_by == admin.id
        assert result.approved_at is not None
        assert result.rejection_reason is None

    async def test_approve_already_approved(self, db_session: AsyncSession):
        """测试重复审批已通过的商家"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user, status="approved")
        admin = await _create_user(db_session, username="admin", phone="13800002701", role="admin")
        service = MerchantService(db_session)

        with pytest.raises(ValidationException) as exc_info:
            await service.approve(merchant.id, admin.id)
        assert "只能审批待审核" in str(exc_info.value.detail)

    async def test_approve_rejected_merchant(self, db_session: AsyncSession):
        """测试审批已拒绝的商家"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user, status="rejected")
        admin = await _create_user(db_session, username="admin", phone="13800002702", role="admin")
        service = MerchantService(db_session)

        with pytest.raises(ValidationException):
            await service.approve(merchant.id, admin.id)

    async def test_approve_not_found(self, db_session: AsyncSession):
        """测试审批不存在的商家"""
        admin = await _create_user(db_session, username="admin", phone="13800002703", role="admin")
        service = MerchantService(db_session)

        with pytest.raises(NotFoundException):
            await service.approve(99999, admin.id)

    async def test_reject_merchant_success(self, db_session: AsyncSession):
        """测试成功拒绝商家"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user, status="pending")
        admin = await _create_user(db_session, username="admin", phone="13800002800", role="admin")
        service = MerchantService(db_session)
        reason = "资质不全"
        result = await service.reject(merchant.id, admin.id, reason)

        assert result.status == "rejected"
        assert result.rejection_reason == reason
        assert result.approved_by == admin.id

    async def test_reject_already_rejected(self, db_session: AsyncSession):
        """测试重复拒绝已拒绝的商家"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user, status="rejected")
        admin = await _create_user(db_session, username="admin", phone="13800002801", role="admin")
        service = MerchantService(db_session)

        with pytest.raises(ValidationException):
            await service.reject(merchant.id, admin.id, "重复拒绝")

    async def test_reject_approved_merchant(self, db_session: AsyncSession):
        """测试拒绝已通过的商家"""
        user = await _create_merchant_user(db_session)
        merchant = await _create_merchant(db_session, user=user, status="approved")
        admin = await _create_user(db_session, username="admin", phone="13800002802", role="admin")
        service = MerchantService(db_session)

        with pytest.raises(ValidationException):
            await service.reject(merchant.id, admin.id, "不应该通过")

    async def test_reject_not_found(self, db_session: AsyncSession):
        """测试拒绝不存在的商家"""
        admin = await _create_user(db_session, username="admin", phone="13800002803", role="admin")
        service = MerchantService(db_session)

        with pytest.raises(NotFoundException):
            await service.reject(99999, admin.id, "不存在")


@pytest.mark.asyncio
class TestPendingMerchants:
    """待审核商家列表测试"""

    async def test_get_pending_merchants_empty(self, db_session: AsyncSession):
        """测试无待审核商家"""
        user = await _create_merchant_user(db_session)
        await _create_merchant(db_session, user=user, status="approved")
        service = MerchantService(db_session)
        merchants, total = await service.get_pending_merchants()

        assert merchants == []
        assert total == 0

    async def test_get_pending_merchants_success(self, db_session: AsyncSession):
        """测试获取待审核商家列表"""
        user1 = await _create_merchant_user(db_session, username="m1", phone="13800002900")
        user2 = await _create_merchant_user(db_session, username="m2", phone="13800002901")
        user3 = await _create_merchant_user(db_session, username="m3", phone="13800002902")
        await _create_merchant(db_session, user=user1, status="pending")
        await _create_merchant(db_session, user=user2, status="pending")
        await _create_merchant(db_session, user=user3, status="approved")
        service = MerchantService(db_session)
        merchants, total = await service.get_pending_merchants()

        assert total == 2
        assert len(merchants) == 2
        for m in merchants:
            assert m.status == "pending"

    async def test_get_pending_merchants_pagination(self, db_session: AsyncSession):
        """测试待审核商家分页"""
        for i in range(5):
            user = await _create_merchant_user(
                db_session,
                username=f"pending_m_{i}",
                phone=f"138000{3000 + i:05d}",
            )
            await _create_merchant(db_session, user=user, status="pending")
        service = MerchantService(db_session)

        page1, total = await service.get_pending_merchants(page=1, page_size=3)
        assert len(page1) == 3
        assert total == 5

        page2, _ = await service.get_pending_merchants(page=2, page_size=3)
        assert len(page2) == 2
