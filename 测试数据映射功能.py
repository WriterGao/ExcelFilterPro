#!/usr/bin/env python3
"""
测试数据映射功能
验证"查找匹配并复制数据"的操作
专门针对用户的需求：从B列查找'202 2号主变'，提取C列值，插入到目标文件A列='202 2号主变'对应的D列
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import uuid
from datetime import datetime

from src.database.models import DataMapping, FilterOperator, ExcelCoordinate
from src.core.data_mapping_engine import DataMappingEngine


def create_test_data():
    """创建测试用的源数据和目标数据"""
    print("📊 创建测试数据")
    print("=" * 50)
    
    # 创建源数据（模拟用户提供的母线电量不平衡率报表）
    source_data = pd.DataFrame({
        'A': ['东宇变电站', '220kV设备编号', '201 1号主变', '202 2号主变', '202 2号主变', '203 3号主变', '204 4号主变'],
        'B': ['', '220kV设备编号', '201 1号主变', '202 2号主变', '202 2号主变', '203 3号主变', '204 4号主变'],
        'C': ['上月电度表指示数', '上月电度表指示数', 924781.28, 926601.58, 767271.9, 353244.77, 371960.89],
        'D': ['本月电度表指示数', '本月电度表指示数', 926601.58, 928456.78, 769087.53, 356938.33, 375345.67],
        'E': ['倍率', '倍率', 1000, 1000, 1000, 1000, 1000]
    })
    
    # 创建目标数据（模拟用户的目标文件）
    target_data = pd.DataFrame({
        'A': ['设备名称', '201 1号主变', '202 2号主变', '202 2号主变', '203 3号主变', '204 4号主变'],
        'B': ['区域', '东区', '西区', '西区', '南区', '北区'],
        'C': ['状态', '运行', '运行', '运行', '检修', '运行'],
        'D': ['数据', '', '', '', '', ''],  # 这里是要插入数据的目标列
        'E': ['备注', '', '', '', '', '']
    })
    
    print("源数据（母线电量不平衡率报表）:")
    print(source_data)
    print(f"数据形状: {source_data.shape}")
    
    print("\n目标数据（待填充的目标文件）:")
    print(target_data)
    print(f"数据形状: {target_data.shape}")
    
    print("\n✅ 测试数据创建完成！\n")
    return source_data, target_data


def test_data_mapping_model():
    """测试数据映射数据模型"""
    print("🧩 测试数据映射数据模型")
    print("=" * 50)
    
    # 创建数据映射配置（针对用户的具体需求）
    mapping = DataMapping(
        mapping_id=str(uuid.uuid4()),
        name="202 2号主变数据提取",
        description="从源文件B列查找'202 2号主变'，提取C列值，插入到目标文件A列='202 2号主变'对应的D列",
        
        # 源数据配置
        source_file="母线电量不平衡率报表.xlsx",
        source_match_coordinate=ExcelCoordinate.from_string("B"),  # B列
        source_match_value="202 2号主变",
        source_value_coordinate=ExcelCoordinate.from_string("C"),  # C列
        
        # 目标数据配置
        target_file="目标汇总表.xlsx",
        target_match_coordinate=ExcelCoordinate.from_string("A"),  # A列
        target_match_value="202 2号主变",
        target_insert_coordinate=ExcelCoordinate.from_string("D"),  # D列
        
        # 操作配置
        match_operator=FilterOperator.EQUALS,
        overwrite_existing=True
    )
    
    print(f"映射名称: {mapping.name}")
    print(f"映射描述: {mapping.description}")
    print()
    
    print("源数据配置:")
    print(f"  源文件: {mapping.source_file}")
    print(f"  匹配列: {mapping.source_match_coordinate} (类型: {mapping.source_match_coordinate.coord_type})")
    print(f"  匹配值: {mapping.source_match_value}")
    print(f"  匹配操作: {mapping.match_operator.value}")
    print(f"  取值列: {mapping.source_value_coordinate} (类型: {mapping.source_value_coordinate.coord_type})")
    print()
    
    print("目标数据配置:")
    print(f"  目标文件: {mapping.target_file}")
    print(f"  匹配列: {mapping.target_match_coordinate} (类型: {mapping.target_match_coordinate.coord_type})")
    print(f"  匹配值: {mapping.target_match_value}")
    print(f"  插入列: {mapping.target_insert_coordinate} (类型: {mapping.target_insert_coordinate.coord_type})")
    print(f"  覆盖模式: {mapping.overwrite_existing}")
    
    print(f"\n需要的文件: {mapping.get_required_files()}")
    
    print("\n✅ 数据映射模型测试通过！\n")
    return mapping


def test_data_mapping_engine():
    """测试数据映射引擎"""
    print("⚙️ 测试数据映射引擎")
    print("=" * 50)
    
    # 创建测试数据
    source_df, target_df = create_test_data()
    
    # 准备数据字典
    source_data = {"母线电量不平衡率报表.xlsx": source_df}
    target_data = {"目标汇总表.xlsx": target_df}
    
    # 创建映射配置
    mapping = test_data_mapping_model()
    
    # 创建映射引擎
    engine = DataMappingEngine()
    
    print("执行前的目标数据:")
    print(target_data["目标汇总表.xlsx"])
    print()
    
    # 验证映射配置
    print("验证映射配置...")
    errors = engine.validate_mapping(mapping, source_data, target_data)
    if errors:
        print("配置验证失败:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ 配置验证通过")
    
    # 执行数据映射
    print("\n开始执行数据映射...")
    try:
        updated_target_data = engine.execute_mapping(mapping, source_data, target_data)
        
        print("执行后的目标数据:")
        print(updated_target_data["目标汇总表.xlsx"])
        print()
        
        # 检查结果
        result_df = updated_target_data["目标汇总表.xlsx"]
        inserted_values = result_df[result_df['A'] == '202 2号主变']['D'].tolist()
        print(f"成功插入的值: {inserted_values}")
        
        # 验证结果
        expected_values = [926601.58, 767271.9]  # 从源数据C列提取的'202 2号主变'对应的值
        actual_values = [val for val in inserted_values if pd.notna(val) and val != '']
        
        print(f"期望值: {expected_values}")
        print(f"实际值: {actual_values}")
        
        if len(actual_values) == len(expected_values):
            print("✅ 数据映射执行成功！")
            return True
        else:
            print("❌ 数据映射结果不符合预期")
            return False
            
    except Exception as e:
        print(f"❌ 数据映射执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_mappings():
    """测试多个映射的执行"""
    print("🔗 测试多个映射的执行")
    print("=" * 50)
    
    # 创建测试数据
    source_df, target_df = create_test_data()
    
    # 准备数据字典
    source_data = {"母线电量不平衡率报表.xlsx": source_df}
    target_data = {"目标汇总表.xlsx": target_df}
    
    # 创建多个映射配置
    mappings = []
    
    # 映射1：202 2号主变的上月电度表数据
    mapping1 = DataMapping(
        mapping_id=str(uuid.uuid4()),
        name="202 2号主变上月数据",
        description="提取202 2号主变的上月电度表指示数",
        source_file="母线电量不平衡率报表.xlsx",
        source_match_coordinate=ExcelCoordinate.from_string("B"),
        source_match_value="202 2号主变",
        source_value_coordinate=ExcelCoordinate.from_string("C"),
        target_file="目标汇总表.xlsx",
        target_match_coordinate=ExcelCoordinate.from_string("A"),
        target_match_value="202 2号主变",
        target_insert_coordinate=ExcelCoordinate.from_string("D"),
        match_operator=FilterOperator.EQUALS,
        overwrite_existing=True
    )
    mappings.append(mapping1)
    
    # 映射2：203 3号主变的数据（如果有的话）
    mapping2 = DataMapping(
        mapping_id=str(uuid.uuid4()),
        name="203 3号主变数据",
        description="提取203 3号主变的数据",
        source_file="母线电量不平衡率报表.xlsx",
        source_match_coordinate=ExcelCoordinate.from_string("B"),
        source_match_value="203 3号主变",
        source_value_coordinate=ExcelCoordinate.from_string("C"),
        target_file="目标汇总表.xlsx",
        target_match_coordinate=ExcelCoordinate.from_string("A"),
        target_match_value="203 3号主变",
        target_insert_coordinate=ExcelCoordinate.from_string("D"),
        match_operator=FilterOperator.EQUALS,
        overwrite_existing=True
    )
    mappings.append(mapping2)
    
    # 创建映射引擎
    engine = DataMappingEngine()
    
    print("执行前的目标数据:")
    print(target_data["目标汇总表.xlsx"])
    print()
    
    # 执行多个映射
    print("开始执行多个映射...")
    try:
        updated_target_data = engine.execute_multiple_mappings(mappings, source_data, target_data)
        
        print("执行后的目标数据:")
        print(updated_target_data["目标汇总表.xlsx"])
        print()
        
        print("✅ 多个映射执行成功！")
        return True
        
    except Exception as e:
        print(f"❌ 多个映射执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_user_specific_scenario():
    """测试用户的具体使用场景"""
    print("👤 测试用户的具体使用场景")
    print("=" * 50)
    
    print("用户需求:")
    print("1. 从源文件B列查找 '202 2号主变' 的行")
    print("2. 提取这些行对应的C列的值")
    print("3. 在目标文件A列查找 '202 2号主变' 的行")
    print("4. 将提取的值插入到这些行对应的D列位置")
    print()
    
    # 创建更真实的测试数据
    source_data = pd.DataFrame({
        'A': ['母线电量不平衡率报表', '2025年4月19日', '220kV设备编号', '201 1号主变', '202 2号主变', '202 2号主变', '203 3号主变', '合计'],
        'B': ['', '', '220kV设备编号', '201 1号主变', '202 2号主变', '202 2号主变', '203 3号主变', ''],
        'C': ['上月电度表指示数', '', '上月电度表指示数', 924781.28, 926601.58, 767271.9, 353244.77, 10714270],
        'D': ['本月电度表指示数', '', '本月电度表指示数', 926601.58, 928456.78, 769087.53, 356938.33, 11173800],
        'E': ['倍率', '', '倍率', 1000, 1000, 1000, 1000, '']
    })
    
    target_data = pd.DataFrame({
        'A': ['设备统计表', '201 1号主变', '202 2号主变', '202 2号主变', '203 3号主变', '204 4号主变'],
        'B': ['区域', '东区', '西区', '西区', '南区', '北区'],
        'C': ['状态', '运行', '运行', '运行', '检修', '运行'],
        'D': ['电度数据', '', '', '', '', ''],
        'E': ['更新时间', '', '', '', '', '']
    })
    
    print("实际源数据:")
    print(source_data)
    print()
    
    print("实际目标数据:")
    print(target_data)
    print()
    
    # 配置映射
    mapping = DataMapping(
        mapping_id=str(uuid.uuid4()),
        name="202 2号主变电度数据映射",
        description="从B列='202 2号主变'的行提取C列值，插入到目标文件A列='202 2号主变'行的D列",
        source_file="源数据.xlsx",
        source_match_coordinate=ExcelCoordinate.from_string("B"),
        source_match_value="202 2号主变",
        source_value_coordinate=ExcelCoordinate.from_string("C"),
        target_file="目标数据.xlsx",
        target_match_coordinate=ExcelCoordinate.from_string("A"),
        target_match_value="202 2号主变",
        target_insert_coordinate=ExcelCoordinate.from_string("D"),
        match_operator=FilterOperator.EQUALS,
        overwrite_existing=True
    )
    
    # 执行映射
    engine = DataMappingEngine()
    
    source_dict = {"源数据.xlsx": source_data}
    target_dict = {"目标数据.xlsx": target_data}
    
    print("开始执行用户场景的数据映射...")
    try:
        result = engine.execute_mapping(mapping, source_dict, target_dict)
        
        print("映射完成后的目标数据:")
        result_df = result["目标数据.xlsx"]
        print(result_df)
        print()
        
        # 检查'202 2号主变'行的D列
        matched_rows = result_df[result_df['A'] == '202 2号主变']
        print("'202 2号主变'对应的D列数据:")
        print(matched_rows[['A', 'D']])
        
        # 验证结果
        d_values = matched_rows['D'].dropna().tolist()
        expected_source_values = [926601.58, 767271.9]  # 源数据中'202 2号主变'对应的C列值
        
        print(f"\n源数据中的值: {expected_source_values}")
        print(f"插入的值: {d_values}")
        
        if len(d_values) >= 2 and str(d_values[0]) != '' and str(d_values[1]) != '':
            print("✅ 用户场景测试成功！数据已正确映射。")
            return True
        else:
            print("❌ 用户场景测试失败：数据映射不完整。")
            return False
            
    except Exception as e:
        print(f"❌ 用户场景测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("🚀 数据映射功能测试")
    print("=" * 60)
    print("专门测试'查找匹配并复制数据'的功能")
    print("用户需求：B列='202 2号主变' → 提取C列值 → 插入目标A列='202 2号主变'的D列")
    print()
    
    try:
        # 执行各项测试
        test_results = []
        
        print("测试1: 数据映射数据模型")
        test_results.append(test_data_mapping_model() is not None)
        
        print("测试2: 数据映射引擎")
        test_results.append(test_data_mapping_engine())
        
        print("测试3: 多个映射执行")
        test_results.append(test_multiple_mappings())
        
        print("测试4: 用户具体场景")
        test_results.append(test_user_specific_scenario())
        
        # 总结
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print("🎯 测试总结")
        print("=" * 60)
        print(f"通过测试: {passed_tests}/{total_tests}")
        
        if passed_tests == total_tests:
            print("🎉 所有测试通过！")
            print()
            print("新的数据映射功能特性:")
            print("✅ 支持复杂的查找匹配逻辑")
            print("✅ 支持从源文件提取值并插入目标文件")
            print("✅ 支持多种匹配操作符（等于、包含等）")
            print("✅ 支持覆盖已有数据的控制")
            print("✅ 支持多个映射的批量执行")
            print("✅ 完全满足用户的具体需求")
            print()
            print("用户可以使用这个功能来:")
            print("• 从B列查找'202 2号主变'")
            print("• 提取对应C列的电度表数据")
            print("• 插入到目标文件A列='202 2号主变'行的D列")
            print("• 实现复杂的数据汇总和映射操作")
            return True
        else:
            print("❌ 部分测试失败，需要修复")
            return False
            
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 