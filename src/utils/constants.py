"""
应用程序常量定义
"""

# 应用程序信息
APP_NAME = "Excel筛选器"
VERSION = "1.0.0"
BUILD_DATE = "2024-12-01"
AUTHOR = "开发团队"

# 文件限制
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_FILE_COUNT = 20
MAX_DATA_ROWS = 1000000  # 100万行

# 支持的文件格式
SUPPORTED_EXCEL_FORMATS = ['.xlsx', '.xls']
EXPORT_FORMATS = ['.xlsx', '.xls']

# 数据库配置
DATABASE_NAME = "excel_filter.db"
DATABASE_VERSION = "1.0"

# 界面配置
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800
WINDOW_DEFAULT_WIDTH = 1400
WINDOW_DEFAULT_HEIGHT = 900

# 颜色主题
COLORS = {
    'primary': '#2E7CF6',
    'secondary': '#F8F9FA', 
    'success': '#28A745',
    'warning': '#FFC107',
    'error': '#DC3545',
    'text': '#212529',
    'muted': '#6C757D'
}

# 筛选操作符
FILTER_OPERATORS = {
    '=': '等于',
    '!=': '不等于',
    '>': '大于',
    '<': '小于',
    '>=': '大于等于',
    '<=': '小于等于',
    'contains': '包含',
    'not_contains': '不包含',
    'startswith': '开头是',
    'endswith': '结尾是',
    'is_null': '为空',
    'is_not_null': '不为空'
}

# 逻辑操作符
LOGIC_OPERATORS = {
    'AND': '与',
    'OR': '或'
}

# 数据类型
DATA_TYPES = {
    'string': '文本',
    'number': '数字',
    'datetime': '日期时间',
    'boolean': '布尔值'
}

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5 