"""
数据映射管理组件
支持完整的数据映射配置和管理
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QLabel, QMessageBox, QTextEdit
)
from PySide6.QtCore import Qt, Signal
from typing import List, Optional
import uuid
from datetime import datetime

from ...utils.logger import get_logger
from ...database.models import DataMapping, DataMappingPlan
from .data_mapping_dialog import DataMappingDialog


class DataMappingWidget(QWidget):
    """数据映射管理组件"""
    
    mappings_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.source_files: List[str] = []  # 数据源文件列表
        self.target_files: List[str] = []  # 目标文件列表
        self.current_mappings: List[DataMapping] = []
        self.excel_processor = None
        
        self.setup_ui()
        self.setup_signals()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 映射管理区域
        mappings_group = QGroupBox("数据映射管理")
        mappings_layout = QVBoxLayout(mappings_group)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.add_mapping_btn = QPushButton("新增映射")
        self.add_mapping_btn.setEnabled(False)
        toolbar_layout.addWidget(self.add_mapping_btn)
        
        self.edit_mapping_btn = QPushButton("编辑映射")
        self.edit_mapping_btn.setEnabled(False)
        toolbar_layout.addWidget(self.edit_mapping_btn)
        
        self.delete_mapping_btn = QPushButton("删除映射")
        self.delete_mapping_btn.setEnabled(False)
        toolbar_layout.addWidget(self.delete_mapping_btn)
        
        toolbar_layout.addStretch()
        
        self.clear_all_btn = QPushButton("清除全部")
        self.clear_all_btn.setEnabled(False)
        toolbar_layout.addWidget(self.clear_all_btn)
        
        mappings_layout.addLayout(toolbar_layout)
        
        # 映射列表
        self.mappings_table = QTableWidget()
        self.mappings_table.setColumnCount(6)
        self.mappings_table.setHorizontalHeaderLabels([
            "映射名称", "源文件", "源配置", "目标文件", "目标配置", "创建时间"
        ])
        
        header = self.mappings_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        mappings_layout.addWidget(self.mappings_table)
        layout.addWidget(mappings_group)
        
        # 映射详情
        details_group = QGroupBox("映射详情")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(120)
        self.details_text.setReadOnly(True)
        self.details_text.setPlaceholderText("选择一个映射查看详细信息...")
        details_layout.addWidget(self.details_text)
        
        layout.addWidget(details_group)
        
        # 使用说明
        help_group = QGroupBox("使用说明")
        help_layout = QVBoxLayout(help_group)
        
        help_text = QLabel("""
