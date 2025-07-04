# 开发指南

## 1. 开发环境搭建

### 1.1 系统要求
- **操作系统**：Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python版本**：Python 3.8+
- **内存**：建议8GB以上
- **磁盘空间**：至少2GB可用空间

### 1.2 环境准备

#### 安装Python
```bash
# 检查Python版本
python --version

# 如果版本低于3.8，请从官网下载安装最新版本
# https://www.python.org/downloads/
```

#### 克隆项目
```bash
git clone <repository-url>
cd excel-filter-desktop
```

#### 创建虚拟环境
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux  
source venv/bin/activate
```

#### 安装依赖
```bash
pip install -r requirements.txt
```

### 1.3 IDE配置

#### 推荐IDE
- **PyCharm Professional/Community**
- **Visual Studio Code**
- **Sublime Text**

#### VSCode配置示例
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"]
}
```

### 1.4 开发工具链

```bash
# 安装开发工具
pip install black flake8 pytest pytest-cov mypy

# 代码格式化
black src/

# 代码检查
flake8 src/

# 类型检查  
mypy src/

# 运行测试
pytest tests/
```

## 2. 项目结构详解

```
excel-filter-desktop/
├── docs/                       # 项目文档
│   ├── requirements.md
│   ├── design.md  
│   ├── user-manual.md
│   ├── dev-guide.md
│   ├── deployment.md
│   └── testing.md
├── src/                        # 源代码
│   ├── __init__.py
│   ├── ui/                     # 用户界面层
│   │   ├── __init__.py
│   │   ├── main_window.py      # 主窗口
│   │   ├── widgets/            # UI组件
│   │   │   ├── __init__.py
│   │   │   ├── upload_widget.py
│   │   │   ├── filter_widget.py
│   │   │   ├── config_widget.py
│   │   │   └── result_widget.py
│   │   └── dialogs/            # 对话框
│   │       ├── __init__.py
│   │       ├── about_dialog.py
│   │       └── settings_dialog.py
│   ├── core/                   # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── excel_processor.py  # Excel处理
│   │   ├── filter_engine.py    # 筛选引擎
│   │   ├── config_manager.py   # 配置管理
│   │   └── data_validator.py   # 数据验证
│   ├── database/               # 数据访问层
│   │   ├── __init__.py
│   │   ├── models.py          # 数据模型
│   │   ├── dao.py             # 数据访问对象
│   │   └── connection.py      # 数据库连接
│   └── utils/                 # 工具模块
│       ├── __init__.py
│       ├── logger.py          # 日志工具
│       ├── exceptions.py      # 异常定义
│       ├── constants.py       # 常量定义
│       └── helpers.py         # 辅助函数
├── tests/                      # 测试代码
│   ├── __init__.py
│   ├── test_excel_processor.py
│   ├── test_filter_engine.py
│   ├── test_config_manager.py
│   └── fixtures/              # 测试数据
├── resources/                  # 资源文件
│   ├── icons/                 # 图标文件
│   ├── styles/                # 样式文件
│   └── sql/                   # SQL脚本
├── build/                     # 构建输出
├── dist/                      # 分发文件
├── .gitignore                 # Git忽略文件
├── .pylintrc                  # Pylint配置
├── pyproject.toml             # 项目配置
├── requirements.txt           # 依赖列表
├── requirements-dev.txt       # 开发依赖
└── main.py                    # 程序入口
```

## 3. 代码规范

### 3.1 Python代码规范

#### 导入规范
```python
# 标准库导入
import os
import sys
from typing import List, Dict, Optional

# 第三方库导入
import pandas as pd
from PySide6.QtWidgets import QApplication

# 本地模块导入
from src.core.excel_processor import ExcelProcessor
from src.utils.logger import get_logger
```

#### 命名规范
```python
# 类名：PascalCase
class ExcelProcessor:
    pass

# 函数和变量名：snake_case
def load_excel_files():
    pass

user_data = {}

# 常量：UPPER_SNAKE_CASE
MAX_FILE_SIZE = 50 * 1024 * 1024

# 私有方法：前缀下划线
def _internal_method():
    pass
```

#### 类型注解
```python
from typing import List, Dict, Optional

def process_data(
    files: List[str], 
    config: Dict[str, str]
) -> Optional[pd.DataFrame]:
    """处理数据文件
    
    Args:
        files: 文件路径列表
        config: 配置参数
        
    Returns:
        处理后的DataFrame，失败时返回None
    """
    pass
```

#### 文档字符串
```python
def filter_data(df: pd.DataFrame, conditions: List[str]) -> pd.DataFrame:
    """根据条件筛选数据
    
    Args:
        df: 输入的DataFrame
        conditions: 筛选条件列表
        
    Returns:
        筛选后的DataFrame
        
    Raises:
        ValueError: 当条件格式不正确时
        
    Examples:
        >>> df = pd.DataFrame({'name': ['张三', '李四'], 'age': [25, 30]})
        >>> result = filter_data(df, ['age > 25'])
        >>> len(result)
        1
    """
    pass
```

### 3.2 Git提交规范

#### 提交消息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

#### 类型说明
- **feat**: 新功能
- **fix**: Bug修复
- **docs**: 文档更新
- **style**: 代码格式化
- **refactor**: 代码重构
- **test**: 测试相关
- **chore**: 构建/工具链更新

#### 示例
```
feat(filter): 添加日期范围筛选功能

- 支持日期字段的范围筛选
- 添加日期格式验证
- 更新UI界面

Closes #123
```

