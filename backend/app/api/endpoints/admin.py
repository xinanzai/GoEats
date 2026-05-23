from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Body, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.merchant import MerchantResponse
from app.schemas.order import OrderResponse, OrderItemResponse
from app.services.user_service import UserService
from app.services.merchant_service import MerchantService
from app.services.admin_service import AdminService
from app.services.order_service import OrderService
from app.core.dependencies import get_current_admin_user
from app.models.user import User

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """获取仪表盘统计数据"""
    admin_service = AdminService(db)
    stats = await admin_service.get_dashboard_stats()
    return stats


@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    search: Optional[str] = Query(None, description="搜索用户名或手机号"),
    role: Optional[str] = Query(None, description="角色筛选"),
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """获取用户列表"""
    user_service = UserService(db)
    users, total = await user_service.list_users(
        page=page,
        page_size=page_size,
        search=search,
        role=role,
    )

    items = []
    for user in users:
        items.append(UserResponse(
            id=user.id,
            username=user.username,
            phone=user.phone,
            avatar=user.avatar,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        ))

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """获取用户详情"""
    admin_service = AdminService(db)
    user = await admin_service.get_user_details(user_id)

    if not user:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("用户", user_id)

    return UserResponse(
        id=user.id,
        username=user.username,
        phone=user.phone,
        avatar=user.avatar,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    update_data: UserUpdate,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """更新用户信息"""
    user_service = UserService(db)
    user = await user_service.update(user_id, update_data)

    return UserResponse(
        id=user.id,
        username=user.username,
        phone=user.phone,
        avatar=user.avatar,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    is_active: bool = Body(..., embed=True),
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """启用/禁用用户"""
    user_service = UserService(db)
    user = await user_service.toggle_active(user_id, is_active)

    return UserResponse(
        id=user.id,
        username=user.username,
        phone=user.phone,
        avatar=user.avatar,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("/merchants")
async def list_merchants(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    search: Optional[str] = Query(None, description="搜索商家名称"),
    status_filter: Optional[str] = Query(None, alias="status", description="状态筛选"),
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """获取商家列表（管理端）"""
    merchant_service = MerchantService(db)
    merchants, total = await merchant_service.list_merchants(
        page=page,
        page_size=page_size,
        search=search,
        status=status_filter,
    )

    items = [MerchantResponse.model_validate(m) for m in merchants]
    total_pages = (total + page_size - 1) // page_size

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/merchants/{merchant_id}", response_model=MerchantResponse)
async def get_merchant(
    merchant_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """获取商家详情（管理端）"""
    admin_service = AdminService(db)
    merchant = await admin_service.get_merchant_details(merchant_id)

    if not merchant:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("商家", merchant_id)

    return MerchantResponse.model_validate(merchant)


@router.put("/merchants/{merchant_id}/approve")
async def approve_merchant(
    merchant_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """审批商家（通过）"""
    merchant_service = MerchantService(db)
    merchant = await merchant_service.approve(merchant_id, admin_user.id)

    return MerchantResponse.model_validate(merchant)


@router.put("/merchants/{merchant_id}/reject")
async def reject_merchant(
    merchant_id: int,
    reason: str = Body(..., embed=True),
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """审批商家（拒绝）"""
    merchant_service = MerchantService(db)
    merchant = await merchant_service.reject(merchant_id, admin_user.id, reason)

    return MerchantResponse.model_validate(merchant)


@router.get("/orders")
async def list_orders(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    status_filter: Optional[str] = Query(None, alias="status", description="状态筛选"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """获取订单列表（管理端）"""
    admin_service = AdminService(db)
    orders, total = await admin_service.list_orders(
        page=page,
        page_size=page_size,
        status=status_filter,
        start_date=start_date,
        end_date=end_date,
    )

    items = []
    for order in orders:
        order_service = OrderService(db)
        order_items = await order_service.get_order_items(order.id)
        item_list = [OrderItemResponse.model_validate(item) for item in order_items]
        items.append(OrderResponse(
            id=order.id,
            order_no=order.order_no,
            user_id=order.user_id,
            merchant_id=order.merchant_id,
            address_id=order.address_id,
            receiver=order.receiver,
            receiver_phone=order.receiver_phone,
            receiver_address=order.receiver_address,
            total_price=order.total_price,
            discount_amount=order.discount_amount,
            delivery_fee=order.delivery_fee,
            pay_amount=order.pay_amount,
            status=order.status,
            paid_at=order.paid_at,
            completed_at=order.completed_at,
            cancel_reason=order.cancel_reason,
            remark=order.remark,
            items=item_list,
            created_at=order.created_at,
            updated_at=order.updated_at,
        ))

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/statistics")
async def get_statistics(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """获取数据统计"""
    admin_service = AdminService(db)

    order_stats = await admin_service.get_order_statistics(days=days)
    popular_products = await admin_service.get_popular_products(limit=10)

    return {
        "order_statistics": order_stats,
        "popular_products": popular_products,
    }
