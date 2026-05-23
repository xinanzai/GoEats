from typing import Optional
from fastapi import APIRouter, Depends, Query, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.order import OrderCreate, OrderResponse, OrderItemResponse
from app.services.order_service import OrderService
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建订单"""
    order_service = OrderService(db)
    order = await order_service.create(current_user.id, order_data)

    items_result = await order_service.get_order_items(order.id)
    from app.schemas.order import OrderItemResponse
    items = [OrderItemResponse.model_validate(item) for item in items_result]

    return OrderResponse(
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
        items=items,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.get("/users/me")
async def list_my_orders(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    status_filter: Optional[str] = Query(None, alias="status", description="订单状态筛选"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的订单列表"""
    order_service = OrderService(db)
    orders, total = await order_service.list_user_orders(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        status=status_filter,
    )

    items = []
    for order in orders:
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


@router.get("/users/me/{order_id}", response_model=OrderResponse)
async def get_my_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的订单详情"""
    order_service = OrderService(db)
    order = await order_service.get_by_id(order_id)

    if order.user_id != current_user.id:
        from app.core.exceptions import PermissionException
        raise PermissionException("没有权限查看此订单")

    order_items = await order_service.get_order_items(order.id)
    items = [OrderItemResponse.model_validate(item) for item in order_items]

    return OrderResponse(
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
        items=items,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.post("/users/me/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int,
    reason: Optional[str] = Body(None, embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """取消订单"""
    order_service = OrderService(db)
    order = await order_service.cancel(order_id, current_user.id, reason)

    order_items = await order_service.get_order_items(order.id)
    items = [OrderItemResponse.model_validate(item) for item in order_items]

    return OrderResponse(
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
        items=items,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.post("/users/me/{order_id}/pay", response_model=OrderResponse)
async def pay_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """支付订单（模拟支付）"""
    order_service = OrderService(db)
    order = await order_service.pay(order_id, current_user.id)

    order_items = await order_service.get_order_items(order.id)
    items = [OrderItemResponse.model_validate(item) for item in order_items]

    return OrderResponse(
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
        items=items,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.get("/merchant/me")
async def list_merchant_orders(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    status_filter: Optional[str] = Query(None, alias="status", description="订单状态筛选"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前商家的订单列表"""
    if current_user.role != "merchant":
        from app.core.exceptions import PermissionException
        raise PermissionException("只有商家角色可以访问此接口")

    order_service = OrderService(db)
    orders, total = await order_service.list_merchant_orders(
        merchant_user_id=current_user.id,
        page=page,
        page_size=page_size,
        status=status_filter,
    )

    items = []
    for order in orders:
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


@router.put("/merchant/me/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    new_status: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新订单状态（商家端）"""
    if current_user.role != "merchant":
        from app.core.exceptions import PermissionException
        raise PermissionException("只有商家角色可以访问此接口")

    order_service = OrderService(db)
    order = await order_service.update_status(order_id, current_user.id, new_status)

    order_items = await order_service.get_order_items(order.id)
    items = [OrderItemResponse.model_validate(item) for item in order_items]

    return OrderResponse(
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
        items=items,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.post("/merchant/me/{order_id}/prepare", response_model=OrderResponse)
async def prepare_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """开始制作订单"""
    if current_user.role != "merchant":
        from app.core.exceptions import PermissionException
        raise PermissionException("只有商家角色可以访问此接口")

    order_service = OrderService(db)
    order = await order_service.prepare(order_id, current_user.id)

    order_items = await order_service.get_order_items(order.id)
    items = [OrderItemResponse.model_validate(item) for item in order_items]

    return OrderResponse(
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
        items=items,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.post("/merchant/me/{order_id}/deliver", response_model=OrderResponse)
async def deliver_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """开始配送订单"""
    if current_user.role != "merchant":
        from app.core.exceptions import PermissionException
        raise PermissionException("只有商家角色可以访问此接口")

    order_service = OrderService(db)
    order = await order_service.deliver(order_id, current_user.id)

    order_items = await order_service.get_order_items(order.id)
    items = [OrderItemResponse.model_validate(item) for item in order_items]

    return OrderResponse(
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
        items=items,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.post("/merchant/me/{order_id}/complete", response_model=OrderResponse)
async def complete_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """完成订单"""
    if current_user.role != "merchant":
        from app.core.exceptions import PermissionException
        raise PermissionException("只有商家角色可以访问此接口")

    order_service = OrderService(db)
    order = await order_service.complete(order_id, current_user.id)

    order_items = await order_service.get_order_items(order.id)
    items = [OrderItemResponse.model_validate(item) for item in order_items]

    return OrderResponse(
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
        items=items,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )
