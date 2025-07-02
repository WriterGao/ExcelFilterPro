"""
辅助函数模块
提供通用的辅助功能
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import re

from .constants import SUPPORTED_EXCEL_FORMATS, MAX_FILE_SIZE
from .exceptions import InvalidFileFormatError, FileSizeExceededError


def resource_path(relative_path: str) -> str:
    """
    获取资源文件的绝对路径
    支持开发环境和PyInstaller打包环境
    
    Args:
        relative_path: 相对路径
        
    Returns:
        资源文件的绝对路径
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包环境
        return os.path.join(sys._MEIPASS, relative_path)
    
    # 开发环境
    current_dir = Path(__file__).parent.parent.parent
    return str(current_dir / relative_path)


def validate_excel_file(file_path: str) -> bool:
    """
    验证Excel文件是否有效
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件是否有效
        
    Raises:
        InvalidFileFormatError: 文件格式不支持
        FileSizeExceededError: 文件大小超限
        FileNotFoundError: 文件不存在
    """
    file_path_obj = Path(file_path)
    
    # 检查文件是否存在
    if not file_path_obj.exists():
        raise FileNotFoundError(f"文件不存在: {file_path_obj}")
    
    # 检查文件格式
    if file_path_obj.suffix.lower() not in SUPPORTED_EXCEL_FORMATS:
        raise InvalidFileFormatError(
            f"不支持的文件格式: {file_path_obj.suffix}。"
            f"支持的格式: {', '.join(SUPPORTED_EXCEL_FORMATS)}"
        )
    
    # 检查文件大小
    file_size = file_path_obj.stat().st_size
    if file_size > MAX_FILE_SIZE:
        raise FileSizeExceededError(
            f"文件大小超限: {file_size / (1024*1024):.1f}MB。"
            f"最大支持: {MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )
    
    return True


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        清理后的文件名
    """
    # 移除或替换非法字符
    illegal_chars = r'[<>:"/\\|?*]'
    filename = re.sub(illegal_chars, '_', filename)
    
    # 移除多余的空格和点
    filename = filename.strip('. ')
    
    # 确保文件名不为空
    if not filename:
        filename = "unnamed"
    
    return filename


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小显示
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        格式化的文件大小字符串
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    安全获取字典值
    
    Args:
        dictionary: 字典对象
        key: 键名
        default: 默认值
        
    Returns:
        字典值或默认值
    """
    try:
        return dictionary.get(key, default)
    except (AttributeError, TypeError):
        return default


def validate_condition_value(value: str, data_type: str) -> Any:
    """
    验证并转换筛选条件值
    
    Args:
        value: 输入值
        data_type: 数据类型
        
    Returns:
        转换后的值
        
    Raises:
        ValueError: 值转换失败
    """
    if data_type == 'number':
        try:
            # 尝试转换为整数
            if '.' not in value:
                return int(value)
            # 转换为浮点数
            return float(value)
        except ValueError:
            raise ValueError(f"无法将 '{value}' 转换为数字")
    
    elif data_type == 'boolean':
        if value.lower() in ('true', '1', 'yes', '是', '真'):
            return True
        elif value.lower() in ('false', '0', 'no', '否', '假'):
            return False
        else:
            raise ValueError(f"无法将 '{value}' 转换为布尔值")
    
    elif data_type == 'datetime':
        try:
            from datetime import datetime
            # 支持多种日期格式
            formats = [
                '%Y-%m-%d',
                '%Y/%m/%d',
                '%Y-%m-%d %H:%M:%S',
                '%Y/%m/%d %H:%M:%S'
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
            raise ValueError(f"无法解析日期格式: {value}")
        except ImportError:
            raise ValueError("日期处理功能不可用")
    
    else:  # string
        return str(value)


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    截断文本并添加省略号
    
    Args:
        text: 原始文本
        max_length: 最大长度
        
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..." 