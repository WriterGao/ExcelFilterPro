"""
字段映射配置组件
允许用户自定义字段映射关系
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QComboBox, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal
from typing import Dict, List, Optional

from ...utils.logger import get_logger


class FieldMappingDialog(QDialog):
    """字段映射配置对话框"""
    
    mapping_confirmed = Signal(dict)  # 字段映射确认信号
    
    def __init__(self, available_fields: List[str], parent=None):
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.available_fields = available_fields
        self.standard_fields = [
            "设备编号", "220kV设备编号", "设备名称", "变电站名称",
            "上月电度表指示数", "本月电度表指示数", 
            "倍率", "输出电量", "功率因数", "电压等级"
        ]
        self.field_mapping: Dict[str, str] = {}
        
        self.setup_ui()
        self.setup_signals()
        
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("字段映射配置")
        self.setModal(True)
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # 说明标签
        info_label = QLabel(
            "请为每个标准字段选择对应的Excel列名。如果某个字段在您的表中不存在，请选择'无对应字段'。"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 映射表格
        self.mapping_table = QTableWidget()
        self.mapping_table.setColumnCount(2)
        self.mapping_table.setHorizontalHeaderLabels(["标准字段名", "Excel列名"])
        
        # 设置表格属性
        header = self.mapping_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        self.populate_mapping_table()
        layout.addWidget(self.mapping_table)
        
        # 按钮组
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept_mapping)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def populate_mapping_table(self):
        """填充映射表格"""
        self.mapping_table.setRowCount(len(self.standard_fields))
        
        # 准备选项列表
        field_options = ["无对应字段"] + self.available_fields
        
        for i, standard_field in enumerate(self.standard_fields):
            # 标准字段名（不可编辑）
            field_item = QTableWidgetItem(standard_field)
            field_item.setFlags(field_item.flags() & ~Qt.ItemIsEditable)
            self.mapping_table.setItem(i, 0, field_item)
            
            # Excel列名选择下拉框
            combo = QComboBox()
            combo.addItems(field_options)
            
            # 尝试智能匹配
            matched_field = self.smart_match_field(standard_field)
            if matched_field:
                index = combo.findText(matched_field)
                if index >= 0:
                    combo.setCurrentIndex(index)
            
            self.mapping_table.setCellWidget(i, 1, combo)
    
    def smart_match_field(self, standard_field: str) -> Optional[str]:
        """智能匹配字段"""
        # 关键词映射
        keyword_map = {
            "设备编号": ["设备", "编号", "device", "equipment"],
            "220kV设备编号": ["220", "kV", "设备"],
            "设备名称": ["设备", "名称", "name"],
            "变电站名称": ["变电站", "station"],
            "上月电度表指示数": ["上月", "电度", "指示"],
            "本月电度表指示数": ["本月", "电度", "指示"],
            "倍率": ["倍率", "ratio"],
            "输出电量": ["输出", "电量", "output"],
            "功率因数": ["功率", "因数", "factor"],
            "电压等级": ["电压", "等级", "voltage"]
        }
        
        keywords = keyword_map.get(standard_field, [])
        
        for available_field in self.available_fields:
            available_lower = available_field.lower()
            
            # 精确匹配
            if standard_field == available_field:
                return available_field
            
            # 关键词匹配
            matches = 0
            for keyword in keywords:
                if keyword.lower() in available_lower:
                    matches += 1
            
            # 如果匹配多个关键词，认为是匹配的
            if matches >= 2:
                return available_field
            
            # 单关键词匹配（权重较低）
            if matches == 1 and len(keywords) == 1:
                return available_field
        
        return None
    
    def accept_mapping(self):
        """确认映射配置"""
        self.field_mapping.clear()
        
        for i in range(self.mapping_table.rowCount()):
            standard_field = self.mapping_table.item(i, 0).text()
            combo = self.mapping_table.cellWidget(i, 1)
            selected_field = combo.currentText()
            
            if selected_field != "无对应字段":
                self.field_mapping[standard_field] = selected_field
        
        if not self.field_mapping:
            QMessageBox.warning(
                self, "警告", 
                "请至少配置一个字段映射关系！"
            )
            return
        
        self.mapping_confirmed.emit(self.field_mapping)
        self.accept()
    
    def setup_signals(self):
        """设置信号连接"""
        pass


class FieldMappingWidget(QWidget):
    """字段映射管理组件"""
    
    mapping_changed = Signal(dict)  # 映射关系变化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.current_mapping: Dict[str, str] = {}
        self.available_fields: List[str] = []
        
        self.setup_ui()
        self.setup_signals()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 字段映射组
        mapping_group = QGroupBox("字段映射配置")
        mapping_layout = QVBoxLayout(mapping_group)
        
        # 状态显示
        self.status_label = QLabel("当前映射: 未配置")
        mapping_layout.addWidget(self.status_label)
        
        # 配置按钮
        button_layout = QHBoxLayout()
        
        self.config_btn = QPushButton("配置字段映射")
        self.config_btn.setEnabled(False)
        button_layout.addWidget(self.config_btn)
        
        self.clear_btn = QPushButton("清除映射")
        self.clear_btn.setEnabled(False)
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        
        mapping_layout.addLayout(button_layout)
        
        layout.addWidget(mapping_group)
        layout.addStretch()
    
    def setup_signals(self):
        """设置信号连接"""
        self.config_btn.clicked.connect(self.configure_mapping)
        self.clear_btn.clicked.connect(self.clear_mapping)
    
    def set_available_fields(self, fields: List[str]):
        """设置可用字段列表"""
        self.available_fields = fields
        self.config_btn.setEnabled(len(fields) > 0)
        
        if not fields:
            self.clear_mapping()
            self.status_label.setText("当前映射: 未加载数据")
        else:
            self.status_label.setText(f"当前映射: 未配置 (可用字段: {len(fields)})")
    
    def configure_mapping(self):
        """配置字段映射"""
        if not self.available_fields:
            QMessageBox.warning(self, "警告", "请先加载数据文件！")
            return
        
        dialog = FieldMappingDialog(self.available_fields, self)
        dialog.mapping_confirmed.connect(self.on_mapping_confirmed)
        dialog.exec()
    
    def on_mapping_confirmed(self, mapping: Dict[str, str]):
        """映射配置确认处理"""
        self.current_mapping = mapping.copy()
        self.clear_btn.setEnabled(True)
        
        # 更新状态显示
        mapped_count = len(mapping)
        self.status_label.setText(f"当前映射: 已配置 {mapped_count} 个字段")
        
        # 发出信号
        self.mapping_changed.emit(self.current_mapping)
        
        self.logger.info(f"字段映射已配置: {mapping}")
    
    def clear_mapping(self):
        """清除字段映射"""
        self.current_mapping.clear()
        self.clear_btn.setEnabled(False)
        
        field_count = len(self.available_fields)
        if field_count > 0:
            self.status_label.setText(f"当前映射: 未配置 (可用字段: {field_count})")
        else:
            self.status_label.setText("当前映射: 未加载数据")
        
        # 发出信号
        self.mapping_changed.emit(self.current_mapping)
        
        self.logger.info("字段映射已清除")
    
    def get_mapping(self) -> Dict[str, str]:
        """获取当前映射关系"""
        return self.current_mapping.copy()
    
    def has_mapping(self) -> bool:
        """检查是否有映射配置"""
        return len(self.current_mapping) > 0 