### 3.3 代码质量检查

#### 配置文件 (.pylintrc)
```ini
[MASTER]
load-plugins=pylint.extensions.docparams

[MESSAGES CONTROL]
disable=missing-module-docstring,
        missing-class-docstring,
        too-few-public-methods

[FORMAT]
max-line-length=88
```

#### Pre-commit配置
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3
        
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```

## 4. 开发流程

### 4.1 功能开发流程

1. **创建分支**
```bash
git checkout -b feature/new-filter-feature
```

2. **编写代码**
   - 编写功能代码
   - 添加单元测试
   - 更新文档

3. **代码检查**
```bash
# 格式化代码
black src/ tests/

# 代码质量检查
flake8 src/ tests/
pylint src/

# 类型检查
mypy src/

# 运行测试
pytest tests/ --cov=src/
```

4. **提交代码**
```bash
git add .
git commit -m "feat(filter): 添加新的筛选功能"
git push origin feature/new-filter-feature
```

5. **创建Pull Request**
   - 填写详细的PR描述
   - 确保所有检查通过
   - 等待代码审查

### 4.2 测试策略

#### 单元测试
```python
import pytest
import pandas as pd
from src.core.excel_processor import ExcelProcessor

class TestExcelProcessor:
    def setup_method(self):
        self.processor = ExcelProcessor()
    
    def test_load_excel_file(self):
        # 测试Excel文件加载
        df = self.processor.load_excel_file("test_data.xlsx")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
    
    def test_extract_headers(self):
        # 测试表头提取
        df = pd.DataFrame({'姓名': ['张三'], '年龄': [25]})
        headers = self.processor.extract_headers(df)
        assert headers == ['姓名', '年龄']
```

#### 集成测试
```python
def test_full_filter_workflow():
    """测试完整的筛选流程"""
    # 准备测试数据
    processor = ExcelProcessor()
    filter_engine = FilterEngine(processor)
    
    # 加载数据
    processor.load_excel_files(['test1.xlsx', 'test2.xlsx'])
    
    # 添加筛选规则
    rule = FilterRule(
        name="测试规则",
        conditions=[FilterCondition('年龄', '>', 25)],
        target_column="A"
    )
    filter_engine.add_filter_rule(rule)
    
    # 执行筛选
    results = filter_engine.execute_filters()
    
    # 验证结果
    assert len(results) > 0
```

### 4.3 调试技巧

#### 日志调试
```python
from src.utils.logger import get_logger

logger = get_logger(__name__)

def process_data(data):
    logger.debug(f"开始处理数据，数据量: {len(data)}")
    
    try:
        # 处理逻辑
        result = do_something(data)
        logger.info(f"数据处理完成，结果量: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"数据处理失败: {e}", exc_info=True)
        raise
```

#### 性能分析
```python
import cProfile
import pstats

def profile_function():
    pr = cProfile.Profile()
    pr.enable()
    
    # 执行需要分析的代码
    your_function()
    
    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

## 5. 依赖管理

### 5.1 核心依赖
```txt
# requirements.txt
PySide6>=6.4.0
pandas>=1.5.0
openpyxl>=3.0.0
SQLAlchemy>=2.0.0
```

### 5.2 开发依赖
```txt
# requirements-dev.txt
black>=22.0.0
flake8>=4.0.0
pytest>=7.0.0
pytest-cov>=3.0.0
mypy>=0.950
pylint>=2.13.0
```

### 5.3 依赖更新
```bash
# 检查过期依赖
pip list --outdated

# 更新依赖
pip install --upgrade package_name

# 生成新的requirements.txt
pip freeze > requirements.txt
```

## 6. 性能优化

### 6.1 代码优化
```python
# 使用pandas向量化操作
# 避免
for index, row in df.iterrows():
    if row['age'] > 25:
        # 处理逻辑
        pass

# 推荐
mask = df['age'] > 25
filtered_df = df[mask]
```

### 6.2 内存优化
```python
# 及时释放大对象
del large_dataframe

# 使用gc强制垃圾回收
import gc
gc.collect()

# 分块处理大文件
chunk_size = 10000
for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
    process_chunk(chunk)
```

## 7. 常见问题解决

### 7.1 开发环境问题

**Q: PySide6安装失败**
```bash
# 解决方案
pip install --upgrade pip
pip install PySide6 --no-cache-dir
```

**Q: 虚拟环境激活失败**
```bash
# Windows PowerShell执行策略问题
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 7.2 代码问题

**Q: 导入模块失败**
```python
# 确保项目根目录在Python路径中
import sys
sys.path.append('.')
```

**Q: Qt相关错误**
```python
# 确保正确的Qt环境变量
import os
os.environ['QT_API'] = 'pyside6'
```

## 8. 贡献指南

### 8.1 贡献流程
1. Fork项目仓库
2. 创建功能分支
3. 提交代码更改
4. 创建Pull Request
5. 代码审查和合并

### 8.2 代码审查清单
- [ ] 代码符合规范
- [ ] 包含充足的测试
- [ ] 文档已更新
- [ ] 性能影响评估
- [ ] 安全性检查

### 8.3 Issue模板
```markdown
**Bug描述**
简单描述bug的现象

**复现步骤**
1. 步骤1
2. 步骤2
3. 步骤3

**期望行为**
描述期望的正确行为

**环境信息**
- 操作系统：
- Python版本：
- 软件版本：
```

---

**维护者**：开发团队  
**最后更新**：2025年7月 
