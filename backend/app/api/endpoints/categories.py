from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.category import CategoryResponse

router = APIRouter()


@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    merchant_id: int = Query(..., description="商家ID"),
    db: AsyncSession = Depends(get_db),
):
    """获取商家分类列表（公开接口）"""
    from app.services.category_service import CategoryService
    category_service = CategoryService(db)
    categories = await category_service.list_by_merchant(merchant_id)
    return categories
