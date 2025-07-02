"""
自定义异常类模块
定义应用程序特定的异常
"""


class ExcelFilterError(Exception):
    """Excel筛选器基础异常类"""
    pass


class FileProcessingError(ExcelFilterError):
    """文件处理异常"""
    pass


class ExcelFileError(FileProcessingError):
    """Excel文件处理异常"""
    pass


class InvalidFileFormatError(ExcelFileError):
    """无效文件格式异常"""
    pass


class FileSizeExceededError(ExcelFileError):
    """文件大小超限异常"""
    pass


class FilterError(ExcelFilterError):
    """筛选操作异常"""
    pass


class InvalidFilterConditionError(FilterError):
    """无效筛选条件异常"""
    pass


class FilterExecutionError(FilterError):
    """筛选执行异常"""
    pass


class ConfigurationError(ExcelFilterError):
    """配置异常"""
    pass


class DatabaseError(ExcelFilterError):
    """数据库操作异常"""
    pass


class UIError(ExcelFilterError):
    """用户界面异常"""
    pass 