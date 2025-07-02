# 系统设计文档

## 1. 系统概述

### 1.1 设计目标
- 构建一个高效、易用的Excel数据筛选桌面应用
- 采用模块化设计，便于维护和扩展
- 提供稳定可靠的数据处理能力
- 实现美观直观的用户界面

### 1.2 设计原则
- **单一职责**：每个模块负责特定的功能
- **开闭原则**：对扩展开放，对修改关闭
- **依赖倒置**：依赖抽象而非具体实现
- **接口隔离**：提供清晰的模块接口

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Presentation  │    │    Business     │    │      Data       │
│      Layer      │    │     Logic       │    │     Access      │
│                 │    │     Layer       │    │     Layer       │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Main Window   │◄──►│ • Filter Engine │◄──►│ • Config DB     │
│ • Upload Widget │    │ • Excel Processor│   │ • File System   │
│ • Filter Widget │    │ • Config Manager│    │ • Cache Layer   │
│ • Result Widget │    │ • Data Validator│    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                      ┌─────────────────┐
                      │   Utility       │
                      │   Layer         │
                      ├─────────────────┤
                      │ • Logger        │
                      │ • Exception     │
                      │ • Constants     │
                      │ • Helpers       │
                      └─────────────────┘
```

### 2.2 技术架构栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 表现层 | PySide6 | GUI框架，负责用户界面 |
| 业务逻辑层 | Python | 核心业务逻辑处理 |
| 数据处理层 | pandas, openpyxl | Excel文件读写和数据处理 |
| 数据访问层 | SQLite, SQLAlchemy | 本地数据库和ORM |
| 工具层 | logging, configparser | 日志和配置管理 |

## 3. 模块设计

### 3.1 模块概览

```
src/
├── ui/                     # 用户界面模块
│   ├── main_window.py      # 主窗口
│   ├── widgets/            # 子组件
│   │   ├── upload_widget.py
│   │   ├── filter_widget.py
│   │   ├── config_widget.py
│   │   └── result_widget.py
│   └── dialogs/            # 对话框
│       ├── about_dialog.py
│       └── settings_dialog.py
├── core/                   # 核心业务逻辑
│   ├── excel_processor.py  # Excel处理引擎
│   ├── filter_engine.py    # 筛选引擎
│   ├── config_manager.py   # 配置管理
│   └── data_validator.py   # 数据验证
├── database/               # 数据访问层
│   ├── models.py          # 数据模型
│   ├── dao.py             # 数据访问对象
│   └── connection.py      # 数据库连接
└── utils/                 # 工具模块
    ├── logger.py          # 日志工具
    ├── exceptions.py      # 异常定义
    ├── constants.py       # 常量定义
    └── helpers.py         # 辅助函数
```

### 3.2 核心模块详细设计

#### 3.2.1 Excel处理模块 (excel_processor.py)

```python
class ExcelProcessor:
    """Excel文件处理核心类"""
    
    def __init__(self):
        self.data_frames = {}  # 存储已加载的DataFrame
        self.headers = {}      # 存储表头信息
    
    def load_excel_files(self, file_paths: List[str]) -> Dict[str, pd.DataFrame]:
        """加载Excel文件"""
        pass
    
    def extract_headers(self, df: pd.DataFrame) -> List[str]:
        """提取表头信息"""
        pass
    
    def infer_data_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """推断数据类型"""
        pass
    
    def write_to_template(self, template_path: str, data: Dict, output_path: str):
        """将数据写入模板"""
        pass
```

#### 3.2.2 筛选引擎模块 (filter_engine.py)

```python
class FilterEngine:
    """数据筛选引擎"""
    
    def __init__(self, excel_processor: ExcelProcessor):
        self.excel_processor = excel_processor
        self.filter_rules = []
    
    def add_filter_rule(self, rule: FilterRule):
        """添加筛选规则"""
        pass
    
    def execute_filters(self) -> Dict[str, pd.DataFrame]:
        """执行所有筛选规则"""
        pass
    
    def _apply_single_filter(self, df: pd.DataFrame, condition: FilterCondition) -> pd.DataFrame:
        """应用单个筛选条件"""
        pass
    
    def _combine_conditions(self, conditions: List[FilterCondition], logic: str) -> str:
        """组合多个筛选条件"""
        pass
