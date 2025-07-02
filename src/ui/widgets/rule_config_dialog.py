"""
规则配置对话框
用于创建和编辑筛选规则的配置
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QCheckBox,
    QGroupBox, QPushButton, QDialogButtonBox, QLabel, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from typing import List, Optional
import uuid
from datetime import datetime

from ...utils.logger import get_logger
from ...database.models import CoordinateFilterRule, RuleOutputConfig


class RuleConfigDialog(QDialog):
    """规则配置对话框"""
    
    rule_configured = Signal(object)  # 规则配置完成信号
    
    def __init__(self, template_files: List[str], rule: Optional[CoordinateFilterRule] = None, parent=None):
        super().__init__(parent)
        self.template_files = template_files
        self.rule = rule
        self.logger = get_logger(__name__)
        
        self.setup_ui()
        self.setup_signals()
        
        if rule:
            self.load_rule(rule)
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("配置筛选规则")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # 规则基本信息
        basic_group = QGroupBox("规则基本信息")
        basic_layout = QFormLayout(basic_group)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入规则名称")
        basic_layout.addRow("规则名称*:", self.name_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("可选：规则描述")
        basic_layout.addRow("规则描述:", self.description_input)
        
        self.logic_combo = QComboBox()
        self.logic_combo.addItems(["AND", "OR"])
        basic_layout.addRow("条件关系:", self.logic_combo)
        
        layout.addWidget(basic_group)
        
        # 输出配置
        output_group = QGroupBox("输出配置")
        output_layout = QFormLayout(output_group)
        
        self.target_file_combo = QComboBox()
        self.target_file_combo.addItems(self.template_files if self.template_files else ["请先选择输出模板"])
        output_layout.addRow("目标文件*:", self.target_file_combo)
        
        self.target_column_combo = QComboBox()
        self.populate_columns()
        output_layout.addRow("目标列*:", self.target_column_combo)
        
        self.start_row_spinbox = QSpinBox()
        self.start_row_spinbox.setMinimum(1)
        self.start_row_spinbox.setMaximum(1048576)
        self.start_row_spinbox.setValue(2)  # 默认从第二行开始（第一行通常是表头）
        output_layout.addRow("起始行*:", self.start_row_spinbox)
        
        self.auto_append_checkbox = QCheckBox()
        self.auto_append_checkbox.setChecked(True)
        self.auto_append_checkbox.setText("自动追加到下一行")
        output_layout.addRow("追加模式:", self.auto_append_checkbox)
        
        layout.addWidget(output_group)
        
        # 配置预览
        preview_group = QGroupBox("配置预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel()
        self.preview_label.setWordWrap(True)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ccc;
                background-color: #f9f9f9;
                padding: 10px;
                border-radius: 4px;
            }
        """)
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_group)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept_config)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # 更新预览
        self.update_preview()
    
    def populate_columns(self):
        """填充列选择器"""
        columns = []
        # A-Z
        for i in range(26):
            columns.append(chr(ord('A') + i))
        # AA-AZ
        for i in range(26):
            columns.append('A' + chr(ord('A') + i))
        
        self.target_column_combo.addItems(columns)
    
    def setup_signals(self):
        """设置信号连接"""
        self.name_input.textChanged.connect(self.update_preview)
        self.description_input.textChanged.connect(self.update_preview)
        self.logic_combo.currentTextChanged.connect(self.update_preview)
        self.target_file_combo.currentTextChanged.connect(self.update_preview)
        self.target_column_combo.currentTextChanged.connect(self.update_preview)
        self.start_row_spinbox.valueChanged.connect(self.update_preview)
        self.auto_append_checkbox.toggled.connect(self.update_preview)
    
    def update_preview(self):
        """更新配置预览"""
        try:
            name = self.name_input.text() or "未命名规则"
            target_file = self.target_file_combo.currentText()
            target_column = self.target_column_combo.currentText()
            start_row = self.start_row_spinbox.value()
            auto_append = self.auto_append_checkbox.isChecked()
            logic = self.logic_combo.currentText()
            
            preview_text = f"""
规则名称: {name}
条件关系: 多个条件之间使用 {logic} 连接
输出目标: {target_file} 的 {target_column} 列
起始位置: 第 {start_row} 行
追加模式: {'开启' if auto_append else '关闭'} - {'符合条件的数据将自动追加到下一行' if auto_append else '每次都从起始行覆盖写入'}
            """.strip()
            
            self.preview_label.setText(preview_text)
            
        except Exception as e:
            self.preview_label.setText(f"预览错误: {e}")
    
    def load_rule(self, rule: CoordinateFilterRule):
        """加载规则数据"""
        self.name_input.setText(rule.name)
        self.description_input.setPlainText(rule.description)
        self.logic_combo.setCurrentText(rule.logic_operator)
        
        if rule.output_config:
            # 设置目标文件
            index = self.target_file_combo.findText(rule.output_config.target_file)
            if index >= 0:
                self.target_file_combo.setCurrentIndex(index)
            
            # 设置目标列
            self.target_column_combo.setCurrentText(rule.output_config.target_column)
            
            # 设置起始行
            self.start_row_spinbox.setValue(rule.output_config.start_row)
            
            # 设置追加模式
            self.auto_append_checkbox.setChecked(rule.output_config.auto_append)
        
        self.update_preview()
    
    def accept_config(self):
        """确认配置"""
        try:
            # 验证输入
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "警告", "请输入规则名称！")
                return
            
            target_file = self.target_file_combo.currentText()
            if not target_file or target_file == "请先选择输出模板":
                QMessageBox.warning(self, "警告", "请选择目标文件！")
                return
            
            target_column = self.target_column_combo.currentText()
            start_row = self.start_row_spinbox.value()
            auto_append = self.auto_append_checkbox.isChecked()
            logic_operator = self.logic_combo.currentText()
            description = self.description_input.toPlainText().strip()
            
            # 创建输出配置
            output_config = RuleOutputConfig(
                target_file=target_file,
                target_column=target_column,
                start_row=start_row,
                auto_append=auto_append
            )
            
            # 创建或更新规则
            if self.rule:
                # 更新现有规则
                self.rule.name = name
                self.rule.description = description
                self.rule.logic_operator = logic_operator
                self.rule.output_config = output_config
                self.rule.modified_time = datetime.now()
            else:
                # 创建新规则
                self.rule = CoordinateFilterRule(
                    rule_id=str(uuid.uuid4()),
                    name=name,
                    description=description,
                    output_config=output_config,
                    logic_operator=logic_operator
                )
            
            self.rule_configured.emit(self.rule)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"配置规则失败: {e}")
    
    def get_rule(self) -> Optional[CoordinateFilterRule]:
        """获取配置的规则"""
        return self.rule 