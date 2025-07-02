"""
数据映射配置对话框
支持"查找匹配并复制数据"的配置
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QGroupBox, QPushButton, QDialogButtonBox, QLabel, QMessageBox, QScrollArea, QWidget
)
from PySide6.QtCore import Qt, Signal
from typing import List, Optional
import uuid
from datetime import datetime

from ...utils.logger import get_logger
from ...database.models import DataMapping, FilterOperator, ExcelCoordinate


class DataMappingDialog(QDialog):
    """数据映射配置对话框"""
    
    mapping_configured = Signal(object)  # 映射配置完成信号
    
    def __init__(self, source_files: List[str], target_files: List[str], 
                 mapping: Optional[DataMapping] = None, parent=None):
        super().__init__(parent)
        self.source_files = source_files
        self.target_files = target_files
        self.mapping = mapping
        self.logger = get_logger(__name__)
        
        self.setup_ui()
        self.setup_signals()
        
        if mapping:
            self.load_mapping(mapping)
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("配置数据映射")
        self.setModal(True)
        self.resize(650, 700)  # 增加高度，确保所有内容都可见
        
        # 使用滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 主内容部件
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # 基本信息
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout(basic_group)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入映射名称")
        basic_layout.addRow("映射名称*:", self.name_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(50)  # 减少高度
        self.description_input.setPlaceholderText("可选：映射描述")
        basic_layout.addRow("映射描述:", self.description_input)
        
        layout.addWidget(basic_group)
        
        # 源数据配置
        source_group = QGroupBox("源数据配置")
        source_layout = QFormLayout(source_group)
        
        self.source_file_combo = QComboBox()
        self.source_file_combo.addItems(self.source_files if self.source_files else ["请先上传数据源"])
        source_layout.addRow("源文件:", self.source_file_combo)
        
        self.source_match_column_combo = QComboBox()
        self.populate_columns(self.source_match_column_combo)
        source_layout.addRow("匹配列:", self.source_match_column_combo)
        
        self.source_match_operator_combo = QComboBox()
        self.populate_operators(self.source_match_operator_combo)
        source_layout.addRow("匹配条件:", self.source_match_operator_combo)
        
        self.source_match_value_input = QLineEdit()
        self.source_match_value_input.setPlaceholderText("如：202 2号主变")
        source_layout.addRow("匹配值:", self.source_match_value_input)
        
        self.source_value_column_combo = QComboBox()
        self.populate_columns(self.source_value_column_combo)
        source_layout.addRow("取值列:", self.source_value_column_combo)
        
        layout.addWidget(source_group)
        
        # 目标数据配置
        target_group = QGroupBox("目标数据配置")
        target_layout = QFormLayout(target_group)
        
        self.target_file_combo = QComboBox()
        self.target_file_combo.addItems(self.target_files if self.target_files else ["请先选择输出模板"])
        target_layout.addRow("目标文件:", self.target_file_combo)
        
        self.target_match_column_combo = QComboBox()
        self.populate_columns(self.target_match_column_combo)
        target_layout.addRow("匹配列:", self.target_match_column_combo)
        
        self.target_match_value_input = QLineEdit()
        self.target_match_value_input.setPlaceholderText("如：202 2号主变")
        target_layout.addRow("匹配值:", self.target_match_value_input)
        
        self.target_insert_column_combo = QComboBox()
        self.populate_columns(self.target_insert_column_combo)
        target_layout.addRow("插入列:", self.target_insert_column_combo)
        
        layout.addWidget(target_group)
        
        # 操作选项
        options_group = QGroupBox("操作选项")
        options_layout = QFormLayout(options_group)
        
        self.overwrite_checkbox = QCheckBox()
        self.overwrite_checkbox.setChecked(True)
        self.overwrite_checkbox.setText("覆盖已有数据")
        options_layout.addRow("覆盖模式:", self.overwrite_checkbox)
        
        layout.addWidget(options_group)
        
        # 配置预览 - 使用可折叠的组件
        preview_group = QGroupBox("配置预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel()
        self.preview_label.setWordWrap(True)
        self.preview_label.setMaximumHeight(120)  # 限制预览高度
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ccc;
                background-color: #f9f9f9;
                padding: 8px;
                border-radius: 4px;
                font-size: 11px;
            }
        """)
        
        # 为预览添加滚动条
        preview_scroll = QScrollArea()
        preview_scroll.setMaximumHeight(120)
        preview_scroll.setWidget(self.preview_label)
        preview_scroll.setWidgetResizable(True)
        preview_layout.addWidget(preview_scroll)
        
        layout.addWidget(preview_group)
        
        # 设置滚动区域的内容
        scroll_area.setWidget(content_widget)
        
        # 主对话框布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        
        # 按钮 - 固定在底部
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept_mapping)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        # 更新预览
        self.update_preview()
    
    def populate_columns(self, combo: QComboBox):
        """填充列选择器"""
        columns = []
        # A-Z
        for i in range(26):
            columns.append(chr(ord('A') + i))
        # AA-AZ
        for i in range(26):
            columns.append('A' + chr(ord('A') + i))
        
        combo.addItems(columns)
    
    def populate_operators(self, combo: QComboBox):
        """填充操作符选择器"""
        operators = [
            ("等于", "等于"),
            ("包含", "包含"),
            ("开头是", "开头是"),
            ("结尾是", "结尾是"),
            ("不等于", "不等于"),
            ("不包含", "不包含")
        ]
        
        for display_name, value in operators:
            combo.addItem(display_name, value)
    
    def setup_signals(self):
        """设置信号连接"""
        # 各种输入变化时更新预览
        self.name_input.textChanged.connect(self.update_preview)
        self.source_file_combo.currentTextChanged.connect(self.update_preview)
        self.source_match_column_combo.currentTextChanged.connect(self.update_preview)
        self.source_match_operator_combo.currentTextChanged.connect(self.update_preview)
        self.source_match_value_input.textChanged.connect(self.update_preview)
        self.source_value_column_combo.currentTextChanged.connect(self.update_preview)
        self.target_file_combo.currentTextChanged.connect(self.update_preview)
        self.target_match_column_combo.currentTextChanged.connect(self.update_preview)
        self.target_match_value_input.textChanged.connect(self.update_preview)
        self.target_insert_column_combo.currentTextChanged.connect(self.update_preview)
        self.overwrite_checkbox.toggled.connect(self.update_preview)
    
    def update_preview(self):
        """更新配置预览"""
        try:
            name = self.name_input.text() or "未命名映射"
            
            # 源配置
            source_file = self.source_file_combo.currentText()
            source_match_col = self.source_match_column_combo.currentText()
            source_operator = self.source_match_operator_combo.currentText()
            source_match_val = self.source_match_value_input.text()
            source_value_col = self.source_value_column_combo.currentText()
            
            # 目标配置
            target_file = self.target_file_combo.currentText()
            target_match_col = self.target_match_column_combo.currentText()
            target_match_val = self.target_match_value_input.text()
            target_insert_col = self.target_insert_column_combo.currentText()
            
            # 操作选项
            overwrite = self.overwrite_checkbox.isChecked()
            
            preview_text = f"""
映射名称: {name}

源数据操作:
• 从文件: {source_file}
• 在 {source_match_col} 列中查找 {source_operator} "{source_match_val}" 的行
• 提取这些行对应的 {source_value_col} 列的值

目标数据操作:
• 到文件: {target_file}
• 在 {target_match_col} 列中查找等于 "{target_match_val}" 的行
• 将提取的值插入到这些行对应的 {target_insert_col} 列

操作模式: {'覆盖已有数据' if overwrite else '仅插入空白位置'}

示例说明:
如果源文件的B列中有3行数据='202 2号主变'，对应的C列值为[100, 200, 300]
那么在目标文件的A列中找到所有='202 2号主变'的行，将[100, 200, 300]依次插入到对应的D列中
            """.strip()
            
            self.preview_label.setText(preview_text)
            
        except Exception as e:
            self.preview_label.setText(f"预览错误: {e}")
    
    def load_mapping(self, mapping: DataMapping):
        """加载映射数据"""
        self.name_input.setText(mapping.name)
        self.description_input.setPlainText(mapping.description)
        
        # 源文件配置
        if mapping.source_file in self.source_files:
            self.source_file_combo.setCurrentText(mapping.source_file)
        
        self.source_match_column_combo.setCurrentText(mapping.source_match_coordinate.column)
        
        # 设置操作符
        for i in range(self.source_match_operator_combo.count()):
            if self.source_match_operator_combo.itemData(i) == mapping.match_operator.value:
                self.source_match_operator_combo.setCurrentIndex(i)
                break
        
        self.source_match_value_input.setText(str(mapping.source_match_value))
        self.source_value_column_combo.setCurrentText(mapping.source_value_coordinate.column)
        
        # 目标文件配置
        if mapping.target_file in self.target_files:
            self.target_file_combo.setCurrentText(mapping.target_file)
        
        self.target_match_column_combo.setCurrentText(mapping.target_match_coordinate.column)
        self.target_match_value_input.setText(str(mapping.target_match_value))
        self.target_insert_column_combo.setCurrentText(mapping.target_insert_coordinate.column)
        
        # 操作选项
        self.overwrite_checkbox.setChecked(mapping.overwrite_existing)
        
        self.update_preview()
    
    def accept_mapping(self):
        """确认映射配置"""
        try:
            # 验证输入
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "警告", "请输入映射名称！")
                return
            
            source_file = self.source_file_combo.currentText()
            if not source_file or source_file == "请先上传数据源":
                QMessageBox.warning(self, "警告", "请选择源文件！")
                return
            
            target_file = self.target_file_combo.currentText()
            if not target_file or target_file == "请先选择输出模板":
                QMessageBox.warning(self, "警告", "请选择目标文件！")
                return
            
            source_match_value = self.source_match_value_input.text().strip()
            if not source_match_value:
                QMessageBox.warning(self, "警告", "请输入源匹配值！")
                return
            
            target_match_value = self.target_match_value_input.text().strip()
            if not target_match_value:
                QMessageBox.warning(self, "警告", "请输入目标匹配值！")
                return
            
            # 获取操作符
            operator_value = self.source_match_operator_combo.currentData()
            operator = None
            for op in FilterOperator:
                if op.value == operator_value:
                    operator = op
                    break
            
            if not operator:
                QMessageBox.warning(self, "警告", "无效的操作符！")
                return
            
            # 创建坐标对象
            source_match_coord = ExcelCoordinate.from_string(self.source_match_column_combo.currentText())
            source_value_coord = ExcelCoordinate.from_string(self.source_value_column_combo.currentText())
            target_match_coord = ExcelCoordinate.from_string(self.target_match_column_combo.currentText())
            target_insert_coord = ExcelCoordinate.from_string(self.target_insert_column_combo.currentText())
            
            # 创建或更新映射
            if self.mapping:
                # 更新现有映射
                self.mapping.name = name
                self.mapping.description = self.description_input.toPlainText().strip()
                self.mapping.source_file = source_file
                self.mapping.source_match_coordinate = source_match_coord
                self.mapping.source_match_value = source_match_value
                self.mapping.source_value_coordinate = source_value_coord
                self.mapping.target_file = target_file
                self.mapping.target_match_coordinate = target_match_coord
                self.mapping.target_match_value = target_match_value
                self.mapping.target_insert_coordinate = target_insert_coord
                self.mapping.match_operator = operator
                self.mapping.overwrite_existing = self.overwrite_checkbox.isChecked()
                self.mapping.modified_time = datetime.now()
            else:
                # 创建新映射
                self.mapping = DataMapping(
                    mapping_id=str(uuid.uuid4()),
                    name=name,
                    description=self.description_input.toPlainText().strip(),
                    source_file=source_file,
                    source_match_coordinate=source_match_coord,
                    source_match_value=source_match_value,
                    source_value_coordinate=source_value_coord,
                    target_file=target_file,
                    target_match_coordinate=target_match_coord,
                    target_match_value=target_match_value,
                    target_insert_coordinate=target_insert_coord,
                    match_operator=operator,
                    overwrite_existing=self.overwrite_checkbox.isChecked()
                )
            
            self.mapping_configured.emit(self.mapping)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"配置映射失败: {e}")
    
    def get_mapping(self) -> Optional[DataMapping]:
        """获取配置的映射"""
        return self.mapping 