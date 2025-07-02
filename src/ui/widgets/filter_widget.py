"""
筛选条件组件
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QGroupBox, QComboBox, QLineEdit,
    QFormLayout, QDialog, QDialogButtonBox, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal

from typing import List, Optional, Dict, Any

from ...utils.logger import get_logger
from ...utils.constants import FILTER_OPERATORS, LOGIC_OPERATORS
from ...database.models import FilterRule, FilterCondition


class FilterConditionDialog(QDialog):
    """筛选条件编辑对话框"""
    
    def __init__(self, available_fields: List[str], condition: Optional[FilterCondition] = None):
        super().__init__()
        self.available_fields = available_fields
        self.condition = condition
        self.setup_ui()
        
        if condition:
            self.load_condition(condition)
    
    def setup_ui(self):
        """设置对话框界面"""
        self.setWindowTitle("编辑筛选条件")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # 表单布局
        form_layout = QFormLayout()
        
        # 字段选择
        self.field_combo = QComboBox()
        self.field_combo.addItems(self.available_fields)
        form_layout.addRow("筛选字段:", self.field_combo)
        
        # 操作符选择
        self.operator_combo = QComboBox()
        for op, desc in FILTER_OPERATORS.items():
            self.operator_combo.addItem(desc, op)
        form_layout.addRow("操作符:", self.operator_combo)
        
        # 筛选值
        self.value_edit = QLineEdit()
        form_layout.addRow("筛选值:", self.value_edit)
        
        # 逻辑连接符
        self.logic_combo = QComboBox()
        for logic, desc in LOGIC_OPERATORS.items():
            self.logic_combo.addItem(desc, logic)
        form_layout.addRow("逻辑连接:", self.logic_combo)
        
        layout.addLayout(form_layout)
        
        # 按钮
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
    
    def load_condition(self, condition: FilterCondition):
        """加载条件到界面"""
        # 设置字段
        field_index = self.field_combo.findText(condition.field)
        if field_index >= 0:
            self.field_combo.setCurrentIndex(field_index)
        
        # 设置操作符
        op_index = self.operator_combo.findData(condition.operator)
        if op_index >= 0:
            self.operator_combo.setCurrentIndex(op_index)
        
        # 设置值
        self.value_edit.setText(str(condition.value) if condition.value is not None else "")
        
        # 设置逻辑连接符
        logic_index = self.logic_combo.findData(condition.logic)
        if logic_index >= 0:
            self.logic_combo.setCurrentIndex(logic_index)
    
    def get_condition(self) -> FilterCondition:
        """获取编辑后的条件"""
        return FilterCondition(
            field=self.field_combo.currentText(),
            operator=self.operator_combo.currentData(),
            value=self.value_edit.text(),
            logic=self.logic_combo.currentData()
        )


class FilterRuleWidget(QWidget):
    """单个筛选规则组件"""
    
    rule_changed = Signal()
    
    def __init__(self, rule: FilterRule, available_fields: List[str]):
        super().__init__()
        self.rule = rule
        self.available_fields = available_fields
        self.logger = get_logger(__name__)
        
        self.setup_ui()
        self.update_display()
    
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 规则信息
        info_layout = QHBoxLayout()
        
        self.rule_label = QLabel()
        self.rule_label.setStyleSheet("QLabel { font-weight: bold; }")
        info_layout.addWidget(self.rule_label)
        
        info_layout.addStretch()
        
        # 按钮
        self.edit_btn = QPushButton("编辑")
        self.delete_btn = QPushButton("删除")
        self.delete_btn.setStyleSheet("QPushButton { color: red; }")
        
        info_layout.addWidget(self.edit_btn)
        info_layout.addWidget(self.delete_btn)
        
        layout.addLayout(info_layout)
        
        # 条件列表
        self.conditions_list = QListWidget()
        self.conditions_list.setMaximumHeight(100)
        layout.addWidget(self.conditions_list)
        
        # 条件管理按钮
        cond_btn_layout = QHBoxLayout()
        self.add_condition_btn = QPushButton("添加条件")
        self.edit_condition_btn = QPushButton("编辑条件")
        self.remove_condition_btn = QPushButton("删除条件")
        
        cond_btn_layout.addWidget(self.add_condition_btn)
        cond_btn_layout.addWidget(self.edit_condition_btn)
        cond_btn_layout.addWidget(self.remove_condition_btn)
        cond_btn_layout.addStretch()
        
        layout.addLayout(cond_btn_layout)
        
        # 连接信号
        self.edit_btn.clicked.connect(self.edit_rule)
        self.delete_btn.clicked.connect(self.delete_rule)
        self.add_condition_btn.clicked.connect(self.add_condition)
        self.edit_condition_btn.clicked.connect(self.edit_condition)
        self.remove_condition_btn.clicked.connect(self.remove_condition)
    
    def update_display(self):
        """更新显示"""
        # 更新规则标签
        target_text = f"输出到: {self.rule.target_column}" if self.rule.target_column else "未设置输出列"
        self.rule_label.setText(f"{self.rule.name} ({target_text})")
        
        # 更新条件列表
        self.conditions_list.clear()
        for i, condition in enumerate(self.rule.conditions):
            text = f"{condition.field} {condition.operator} {condition.value}"
            if i > 0:
                text = f"{condition.logic} {text}"
            
            item = QListWidgetItem(text)
            self.conditions_list.addItem(item)
    
    def edit_rule(self):
        """编辑规则基本信息"""
        # 这里可以实现规则编辑对话框
        pass
    
    def delete_rule(self):
        """删除规则"""
        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除规则 '{self.rule.name}' 吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.setParent(None)
            self.rule_changed.emit()
    
    def add_condition(self):
        """添加条件"""
        dialog = FilterConditionDialog(self.available_fields)
        if dialog.exec():
            condition = dialog.get_condition()
            self.rule.add_condition(condition)
            self.update_display()
            self.rule_changed.emit()
    
    def edit_condition(self):
        """编辑选中的条件"""
        current_row = self.conditions_list.currentRow()
        if current_row >= 0 and current_row < len(self.rule.conditions):
            condition = self.rule.conditions[current_row]
            dialog = FilterConditionDialog(self.available_fields, condition)
            
            if dialog.exec():
                new_condition = dialog.get_condition()
                self.rule.conditions[current_row] = new_condition
                self.update_display()
                self.rule_changed.emit()
    
    def remove_condition(self):
        """删除选中的条件"""
        current_row = self.conditions_list.currentRow()
        if current_row >= 0:
            self.rule.remove_condition(current_row)
            self.update_display()
            self.rule_changed.emit()


class FilterWidget(QWidget):
    """筛选条件主组件"""
    
    rules_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.filter_rules: List[FilterRule] = []
        self.available_fields: List[str] = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.add_rule_btn = QPushButton("新增规则")
        self.clear_rules_btn = QPushButton("清空规则")
        
        toolbar_layout.addWidget(self.add_rule_btn)
        toolbar_layout.addWidget(self.clear_rules_btn)
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # 规则列表区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.rules_container = QWidget()
        self.rules_layout = QVBoxLayout(self.rules_container)
        self.rules_layout.addStretch()
        
        self.scroll_area.setWidget(self.rules_container)
        layout.addWidget(self.scroll_area)
        
        # 信息标签
        self.info_label = QLabel("暂无筛选规则")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("QLabel { color: #999; padding: 20px; }")
        layout.addWidget(self.info_label)
        
        # 连接信号
        self.add_rule_btn.clicked.connect(self.add_rule)
        self.clear_rules_btn.clicked.connect(self.clear_rules)
    
    def set_available_fields(self, fields: List[str]):
        """设置可用字段"""
        self.available_fields = fields
        self.logger.info(f"设置可用字段: {len(fields)} 个")
    
    def add_rule(self):
        """添加新规则"""
        if not self.available_fields:
            QMessageBox.warning(self, "警告", "请先加载数据源文件获取可用字段")
            return
        
        # 创建新规则
        rule = FilterRule(
            name=f"规则 {len(self.filter_rules) + 1}",
            target_column="",
            is_enabled=True
        )
        
        self.filter_rules.append(rule)
        self.add_rule_widget(rule)
        self.update_display()
        self.rules_changed.emit()
    
    def add_rule_widget(self, rule: FilterRule):
        """添加规则组件"""
        rule_widget = FilterRuleWidget(rule, self.available_fields)
        rule_widget.rule_changed.connect(self.on_rule_changed)
        
        # 插入到stretch之前
        self.rules_layout.insertWidget(self.rules_layout.count() - 1, rule_widget)
    
    def clear_rules(self):
        """清空所有规则"""
        if self.filter_rules:
            reply = QMessageBox.question(
                self, "确认清空", "确定要清空所有筛选规则吗？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.filter_rules.clear()
                self.clear_rule_widgets()
                self.update_display()
                self.rules_changed.emit()
    
    def clear_rule_widgets(self):
        """清空规则组件"""
        while self.rules_layout.count() > 1:  # 保留stretch
            item = self.rules_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def on_rule_changed(self):
        """规则变化处理"""
        self.update_display()
        self.rules_changed.emit()
    
    def update_display(self):
        """更新显示"""
        if self.filter_rules:
            self.info_label.hide()
            self.scroll_area.show()
        else:
            self.info_label.show()
            self.scroll_area.hide()
    
    def get_filter_rules(self) -> List[FilterRule]:
        """获取筛选规则"""
        return self.filter_rules.copy()
    
    def set_filter_rules(self, rules: List[FilterRule]):
        """设置筛选规则"""
        self.filter_rules = rules.copy()
        self.clear_rule_widgets()
        
        for rule in self.filter_rules:
            self.add_rule_widget(rule)
        
        self.update_display()