<b>数据映射功能说明：</b><br/>
• <b>新增映射</b>：配置从源文件查找匹配数据并复制到目标文件的规则<br/>
• <b>源数据配置</b>：源文件 + 匹配列 + 匹配值 + 取值列<br/>
• <b>目标数据配置</b>：目标文件 + 匹配列 + 匹配值 + 插入列<br/>
• <b>示例</b>：从源文件B列查找'202 2号主变'，提取C列值，插入到目标文件A列='202 2号主变'行的D列
        """)
        help_text.setWordWrap(True)
        help_layout.addWidget(help_text)
        
        layout.addWidget(help_group)
    
    def setup_signals(self):
        """设置信号连接"""
        # 按钮信号
        self.add_mapping_btn.clicked.connect(self.add_mapping)
        self.edit_mapping_btn.clicked.connect(self.edit_mapping)
        self.delete_mapping_btn.clicked.connect(self.delete_mapping)
        self.clear_all_btn.clicked.connect(self.clear_all_mappings)
        
        # 表格选择
        self.mappings_table.itemSelectionChanged.connect(self.on_mapping_selection_changed)
    
    def set_source_files(self, files: List[str], excel_processor=None):
        """设置数据源文件列表"""
        self.source_files = files
        if excel_processor:
            self.excel_processor = excel_processor
        self._update_button_states()
        self.logger.info(f"数据源文件已更新: {len(files)} 个文件")
    
    def set_target_files(self, files: List[str]):
        """设置目标文件列表"""
        self.target_files = files
        self._update_button_states()
        self.logger.info(f"目标文件已更新: {len(files)} 个文件")
    
    def _update_button_states(self):
        """更新按钮状态"""
        has_source = len(self.source_files) > 0
        has_target = len(self.target_files) > 0
        can_create = has_source and has_target
        
        self.add_mapping_btn.setEnabled(can_create)
        self.clear_all_btn.setEnabled(len(self.current_mappings) > 0)
        
        # 映射相关按钮
        has_selected = self.mappings_table.currentRow() >= 0
        self.edit_mapping_btn.setEnabled(has_selected and can_create)
        self.delete_mapping_btn.setEnabled(has_selected)
        
        # 设置工具提示
        if not can_create:
            if not has_source and not has_target:
                self.add_mapping_btn.setToolTip("请先上传数据源文件和选择目标文件")
            elif not has_source:
                self.add_mapping_btn.setToolTip("请先上传数据源文件")
            elif not has_target:
                self.add_mapping_btn.setToolTip("请先选择目标文件")
        else:
            self.add_mapping_btn.setToolTip("创建新的数据映射")
    
    def add_mapping(self):
        """新增映射"""
        dialog = DataMappingDialog(self.source_files, self.target_files, parent=self)
        dialog.mapping_configured.connect(self._on_mapping_configured)
        dialog.exec()
    
    def edit_mapping(self):
        """编辑映射"""
        current_row = self.mappings_table.currentRow()
        if current_row < 0 or current_row >= len(self.current_mappings):
            return
        
        mapping = self.current_mappings[current_row]
        dialog = DataMappingDialog(self.source_files, self.target_files, mapping, parent=self)
        dialog.mapping_configured.connect(self._on_mapping_configured)
        dialog.exec()
    
    def delete_mapping(self):
        """删除映射"""
        current_row = self.mappings_table.currentRow()
        if current_row < 0 or current_row >= len(self.current_mappings):
            return
        
        mapping = self.current_mappings[current_row]
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除映射 '{mapping.name}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.current_mappings[current_row]
            self.refresh_mappings_table()
            self.mappings_changed.emit()
            self.logger.info(f"删除映射: {mapping.name}")
    
    def clear_all_mappings(self):
        """清除全部映射"""
        if not self.current_mappings:
            return
        
        reply = QMessageBox.question(
            self, "确认清除",
            f"确定要清除全部 {len(self.current_mappings)} 个映射吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.current_mappings.clear()
            self.refresh_mappings_table()
            self.mappings_changed.emit()
            self.logger.info("清除全部映射")
    
    def add_mapping_from_data(self, mapping: DataMapping):
        """从数据对象添加映射（用于加载保存的方案）"""
        # 检查是否为新映射
        existing_index = -1
        for i, existing_mapping in enumerate(self.current_mappings):
            if existing_mapping.mapping_id == mapping.mapping_id:
                existing_index = i
                break
        
        if existing_index >= 0:
            # 更新现有映射
            self.current_mappings[existing_index] = mapping
        else:
            # 添加新映射
            self.current_mappings.append(mapping)
        
        self.refresh_mappings_table()
        self.mappings_changed.emit()
        self.logger.info(f"从数据添加映射: {mapping.name}")
    
    def _on_mapping_configured(self, mapping: DataMapping):
        """映射配置完成处理"""
        # 检查是否为新映射
        existing_index = -1
        for i, existing_mapping in enumerate(self.current_mappings):
            if existing_mapping.mapping_id == mapping.mapping_id:
                existing_index = i
                break
        
        if existing_index >= 0:
            # 更新现有映射
            self.current_mappings[existing_index] = mapping
        else:
            # 添加新映射
            self.current_mappings.append(mapping)
        
        self.refresh_mappings_table()
        
        # 选择当前映射
        if existing_index >= 0:
            self.mappings_table.selectRow(existing_index)
        else:
            self.mappings_table.selectRow(len(self.current_mappings) - 1)
        
        self.mappings_changed.emit()
        self.logger.info(f"映射配置完成: {mapping.name}")
    
    def refresh_mappings_table(self):
        """刷新映射表格"""
        self.mappings_table.setRowCount(len(self.current_mappings))
        
        for row, mapping in enumerate(self.current_mappings):
            # 映射名称
            self.mappings_table.setItem(row, 0, QTableWidgetItem(mapping.name))
            
            # 源文件
            self.mappings_table.setItem(row, 1, QTableWidgetItem(mapping.source_file))
            
            # 源配置
            source_config = f"{mapping.source_match_coordinate}={mapping.source_match_value} → {mapping.source_value_coordinate}"
            self.mappings_table.setItem(row, 2, QTableWidgetItem(source_config))
            
            # 目标文件
            self.mappings_table.setItem(row, 3, QTableWidgetItem(mapping.target_file))
            
            # 目标配置
            target_config = f"{mapping.target_match_coordinate}={mapping.target_match_value} → {mapping.target_insert_coordinate}"
            self.mappings_table.setItem(row, 4, QTableWidgetItem(target_config))
            
            # 创建时间
            time_str = mapping.created_time.strftime("%m-%d %H:%M")
            self.mappings_table.setItem(row, 5, QTableWidgetItem(time_str))
        
        self._update_button_states()
    
    def on_mapping_selection_changed(self):
        """映射选择变化处理"""
        current_row = self.mappings_table.currentRow()
        
        if current_row < 0 or current_row >= len(self.current_mappings):
            self.details_text.clear()
            self._update_button_states()
            return
        
        mapping = self.current_mappings[current_row]
        self.update_mapping_details(mapping)
        self._update_button_states()
    
    def update_mapping_details(self, mapping: DataMapping):
        """更新映射详情"""
        details = f"""
<b>映射名称:</b> {mapping.name}<br/>
<b>映射描述:</b> {mapping.description}<br/>
<br/>
<b>源数据配置:</b><br/>
• 源文件: {mapping.source_file}<br/>
• 匹配列: {mapping.source_match_coordinate} (查找 {mapping.match_operator.value} "{mapping.source_match_value}")<br/>
• 取值列: {mapping.source_value_coordinate}<br/>
<br/>
<b>目标数据配置:</b><br/>
• 目标文件: {mapping.target_file}<br/>
• 匹配列: {mapping.target_match_coordinate} (查找等于 "{mapping.target_match_value}")<br/>
• 插入列: {mapping.target_insert_coordinate}<br/>
<br/>
<b>操作模式:</b> {'覆盖已有数据' if mapping.overwrite_existing else '仅插入空白位置'}
        """.strip()
        
        self.details_text.setHtml(details)
    
    def get_data_mappings(self) -> List[DataMapping]:
        """获取当前配置的数据映射"""
        return self.current_mappings.copy()
    
    def set_data_mappings(self, mappings: List[DataMapping]):
        """设置数据映射"""
        self.current_mappings = mappings.copy()
        self.refresh_mappings_table()
        self._update_button_states()
        self.logger.info(f"加载数据映射: {len(mappings)} 个")
    
    def execute_mappings(self):
        """执行所有映射（供外部调用）"""
        if not self.current_mappings:
            QMessageBox.warning(self, "警告", "没有配置任何数据映射！")
            return None
        
        if not self.excel_processor:
            QMessageBox.warning(self, "警告", "Excel处理器未初始化！")
            return None
        
        return self.current_mappings 