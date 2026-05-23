import os
import uuid
from typing import Optional
from fastapi import UploadFile
from app.config import settings


def save_file(file: UploadFile, directory: Optional[str] = None) -> str:
    """保存上传的文件

    Args:
        file: 上传的文件对象。
        directory: 保存的子目录。

    Returns:
        文件的访问路径。
    """
    if directory is None:
        directory = settings.UPLOAD_DIR
    else:
        directory = os.path.join(settings.UPLOAD_DIR, directory)

    os.makedirs(directory, exist_ok=True)

    # 生成唯一文件名
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(directory, unique_filename)

    # 保存文件
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)

    # 返回访问路径
    return f"/uploads/{directory}/{unique_filename}"


def delete_file(file_path: str) -> bool:
    """删除文件

    Args:
        file_path: 文件的访问路径。

    Returns:
        是否删除成功。
    """
    try:
        full_path = os.path.join(settings.UPLOAD_DIR, file_path.lstrip("/"))
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False
    except Exception:
        return False