```

#### 3.2.3 配置管理模块 (config_manager.py)

```python
class ConfigManager:
    """配置管理器"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def save_filter_plan(self, plan: FilterPlan) -> int:
        """保存筛选方案"""
        pass
    
    def load_filter_plan(self, plan_id: int) -> FilterPlan:
        """加载筛选方案"""
        pass
    
    def list_filter_plans(self) -> List[FilterPlan]:
        """获取所有筛选方案"""
        pass
    
    def delete_filter_plan(self, plan_id: int) -> bool:
        """删除筛选方案"""
        pass
    
    def export_plan(self, plan_id: int, file_path: str):
        """导出方案到文件"""
        pass
    
    def import_plan(self, file_path: str) -> FilterPlan:
        """从文件导入方案"""
        pass
```

## 4. 数据模型设计

### 4.1 数据库设计

#### 4.1.1 筛选方案表 (filter_plans)

| 字段名 | 类型 | 长度 | 约束 | 说明 |
|--------|------|------|------|------|
| id | INTEGER | - | PRIMARY KEY | 方案ID |
| name | VARCHAR | 100 | NOT NULL | 方案名称 |
| description | TEXT | - | NULL | 方案描述 |
| created_time | DATETIME | - | NOT NULL | 创建时间 |
| updated_time | DATETIME | - | NOT NULL | 更新时间 |
| is_active | BOOLEAN | - | DEFAULT TRUE | 是否激活 |

#### 4.1.2 筛选规则表 (filter_rules)

| 字段名 | 类型 | 长度 | 约束 | 说明 |
|--------|------|------|------|------|
| id | INTEGER | - | PRIMARY KEY | 规则ID |
| plan_id | INTEGER | - | FOREIGN KEY | 所属方案ID |
| name | VARCHAR | 100 | NOT NULL | 规则名称 |
| conditions | TEXT | - | NOT NULL | 筛选条件(JSON) |
| target_column | VARCHAR | 50 | NOT NULL | 目标输出列 |
| order_index | INTEGER | - | DEFAULT 0 | 排序索引 |
| is_enabled | BOOLEAN | - | DEFAULT TRUE | 是否启用 |

#### 4.1.3 应用配置表 (app_settings)

| 字段名 | 类型 | 长度 | 约束 | 说明 |
|--------|------|------|------|------|
| id | INTEGER | - | PRIMARY KEY | 配置ID |
| key | VARCHAR | 100 | UNIQUE | 配置键 |
| value | TEXT | - | NULL | 配置值 |
| description | VARCHAR | 200 | NULL | 配置说明 |

### 4.2 数据模型类

#### 4.2.1 FilterPlan 模型

```python
@dataclass
class FilterPlan:
    """筛选方案数据模型"""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    rules: List['FilterRule'] = field(default_factory=list)
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    is_active: bool = True
    
    def add_rule(self, rule: 'FilterRule'):
        """添加筛选规则"""
        rule.plan_id = self.id
        self.rules.append(rule)
    
    def remove_rule(self, rule_id: int):
        """移除筛选规则"""
        self.rules = [r for r in self.rules if r.id != rule_id]
```

#### 4.2.2 FilterRule 模型

```python
@dataclass  
class FilterRule:
    """筛选规则数据模型"""
    id: Optional[int] = None
    plan_id: Optional[int] = None
    name: str = ""
    conditions: List['FilterCondition'] = field(default_factory=list)
    target_column: str = ""
    order_index: int = 0
    is_enabled: bool = True
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'conditions': [c.to_dict() for c in self.conditions],
            'target_column': self.target_column,
            'is_enabled': self.is_enabled
        }
```

#### 4.2.3 FilterCondition 模型

```python
@dataclass
class FilterCondition:
    """筛选条件数据模型"""
    field: str = ""           # 字段名
    operator: str = ""        # 操作符 (=, >, <, contains, etc.)
    value: Any = None         # 比较值
    logic: str = "AND"        # 逻辑连接符 (AND, OR)
    
    def to_dict(self) -> dict:
        return {
            'field': self.field,
            'operator': self.operator, 
            'value': self.value,
            'logic': self.logic
        }
    
    def to_pandas_query(self) -> str:
        """转换为pandas查询语句"""
        if self.operator == '=':
            return f"`{self.field}` == '{self.value}'"
        elif self.operator == '>':
            return f"`{self.field}` > {self.value}"
        elif self.operator == '<':
            return f"`{self.field}` < {self.value}"
        elif self.operator == 'contains':
            return f"`{self.field}`.str.contains('{self.value}')"
        # ... 其他操作符
```

## 5. 界面设计

### 5.1 主窗口布局

```
┌─────────────────────────────────────────────────────────────┐
│ 菜单栏: 文件 | 编辑 | 视图 | 工具 | 帮助                      │
├─────────────────────────────────────────────────────────────┤
│ 工具栏: [打开] [保存] [执行] [设置]                         │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────────────────────────────────┐ │
│ │    文件     │ │              筛选条件设置               │ │
│ │   上传区    │ │                                         │ │
│ │             │ │  ┌────────────┐ ┌────────────────────┐ │ │
│ │ 数据源:     │ │  │ 可用字段   │ │    筛选规则列表    │ │ │
│ │ ○ file1.xlsx│ │  │ • 姓名     │ │ 规则1: 姓名=张三   │ │ │
│ │ ○ file2.xlsx│ │  │ • 年龄     │ │ 规则2: 年龄>20     │ │ │
│ │             │ │  │ • 部门     │ │ [新增] [编辑] [删除]│ │ │
│ │ 模板:       │ │  └────────────┘ └────────────────────┘ │ │
│ │ ○ template  │ │                                         │ │
│ └─────────────┘ └─────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────────────────────────────────┐ │
│ │ 方案管理    │ │              结果预览                   │ │
│ │             │ │                                         │ │
│ │ 已保存方案: │ │ ┌─────────────────────────────────────┐ │ │
│ │ • 销售分析  │ │ │          表格数据预览               │ │ │
│ │ • 年龄统计  │ │ │                                     │ │ │
│ │ • 部门筛选  │ │ │                                     │ │ │
│ │             │ │ │                                     │ │ │
│ │ [加载][保存]│ │ └─────────────────────────────────────┘ │ │
│ │ [导入][导出]│ │ [预览] [导出Excel]                      │ │
│ └─────────────┘ └─────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ 状态栏: 就绪 | 处理进度: █████░░░░░ 50% | 内存: 128MB       │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 组件设计规范

#### 5.2.1 颜色方案
- **主色调**：#2E7CF6 (蓝色)
- **辅助色**：#F8F9FA (浅灰)
- **成功色**：#28A745 (绿色)
- **警告色**：#FFC107 (黄色)
- **错误色**：#DC3545 (红色)

#### 5.2.2 字体规范
- **标题字体**：16px, 加粗
- **正文字体**：12px, 常规
- **按钮字体**：12px, 加粗
- **状态字体**：10px, 常规

## 6. 性能设计

### 6.1 数据处理优化
- **分块读取**：大文件分块加载，避免内存溢出
- **延迟加载**：按需加载数据，提高响应速度
- **缓存机制**：缓存常用数据和计算结果
- **并行处理**：利用多线程处理大数据量

### 6.2 内存管理
- **对象池**：重用DataFrame对象
- **垃圾回收**：及时释放无用对象
- **内存监控**：实时监控内存使用情况

### 6.3 界面响应优化
- **异步处理**：UI操作与数据处理分离
- **进度提示**：长时间操作显示进度条
- **懒加载**：按需加载界面组件

## 7. 安全设计

### 7.1 数据安全
- **本地处理**：所有数据在本地处理，不上传云端
- **文件权限**：严格控制文件访问权限
- **数据加密**：敏感配置信息加密存储

### 7.2 输入验证
- **文件类型检查**：验证上传文件格式
- **数据格式验证**：检查Excel数据格式
- **SQL注入防护**：使用参数化查询

### 7.3 异常处理
- **优雅降级**：异常情况下保证基本功能可用
- **错误恢复**：提供错误恢复机制
- **日志记录**：详细记录异常信息

## 8. 可扩展性设计

### 8.1 插件架构
- **筛选器插件**：支持自定义筛选器
- **输出格式插件**：支持多种输出格式
- **数据源插件**：支持多种数据源

### 8.2 接口设计
- **标准化接口**：定义清晰的模块接口
- **版本兼容**：保证向后兼容性
- **配置化**：通过配置文件扩展功能

## 9. 部署设计

### 9.1 打包策略
- **单文件打包**：使用PyInstaller打包成单个可执行文件
- **依赖管理**：自动打包所有依赖项
- **资源嵌入**：将图标、样式等资源嵌入

### 9.2 安装方案
- **绿色版本**：无需安装，直接运行
- **安装包版本**：提供安装向导
- **自动更新**：支持在线更新功能 