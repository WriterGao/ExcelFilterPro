"""
Excel处理引擎
负责Excel文件的加载、解析、处理和输出
"""

import pandas as pd
import openpyxl
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from datetime import datetime

from ..utils.logger import get_logger
from ..utils.helpers import validate_excel_file, format_file_size
from ..utils.exceptions import ExcelFileError, FileProcessingError
from ..utils.constants import SUPPORTED_EXCEL_FORMATS, MAX_DATA_ROWS


class ExcelProcessor:
    """Excel文件处理核心类"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.data_frames: Dict[str, pd.DataFrame] = {}
        self.file_info: Dict[str, Dict[str, Any]] = {}
        self.headers: Dict[str, List[str]] = {}
        self.data_types: Dict[str, Dict[str, str]] = {}
        
    def load_excel_files(self, file_paths: List[str]) -> Dict[str, pd.DataFrame]:
        """
        加载多个Excel文件
        
        Args:
            file_paths: Excel文件路径列表
            
        Returns:
            文件名到DataFrame的映射
            
        Raises:
            ExcelFileError: Excel文件处理失败
        """
        self.logger.info(f"开始加载{len(file_paths)}个Excel文件")
        loaded_files = {}
        
        for file_path in file_paths:
            try:
                # 验证文件
                validate_excel_file(file_path)
                
                # 加载单个文件
                file_key = Path(file_path).stem
                df = self.load_single_excel_file(file_path)
                
                if df is not None and not df.empty:
                    loaded_files[file_key] = df
                    self.data_frames[file_key] = df
                    self.logger.info(f"成功加载文件: {file_path}, 数据行数: {len(df)}")
                else:
                    self.logger.warning(f"文件为空或加载失败: {file_path}")
                    
            except Exception as e:
                self.logger.error(f"加载文件失败 {file_path}: {e}")
                raise ExcelFileError(f"无法加载Excel文件 {file_path}: {str(e)}")
        
        # 提取所有文件的表头和数据类型
        self._extract_all_metadata()
        
        self.logger.info(f"成功加载{len(loaded_files)}个Excel文件")
        return loaded_files
    
    def load_single_excel_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        加载单个Excel文件
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            DataFrame对象，失败时返回None
        """
        try:
            file_path_obj = Path(file_path)
            
            # 记录文件信息
            file_stat = file_path_obj.stat()
            file_key = file_path_obj.stem
            
            self.file_info[file_key] = {
                'path': str(file_path_obj),
                'size': file_stat.st_size,
                'size_formatted': format_file_size(file_stat.st_size),
                'modified_time': datetime.fromtimestamp(file_stat.st_mtime),
                'sheet_names': []
            }
            
            # 根据文件扩展名选择读取方法
            if file_path_obj.suffix.lower() == '.xlsx':
                df = pd.read_excel(file_path, engine='openpyxl')
                # 获取工作表名称
                with pd.ExcelFile(file_path) as xls:
                    self.file_info[file_key]['sheet_names'] = xls.sheet_names
            elif file_path_obj.suffix.lower() == '.xls':
                df = pd.read_excel(file_path, engine='xlrd')
                with pd.ExcelFile(file_path) as xls:
                    self.file_info[file_key]['sheet_names'] = xls.sheet_names
            else:
                raise ExcelFileError(f"不支持的文件格式: {file_path_obj.suffix}")
            
            # 检查数据行数限制
            if len(df) > MAX_DATA_ROWS:
                self.logger.warning(f"文件数据行数({len(df)})超过限制({MAX_DATA_ROWS})")
                df = df.head(MAX_DATA_ROWS)
            
            # 清理数据
            df = self._clean_dataframe(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"读取Excel文件失败 {file_path}: {e}")
            raise ExcelFileError(f"读取Excel文件失败: {str(e)}")
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清理DataFrame数据
        
        Args:
            df: 原始DataFrame
            
        Returns:
            清理后的DataFrame
        """
        # 移除完全为空的行和列
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # 重置索引
        df = df.reset_index(drop=True)
        
        # 处理列名
        df.columns = [str(col).strip() if col is not None else f'Column_{i}' 
                     for i, col in enumerate(df.columns)]
        
        # 移除重复的列名
        df.columns = self._make_unique_columns(df.columns.tolist())
        
        return df
    
    def _make_unique_columns(self, columns: List[str]) -> List[str]:
        """
        确保列名唯一
        
        Args:
            columns: 原始列名列表
            
        Returns:
            唯一的列名列表
        """
        unique_columns = []
        seen = {}
        
        for col in columns:
            if col in seen:
                seen[col] += 1
                unique_columns.append(f"{col}_{seen[col]}")
            else:
                seen[col] = 0
                unique_columns.append(col)
        
        return unique_columns
    
    def extract_headers(self, df: pd.DataFrame) -> List[str]:
        """
        提取DataFrame的表头
        
        Args:
            df: DataFrame对象
            
        Returns:
            表头列表
        """
        return df.columns.tolist()
    
    def infer_data_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        推断DataFrame各列的数据类型
        
        Args:
            df: DataFrame对象
            
        Returns:
            列名到数据类型的映射
        """
        type_mapping = {}
        
        for column in df.columns:
            col_data = df[column].dropna()
            
            if len(col_data) == 0:
                type_mapping[column] = 'string'
                continue
            
            # 尝试推断数据类型
            if pd.api.types.is_numeric_dtype(col_data):
                type_mapping[column] = 'number'
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                type_mapping[column] = 'datetime'
            elif pd.api.types.is_bool_dtype(col_data):
                type_mapping[column] = 'boolean'
            else:
                # 尝试解析日期
                if self._try_parse_datetime(col_data):
                    type_mapping[column] = 'datetime'
                # 尝试解析数字
                elif self._try_parse_numeric(col_data):
                    type_mapping[column] = 'number'
                else:
                    type_mapping[column] = 'string'
        
        return type_mapping
    
    def _try_parse_datetime(self, series: pd.Series) -> bool:
        """
        尝试将系列解析为日期时间
        
        Args:
            series: pandas Series
            
        Returns:
            是否能解析为日期时间
        """
        try:
            # 取样本进行测试
            sample_size = min(10, len(series))
            sample = series.head(sample_size)
            
            parsed_count = 0
            for value in sample:
                try:
                    pd.to_datetime(str(value))
                    parsed_count += 1
                except:
                    continue
            
            # 如果超过80%的样本能解析为日期，则认为是日期类型
            return parsed_count / sample_size > 0.8
            
        except:
            return False
    
    def _try_parse_numeric(self, series: pd.Series) -> bool:
        """
        尝试将系列解析为数字
        
        Args:
            series: pandas Series
            
        Returns:
            是否能解析为数字
        """
        try:
            # 取样本进行测试
            sample_size = min(10, len(series))
            sample = series.head(sample_size)
            
            parsed_count = 0
            for value in sample:
                try:
                    float(str(value).replace(',', ''))
                    parsed_count += 1
                except:
                    continue
            
            # 如果超过80%的样本能解析为数字，则认为是数字类型
            return parsed_count / sample_size > 0.8
            
        except:
            return False
    
    def _extract_all_metadata(self):
        """提取所有已加载文件的元数据"""
        for file_key, df in self.data_frames.items():
            self.headers[file_key] = self.extract_headers(df)
            self.data_types[file_key] = self.infer_data_types(df)
    
    def get_all_unique_headers(self) -> List[str]:
        """
        获取所有文件的唯一表头
        
        Returns:
            去重后的表头列表
        """
        all_headers = set()
        for headers in self.headers.values():
            all_headers.update(headers)
        
        return sorted(list(all_headers))
    
    def get_combined_dataframe(self) -> pd.DataFrame:
        """
        将所有数据源合并为一个DataFrame
        
        Returns:
            合并后的DataFrame
        """
        if not self.data_frames:
            return pd.DataFrame()
        
        # 获取所有唯一列名
        all_columns = self.get_all_unique_headers()
        
        # 标准化所有DataFrame的列
        standardized_dfs = []
        for file_key, df in self.data_frames.items():
            # 为每个DataFrame添加缺失的列
            for col in all_columns:
                if col not in df.columns:
                    df[col] = None
            
            # 重新排序列
            df = df[all_columns]
            
            # 添加数据源标识
            df['_source_file'] = file_key
            
            standardized_dfs.append(df)
        
        # 合并所有DataFrame
        combined_df = pd.concat(standardized_dfs, ignore_index=True)
        
        return combined_df
    
    def write_to_template(self, template_path: str, filtered_data: Dict[str, pd.DataFrame], 
                         output_path: str) -> bool:
        """
        将筛选结果写入模板文件
        
        Args:
            template_path: 模板文件路径
            filtered_data: 筛选结果数据，格式为{列名: DataFrame}
            output_path: 输出文件路径
            
        Returns:
            是否写入成功
        """
        try:
            # 加载模板文件
            template_df = self.load_single_excel_file(template_path)
            if template_df is None:
                raise ExcelFileError("无法加载模板文件")
            
            # 复制模板结构
            output_df = template_df.copy()
            
            # 清空数据行，保留表头
            if len(output_df) > 0:
                output_df = output_df.iloc[0:0]  # 保留列结构，清空行
            
            # 计算需要的总行数
            max_rows_needed = 0
            for column_name, data in filtered_data.items():
                if column_name in output_df.columns:
                    max_rows_needed = max(max_rows_needed, len(data))
            
            # 扩展输出DataFrame的行数
            if max_rows_needed > 0:
                # 创建空行
                empty_rows = pd.DataFrame(index=range(max_rows_needed), 
                                        columns=output_df.columns)
                output_df = pd.concat([output_df, empty_rows], ignore_index=True)
            
            # 填充筛选结果到对应列
            for column_name, data in filtered_data.items():
                if column_name in output_df.columns and not data.empty:
                    # 取第一列的数据（假设筛选结果是单列数据或取第一个非空列）
                    if len(data.columns) > 0:
                        source_column = data.columns[0]
                        values = data[source_column].dropna().tolist()
                        
                        # 填充到目标列
                        for i, value in enumerate(values):
                            if i < len(output_df):
                                output_df.loc[i, column_name] = value
            
            # 保存到输出文件
            output_df.to_excel(output_path, index=False, engine='openpyxl')
            
            self.logger.info(f"成功将结果写入文件: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"写入模板文件失败: {e}")
            raise FileProcessingError(f"写入模板文件失败: {str(e)}")
    
    def get_file_summary(self) -> Dict[str, Any]:
        """
        获取已加载文件的汇总信息
        
        Returns:
            文件汇总信息
        """
        summary = {
            'total_files': len(self.data_frames),
            'total_rows': sum(len(df) for df in self.data_frames.values()),
            'total_columns': len(self.get_all_unique_headers()),
            'files_info': []
        }
        
        for file_key, df in self.data_frames.items():
            file_info = self.file_info.get(file_key, {})
            summary['files_info'].append({
                'name': file_key,
                'rows': len(df),
                'columns': len(df.columns),
                'size': file_info.get('size_formatted', 'Unknown'),
                'headers': self.headers.get(file_key, [])
            })
        
        return summary
    
    def clear_data(self):
        """清空所有加载的数据"""
        self.data_frames.clear()
        self.file_info.clear()
        self.headers.clear()
        self.data_types.clear()
        self.logger.info("已清空所有数据") 