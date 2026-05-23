from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import ProductService
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/merchant/me")
async def get_my_products(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    keyword: Optional[str] = Query(None, description="搜索商品名称"),
    category_id: Optional[int] = Query(None, description="分类ID筛选"),
    is_available: Optional[bool] = Query(None, description="上架状态筛选"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前商家的商品列表"""
    if current_user.role != "merchant":
        from app.core.exceptions import PermissionException
        raise PermissionException("只有商家角色可以访问此接口")

    product_service = ProductService(db)
    products, total = await product_service.list_by_merchant(
        merchant_user_id=current_user.id,
        page=page,
        page_size=page_size,
        keyword=keyword,
        category_id=category_id,
        is_available=is_available,
    )

    items = [ProductResponse.model_validate(p) for p in products]
    total_pages = (total + page_size - 1) // page_size

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.post("/merchant/me", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建商品"""
    if current_user.role != "merchant":
        from app.core.exceptions import PermissionException
        raise PermissionException("只有商家角色可以访问此接口")

    product_service = ProductService(db)
    product = await product_service.create(current_user.id, product_data)
    return product


@router.put("/merchant/me/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新商品"""
    if current_user.role != "merchant":
        from app.core.exceptions import PermissionException
        raise PermissionException("只有商家角色可以访问此接口")

    product_service = ProductService(db)
    product = await product_service.update(product_id, current_user.id, product_data)
    return product


@router.delete("/merchant/me/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除商品"""
    if current_user.role != "merchant":
        from app.core.exceptions import PermissionException
        raise PermissionException("只有商家角色可以访问此接口")

    product_service = ProductService(db)
    await product_service.delete(product_id, current_user.id)


@router.put("/merchant/me/{product_id}/toggle", response_model=ProductResponse)
async def toggle_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """切换商品上架/下架状态"""
    if current_user.role != "merchant":
        from app.core.exceptions import PermissionException
        raise PermissionException("只有商家角色可以访问此接口")

    product_service = ProductService(db)
    product = await product_service.toggle_available(product_id, current_user.id)
    return product


@router.get("")
async def list_products(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    merchant_id: Optional[int] = Query(None, description="商家ID"),
    category_id: Optional[int] = Query(None, description="分类ID"),
    search: Optional[str] = Query(None, description="搜索商品名称"),
    db: AsyncSession = Depends(get_db),
):
    """获取商品列表（公开接口，只显示上架商品）"""
    product_service = ProductService(db)
    products, total = await product_service.list_products(
        page=page,
        page_size=page_size,
        merchant_id=merchant_id,
        category_id=category_id,
        search=search,
        available_only=True,
    )

    items = [ProductResponse.model_validate(p) for p in products]
    total_pages = (total + page_size - 1) // page_size

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取商品详情（公开接口）"""
    product_service = ProductService(db)
    product = await product_service.get_by_id(product_id)
    return product
