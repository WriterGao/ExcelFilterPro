"""
数据模型定义
使用dataclass定义应用程序的数据结构
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Any, Dict
import json
from enum import Enum


class FilterOperator(Enum):
    """筛选操作符枚举"""
    EQUALS = "等于"
    NOT_EQUALS = "不等于"
    GREATER_THAN = "大于"
    GREATER_EQUAL = "大于等于"
    LESS_THAN = "小于"
    LESS_EQUAL = "小于等于"
    CONTAINS = "包含"
    NOT_CONTAINS = "不包含"
    STARTS_WITH = "开头是"
    ENDS_WITH = "结尾是"
    IS_EMPTY = "为空"
    IS_NOT_EMPTY = "不为空"


@dataclass
class ExcelCoordinate:
    """Excel坐标类 - 支持单个坐标、范围、整列、整行"""
    column: str = ""     # 列标识，如 A, B, C, AA等
    row: int = 0         # 行号，从1开始
    end_column: str = "" # 结束列（用于范围）
    end_row: int = 0     # 结束行（用于范围）
    coord_type: str = "single"  # 坐标类型：single, range, column, row
    
    def __str__(self) -> str:
        if self.coord_type == "single":
            return f"{self.column}{self.row}"
        elif self.coord_type == "range":
            return f"{self.column}{self.row}:{self.end_column}{self.end_row}"
        elif self.coord_type == "column":
            return self.column if self.column else "A"
        elif self.coord_type == "row":
            return str(self.row) if self.row > 0 else "1"
        return ""
    
    @classmethod
    def from_string(cls, coord_str: str) -> 'ExcelCoordinate':
        """从字符串解析Excel坐标，支持多种格式"""
        coord_str = coord_str.upper().strip()
        
        # 检查是否为范围（包含冒号）
        if ':' in coord_str:
            return cls._parse_range(coord_str)
        
        # 检查是否为整列（只有字母）
        if coord_str.isalpha():
            return cls(column=coord_str, coord_type="column")
        
        # 检查是否为整行（只有数字）
        if coord_str.isdigit():
            return cls(row=int(coord_str), coord_type="row")
        
        # 解析单个坐标
        return cls._parse_single(coord_str)
    
    @classmethod
    def _parse_single(cls, coord_str: str) -> 'ExcelCoordinate':
        """解析单个坐标"""
        col_part = ""
        row_part = ""
        
        for i, char in enumerate(coord_str):
            if char.isdigit():
                col_part = coord_str[:i]
                row_part = coord_str[i:]
                break
        
        if not col_part or not row_part:
            raise ValueError(f"无效的Excel坐标格式: {coord_str}")
        
        try:
            row = int(row_part)
            if row < 1:
                raise ValueError("行号必须大于0")
        except ValueError:
            raise ValueError(f"无效的行号: {row_part}")
        
        return cls(column=col_part, row=row, coord_type="single")
    
    @classmethod
    def _parse_range(cls, coord_str: str) -> 'ExcelCoordinate':
        """解析范围坐标"""
        try:
            start_str, end_str = coord_str.split(':')
            start_str = start_str.strip()
            end_str = end_str.strip()
            
            # 检查是否为整列格式 (如A:A)
            if start_str.isalpha() and end_str.isalpha() and start_str == end_str:
                return cls(column=start_str, coord_type="column")
            
            # 检查是否为整行格式 (如1:1)
            if start_str.isdigit() and end_str.isdigit() and start_str == end_str:
                return cls(row=int(start_str), coord_type="row")
            
            # 解析正常的范围格式
            start_coord = cls._parse_single(start_str)
            end_coord = cls._parse_single(end_str)
            
            return cls(
                column=start_coord.column,
                row=start_coord.row,
                end_column=end_coord.column,
                end_row=end_coord.row,
                coord_type="range"
            )
        except Exception as e:
            raise ValueError(f"无效的范围格式: {coord_str} - {e}")
    
    def to_pandas_index(self) -> tuple:
        """转换为pandas的行列索引（0-based）"""
        col_index = self.column_to_index(self.column)
        row_index = self.row - 1  # pandas是0-based
        return row_index, col_index
    
    @staticmethod
    def column_to_index(column: str) -> int:
        """将Excel列标识转换为数字索引（0-based）"""
        result = 0
        for char in column:
            result = result * 26 + (ord(char) - ord('A') + 1)
        return result - 1
    
    @staticmethod
    def index_to_column(index: int) -> str:
        """将数字索引转换为Excel列标识"""
        result = ""
        index += 1  # 转换为1-based
        
        while index > 0:
            index -= 1
            result = chr(index % 26 + ord('A')) + result
            index //= 26
        
        return result


@dataclass
class CoordinateFilterCondition:
    """基于坐标的筛选条件"""
    source_file: str                    # 源文件名
    source_coordinate: ExcelCoordinate  # 源数据坐标（支持范围、整列、整行）
    operator: FilterOperator            # 筛选操作符
    value: Any                          # 筛选值
    
    def __post_init__(self):
        """初始化后处理"""
        if isinstance(self.source_coordinate, str):
            self.source_coordinate = ExcelCoordinate.from_string(self.source_coordinate)
        if isinstance(self.operator, str):
            # 尝试从字符串转换为枚举
            for op in FilterOperator:
                if op.value == self.operator:
                    self.operator = op
                    break


@dataclass 
class RuleOutputConfig:
    """规则输出配置"""
    target_file: str        # 目标文件名
    target_column: str      # 目标列（如A, B, C）
    start_row: int = 1      # 起始行号
    auto_append: bool = True # 是否自动追加

@dataclass
class CoordinateFilterRule:
    """基于坐标的筛选规则"""
    rule_id: str
    name: str
    description: str
    output_config: Optional[RuleOutputConfig] = None  # 输出配置
    conditions: List[CoordinateFilterCondition] = field(default_factory=list)
    logic_operator: str = "AND"  # AND 或 OR
    created_time: datetime = field(default_factory=datetime.now)
    modified_time: datetime = field(default_factory=datetime.now)
    
    def add_condition(self, condition: CoordinateFilterCondition):
        """添加筛选条件"""
        self.conditions.append(condition)
        self.modified_time = datetime.now()
    
    def remove_condition(self, index: int):
        """删除筛选条件"""
        if 0 <= index < len(self.conditions):
            del self.conditions[index]
            self.modified_time = datetime.now()
    
    def get_required_files(self) -> set:
        """获取规则需要的所有文件"""
        files = set()
        for condition in self.conditions:
            files.add(condition.source_file)
        if self.output_config:
            files.add(self.output_config.target_file)
        return files


@dataclass
class CoordinateFilterPlan:
    """基于坐标的筛选方案"""
    plan_id: str
    name: str
    description: str
    rules: List[CoordinateFilterRule] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_time: datetime = field(default_factory=datetime.now)
    modified_time: datetime = field(default_factory=datetime.now)
    
    def add_rule(self, rule: CoordinateFilterRule):
        """添加规则"""
        self.rules.append(rule)
        self.modified_time = datetime.now()
    
    def remove_rule(self, rule_id: str):
        """删除规则"""
        self.rules = [r for r in self.rules if r.rule_id != rule_id]
        self.modified_time = datetime.now()
    
    def get_rule_by_id(self, rule_id: str) -> Optional[CoordinateFilterRule]:
        """根据ID获取规则"""
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        return None
    
    def get_required_files(self) -> set:
        """获取方案需要的所有文件"""
        files = set()
        for rule in self.rules:
            files.update(rule.get_required_files())
        return files


# 为了兼容性，保留原有的模型
@dataclass
class FilterCondition:
    """筛选条件（兼容性保留）"""
    field_name: str
    operator: str
    value: Any
    data_type: str = "string"


@dataclass
class FilterRule:
    """筛选规则（兼容性保留）"""
    rule_id: str
    output_column: str
    conditions: List[FilterCondition] = field(default_factory=list)
    logic_operator: str = "AND"
    
    def add_condition(self, condition: FilterCondition):
        """添加筛选条件"""
        self.conditions.append(condition)


@dataclass
class FilterPlan:
    """筛选方案（兼容性保留）"""
    plan_id: str
    name: str
    description: str
    rules: List[FilterRule] = field(default_factory=list)
    created_time: datetime = field(default_factory=datetime.now)
    
    def add_rule(self, rule: FilterRule):
        """添加规则"""
        self.rules.append(rule)


@dataclass
class AppSetting:
    """应用设置数据模型"""
    id: Optional[int] = None
    key: str = ""
    value: str = ""
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppSetting':
        """从字典创建实例"""
        return cls(
            id=data.get('id'),
            key=data.get('key', ''),
            value=data.get('value', ''),
            description=data.get('description', '')
        )


@dataclass
class DataMapping:
    """数据映射配置"""
    mapping_id: str
    name: str
    description: str
    
    # 源数据配置
    source_file: str                      # 源文件名
    source_match_coordinate: ExcelCoordinate  # 源匹配列坐标（如B列）
    source_match_value: Any               # 源匹配值（如'202 2号主变'）
    source_value_coordinate: ExcelCoordinate  # 源取值列坐标（如C列）
    
    # 目标数据配置  
    target_file: str                      # 目标文件名
    target_match_coordinate: ExcelCoordinate  # 目标匹配列坐标（如A列）
    target_match_value: Any               # 目标匹配值（如'202 2号主变'）
    target_insert_coordinate: ExcelCoordinate # 目标插入列坐标（如D列）
    
    # 操作配置
    match_operator: FilterOperator = FilterOperator.EQUALS  # 匹配操作符
    overwrite_existing: bool = True       # 是否覆盖已有数据
    created_time: datetime = field(default_factory=datetime.now)
    modified_time: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """初始化后处理"""
        # 处理坐标字符串
        if isinstance(self.source_match_coordinate, str):
            self.source_match_coordinate = ExcelCoordinate.from_string(self.source_match_coordinate)
        if isinstance(self.source_value_coordinate, str):
            self.source_value_coordinate = ExcelCoordinate.from_string(self.source_value_coordinate)
        if isinstance(self.target_match_coordinate, str):
            self.target_match_coordinate = ExcelCoordinate.from_string(self.target_match_coordinate)
        if isinstance(self.target_insert_coordinate, str):
            self.target_insert_coordinate = ExcelCoordinate.from_string(self.target_insert_coordinate)
    
    def get_required_files(self) -> set:
        """获取需要的文件"""
        return {self.source_file, self.target_file}


@dataclass 
class DataMappingPlan:
    """数据映射方案"""
    plan_id: str
    name: str
    description: str
    mappings: List[DataMapping] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_time: datetime = field(default_factory=datetime.now)
    modified_time: datetime = field(default_factory=datetime.now)
    
    def add_mapping(self, mapping: DataMapping):
        """添加映射"""
        self.mappings.append(mapping)
        self.modified_time = datetime.now()
    
    def remove_mapping(self, mapping_id: str):
        """删除映射"""
        self.mappings = [m for m in self.mappings if m.mapping_id != mapping_id]
        self.modified_time = datetime.now()
    
    def get_mapping_by_id(self, mapping_id: str) -> Optional[DataMapping]:
        """根据ID获取映射"""
        for mapping in self.mappings:
            if mapping.mapping_id == mapping_id:
                return mapping
        return None
    
    def get_required_files(self) -> set:
        """获取方案需要的所有文件"""
        files = set()
        for mapping in self.mappings:
            files.update(mapping.get_required_files())
        return files 