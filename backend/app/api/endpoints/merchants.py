from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.merchant import MerchantUpdate, MerchantResponse
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.merchant_service import MerchantService
from app.services.category_service import CategoryService
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("")
async def list_merchants(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    search: Optional[str] = Query(None, description="搜索商家名称"),
    db: AsyncSession = Depends(get_db),
):
    """获取商家列表（公开接口，只显示已通过的商家）"""
    merchant_service = MerchantService(db)
    merchants, total = await merchant_service.list_merchants(
        page=page,
        page_size=page_size,
        search=search,
        approved_only=True,
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


@router.get("/me", response_model=MerchantResponse)
async def get_my_merchant(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前商家的信息"""
    if current_user.role != "merchant":
        from app.core.exceptions import PermissionException
        raise PermissionException("只有商家角色可以访问此接口")

    merchant_service = MerchantService(db)
    merchant = await merchant_service.get_by_user_id(current_user.id)

    if not merchant:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("商家信息", current_user.id)

    return merchant


@router.put("/me", response_model=MerchantResponse)
async def update_my_merchant(
    update_data: MerchantUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新当前商家的信息"""
    if current_user.role != "merchant":
        from app.core.exceptions import PermissionException
        raise PermissionException("只有商家角色可以访问此接口")

    merchant_service = MerchantService(db)
    merchant = await merchant_service.get_by_user_id(current_user.id)

    if not merchant:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("商家信息", current_user.id)

    updated_merchant = await merchant_service.update(merchant.id, current_user.id, update_data)
    return updated_merchant


@router.get("/me/categories", response_model=list[CategoryResponse])
async def get_my_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前商家的分类列表"""
    if current_user.role != "merchant":
        from app.core.exceptions import PermissionException
        raise PermissionException("只有商家角色可以访问此接口")

    category_service = CategoryService(db)
    categories = await category_service.list_by_merchant(current_user.id)
    return categories


@router.post("/me/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建商家分类"""
    if current_user.role != "merchant":
        from app.core.exceptions import PermissionException
        raise PermissionException("只有商家角色可以访问此接口")

    category_service = CategoryService(db)
    category = await category_service.create(current_user.id, category_data)
    return category


@router.put("/me/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新商家分类"""
    if current_user.role != "merchant":
        from app.core.exceptions import PermissionException
        raise PermissionException("只有商家角色可以访问此接口")

    category_service = CategoryService(db)
    category = await category_service.update(category_id, current_user.id, category_data)
    return category


@router.delete("/me/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除商家分类"""
    if current_user.role != "merchant":
        from app.core.exceptions import PermissionException
        raise PermissionException("只有商家角色可以访问此接口")

    category_service = CategoryService(db)
    await category_service.delete(category_id, current_user.id)


@router.get("/{merchant_id}", response_model=MerchantResponse)
async def get_merchant(
    merchant_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取商家信息（公开接口）"""
    merchant_service = MerchantService(db)
    merchant = await merchant_service.get_by_id(merchant_id)
    return merchant
