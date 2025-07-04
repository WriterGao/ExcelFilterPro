"""
数据映射引擎
支持"查找匹配并复制数据"的操作
"""

import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from ..utils.logger import get_logger
from ..database.models import DataMapping, FilterOperator, ExcelCoordinate


class DataMappingEngine:
    """数据映射引擎"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.logger.info("📋 数据映射引擎初始化完成")
    
    def execute_mapping(self, mapping: DataMapping, source_data: Dict[str, pd.DataFrame], 
                       target_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        执行数据映射
        
        Args:
            mapping: 数据映射配置
            source_data: 源数据 {文件名: DataFrame}
            target_data: 目标数据 {文件名: DataFrame}
            
        Returns:
            更新后的目标数据
        """
        try:
            self.logger.info(f"🚀 开始执行数据映射: {mapping.name}")
            self.logger.info(f"📝 映射描述: {mapping.description}")
            
            # 打印映射配置详情
            self.logger.info(f"🔧 映射配置详情:")
            self.logger.info(f"   源文件: {mapping.source_file}")
            self.logger.info(f"   源匹配列: {mapping.source_match_coordinate}")
            self.logger.info(f"   源匹配值: '{mapping.source_match_value}'")
            self.logger.info(f"   源取值列: {mapping.source_value_coordinate}")
            self.logger.info(f"   目标文件: {mapping.target_file}")
            self.logger.info(f"   目标匹配列: {mapping.target_match_coordinate}")
            self.logger.info(f"   目标匹配值: '{mapping.target_match_value}'")
            self.logger.info(f"   目标插入列: {mapping.target_insert_coordinate}")
            self.logger.info(f"   匹配操作符: {mapping.match_operator.value}")
            
            # 打印源数据详情
            if mapping.source_file in source_data:
                source_df = source_data[mapping.source_file]
                self.logger.info(f"📊 源数据文件详情:")
                self.logger.info(f"   文件名: {mapping.source_file}")
                self.logger.info(f"   数据形状: {source_df.shape} (行数: {source_df.shape[0]}, 列数: {source_df.shape[1]})")
                
                # 显示源数据的前几行
                self.logger.info(f"   源数据前5行:")
                for idx, row in source_df.head(5).iterrows():
                    row_data = [str(val)[:20] + "..." if len(str(val)) > 20 else str(val) for val in row.values]
                    self.logger.info(f"     第{idx+1}行: {row_data}")
            
            # 打印目标数据详情
            if mapping.target_file in target_data:
                target_df = target_data[mapping.target_file]
                self.logger.info(f"🎯 目标数据文件详情:")
                self.logger.info(f"   文件名: {mapping.target_file}")
                self.logger.info(f"   数据形状: {target_df.shape} (行数: {target_df.shape[0]}, 列数: {target_df.shape[1]})")
                
                # 显示目标数据的前几行
                self.logger.info(f"   目标数据前5行:")
                for idx, row in target_df.head(5).iterrows():
                    row_data = [str(val)[:20] + "..." if len(str(val)) > 20 else str(val) for val in row.values]
                    self.logger.info(f"     第{idx+1}行: {row_data}")
            
            # 1. 从源文件中查找匹配的数据并提取值
            source_values = self._extract_source_values(mapping, source_data)
            if not source_values:
                self.logger.warning(f"❌ 源文件中未找到匹配的数据: {mapping.source_match_value}")
                return target_data
            
            # 2. 在目标文件中找到匹配的位置
            target_positions = self._find_target_positions(mapping, target_data)
            if not target_positions:
                self.logger.info(f"❌ 目标文件 {mapping.target_file} 中未找到匹配值 '{mapping.target_match_value}' 的位置，将跳过此映射")
                # 打印调试信息，帮助用户了解目标文件的数据结构
                if mapping.target_file in target_data:
                    df = target_data[mapping.target_file]
                    match_col_index = self._get_column_index(mapping.target_match_coordinate, df)
                    if match_col_index < len(df.columns):
                        unique_values = df.iloc[:, match_col_index].dropna().unique()[:10]  # 只显示前10个唯一值
                        self.logger.info(f"   目标匹配列的可用值示例: {list(unique_values)}")
                return target_data
            
            # 3. 将源值插入到目标位置
            updated_target_data = self._insert_values(mapping, target_data, source_values, target_positions)
            
            self.logger.info(f"✅ 数据映射完成: 处理了 {len(source_values)} 个源值，{len(target_positions)} 个目标位置")
            return updated_target_data
            
        except Exception as e:
            self.logger.error(f"❌ 执行数据映射失败: {e}")
            raise
    
    def _extract_source_values(self, mapping: DataMapping, source_data: Dict[str, pd.DataFrame]) -> List[Any]:
        """从源文件中提取匹配的值"""
        if mapping.source_file not in source_data:
            raise ValueError(f"源文件未找到: {mapping.source_file}")
        
        df = source_data[mapping.source_file]
        self.logger.info(f"🔍 开始从源文件提取数据:")
        
        # 获取源匹配列和取值列的索引
        match_col_index = self._get_column_index(mapping.source_match_coordinate, df)
        value_col_index = self._get_column_index(mapping.source_value_coordinate, df)
        
        self.logger.info(f"   源匹配列索引: {match_col_index} ({mapping.source_match_coordinate})")
        self.logger.info(f"   源取值列索引: {value_col_index} ({mapping.source_value_coordinate})")
        
        if match_col_index >= len(df.columns) or value_col_index >= len(df.columns):
            raise ValueError("列索引超出范围")
        
        # 查找匹配的行
        match_column = df.iloc[:, match_col_index]
        value_column = df.iloc[:, value_col_index]
        
        # 新增：只在指定行范围查找
        if mapping.source_match_row_range:
            start, end = mapping.source_match_row_range
            # Excel行号从1开始，DataFrame索引从0开始
            match_column = match_column.iloc[start-1:end]
            value_column = value_column.iloc[start-1:end]
            self.logger.info(f"   仅在第{start}行到第{end}行查找匹配")
        
        # 打印匹配列的所有值
        self.logger.info(f"   源匹配列(第{match_col_index+1}列)的所有值:")
        for idx, val in match_column.items():
            val_str = str(val) if pd.notna(val) else "空值"
            if isinstance(idx, int):
                row_no = idx + 1
            else:
                row_no = idx
            self.logger.info(f"     第{row_no}行: '{val_str}'")
        
        self.logger.info(f"   正在查找匹配值: '{mapping.source_match_value}' (操作符: {mapping.match_operator.value})")
        
        # 根据操作符进行匹配
        matched_rows = self._apply_match_operator(
            match_column, mapping.source_match_value, mapping.match_operator
        )
        
        # 显示匹配结果
        matched_indices = matched_rows[matched_rows].index.tolist()
        self.logger.info(f"   找到匹配的行索引: {matched_indices}")
        
        if matched_indices:
            self.logger.info(f"   匹配行的详细信息:")
            for idx in matched_indices:
                match_val = match_column.loc[idx]
                value_val = value_column.loc[idx]
                if isinstance(idx, int):
                    row_no = idx + 1
                else:
                    row_no = idx
                self.logger.info(f"     第{row_no}行: 匹配列='{match_val}', 取值列='{value_val}'")
        
        # 提取匹配行的值
        source_values = value_column[matched_rows].dropna().tolist()
        
        self.logger.info(f"✅ 从源文件提取到 {len(source_values)} 个值: {source_values}")
        return source_values
    
    def _find_target_positions(self, mapping: DataMapping, target_data: Dict[str, pd.DataFrame]) -> List[int]:
        """在目标文件中查找匹配的位置"""
        if mapping.target_file not in target_data:
            raise ValueError(f"目标文件未找到: {mapping.target_file}")
        
        df = target_data[mapping.target_file]
        self.logger.info(f"🎯 开始在目标文件中查找插入位置:")
        
        # 获取目标匹配列的索引
        match_col_index = self._get_column_index(mapping.target_match_coordinate, df)
        
        self.logger.info(f"   目标匹配列索引: {match_col_index} ({mapping.target_match_coordinate})")
        
        if match_col_index >= len(df.columns):
            raise ValueError("目标匹配列索引超出范围")
        
        # 查找匹配的行
        match_column = df.iloc[:, match_col_index]
        
        # 新增：只在指定行范围查找
        if mapping.target_match_row_range:
            start, end = mapping.target_match_row_range
            match_column = match_column.iloc[start-1:end]
            self.logger.info(f"   仅在第{start}行到第{end}行查找匹配")
        
        # 打印目标匹配列的所有值
        self.logger.info(f"   目标匹配列(第{match_col_index+1}列)的所有值:")
        for idx, val in match_column.items():
            val_str = str(val) if pd.notna(val) else "空值"
            if isinstance(idx, int):
                row_no = idx + 1
            else:
                row_no = idx
            self.logger.info(f"     第{row_no}行: '{val_str}'")
        
        self.logger.info(f"   正在查找目标匹配值: '{mapping.target_match_value}'")
        
        # 根据操作符进行匹配（目标匹配通常使用等于操作符）
        matched_rows = self._apply_match_operator(
            match_column, mapping.target_match_value, mapping.match_operator
        )
        
        # 获取匹配行的索引
        target_positions = matched_rows[matched_rows].index.tolist()
        
        self.logger.info(f"   找到目标匹配行索引: {target_positions}")
        
        if target_positions:
            self.logger.info(f"   目标匹配行的详细信息:")
            for pos in target_positions:
                match_val = match_column.loc[pos]
                if isinstance(pos, int):
                    row_no = pos + 1
                else:
                    row_no = pos
                self.logger.info(f"     第{row_no}行: 匹配列='{match_val}'")
        
        self.logger.info(f"✅ 在目标文件找到 {len(target_positions)} 个匹配位置")
        return target_positions
    
    def _insert_values(self, mapping: DataMapping, target_data: Dict[str, pd.DataFrame], 
                      source_values: List[Any], target_positions: List[int]) -> Dict[str, pd.DataFrame]:
        """将源值插入到目标位置"""
        updated_target_data = target_data.copy()
        df = updated_target_data[mapping.target_file].copy()
        
        self.logger.info(f"📝 开始插入数据到目标文件:")
        
        # 获取目标插入列的索引
        insert_col_index = self._get_column_index(mapping.target_insert_coordinate, df)
        
        self.logger.info(f"   目标插入列索引: {insert_col_index} ({mapping.target_insert_coordinate})")
        
        if insert_col_index >= len(df.columns):
            raise ValueError("目标插入列索引超出范围")
        
        # 显示插入前的目标列状态
        insert_column = df.iloc[:, insert_col_index]
        self.logger.info(f"   插入前目标列(第{insert_col_index+1}列)的值:")
        for idx, val in insert_column.items():
            val_str = str(val) if pd.notna(val) else "空值"
            if isinstance(idx, int):
                row_no = idx + 1
            else:
                row_no = idx
            self.logger.info(f"     第{row_no}行: '{val_str}'")
        
        # 插入数据
        insert_count = 0
        self.logger.info(f"   准备插入的源值: {source_values}")
        self.logger.info(f"   目标插入位置: {[pos+1 for pos in target_positions]} (行号)")
        
        for i, pos in enumerate(target_positions):
            if i < len(source_values):
                old_value = df.iloc[pos, insert_col_index]
                new_value = source_values[i]
                
                # 检查是否允许覆盖
                if mapping.overwrite_existing or pd.isna(old_value):
                    df.iloc[pos, insert_col_index] = new_value
                    insert_count += 1
                    self.logger.info(f"   ✅ 第{pos+1}行: '{old_value}' → '{new_value}'")
                else:
                    self.logger.info(f"   ⏭️  第{pos+1}行: 跳过覆盖 '{old_value}' (overwrite_existing=False)")
            else:
                # 源值数量不足，可以重复使用最后一个值或者停止
                if source_values:  # 如果有值，使用最后一个
                    old_value = df.iloc[pos, insert_col_index]
                    new_value = source_values[-1]
                    
                    if mapping.overwrite_existing or pd.isna(old_value):
                        df.iloc[pos, insert_col_index] = new_value
                        insert_count += 1
                        self.logger.info(f"   ✅ 第{pos+1}行: '{old_value}' → '{new_value}' (重复使用最后值)")
                    else:
                        self.logger.info(f"   ⏭️  第{pos+1}行: 跳过覆盖 '{old_value}' (overwrite_existing=False)")
        
        updated_target_data[mapping.target_file] = df
        
        # 显示插入后的目标列状态
        updated_insert_column = df.iloc[:, insert_col_index]
        self.logger.info(f"   插入后目标列(第{insert_col_index+1}列)的值:")
        for idx, val in updated_insert_column.items():
            val_str = str(val) if pd.notna(val) else "空值"
            if isinstance(idx, int):
                row_no = idx + 1
            else:
                row_no = idx
            self.logger.info(f"     第{row_no}行: '{val_str}'")
        
        self.logger.info(f"✅ 成功插入 {insert_count} 个值到目标文件")
        return updated_target_data
    
    def _get_column_index(self, coordinate: ExcelCoordinate, df: pd.DataFrame) -> int:
        """获取坐标对应的列索引"""
        if coordinate.coord_type == "column":
            # 整列：根据列标识获取索引
            return coordinate.column_to_index(coordinate.column)
        elif coordinate.coord_type == "single":
            # 单个坐标：根据列标识获取索引
            return coordinate.column_to_index(coordinate.column)
        else:
            raise ValueError(f"不支持的坐标类型用于列索引: {coordinate.coord_type}")
    
    def _apply_match_operator(self, column: pd.Series, value: Any, operator: FilterOperator) -> pd.Series:
        """应用匹配操作符"""
        try:
            if operator == FilterOperator.EQUALS:
                # 先尝试直接匹配
                direct_match = column == value
                
                # 如果没有匹配到，尝试类型转换匹配
                if not direct_match.any():
                    # 尝试将目标值转换为不同类型进行匹配
                    type_converted_matches = []
                    
                    # 如果value是字符串，尝试转换为数字
                    if isinstance(value, str):
                        try:
                            # 尝试转换为整数
                            int_value = int(value)
                            int_match = column == int_value
                            type_converted_matches.append(int_match)
                            self.logger.info(f"   🔄 尝试整数匹配: '{value}' -> {int_value}, 匹配到: {int_match.sum()}个")
                        except ValueError:
                            pass
                        
                        try:
                            # 尝试转换为浮点数
                            float_value = float(value)
                            float_match = column == float_value
                            type_converted_matches.append(float_match)
                            self.logger.info(f"   🔄 尝试浮点数匹配: '{value}' -> {float_value}, 匹配到: {float_match.sum()}个")
                        except ValueError:
                            pass
                    
                    # 如果value是数字，尝试转换为字符串
                    elif isinstance(value, (int, float)):
                        str_value = str(value)
                        str_match = column.astype(str) == str_value
                        type_converted_matches.append(str_match)
                        self.logger.info(f"   🔄 尝试字符串匹配: {value} -> '{str_value}', 匹配到: {str_match.sum()}个")
                    
                    # 合并所有匹配结果
                    if type_converted_matches:
                        combined_match = direct_match
                        for match in type_converted_matches:
                            combined_match = combined_match | match
                        return combined_match
                
                return direct_match
                
            elif operator == FilterOperator.NOT_EQUALS:
                return column != value
            elif operator == FilterOperator.CONTAINS:
                return column.astype(str).str.contains(str(value), na=False)
            elif operator == FilterOperator.NOT_CONTAINS:
                return ~column.astype(str).str.contains(str(value), na=False)
            elif operator == FilterOperator.STARTS_WITH:
                return column.astype(str).str.startswith(str(value), na=False)
            elif operator == FilterOperator.ENDS_WITH:
                return column.astype(str).str.endswith(str(value), na=False)
            elif operator == FilterOperator.GREATER_THAN:
                return pd.to_numeric(column, errors='coerce') > float(value)
            elif operator == FilterOperator.GREATER_EQUAL:
                return pd.to_numeric(column, errors='coerce') >= float(value)
            elif operator == FilterOperator.LESS_THAN:
                return pd.to_numeric(column, errors='coerce') < float(value)
            elif operator == FilterOperator.LESS_EQUAL:
                return pd.to_numeric(column, errors='coerce') <= float(value)
            elif operator == FilterOperator.IS_EMPTY:
                return column.isna() | (column.astype(str).str.strip() == '')
            elif operator == FilterOperator.IS_NOT_EMPTY:
                return ~(column.isna() | (column.astype(str).str.strip() == ''))
            else:
                raise ValueError(f"不支持的操作符: {operator}")
                
        except Exception as e:
            self.logger.error(f"应用匹配操作符失败: {e}")
            return pd.Series([False] * len(column))
    
    def execute_multiple_mappings(self, mappings: List[DataMapping], 
                                 source_data: Dict[str, pd.DataFrame], 
                                 target_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """执行多个数据映射"""
        current_target_data = target_data.copy()
        
        for mapping in mappings:
            try:
                current_target_data = self.execute_mapping(mapping, source_data, current_target_data)
            except Exception as e:
                self.logger.error(f"执行映射 '{mapping.name}' 失败: {e}")
                continue
        
        return current_target_data
    
    def validate_mapping(self, mapping: DataMapping, source_data: Dict[str, pd.DataFrame], 
                        target_data: Dict[str, pd.DataFrame]) -> List[str]:
        """验证数据映射配置"""
        errors = []
        
        # 检查源文件
        if mapping.source_file not in source_data:
            errors.append(f"源文件不存在: {mapping.source_file}")
        else:
            df = source_data[mapping.source_file]
            # 检查源列索引
            try:
                match_col_index = self._get_column_index(mapping.source_match_coordinate, df)
                value_col_index = self._get_column_index(mapping.source_value_coordinate, df)
                
                if match_col_index >= len(df.columns):
                    errors.append(f"源匹配列索引超出范围: {mapping.source_match_coordinate}")
                if value_col_index >= len(df.columns):
                    errors.append(f"源取值列索引超出范围: {mapping.source_value_coordinate}")
            except Exception as e:
                errors.append(f"源列配置错误: {e}")
        
        # 检查目标文件
        if mapping.target_file not in target_data:
            errors.append(f"目标文件不存在: {mapping.target_file}")
        else:
            df = target_data[mapping.target_file]
            # 检查目标列索引
            try:
                match_col_index = self._get_column_index(mapping.target_match_coordinate, df)
                insert_col_index = self._get_column_index(mapping.target_insert_coordinate, df)
                
                if match_col_index >= len(df.columns):
                    errors.append(f"目标匹配列索引超出范围: {mapping.target_match_coordinate}")
                if insert_col_index >= len(df.columns):
                    errors.append(f"目标插入列索引超出范围: {mapping.target_insert_coordinate}")
            except Exception as e:
                errors.append(f"目标列配置错误: {e}")
        
        return errors 