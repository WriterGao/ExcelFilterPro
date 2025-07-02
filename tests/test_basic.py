#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础功能测试
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import sys

# 添加src目录到测试路径
current_dir = Path(__file__).parent.parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from src.core.enhanced_excel_processor import EnhancedExcelProcessor
from src.core.data_mapping_engine import DataMappingEngine
from src.database.models import DataMapping, FilterOperator, ExcelCoordinate


class TestEnhancedExcelProcessor:
    """测试增强Excel处理器"""
    
    def setup_method(self):
        """测试前准备"""
        self.processor = EnhancedExcelProcessor()
        
        # 创建临时测试文件
        self.test_data = {
            'A': ['姓名', '张三', '李四', '王五'],
            'B': ['年龄', 25, 30, 35],
            'C': ['城市', '北京', '上海', '广州']
        }
        
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        df = pd.DataFrame(self.test_data)
        df.to_excel(self.temp_file.name, index=False, header=False)
        self.temp_file.close()
    
    def teardown_method(self):
        """测试后清理"""
        Path(self.temp_file.name).unlink(missing_ok=True)
    
    def test_load_excel_file(self):
        """测试加载Excel文件"""
        # 测试加载单个文件
        self.processor.load_excel_files([self.temp_file.name])
        
        assert len(self.processor.data_frames) > 0
        
        # 检查数据内容
        for key, df in self.processor.data_frames.items():
            assert not df.empty
            assert df.shape[0] == 4  # 4行数据
            assert df.shape[1] == 3  # 3列数据


class TestDataMappingEngine:
    """测试数据映射引擎"""
    
    def setup_method(self):
        """测试前准备"""
        self.engine = DataMappingEngine()
    
    def test_engine_initialization(self):
        """测试引擎初始化"""
        assert self.engine is not None
        assert hasattr(self.engine, 'execute_mapping')
        assert hasattr(self.engine, 'execute_multiple_mappings')


if __name__ == "__main__":
    pytest.main([__file__])
