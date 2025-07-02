# 测试文档

## 1. 测试概述

### 1.1 测试目标
- 确保Excel筛选器功能正确性
- 验证性能和稳定性要求
- 保证用户体验质量
- 防止回归问题

### 1.2 测试策略
- **单元测试**：测试各个模块的独立功能
- **集成测试**：验证模块间的协作
- **系统测试**：完整的端到端功能测试
- **性能测试**：验证性能指标
- **UI测试**：界面交互和用户体验

## 2. 测试环境

### 2.1 测试平台
- Windows 10/11
- macOS 10.14+
- Ubuntu 18.04+

### 2.2 测试工具
- **pytest**：单元测试框架
- **pytest-qt**：Qt应用测试
- **pytest-cov**：代码覆盖率
- **pytest-benchmark**：性能基准测试

## 3. 测试用例

### 3.1 Excel处理模块测试

#### TC001: Excel文件加载
```python
def test_load_excel_file():
    """测试Excel文件加载功能"""
    # 准备
    processor = ExcelProcessor()
    
    # 执行
    df = processor.load_excel_file("test_data.xlsx")
    
    # 验证
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
```

#### TC002: 表头识别
```python
def test_extract_headers():
    """测试表头识别功能"""
    # 准备
    processor = ExcelProcessor()
    df = pd.DataFrame({'姓名': ['张三'], '年龄': [25]})
    
    # 执行
    headers = processor.extract_headers(df)
    
    # 验证
    assert headers == ['姓名', '年龄']
```

### 3.2 筛选引擎测试

#### TC003: 单条件筛选
```python
def test_single_condition_filter():
    """测试单条件筛选"""
    # 准备
    df = pd.DataFrame({
        '姓名': ['张三', '李四', '王五'],
        '年龄': [25, 30, 35]
    })
    engine = FilterEngine()
    condition = FilterCondition('年龄', '>', 28)
    
    # 执行
    result = engine._apply_single_filter(df, condition)
    
    # 验证
    assert len(result) == 2
    assert '李四' in result['姓名'].values
    assert '王五' in result['姓名'].values
```

#### TC004: 组合条件筛选
```python
def test_combined_condition_filter():
    """测试组合条件筛选"""
    # 准备
    df = pd.DataFrame({
        '姓名': ['张三', '李四', '王五'],
        '年龄': [25, 30, 35],
        '部门': ['销售', '技术', '销售']
    })
    engine = FilterEngine()
    conditions = [
        FilterCondition('年龄', '>', 20),
        FilterCondition('部门', '=', '销售')
    ]
    
    # 执行
    result = engine._apply_combined_filter(df, conditions, 'AND')
    
    # 验证
    assert len(result) == 2
```

### 3.3 配置管理测试

#### TC005: 方案保存
```python
def test_save_filter_plan():
    """测试筛选方案保存"""
    # 准备
    config_manager = ConfigManager()
    plan = FilterPlan(name="测试方案", description="测试用")
    
    # 执行
    plan_id = config_manager.save_filter_plan(plan)
    
    # 验证
    assert plan_id > 0
    saved_plan = config_manager.load_filter_plan(plan_id)
    assert saved_plan.name == "测试方案"
```

### 3.4 UI功能测试

#### TC006: 文件上传界面
```python
def test_upload_widget(qtbot):
    """测试文件上传界面"""
    # 准备
    widget = UploadWidget()
    qtbot.addWidget(widget)
    
    # 执行
    # 模拟文件选择
    with mock.patch('PySide6.QtWidgets.QFileDialog.getOpenFileNames') as mock_dialog:
        mock_dialog.return_value = (['test.xlsx'], '')
        widget.select_files()
    
    # 验证
    assert len(widget.file_list) == 1
    assert 'test.xlsx' in widget.file_list
```

## 4. 性能测试

### 4.1 大文件处理测试
```python
@pytest.mark.benchmark
def test_large_file_performance(benchmark):
    """测试大文件处理性能"""
    # 准备大文件数据
    large_df = pd.DataFrame({
        '姓名': [f'用户{i}' for i in range(100000)],
        '年龄': np.random.randint(18, 65, 100000)
    })
    
    processor = ExcelProcessor()
    condition = FilterCondition('年龄', '>', 30)
    
    # 基准测试
    result = benchmark(processor.apply_filter, large_df, condition)
    
    # 验证性能要求
    assert benchmark.stats['mean'] < 5.0  # 5秒内完成
```

