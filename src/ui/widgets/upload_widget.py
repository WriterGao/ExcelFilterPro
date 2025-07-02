"""
文件上传组件
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QGroupBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

from typing import List
from pathlib import Path

from ...utils.logger import get_logger
from ...utils.helpers import validate_excel_file, format_file_size
from ...utils.constants import SUPPORTED_EXCEL_FORMATS


class UploadWidget(QWidget):
    """文件上传组件"""
    
    files_changed = Signal(list)  # 文件列表变化信号
    template_changed = Signal(str)  # 模板文件变化信号
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.data_files: List[str] = []
        self.template_file: str = ""
        
        self.setup_ui()
        self.setup_signals()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 数据源文件组
        data_group = QGroupBox("数据源文件")
        data_layout = QVBoxLayout(data_group)
        
        # 数据文件列表
        self.data_file_list = QListWidget()
        self.data_file_list.setMaximumHeight(150)
        data_layout.addWidget(self.data_file_list)
        
        # 数据文件按钮
        data_btn_layout = QHBoxLayout()
        self.add_data_btn = QPushButton("添加数据源")
        self.remove_data_btn = QPushButton("移除选中")
        self.clear_data_btn = QPushButton("清空列表")
        
        data_btn_layout.addWidget(self.add_data_btn)
        data_btn_layout.addWidget(self.remove_data_btn)
        data_btn_layout.addWidget(self.clear_data_btn)
        data_btn_layout.addStretch()
        
        data_layout.addLayout(data_btn_layout)
        layout.addWidget(data_group)
        
        # 模板文件组
        template_group = QGroupBox("输出模板")
        template_layout = QVBoxLayout(template_group)
        
        self.template_label = QLabel("未选择模板文件")
        self.template_label.setStyleSheet("QLabel { color: #666; padding: 10px; }")
        template_layout.addWidget(self.template_label)
        
        # 模板文件按钮
        template_btn_layout = QHBoxLayout()
        self.select_template_btn = QPushButton("选择模板")
        self.clear_template_btn = QPushButton("清除模板")
        
        template_btn_layout.addWidget(self.select_template_btn)
        template_btn_layout.addWidget(self.clear_template_btn)
        template_btn_layout.addStretch()
        
        template_layout.addLayout(template_btn_layout)
        layout.addWidget(template_group)
        
        # 文件信息标签
        self.info_label = QLabel("请选择Excel文件")
        self.info_label.setStyleSheet("QLabel { color: #999; font-size: 12px; }")
        layout.addWidget(self.info_label)
        
        layout.addStretch()
    
    def setup_signals(self):
        """设置信号连接"""
        self.add_data_btn.clicked.connect(self.add_data_files)
        self.remove_data_btn.clicked.connect(self.remove_selected_data_file)
        self.clear_data_btn.clicked.connect(self.clear_data_files)
        self.select_template_btn.clicked.connect(self.select_template_file)
        self.clear_template_btn.clicked.connect(self.clear_template_file)
    
    def add_data_files(self):
        """添加数据源文件"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter(f"Excel文件 ({' '.join(['*' + ext for ext in SUPPORTED_EXCEL_FORMATS])})")
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            valid_files = []
            
            for file_path in selected_files:
                try:
                    validate_excel_file(file_path)
                    if file_path not in self.data_files:
                        valid_files.append(file_path)
                    else:
                        self.logger.warning(f"文件已存在: {file_path}")
                except Exception as e:
                    QMessageBox.warning(self, "文件验证失败", f"文件 {Path(file_path).name}: {str(e)}")
            
            if valid_files:
                self.data_files.extend(valid_files)
                self.update_data_file_list()
                self.files_changed.emit(self.data_files)
                self.logger.info(f"添加了 {len(valid_files)} 个数据文件")
    
    def remove_selected_data_file(self):
        """移除选中的数据文件"""
        current_row = self.data_file_list.currentRow()
        if current_row >= 0:
            removed_file = self.data_files.pop(current_row)
            self.update_data_file_list()
            self.files_changed.emit(self.data_files)
            self.logger.info(f"移除数据文件: {removed_file}")
    
    def clear_data_files(self):
        """清空所有数据文件"""
        if self.data_files:
            self.data_files.clear()
            self.update_data_file_list()
            self.files_changed.emit(self.data_files)
            self.logger.info("清空所有数据文件")
    
    def update_data_file_list(self):
        """更新数据文件列表显示"""
        self.data_file_list.clear()
        
        for file_path in self.data_files:
            file_path_obj = Path(file_path)
            file_size = format_file_size(file_path_obj.stat().st_size)
            
            item = QListWidgetItem(f"{file_path_obj.name} ({file_size})")
            item.setToolTip(str(file_path_obj))
            self.data_file_list.addItem(item)
        
        # 更新信息标签
        if self.data_files:
            total_files = len(self.data_files)
            self.info_label.setText(f"已选择 {total_files} 个数据源文件")
        else:
            self.info_label.setText("请选择Excel文件")
    
    def select_template_file(self):
        """选择模板文件"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter(f"Excel文件 ({' '.join(['*' + ext for ext in SUPPORTED_EXCEL_FORMATS])})")
        
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            
            try:
                validate_excel_file(file_path)
                self.template_file = file_path
                self.update_template_display()
                self.template_changed.emit(self.template_file)
                self.logger.info(f"选择模板文件: {file_path}")
                
            except Exception as e:
                QMessageBox.warning(self, "模板文件验证失败", str(e))
    
    def clear_template_file(self):
        """清除模板文件"""
        if self.template_file:
            self.template_file = ""
            self.update_template_display()
            self.template_changed.emit(self.template_file)
            self.logger.info("清除模板文件")
    
    def update_template_display(self):
        """更新模板文件显示"""
        if self.template_file:
            file_path_obj = Path(self.template_file)
            file_size = format_file_size(file_path_obj.stat().st_size)
            self.template_label.setText(f"{file_path_obj.name} ({file_size})")
            self.template_label.setStyleSheet("QLabel { color: #333; padding: 10px; }")
            self.template_label.setToolTip(str(file_path_obj))
        else:
            self.template_label.setText("未选择模板文件")
            self.template_label.setStyleSheet("QLabel { color: #666; padding: 10px; }")
            self.template_label.setToolTip("")
    
    def get_data_files(self) -> List[str]:
        """获取数据源文件列表"""
        return self.data_files.copy()
    
    def get_template_file(self) -> str:
        """获取模板文件路径"""
        return self.template_file
    
    def has_files(self) -> bool:
        """检查是否有文件"""
        return len(self.data_files) > 0
    
    def has_template(self) -> bool:
        """检查是否有模板"""
        return bool(self.template_file)
