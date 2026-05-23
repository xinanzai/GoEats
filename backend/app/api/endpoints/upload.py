import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import settings
from app.core.dependencies import get_current_user
from app.models.user import User
from app.core.exceptions import PermissionException, ValidationException

router = APIRouter()

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ALLOWED_CONTENT_TYPES = {
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
}


def validate_image_file(file: UploadFile) -> None:
    """验证上传的文件是否为合法图片"""
    if not file.filename:
        raise ValidationException("文件名不能为空")

    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise ValidationException(
            f"不支持的文件类型: {file_extension}。"
            f"支持的文件类型: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationException(f"不支持的内容类型: {file.content_type}")

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > settings.MAX_FILE_SIZE:
        max_size_mb = settings.MAX_FILE_SIZE // (1024 * 1024)
        raise ValidationException(f"文件大小超过限制（最大 {max_size_mb}MB）")


async def save_upload_file(file: UploadFile, subdirectory: Optional[str] = None) -> tuple[str, int]:
    """保存上传的文件到服务器

    Args:
        file: 上传的文件对象。
        subdirectory: 保存的子目录名称。

    Returns:
        文件的访问路径 URL 和文件大小。
    """
    if subdirectory:
        directory = os.path.join(settings.UPLOAD_DIR, subdirectory)
    else:
        directory = settings.UPLOAD_DIR

    os.makedirs(directory, exist_ok=True)

    file_extension = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(directory, unique_filename)

    content = await file.read()
    file_size = len(content)
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    if subdirectory:
        file_url = f"/uploads/{subdirectory}/{unique_filename}"
    else:
        file_url = f"/uploads/{unique_filename}"

    return file_url, file_size


@router.post("", status_code=status.HTTP_200_OK)
async def upload_file(
    file: UploadFile = File(..., description="要上传的文件"),
    directory: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传图片文件

    支持的文件类型: jpg, jpeg, png, gif, webp
    最大文件大小: 10MB

    Args:
        file: 上传的图片文件。
        directory: 可选的子目录，如 'products', 'merchants', 'avatars'。
        current_user: 当前登录用户。
        db: 数据库会话。

    Returns:
        包含文件URL的字典。
    """
    validate_image_file(file)

    valid_directories = ['products', 'merchants', 'avatars', '']
    if directory and directory not in valid_directories:
        raise ValidationException(
            f"无效的子目录。允许的子目录: {', '.join(valid_directories)}"
        )

    file_url, file_size = await save_upload_file(file, directory if directory else None)

    return {
        "code": 200,
        "message": "文件上传成功",
        "data": {
            "url": file_url,
            "filename": file.filename,
            "size": file_size,
        }
    }


@router.post("/product", status_code=status.HTTP_200_OK)
async def upload_product_image(
    file: UploadFile = File(..., description="商品图片"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传商品图片（商家专用）

    Args:
        file: 商品图片文件。
        current_user: 当前登录用户（必须为商家）。
        db: 数据库会话。

    Returns:
        包含图片URL的字典。
    """
    if current_user.role != "merchant":
        raise PermissionException("只有商家角色可以上传商品图片")

    validate_image_file(file)
    file_url, _ = await save_upload_file(file, "products")

    return {
        "code": 200,
        "message": "商品图片上传成功",
        "data": {
            "url": file_url,
            "filename": file.filename,
        }
    }


@router.post("/merchant/logo", status_code=status.HTTP_200_OK)
async def upload_merchant_logo(
    file: UploadFile = File(..., description="商家Logo"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传商家Logo

    Args:
        file: Logo图片文件。
        current_user: 当前登录用户（必须为商家）。
        db: 数据库会话。

    Returns:
        包含Logo URL的字典。
    """
    if current_user.role != "merchant":
        raise PermissionException("只有商家角色可以上传Logo")

    validate_image_file(file)
    file_url, _ = await save_upload_file(file, "merchants")

    return {
        "code": 200,
        "message": "Logo上传成功",
        "data": {
            "url": file_url,
            "filename": file.filename,
        }
    }


@router.post("/avatar", status_code=status.HTTP_200_OK)
async def upload_avatar(
    file: UploadFile = File(..., description="头像图片"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传用户头像

    Args:
        file: 头像图片文件。
        current_user: 当前登录用户。
        db: 数据库会话。

    Returns:
        包含头像URL的字典。
    """
    validate_image_file(file)
    file_url, _ = await save_upload_file(file, "avatars")

    return {
        "code": 200,
        "message": "头像上传成功",
        "data": {
            "url": file_url,
            "filename": file.filename,
        }
    }
