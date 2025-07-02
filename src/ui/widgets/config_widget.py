"""
配置管理组件
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QGroupBox, QLineEdit, QTextEdit,
    QDialog, QDialogButtonBox, QMessageBox, QFileDialog, QFormLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from typing import List, Optional
from pathlib import Path
import json
import uuid
from datetime import datetime

from ...utils.logger import get_logger
from ...database.models import DataMappingPlan, DataMapping, FilterOperator


class DataMappingPlanEditDialog(QDialog):
    """数据映射方案编辑对话框"""
    
    def __init__(self, plan: Optional[DataMappingPlan] = None):
        super().__init__()
        self.plan = plan
        self.setup_ui()
        
        if plan:
            self.load_plan(plan)
    
    def setup_ui(self):
        """设置对话框界面"""
        title = "编辑数据映射方案" if self.plan else "新建数据映射方案"
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # 表单布局
        form_layout = QFormLayout()
        
        # 方案名称
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入方案名称")
        form_layout.addRow("方案名称:", self.name_edit)
        
        # 方案描述
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("请输入方案描述（可选）")
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("方案描述:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # 按钮
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        
        # 验证
        self.name_edit.textChanged.connect(self.validate_input)
        self.validate_input()
    
    def load_plan(self, plan: DataMappingPlan):
        """加载方案到界面"""
        self.name_edit.setText(plan.name)
        self.description_edit.setPlainText(plan.description)
    
    def validate_input(self):
        """验证输入"""
        name = self.name_edit.text().strip()
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(bool(name))
    
    def get_plan_data(self) -> tuple:
        """获取方案数据"""
        return (
            self.name_edit.text().strip(),
            self.description_edit.toPlainText().strip()
        )


class ConfigWidget(QWidget):
    """数据映射方案配置管理组件"""
    
    plan_selected = Signal(object)  # 方案选中信号
    plan_loaded = Signal(object)    # 方案加载信号
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.current_plan: Optional[DataMappingPlan] = None
        self.current_mappings: List[DataMapping] = []
        self.data_mapping_widget = None  # 引用数据映射组件
        self.plan_file_paths = {}  # 方案ID到文件路径的映射
        
        self.setup_ui()
        self.load_plans()
    
    def set_data_mapping_widget(self, widget):
        """设置数据映射组件的引用"""
        self.data_mapping_widget = widget
    
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 当前方案组
        current_group = QGroupBox("当前方案")
        current_layout = QVBoxLayout(current_group)
        
        self.current_plan_label = QLabel("无当前方案")
        self.current_plan_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        current_layout.addWidget(self.current_plan_label)
        
        # 当前方案按钮
        current_btn_layout = QHBoxLayout()
        self.save_current_btn = QPushButton("保存当前")
        self.save_as_btn = QPushButton("另存为")
        self.clear_current_btn = QPushButton("清空当前")
        
        current_btn_layout.addWidget(self.save_current_btn)
        current_btn_layout.addWidget(self.save_as_btn)
        current_btn_layout.addWidget(self.clear_current_btn)
        current_btn_layout.addStretch()
        
        current_layout.addLayout(current_btn_layout)
        layout.addWidget(current_group)
        
        # 已保存方案组
        saved_group = QGroupBox("已保存方案")
        saved_layout = QVBoxLayout(saved_group)
        
        # 方案列表
        self.plans_list = QListWidget()
        self.plans_list.setMaximumHeight(200)
        saved_layout.addWidget(self.plans_list)
        
        # 方案管理按钮
        plans_btn_layout = QHBoxLayout()
        self.new_plan_btn = QPushButton("新建方案")
        self.load_plan_btn = QPushButton("加载方案")
        self.edit_plan_btn = QPushButton("编辑方案")
        self.delete_plan_btn = QPushButton("删除方案")
        
        plans_btn_layout.addWidget(self.new_plan_btn)
        plans_btn_layout.addWidget(self.load_plan_btn)
        plans_btn_layout.addWidget(self.edit_plan_btn)
        plans_btn_layout.addWidget(self.delete_plan_btn)
        
        saved_layout.addLayout(plans_btn_layout)
        
        # 导入导出按钮
        io_btn_layout = QHBoxLayout()
        self.import_btn = QPushButton("导入方案")
        self.export_btn = QPushButton("导出方案")
        
        io_btn_layout.addWidget(self.import_btn)
        io_btn_layout.addWidget(self.export_btn)
        io_btn_layout.addStretch()
        
        saved_layout.addLayout(io_btn_layout)
        layout.addWidget(saved_group)
        
        layout.addStretch()
        
        # 连接信号
        self.save_current_btn.clicked.connect(self.save_current_plan)
        self.save_as_btn.clicked.connect(self.save_as_plan)
        self.clear_current_btn.clicked.connect(self.clear_current_plan)
        self.new_plan_btn.clicked.connect(self.new_plan)
        self.load_plan_btn.clicked.connect(self.load_selected_plan)
        self.edit_plan_btn.clicked.connect(self.edit_selected_plan)
        self.delete_plan_btn.clicked.connect(self.delete_selected_plan)
        self.import_btn.clicked.connect(self.import_plan)
        self.export_btn.clicked.connect(self.export_selected_plan)
        
        self.plans_list.currentRowChanged.connect(self.on_plan_selection_changed)
        self.plans_list.itemDoubleClicked.connect(self.load_selected_plan)
    
    def update_current_plan_display(self):
        """更新当前方案显示"""
        if self.current_plan:
            mappings_count = len(self.current_mappings)
            text = f"""
            <b>{self.current_plan.name}</b><br/>
            <small>{self.current_plan.description}</small><br/>
            <small>映射数量: {mappings_count}</small>
            """
            self.current_plan_label.setText(text)
            
            # 启用相关按钮
            self.save_current_btn.setEnabled(True)
            self.save_as_btn.setEnabled(True)
            self.clear_current_btn.setEnabled(True)
        else:
            self.current_plan_label.setText("无当前方案")
            
            # 禁用相关按钮
            self.save_current_btn.setEnabled(False)
            self.save_as_btn.setEnabled(False)
            self.clear_current_btn.setEnabled(False)
    
    def sync_with_mapping_widget(self):
        """与数据映射组件同步"""
        if self.data_mapping_widget:
            self.current_mappings = self.data_mapping_widget.get_data_mappings()
            self.update_current_plan_display()
    
    def load_plans(self):
        """加载已保存的方案"""
        try:
            plans_dir = Path("saved_plans")
            if not plans_dir.exists():
                self.plans_list.clear()
                self.logger.info("saved_plans文件夹不存在，无保存的方案")
                return
            
            plan_files = list(plans_dir.glob("*.json"))
            self.plans_list.clear()
            
            plans_info = []
            for plan_file in plan_files:
                try:
                    with open(plan_file, 'r', encoding='utf-8') as f:
                        plan_data = json.load(f)
                    
                    # 转换为DataMappingPlan对象
                    plan = self._json_to_plan(plan_data, plan_file)
                    plans_info.append(plan)
                    
                except Exception as e:
                    self.logger.warning(f"读取方案文件失败: {plan_file}, 错误: {e}")
            
            # 按创建时间排序
            plans_info.sort(key=lambda x: x.created_time, reverse=True)
            
            for plan in plans_info:
                mappings_count = len(plan.mappings)
                item_text = f"{plan.name} ({mappings_count} 个映射)"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, plan)
                item.setToolTip(f"{plan.description}\n创建时间: {plan.created_time.strftime('%Y-%m-%d %H:%M:%S')}")
                self.plans_list.addItem(item)
                
            self.logger.info(f"加载了 {len(plans_info)} 个已保存的数据映射方案")
            
        except Exception as e:
            self.logger.error(f"加载方案失败: {e}")
            QMessageBox.warning(self, "错误", f"加载方案失败: {str(e)}")
    
    def _json_to_plan(self, plan_data: dict, plan_file: Path) -> DataMappingPlan:
        """将JSON数据转换为DataMappingPlan对象"""
        mappings = []
        for mapping_data in plan_data.get('mappings', []):
            # 解析匹配操作符
            match_operator_str = mapping_data.get('match_operator', '等于')
            if match_operator_str == '等于':
                match_operator = FilterOperator.EQUALS
            elif match_operator_str == '包含':
                match_operator = FilterOperator.CONTAINS
            elif match_operator_str == '开始于':
                match_operator = FilterOperator.STARTS_WITH
            elif match_operator_str == '结束于':
                match_operator = FilterOperator.ENDS_WITH
            else:
                match_operator = FilterOperator.EQUALS
            
            mapping = DataMapping(
                mapping_id=mapping_data.get('mapping_id', str(uuid.uuid4())),
                name=mapping_data.get('name', ''),
                description=mapping_data.get('description', ''),
                source_file=mapping_data.get('source_file', ''),
                source_match_coordinate=mapping_data.get('source_match_coordinate', 'A'),
                source_match_value=mapping_data.get('source_match_value', ''),
                source_value_coordinate=mapping_data.get('source_value_coordinate', 'B'),
                target_file=mapping_data.get('target_file', ''),
                target_match_coordinate=mapping_data.get('target_match_coordinate', 'A'),
                target_match_value=mapping_data.get('target_match_value', ''),
                target_insert_coordinate=mapping_data.get('target_insert_coordinate', 'B'),
                match_operator=match_operator,
                overwrite_existing=mapping_data.get('overwrite_existing', True)
            )
            mappings.append(mapping)
        
        # 解析创建时间
        created_time_str = plan_data.get('created_time', '')
        try:
            created_time = datetime.fromisoformat(created_time_str)
        except:
            created_time = datetime.now()
        
        plan = DataMappingPlan(
            plan_id=plan_data.get('plan_id', str(uuid.uuid4())),
            name=plan_data.get('name', plan_file.stem),
            description=plan_data.get('description', ''),
            mappings=mappings,
            created_time=created_time
        )
        
        # 添加文件路径信息（用于后续操作）
        self.plan_file_paths[plan.plan_id] = plan_file
        
        return plan
    
    def _plan_to_json(self, plan: DataMappingPlan) -> dict:
        """将DataMappingPlan对象转换为JSON数据"""
        plan_data = {
            'plan_id': plan.plan_id,
            'name': plan.name,
            'description': plan.description,
            'created_time': plan.created_time.isoformat(),
            'mappings': []
        }
        
        for mapping in plan.mappings:
            mapping_data = {
                'mapping_id': mapping.mapping_id,
                'name': mapping.name,
                'description': mapping.description,
                'source_file': mapping.source_file,
                'source_match_coordinate': str(mapping.source_match_coordinate),
                'source_match_value': str(mapping.source_match_value),
                'source_value_coordinate': str(mapping.source_value_coordinate),
                'target_file': mapping.target_file,
                'target_match_coordinate': str(mapping.target_match_coordinate),
                'target_match_value': str(mapping.target_match_value),
                'target_insert_coordinate': str(mapping.target_insert_coordinate),
                'match_operator': mapping.match_operator.value,
                'overwrite_existing': mapping.overwrite_existing
            }
            plan_data['mappings'].append(mapping_data)
        
        return plan_data
    
    def set_current_plan(self, mappings: List[DataMapping]):
        """设置当前方案（从数据映射组件）"""
        self.current_mappings = mappings.copy()
        
        if mappings:
            # 创建临时方案对象
            self.current_plan = DataMappingPlan(
                plan_id=str(uuid.uuid4()),
                name="当前配置",
                description=f"包含 {len(mappings)} 个数据映射",
                mappings=mappings
            )
        else:
            self.current_plan = None
        
        self.update_current_plan_display()
    
    def save_current_plan(self):
        """保存当前方案"""
        # 同步数据
        self.sync_with_mapping_widget()
        
        if not self.current_mappings:
            QMessageBox.warning(self, "警告", "当前没有数据映射配置，无法保存")
            return
        
        if self.current_plan and self.current_plan.plan_id in self.plan_file_paths:
            # 更新现有方案
            try:
                self.current_plan.mappings = self.current_mappings.copy()
                self.current_plan.modified_time = datetime.now()
                
                plan_data = self._plan_to_json(self.current_plan)
                
                with open(self.plan_file_paths[self.current_plan.plan_id], 'w', encoding='utf-8') as f:
                    json.dump(plan_data, f, ensure_ascii=False, indent=2)
                
                self.load_plans()
                QMessageBox.information(self, "成功", f"方案 '{self.current_plan.name}' 更新成功！")
                self.logger.info(f"更新方案: {self.current_plan.name}")
                
            except Exception as e:
                self.logger.error(f"更新方案失败: {e}")
                QMessageBox.warning(self, "错误", f"更新方案失败: {str(e)}")
        else:
            # 另存为新方案
            self.save_as_plan()
    
    def save_as_plan(self):
        """另存为方案"""
        # 同步数据
        self.sync_with_mapping_widget()
        
        if not self.current_mappings:
            QMessageBox.warning(self, "警告", "当前没有数据映射配置，无法保存")
            return
        
        dialog = DataMappingPlanEditDialog()
        if self.current_plan:
            dialog.name_edit.setText(f"{self.current_plan.name} - 副本")
            dialog.description_edit.setPlainText(self.current_plan.description)
        else:
            dialog.name_edit.setText(f"数据映射方案_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        if dialog.exec():
            name, description = dialog.get_plan_data()
            
            try:
                # 创建新方案
                new_plan = DataMappingPlan(
                    plan_id=str(uuid.uuid4()),
                    name=name,
                    description=description,
                    mappings=self.current_mappings.copy()
                )
                
                # 保存到文件
                plans_dir = Path("saved_plans")
                plans_dir.mkdir(exist_ok=True)
                
                plan_file = plans_dir / f"{name}.json"
                plan_data = self._plan_to_json(new_plan)
                
                with open(plan_file, 'w', encoding='utf-8') as f:
                    json.dump(plan_data, f, ensure_ascii=False, indent=2)
                
                # 设置为当前方案
                self.plan_file_paths[new_plan.plan_id] = plan_file
                self.current_plan = new_plan
                self.update_current_plan_display()
                
                # 刷新列表
                self.load_plans()
                
                QMessageBox.information(self, "成功", f"方案 '{name}' 保存成功！")
                self.logger.info(f"保存新方案: {name}")
                
            except Exception as e:
                self.logger.error(f"保存方案失败: {e}")
                QMessageBox.warning(self, "错误", f"保存方案失败: {str(e)}")
    
    def clear_current_plan(self):
        """清空当前方案"""
        reply = QMessageBox.question(
            self, "确认清空", "确定要清空当前方案吗？\n这将清除所有数据映射配置。",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.current_plan = None
            self.current_mappings.clear()
            
            # 清空数据映射组件
            if self.data_mapping_widget:
                self.data_mapping_widget.clear_all_mappings()
            
            self.update_current_plan_display()
            self.logger.info("已清空当前方案")
    
    def new_plan(self):
        """新建方案"""
        dialog = DataMappingPlanEditDialog()
        dialog.name_edit.setText(f"新数据映射方案_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        if dialog.exec():
            name, description = dialog.get_plan_data()
            
            # 清空当前配置，准备新建
            self.clear_current_plan()
            
            # 创建新方案
            new_plan = DataMappingPlan(
                plan_id=str(uuid.uuid4()),
                name=name,
                description=description
            )
            
            self.current_plan = new_plan
            self.update_current_plan_display()
            
            self.logger.info(f"新建方案: {name}")
    
    def load_selected_plan(self):
        """加载选中的方案"""
        current_item = self.plans_list.currentItem()
        if not current_item:
            return
        
        plan = current_item.data(Qt.UserRole)
        if plan:
            try:
                # 设置为当前方案
                self.current_plan = plan
                self.current_mappings = plan.mappings.copy()
                self.update_current_plan_display()
                
                # 更新数据映射组件
                if self.data_mapping_widget:
                    self.data_mapping_widget.clear_all_mappings()
                    for mapping in plan.mappings:
                        self.data_mapping_widget.add_mapping_from_data(mapping)
                
                # 发出信号
                self.plan_loaded.emit(plan)
                
                QMessageBox.information(self, "加载成功", f"方案 '{plan.name}' 加载成功！\n包含 {len(plan.mappings)} 个数据映射配置")
                self.logger.info(f"加载方案: {plan.name}")
                
            except Exception as e:
                self.logger.error(f"加载方案失败: {e}")
                QMessageBox.warning(self, "错误", f"加载方案失败: {str(e)}")
    
    def edit_selected_plan(self):
        """编辑选中的方案"""
        current_item = self.plans_list.currentItem()
        if not current_item:
            return
        
        plan = current_item.data(Qt.UserRole)
        dialog = DataMappingPlanEditDialog(plan)
        
        if dialog.exec():
            name, description = dialog.get_plan_data()
            
            try:
                # 更新方案信息
                plan.name = name
                plan.description = description
                plan.modified_time = datetime.now()
                
                # 保存到文件
                if plan.plan_id in self.plan_file_paths:
                    plan_data = self._plan_to_json(plan)
                    current_path = self.plan_file_paths[plan.plan_id]
                    with open(current_path, 'w', encoding='utf-8') as f:
                        json.dump(plan_data, f, ensure_ascii=False, indent=2)
                    
                    # 重命名文件
                    new_file_path = current_path.parent / f"{name}.json"
                    if new_file_path != current_path:
                        current_path.rename(new_file_path)
                        self.plan_file_paths[plan.plan_id] = new_file_path
                
                # 刷新列表
                self.load_plans()
                
                # 如果编辑的是当前方案，更新显示
                if self.current_plan and self.current_plan.plan_id == plan.plan_id:
                    self.current_plan = plan
                    self.update_current_plan_display()
                
                QMessageBox.information(self, "成功", f"方案 '{name}' 编辑成功！")
                self.logger.info(f"编辑方案: {name}")
                
            except Exception as e:
                self.logger.error(f"编辑方案失败: {e}")
                QMessageBox.warning(self, "错误", f"编辑方案失败: {str(e)}")
    
    def delete_selected_plan(self):
        """删除选中的方案"""
        current_item = self.plans_list.currentItem()
        if not current_item:
            return
        
        plan = current_item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除方案 '{plan.name}' 吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 删除文件
                if plan.plan_id in self.plan_file_paths:
                    file_path = self.plan_file_paths[plan.plan_id]
                    if file_path.exists():
                        file_path.unlink()
                    del self.plan_file_paths[plan.plan_id]
                
                # 如果删除的是当前方案，清空当前方案
                if self.current_plan and self.current_plan.plan_id == plan.plan_id:
                    self.clear_current_plan()
                
                # 刷新列表
                self.load_plans()
                
                QMessageBox.information(self, "成功", f"方案 '{plan.name}' 删除成功！")
                self.logger.info(f"删除方案: {plan.name}")
                
            except Exception as e:
                self.logger.error(f"删除方案失败: {e}")
                QMessageBox.warning(self, "错误", f"删除方案失败: {str(e)}")
    
    def import_plan(self):
        """导入方案"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("JSON文件 (*.json)")
        file_dialog.setWindowTitle("选择要导入的数据映射方案文件")
        
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    plan_data = json.load(f)
                
                # 转换为方案对象
                imported_plan = self._json_to_plan(plan_data, Path(file_path))
                
                # 生成新的ID和名称避免冲突
                imported_plan.plan_id = str(uuid.uuid4())
                imported_plan.name = f"{imported_plan.name}_导入_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # 保存到saved_plans文件夹
                plans_dir = Path("saved_plans")
                plans_dir.mkdir(exist_ok=True)
                
                new_file_path = plans_dir / f"{imported_plan.name}.json"
                plan_data = self._plan_to_json(imported_plan)
                
                with open(new_file_path, 'w', encoding='utf-8') as f:
                    json.dump(plan_data, f, ensure_ascii=False, indent=2)
                
                self.plan_file_paths[imported_plan.plan_id] = new_file_path
                
                # 刷新列表
                self.load_plans()
                
                QMessageBox.information(self, "导入成功", f"方案 '{imported_plan.name}' 导入成功！\n包含 {len(imported_plan.mappings)} 个数据映射配置")
                self.logger.info(f"导入方案: {imported_plan.name}")
                
            except Exception as e:
                self.logger.error(f"导入方案失败: {e}")
                QMessageBox.warning(self, "导入失败", f"导入方案失败: {str(e)}")
    
    def export_selected_plan(self):
        """导出选中的方案"""
        current_item = self.plans_list.currentItem()
        if not current_item:
            return
        
        plan = current_item.data(Qt.UserRole)
        
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setNameFilter("JSON文件 (*.json)")
        file_dialog.setDefaultSuffix("json")
        file_dialog.selectFile(f"{plan.name}.json")
        file_dialog.setWindowTitle("导出数据映射方案")
        
        if file_dialog.exec():
            export_path = file_dialog.selectedFiles()[0]
            
            try:
                plan_data = self._plan_to_json(plan)
                
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(plan_data, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(self, "导出成功", f"方案 '{plan.name}' 导出成功！\n文件位置: {export_path}")
                self.logger.info(f"导出方案: {plan.name} 到 {export_path}")
                
            except Exception as e:
                self.logger.error(f"导出方案失败: {e}")
                QMessageBox.warning(self, "导出失败", f"导出方案失败: {str(e)}")
    
    def on_plan_selection_changed(self, current_row):
        """方案选择变化"""
        has_selection = current_row >= 0
        
        self.load_plan_btn.setEnabled(has_selection)
        self.edit_plan_btn.setEnabled(has_selection)
        self.delete_plan_btn.setEnabled(has_selection)
        self.export_btn.setEnabled(has_selection)
        
        if has_selection:
            item = self.plans_list.item(current_row)
            plan = item.data(Qt.UserRole)
            self.plan_selected.emit(plan)
