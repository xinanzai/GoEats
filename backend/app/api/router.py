from fastapi import APIRouter
from app.api.endpoints import (
    auth,
    users,
    merchants,
    categories,
    products,
    orders,
    admin,
    upload,
)


router = APIRouter()

# 注册各模块路由
router.include_router(auth.router, prefix="/auth", tags=["认证"])
router.include_router(users.router, prefix="/users", tags=["用户"])
router.include_router(merchants.router, prefix="/merchants", tags=["商家"])
router.include_router(categories.router, prefix="/categories", tags=["分类"])
router.include_router(products.router, prefix="/products", tags=["商品"])
router.include_router(orders.router, prefix="/orders", tags=["订单"])
router.include_router(admin.router, prefix="/admin", tags=["管理"])
router.include_router(upload.router, prefix="/upload", tags=["文件上传"])
