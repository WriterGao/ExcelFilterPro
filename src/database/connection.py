"""
数据库连接模块
"""

import sqlite3
from pathlib import Path
from typing import Optional

from ..utils.logger import get_logger
from ..utils.constants import DATABASE_NAME


class DatabaseConnection:
    """数据库连接管理"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.logger = get_logger(__name__)
        self.db_path = db_path or DATABASE_NAME
        self.connection: Optional[sqlite3.Connection] = None
        
    def connect(self) -> sqlite3.Connection:
        """建立数据库连接"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.logger.info(f"数据库连接成功: {self.db_path}")
            return self.connection
        except Exception as e:
            self.logger.error(f"数据库连接失败: {e}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.logger.info("数据库连接已关闭")
    
    def execute_script(self, script: str):
        """执行SQL脚本"""
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            cursor.executescript(script)
            self.connection.commit()
            self.logger.info("SQL脚本执行成功")
        except Exception as e:
            self.logger.error(f"SQL脚本执行失败: {e}")
            raise
    
    def init_database(self):
        """初始化数据库"""
        init_sql = """
        CREATE TABLE IF NOT EXISTS filter_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            created_time DATETIME NOT NULL,
            updated_time DATETIME NOT NULL,
            is_active BOOLEAN DEFAULT TRUE
        );
        
        CREATE TABLE IF NOT EXISTS filter_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL,
            name VARCHAR(100) NOT NULL,
            conditions TEXT NOT NULL,
            target_column VARCHAR(50) NOT NULL,
            order_index INTEGER DEFAULT 0,
            is_enabled BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (plan_id) REFERENCES filter_plans (id)
        );
        
        CREATE TABLE IF NOT EXISTS app_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key VARCHAR(100) UNIQUE NOT NULL,
            value TEXT,
            description VARCHAR(200)
        );
        """
        
        self.execute_script(init_sql)
        self.logger.info("数据库初始化完成")
