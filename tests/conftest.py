"""
pytest配置文件
提供测试fixtures和配置
"""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path


@pytest.fixture
def sample_dataframe():
    """提供标准测试数据"""
    return pd.DataFrame({
        '姓名': ['张三', '李四', '王五', '赵六'],
        '年龄': [25, 30, 35, 40],
        '部门': ['销售', '技术', '销售', '财务'],
        '工资': [8000, 12000, 9000, 15000]
    })


@pytest.fixture
def large_dataframe():
    """提供大数据量测试数据"""
    import numpy as np
    return pd.DataFrame({
        '姓名': [f'用户{i}' for i in range(1000)],
        '年龄': np.random.randint(18, 65, 1000),
        '工资': np.random.randint(3000, 20000, 1000)
    })


@pytest.fixture
def temp_excel_file(sample_dataframe):
    """创建临时Excel测试文件"""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        sample_dataframe.to_excel(f.name, index=False)
        yield f.name
    
    # 清理临时文件
    if os.path.exists(f.name):
        os.unlink(f.name)


@pytest.fixture
def temp_directory():
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def app_config():
    """提供应用配置"""
    return {
        'database_name': ':memory:',  # 使用内存数据库进行测试
        'log_level': 'DEBUG',
        'max_file_size': 1024 * 1024,  # 1MB
        'max_file_count': 5
    } 