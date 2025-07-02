#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel筛选器演示程序
展示核心功能的使用方法
"""

import pandas as pd
from pathlib import Path
import sys

# 添加src目录到Python路径
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from src.core.enhanced_excel_processor import EnhancedExcelProcessor
from src.core.data_mapping_engine import DataMappingEngine
from src.database.models import DataMapping, FilterOperator, ExcelCoordinate


def demo_enhanced_processor():
    """演示增强Excel处理器"""
    print("=" * 50)
    print("演示增强Excel处理器")
    print("=" * 50)
    
    processor = EnhancedExcelProcessor()
    
    # 创建示例数据
    test_data_dir = Path("test_data")
    test_data_dir.mkdir(exist_ok=True)
    
    # 创建示例Excel文件
    sample_data = {
        'A': ['名称', '产品A', '产品B', '产品C'],
        'B': ['价格', 100, 200, 300],
        'C': ['库存', 50, 30, 20],
        'D': ['分类', '电子', '家具', '服装']
    }
    
    df = pd.DataFrame(sample_data)
    sample_file = test_data_dir / "sample.xlsx"
    df.to_excel(sample_file, index=False, header=False)
    
    print(f"创建示例文件: {sample_file}")
    
    # 加载文件
    try:
        processor.load_excel_files([str(sample_file)])
        print("✅ 文件加载成功")
        
        # 显示数据信息
        for key, data in processor.data_frames.items():
            print(f"数据文件: {key}")
            print(f"形状: {data.shape}")
            print(f"前3行:\n{data.head(3)}")
            print()
            
    except Exception as e:
        print(f"❌ 文件加载失败: {e}")
    
    return processor


def demo_data_mapping():
    """演示数据映射功能"""
    print("=" * 50)
    print("演示数据映射功能")
    print("=" * 50)
    
    processor = demo_enhanced_processor()
    engine = DataMappingEngine()
    
    # 创建示例映射配置
    try:
        # 创建坐标对象
        source_match_coord = ExcelCoordinate.from_string("A1:A10")
        source_value_coord = ExcelCoordinate.from_string("B1:B10")
        target_match_coord = ExcelCoordinate.from_string("A1:A10")
        target_insert_coord = ExcelCoordinate.from_string("C1:C10")
        
        mapping = DataMapping(
            name="价格映射示例",
            source_file="sample.xlsx",
            target_file="template.xlsx",
            source_match_coordinate=source_match_coord,
            source_match_value="产品A",
            source_value_coordinate=source_value_coord,
            target_match_coordinate=target_match_coord,
            target_match_value="产品A",
            target_insert_coordinate=target_insert_coord,
            match_operator=FilterOperator.EQUALS,
            overwrite_existing=True
        )
        
        print("✅ 映射配置创建成功")
        print(f"映射名称: {mapping.name}")
        print(f"源文件: {mapping.source_file}")
        print(f"目标文件: {mapping.target_file}")
        
    except Exception as e:
        print(f"❌ 映射配置创建失败: {e}")


def main():
    """主演示函数"""
    print("🚀 Excel筛选器功能演示")
    print()
    
    # 演示增强处理器
    processor = demo_enhanced_processor()
    
    # 演示数据映射
    demo_data_mapping()
    
    print("=" * 50)
    print("演示完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
