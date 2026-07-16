"""
文件工具
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from PySide6.QtWidgets import QWidget, QFileDialog

logger = logging.getLogger(__name__)


def get_resource_path(relative_path: str) -> Path:
    """
    获取资源文件的绝对路径
    支持开发环境和 PyInstaller 打包后的环境

    Args:
        relative_path: 相对于项目根目录的路径

    Returns:
        资源文件的绝对路径
    """
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller 打包后的环境
        base_path = Path(sys._MEIPASS)
    else:
        # 开发环境 - 项目根目录
        base_path = Path(__file__).parent.parent.parent

    return base_path / relative_path


def get_file_info(file_path: str) -> Dict[str, Any]:
    """获取文件信息"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    if not path.is_file():
        raise ValueError(f"路径不是文件: {file_path}")
    stat = path.stat()
    return {
        "name": path.name,
        "path": str(path.absolute()),
        "size": stat.st_size,
        "modified": stat.st_mtime,
    }


def format_file_size(bytes_size: int) -> str:
    """格式化文件大小"""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    elif bytes_size < 1024 * 1024 * 1024:
        return f"{bytes_size / (1024 * 1024):.1f} MB"
    else:
        return f"{bytes_size / (1024 * 1024 * 1024):.2f} GB"


def select_files(
    parent_widget: Optional[QWidget] = None,
    file_filter: str = "PDF Files (*.pdf)",
    multiple: bool = True,
) -> List[str]:
    """选择文件对话框"""
    if multiple:
        files, _ = QFileDialog.getOpenFileNames(
            parent_widget, "选择 PDF 文件", "", file_filter
        )
        return files
    else:
        file, _ = QFileDialog.getOpenFileName(
            parent_widget, "选择 PDF 文件", "", file_filter
        )
        return [file] if file else []


def select_directory(
    parent_widget: Optional[QWidget] = None, caption: str = "选择目录"
) -> Optional[str]:
    """选择目录对话框"""
    directory = QFileDialog.getExistingDirectory(parent_widget, caption, "")
    return directory if directory else None


def save_file(
    parent_widget: Optional[QWidget] = None,
    caption: str = "保存文件",
    file_filter: str = "All Files (*.*)",
    default_name: str = "",
) -> Optional[str]:
    """保存文件对话框"""
    file_path, _ = QFileDialog.getSaveFileName(
        parent_widget, caption, default_name, file_filter
    )
    return file_path if file_path else None


def open_file_location(file_path: str) -> bool:
    """打开文件所在位置"""
    import platform
    import subprocess

    path = Path(file_path).absolute()
    if not path.exists():
        logger.warning(f"文件不存在，无法打开位置: {path}")
        return False

    try:
        if platform.system() == "Windows":
            subprocess.run(["explorer", "/select,", str(path)], check=False)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", "-R", str(path)], check=False)
        else:  # Linux
            subprocess.run(["xdg-open", str(path.parent)], check=False)
        return True
    except (OSError, subprocess.SubprocessError) as e:
        logger.error(f"打开文件位置失败: {e}")
        return False


def open_file(file_path: str) -> bool:
    """打开文件"""
    import platform
    import subprocess

    path = Path(file_path).absolute()
    if not path.exists() or not path.is_file():
        logger.warning(f"文件不存在或不是文件: {path}")
        return False

    try:
        if platform.system() == "Windows":
            os.startfile(str(path))
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", str(path)], check=False)
        else:  # Linux
            subprocess.run(["xdg-open", str(path)], check=False)
        return True
    except (OSError, subprocess.SubprocessError) as e:
        logger.error(f"打开文件失败: {e}")
        return False


def ensure_directory(directory: str) -> Path:
    """确保目录存在"""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_extension(file_path: str) -> str:
    """获取文件扩展名"""
    return Path(file_path).suffix.lower()


def is_pdf_file(file_path: str) -> bool:
    """检查是否为 PDF 文件"""
    return get_file_extension(file_path) == ".pdf"


def get_filename_without_extension(file_path: str) -> str:
    """获取不带扩展名的文件名"""
    return Path(file_path).stem


def get_parent_directory(file_path: str) -> str:
    """获取父目录"""
    return str(Path(file_path).parent)


def file_exists(file_path: str) -> bool:
    """检查文件是否存在"""
    return Path(file_path).exists() and Path(file_path).is_file()


def directory_exists(directory: str) -> bool:
    """检查目录是否存在"""
    return Path(directory).exists() and Path(directory).is_dir()