### 4.2 内存使用测试
```python
def test_memory_usage():
    """测试内存使用情况"""
    import psutil
    import gc
    
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    # 处理大量数据
    processor = ExcelProcessor()
    for i in range(10):
        df = pd.DataFrame({'data': range(10000)})
        processor.process_data(df)
    
    # 强制垃圾回收
    gc.collect()
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # 验证内存增长在合理范围内
    assert memory_increase < 100 * 1024 * 1024  # 100MB
```

## 5. 集成测试

### 5.1 完整流程测试
```python
def test_complete_workflow():
    """测试完整的筛选流程"""
    # 准备测试数据
    test_data = pd.DataFrame({
        '姓名': ['张三', '李四', '王五', '赵六'],
        '年龄': [25, 30, 35, 40],
        '部门': ['销售', '技术', '销售', '财务']
    })
    
    # 初始化组件
    processor = ExcelProcessor()
    filter_engine = FilterEngine(processor)
    config_manager = ConfigManager()
    
    # 1. 加载数据
    processor.data_frames['test'] = test_data
    
    # 2. 创建筛选规则
    rule = FilterRule(
        name="销售部门筛选",
        conditions=[FilterCondition('部门', '=', '销售')],
        target_column="A"
    )
    filter_engine.add_filter_rule(rule)
    
    # 3. 执行筛选
    results = filter_engine.execute_filters()
    
    # 4. 验证结果
    assert len(results) == 1
    assert len(results['sales_filter']) == 2
    
    # 5. 保存方案
    plan = FilterPlan(name="销售分析", rules=[rule])
    plan_id = config_manager.save_filter_plan(plan)
    assert plan_id > 0
```

## 6. 错误处理测试

### 6.1 异常情况测试
```python
def test_invalid_excel_file():
    """测试无效Excel文件处理"""
    processor = ExcelProcessor()
    
    with pytest.raises(FileNotFoundError):
        processor.load_excel_file("nonexistent.xlsx")
    
    with pytest.raises(ValueError):
        processor.load_excel_file("invalid.txt")
```

### 6.2 边界条件测试
```python
def test_empty_dataframe():
    """测试空数据处理"""
    processor = ExcelProcessor()
    empty_df = pd.DataFrame()
    
    headers = processor.extract_headers(empty_df)
    assert headers == []
    
    filter_engine = FilterEngine(processor)
    condition = FilterCondition('name', '=', 'test')
    result = filter_engine._apply_single_filter(empty_df, condition)
    assert len(result) == 0
```

## 7. 测试数据管理

### 7.1 测试数据文件
```
tests/
├── fixtures/
│   ├── sample_data.xlsx      # 标准测试数据
│   ├── large_data.xlsx       # 大文件测试数据
│   ├── chinese_data.xlsx     # 中文数据测试
│   ├── empty_file.xlsx       # 空文件测试
│   └── malformed.xlsx        # 格式错误文件
└── conftest.py               # pytest配置
```

### 7.2 测试数据生成
```python
# tests/conftest.py
import pytest
import pandas as pd

@pytest.fixture
def sample_dataframe():
    """生成标准测试数据"""
    return pd.DataFrame({
        '姓名': ['张三', '李四', '王五'],
        '年龄': [25, 30, 35],
        '部门': ['销售', '技术', '销售'],
        '工资': [8000, 12000, 9000]
    })

@pytest.fixture
def large_dataframe():
    """生成大数据量测试数据"""
    import numpy as np
    return pd.DataFrame({
        '姓名': [f'用户{i}' for i in range(10000)],
        '年龄': np.random.randint(18, 65, 10000),
        '工资': np.random.randint(3000, 20000, 10000)
    })
```

## 8. 测试执行

### 8.1 运行所有测试
```bash
# 运行全部测试
pytest tests/

# 运行特定模块测试
pytest tests/test_excel_processor.py

# 运行带覆盖率的测试
pytest tests/ --cov=src/ --cov-report=html

# 运行性能测试
pytest tests/ --benchmark-only
```

### 8.2 测试配置
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=80
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    benchmark: marks tests as benchmark tests
```

## 9. 持续集成

### 9.1 CI配置
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: [3.8, 3.9, '3.10']
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: pytest tests/ --cov=src/
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## 10. 测试报告

### 10.1 覆盖率要求
- **总体覆盖率**：≥ 80%
- **核心模块**：≥ 90%
- **UI模块**：≥ 60%

### 10.2 质量指标
- **测试通过率**：100%
- **性能测试**：符合规定指标
- **内存泄漏**：无明显泄漏
- **稳定性**：长时间运行无崩溃

---

**维护者**：测试团队  
**最后更新**：2024年12月 