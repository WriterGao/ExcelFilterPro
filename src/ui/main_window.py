#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口模块
应用程序的主界面
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QTabWidget, QMenuBar, QToolBar, QStatusBar,
    QLabel, QProgressBar, QMessageBox, QDialog, QListWidget, QPushButton, QDialogButtonBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QAction

from ..core.enhanced_excel_processor import EnhancedExcelProcessor
from ..core.data_mapping_engine import DataMappingEngine
from ..core.config_manager import ConfigManager
from ..utils.logger import get_logger
from ..utils.constants import (
    APP_NAME, VERSION, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT
)
from .widgets.upload_widget import UploadWidget
from .widgets.config_widget import ConfigWidget
from .widgets.data_mapping_widget import DataMappingWidget
from .widgets.result_widget import ResultWidget
from pathlib import Path
from ..database.models import DataMappingPlan, DataMapping, FilterOperator
from datetime import datetime
import uuid
import json


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.logger.info("🏠 开始初始化主窗口")
        
        # 初始化核心组件
        self.logger.info("📊 正在初始化Excel处理器...")
        self.excel_processor = EnhancedExcelProcessor()
        
        self.logger.info("🔗 正在初始化数据映射引擎...")
        self.data_mapping_engine = DataMappingEngine()
        
        self.logger.info("⚙️ 正在初始化配置管理器...")
        self.config_manager = ConfigManager()
        
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbar()
        self.setup_statusbar()
        self.setup_signals()
        
        self.logger.info("✅ 主窗口初始化完成")
        
    def setup_ui(self):
        """设置用户界面"""
        # 设置窗口属性
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)
        
        # 创建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧面板（文件上传和方案管理）
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # 右侧面板（数据映射和结果）
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
    def create_left_panel(self) -> QWidget:
        """创建左侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 文件上传组件
        self.upload_widget = UploadWidget()
        layout.addWidget(self.upload_widget)
        
        # 方案管理组件
        self.config_widget = ConfigWidget()
        layout.addWidget(self.config_widget)
        
        return panel
        
    def create_right_panel(self) -> QWidget:
        """创建右侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 创建选项卡组件
        tab_widget = QTabWidget()
        
        # 数据映射选项卡
        self.data_mapping_widget = DataMappingWidget()
        tab_widget.addTab(self.data_mapping_widget, "🔗 数据映射")
        
        # 结果预览组件
        self.result_widget = ResultWidget()
        layout.addWidget(tab_widget)
        layout.addWidget(self.result_widget)
        
        return panel
        
    def setup_menus(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        # 打开数据源
        open_action = QAction("打开数据源(&O)", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_data_source)
        file_menu.addAction(open_action)
        
        # 保存方案
        save_action = QAction("保存方案(&S)", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_plan)
        file_menu.addAction(save_action)
        
        # 加载方案
        load_action = QAction("加载方案(&L)", self)
        load_action.setShortcut("Ctrl+L")
        load_action.triggered.connect(self.load_plan)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")
        
        # 新建规则
        new_rule_action = QAction("新建规则(&N)", self)
        new_rule_action.setShortcut("Ctrl+N")
        new_rule_action.triggered.connect(self.new_rule)
        edit_menu.addAction(new_rule_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")
        
        # 刷新
        refresh_action = QAction("刷新(&R)", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_view)
        view_menu.addAction(refresh_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        # 关于
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_toolbar(self):
        """设置工具栏"""
        toolbar = self.addToolBar("主工具栏")
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # 打开文件
        open_action = QAction("打开", self)
        open_action.triggered.connect(self.open_data_source)
        toolbar.addAction(open_action)
        
        # 保存方案
        save_action = QAction("保存", self)
        save_action.triggered.connect(self.save_plan)
        toolbar.addAction(save_action)
        
        # 加载方案
        load_action = QAction("加载", self)
        load_action.triggered.connect(self.load_plan)
        toolbar.addAction(load_action)
        
        toolbar.addSeparator()
        
        # 执行筛选
        execute_action = QAction("执行筛选", self)
        execute_action.triggered.connect(self.execute_filter)
        toolbar.addAction(execute_action)
        
        # 导出结果
        export_action = QAction("导出Excel", self)
        export_action.triggered.connect(self.export_result)
        toolbar.addAction(export_action)
        
    def setup_statusbar(self):
        """设置状态栏"""
        statusbar = self.statusBar()
        
        # 状态标签
        self.status_label = QLabel("就绪")
        statusbar.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        statusbar.addPermanentWidget(self.progress_bar)
        
        # 内存使用标签
        self.memory_label = QLabel("内存: 0MB")
        statusbar.addPermanentWidget(self.memory_label)
        
        # 定时更新内存使用
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self.update_memory_usage)
        self.memory_timer.start(5000)  # 每5秒更新一次
        
    def setup_signals(self):
        """设置信号连接"""
        # 数据上传和处理信号
        self.upload_widget.files_changed.connect(self.on_files_changed)
        self.upload_widget.template_changed.connect(self.on_template_changed)
        
        # 数据映射变化信号
        self.data_mapping_widget.mappings_changed.connect(self.on_mappings_changed)
        
        # 方案加载信号
        self.config_widget.plan_loaded.connect(self.on_plan_loaded)
        
        # 连接配置组件和数据映射组件
        self.config_widget.set_data_mapping_widget(self.data_mapping_widget)
        
        # 数据映射变化时同步到配置组件
        self.data_mapping_widget.mappings_changed.connect(lambda: self.config_widget.set_current_plan(self.data_mapping_widget.get_data_mappings()))
        
        self.logger.info("信号连接完成")
        
    def on_files_changed(self, file_paths):
        """文件列表变化处理"""
        try:
            if file_paths:
                # 加载Excel文件
                self.excel_processor.load_excel_files(file_paths)
                
                # 获取原始文件名列表（不包含工作表后缀）
                original_file_names = self.excel_processor.get_original_file_names()
                
                # 更新数据映射组件的数据源文件
                self.data_mapping_widget.set_source_files(original_file_names, self.excel_processor)
                
                self.set_status(f"已加载 {len(file_paths)} 个数据文件")
                self.logger.info(f"加载了 {len(file_paths)} 个数据文件，包含 {len(original_file_names)} 个源文件")
            else:
                # 清空数据
                self.excel_processor.clear_data()
                self.data_mapping_widget.set_source_files([])
                self.set_status("已清空数据文件")
                
        except Exception as e:
            self.logger.error(f"加载数据文件失败: {e}")
            QMessageBox.warning(self, "错误", f"加载数据文件失败: {str(e)}")
    
    def on_template_changed(self, template_path):
        """模板文件变化处理"""
        if template_path:
            # 更新结果组件
            self.result_widget.set_components(self.excel_processor, template_path)
            
            # 更新数据映射组件的目标文件
            self.data_mapping_widget.set_target_files([template_path])
            
            self.set_status(f"已选择模板: {template_path}")
        else:
            self.result_widget.set_components(self.excel_processor, "")
            self.data_mapping_widget.set_target_files([])
            self.set_status("已清除模板")
    
    def on_mappings_changed(self):
        """数据映射变化处理"""
        mappings = self.data_mapping_widget.get_data_mappings()
        self.set_status(f"当前数据映射数: {len(mappings)}")
        self.logger.info(f"数据映射数量变化: {len(mappings)}")
    
    def on_plan_loaded(self, plan):
        """方案加载处理"""
        try:
            # TODO: 实现坐标筛选方案加载
            self.set_status(f"已加载方案: {plan.name}")
            self.logger.info(f"加载方案: {plan.name}")
        except Exception as e:
            self.logger.error(f"加载方案失败: {e}")
            QMessageBox.warning(self, "错误", f"加载方案失败: {str(e)}")
    
    def open_data_source(self):
        """打开数据源"""
        self.upload_widget.add_data_files()
        
    def save_plan(self):
        """保存方案"""
        try:
            # 获取当前的数据映射配置
            mappings = self.data_mapping_widget.get_data_mappings()
            
            if not mappings:
                QMessageBox.warning(self, "警告", "当前没有数据映射配置，无法保存")
                return
            
            # 弹出对话框让用户输入方案名称
            from PySide6.QtWidgets import QInputDialog
            name, ok = QInputDialog.getText(
                self, "保存数据映射方案", "请输入方案名称:", 
                text=f"数据映射方案_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            if not ok or not name.strip():
                return
            
            # 创建数据映射方案
            plan = DataMappingPlan(
                plan_id=str(uuid.uuid4()),
                name=name.strip(),
                description=f"包含 {len(mappings)} 个数据映射配置",
                mappings=mappings
            )
            
            # 保存到JSON文件（简单实现）
            plans_dir = Path("saved_plans")
            plans_dir.mkdir(exist_ok=True)
            
            plan_file = plans_dir / f"{plan.name}.json"
            
            # 转换为可序列化的格式
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
            
            # 保存文件
            with open(plan_file, 'w', encoding='utf-8') as f:
                json.dump(plan_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"数据映射方案已保存: {plan_file}")
            QMessageBox.information(
                self, "保存成功", 
                f"数据映射方案已保存!\n文件位置: {plan_file}\n包含 {len(mappings)} 个映射配置"
            )
            self.set_status(f"已保存数据映射方案: {plan.name}")
            
        except Exception as e:
            self.logger.error(f"保存数据映射方案失败: {e}")
            QMessageBox.warning(self, "保存失败", f"保存数据映射方案失败: {str(e)}")
    
    def load_plan(self):
        """加载已保存的方案"""
        try:
            plans_dir = Path("saved_plans")
            if not plans_dir.exists():
                QMessageBox.information(self, "提示", "尚未保存任何方案")
                return
            
            # 获取所有保存的方案文件
            plan_files = list(plans_dir.glob("*.json"))
            if not plan_files:
                QMessageBox.information(self, "提示", "没有找到已保存的方案")
                return
            
            # 读取方案信息
            plans_info = []
            for plan_file in plan_files:
                try:
                    with open(plan_file, 'r', encoding='utf-8') as f:
                        plan_data = json.load(f)
                    
                    plans_info.append({
                        'file': plan_file,
                        'name': plan_data.get('name', plan_file.stem),
                        'description': plan_data.get('description', ''),
                        'created_time': plan_data.get('created_time', ''),
                        'mappings_count': len(plan_data.get('mappings', []))
                    })
                except Exception as e:
                    self.logger.warning(f"读取方案文件失败: {plan_file}, 错误: {e}")
            
            if not plans_info:
                QMessageBox.information(self, "提示", "没有有效的方案文件")
                return
            
            # 创建选择对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("选择数据映射方案")
            dialog.setMinimumSize(600, 400)
            
            layout = QVBoxLayout(dialog)
            
            # 说明标签
            info_label = QLabel("选择要加载的数据映射方案：")
            layout.addWidget(info_label)
            
            # 方案列表
            plans_list = QListWidget()
            for plan_info in plans_info:
                item_text = f"""方案名称: {plan_info['name']}
描述: {plan_info['description']}
映射数量: {plan_info['mappings_count']} 个
创建时间: {plan_info['created_time'][:19] if plan_info['created_time'] else '未知'}"""
                
                from PySide6.QtWidgets import QListWidgetItem
                item = QListWidgetItem(item_text)
                item.setData(1, plan_info)  # 存储方案信息
                plans_list.addItem(item)
            
            layout.addWidget(plans_list)
            
            # 按钮
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            # 只有选中项时才能确定
            def on_selection_changed():
                button_box.button(QDialogButtonBox.Ok).setEnabled(plans_list.currentItem() is not None)
            
            plans_list.currentItemChanged.connect(on_selection_changed)
            on_selection_changed()  # 初始状态
            
            # 显示对话框
            if dialog.exec() == QDialog.Accepted:
                current_item = plans_list.currentItem()
                if current_item:
                    selected_plan = current_item.data(1)
                    self._load_plan_from_file(selected_plan['file'])
                    
        except Exception as e:
            self.logger.error(f"加载方案失败: {e}")
            QMessageBox.warning(self, "加载失败", f"加载方案失败: {str(e)}")
    
    def _load_plan_from_file(self, plan_file: Path):
        """从文件加载方案配置"""
        try:
            with open(plan_file, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)
            
            # 清除现有配置
            self.data_mapping_widget.clear_all_mappings()
            
            # 加载映射配置
            mappings_data = plan_data.get('mappings', [])
            
            for mapping_data in mappings_data:
                # 重新构建DataMapping对象
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
                    mapping_id=mapping_data.get('mapping_id', ''),
                    name=mapping_data.get('name', ''),
                    description=mapping_data.get('description', ''),
                    source_file=mapping_data.get('source_file', ''),
                    source_match_coordinate=mapping_data.get('source_match_coordinate', ''),
                    source_match_value=mapping_data.get('source_match_value', ''),
                    source_value_coordinate=mapping_data.get('source_value_coordinate', ''),
                    target_file=mapping_data.get('target_file', ''),
                    target_match_coordinate=mapping_data.get('target_match_coordinate', ''),
                    target_match_value=mapping_data.get('target_match_value', ''),
                    target_insert_coordinate=mapping_data.get('target_insert_coordinate', ''),
                    match_operator=match_operator,
                    overwrite_existing=mapping_data.get('overwrite_existing', True)
                )
                
                # 添加到界面
                self.data_mapping_widget.add_mapping_from_data(mapping)
            
            self.logger.info(f"成功加载方案: {plan_data.get('name')}, 包含 {len(mappings_data)} 个映射")
            QMessageBox.information(
                self, "加载成功", 
                f"成功加载方案: {plan_data.get('name')}\n包含 {len(mappings_data)} 个数据映射配置"
            )
            self.set_status(f"已加载方案: {plan_data.get('name')}")
            
        except Exception as e:
            self.logger.error(f"从文件加载方案失败: {e}")
            QMessageBox.warning(self, "加载失败", f"从文件加载方案失败: {str(e)}")
    
    def new_rule(self):
        """新建规则"""
        # 实现新建规则的逻辑
        pass
        
    def refresh_view(self):
        """刷新视图"""
        self.config_widget.load_plans()
        self.set_status("视图已刷新")
        
    def execute_filter(self):
        """执行数据映射"""
        try:
            # 检查是否有数据
            if not self.excel_processor.data_frames:
                QMessageBox.warning(self, "警告", "请先加载数据文件")
                return
            
            # 执行数据映射
            self.execute_data_mapping()
                
        except Exception as e:
            self.hide_progress()
            self.logger.error(f"执行失败: {e}")
            QMessageBox.warning(self, "错误", f"执行失败: {str(e)}")
            self.set_status("执行失败")
    
    def execute_data_mapping(self):
        """执行数据映射"""
        self.logger.info("🚀 ========== 开始执行数据映射流程 ==========")
        try:
            mappings = self.data_mapping_widget.get_data_mappings()
            self.logger.info(f"📋 获取到 {len(mappings)} 个数据映射配置")
            
            if not mappings:
                self.logger.warning("⚠️ 没有配置任何数据映射，停止执行")
                QMessageBox.warning(self, "警告", "请先创建数据映射")
                return
            
            # 显示所有映射配置的概要
            for i, mapping in enumerate(mappings):
                self.logger.info(f"📝 映射 {i+1}: {mapping.name}")
                self.logger.info(f"   源: {mapping.source_file}[{mapping.source_match_coordinate}='{mapping.source_match_value}'] -> [{mapping.source_value_coordinate}]")
                self.logger.info(f"   目标: {mapping.target_file}[{mapping.target_match_coordinate}='{mapping.target_match_value}'] -> [{mapping.target_insert_coordinate}]")
            
            # 显示进度
            self.show_progress(0)
            self.set_status("正在执行数据映射...")
            
            # 准备数据
            source_data = {}
            target_data = {}
            
            self.logger.info("📊 ========== 准备源数据 ==========")
            # 获取源数据
            for mapping in mappings:
                if mapping.source_file not in source_data:
                    # 从Excel处理器获取数据
                    if mapping.source_file in [name for name in self.excel_processor.get_original_file_names()]:
                        df = self.excel_processor.get_dataframe_by_original_name(mapping.source_file)
                        if df is not None:
                            source_data[mapping.source_file] = df
                
                if mapping.target_file not in target_data:
                    # 智能加载目标文件：优先使用映射配置中的目标文件路径
                    template_path = None
                    
                    # 首先尝试映射配置中的目标文件路径
                    if mapping.target_file and Path(mapping.target_file).exists():
                        template_path = mapping.target_file
                        self.logger.info(f"🎯 使用映射配置中的目标文件: {template_path}")
                    # 然后尝试用户上传的模板文件
                    elif hasattr(self.upload_widget, 'template_path') and self.upload_widget.template_path:
                        template_path = self.upload_widget.template_path
                        self.logger.info(f"🎯 使用用户上传的模板文件: {template_path}")
                    # 最后尝试当前目录下的111_fixed.xlsx文件
                    else:
                        fallback_template = Path("111_fixed.xlsx")
                        if fallback_template.exists():
                            template_path = str(fallback_template)
                            self.logger.info(f"🔧 使用备用模板文件: {template_path}")
                    
                    if template_path and Path(template_path).exists():
                        try:
                            self.logger.info(f"🎯 正在加载目标模板文件: {template_path}")
                            target_df = self.excel_processor._load_standard_excel(template_path)
                            if target_df is not None and not target_df.empty:
                                # 使用实际的模板文件，但键值使用映射配置中的文件名
                                target_data[mapping.target_file] = target_df
                                self.logger.info(f"✅ 成功加载模板文件到键'{mapping.target_file}'，包含 {len(target_df)} 行 {len(target_df.columns)} 列")
                                
                                # 打印目标文件的详细调试信息
                                self.logger.info(f"📋 目标文件完整内容:")
                                self.logger.info(f"   列名: {list(target_df.columns)}")
                                self.logger.info(f"   数据形状: {target_df.shape}")
                                for idx, row in target_df.iterrows():
                                    row_data = [f"{val}({type(val).__name__})" for val in row.values]
                                    self.logger.info(f"   第{idx+1}行: {row_data}")
                                
                                # 特别关注A列数据
                                self.logger.info(f"📍 A列详细信息:")
                                for idx, val in enumerate(target_df.iloc[:, 0]):
                                    import pandas as pd
                                    self.logger.info(f"   A列第{idx+1}行: {repr(val)} (类型:{type(val)}, 是否NaN:{pd.isna(val)})")
                                
                            else:
                                raise Exception("模板文件加载结果为空")
                        except Exception as e:
                            self.logger.error(f"❌ 加载模板文件失败: {e}")
                            # 创建备用空模板
                            import pandas as pd
                            import string
                            
                            self.logger.info("⚠️ 使用备用空模板")
                            columns = list(string.ascii_uppercase)
                            empty_data = {col: [None] * 10 for col in columns}
                            target_data[mapping.target_file] = pd.DataFrame(empty_data)
                    else:
                        self.logger.warning(f"⚠️ 未找到模板文件，将使用默认空模板进行数据映射")
                        # 创建备用空模板
                        import pandas as pd
                        import string
                        
                        columns = list(string.ascii_uppercase)
                        empty_data = {col: [None] * 10 for col in columns}
                        target_data[mapping.target_file] = pd.DataFrame(empty_data)
            
            # 打印调试信息
            self.logger.info(f"准备执行数据映射，源文件: {list(source_data.keys())}, 目标文件: {list(target_data.keys())}")
            for mapping in mappings:
                self.logger.info(f"映射配置: {mapping.name} - 源:{mapping.source_file} 目标:{mapping.target_file}")
                self.logger.info(f"  源匹配: {mapping.source_match_coordinate}='{mapping.source_match_value}' -> {mapping.source_value_coordinate}")
                self.logger.info(f"  目标匹配: {mapping.target_match_coordinate}='{mapping.target_match_value}' -> {mapping.target_insert_coordinate}")
            
            # 执行数据映射
            result_data = self.data_mapping_engine.execute_multiple_mappings(
                mappings, source_data, target_data
            )
            
            # 直接更新原始模板文件
            self.logger.info("💾 开始更新原始模板文件...")
            updated_files = []
            for file_key, result_df in result_data.items():
                try:
                    # 找到对应的原始模板文件路径
                    template_path = None
                    if hasattr(self.upload_widget, 'template_path') and self.upload_widget.template_path:
                        template_path = self.upload_widget.template_path
                    
                    # 如果没有上传的模板，使用默认模板
                    if not template_path or not Path(template_path).exists():
                        fallback_template = Path("输出模板.xlsx")
                        if fallback_template.exists():
                            template_path = str(fallback_template)
                    
                    if template_path and Path(template_path).exists():
                        # 直接覆盖原始模板文件
                        result_df.to_excel(template_path, index=False, engine='openpyxl')
                        updated_files.append(template_path)
                        self.logger.info(f"✅ 直接更新模板文件: {template_path}")
                        
                        # 显示更新的数据内容
                        self.logger.info(f"📄 更新的数据内容 ({result_df.shape}):")
                        for idx, row in result_df.iterrows():
                            row_data = [str(val) if val is not None else "空" for val in row.values]
                            self.logger.info(f"   第{idx+1}行: {row_data[:5]}")  # 只显示前5列
                    else:
                        # 如果没有找到模板文件，创建新的结果文件
                        if file_key.endswith('.xlsx'):
                            output_filename = file_key.replace('.xlsx', '_结果.xlsx')
                        else:
                            output_filename = f"{file_key}_结果.xlsx"
                        
                        output_path = Path(output_filename)
                        result_df.to_excel(output_path, index=False, engine='openpyxl')
                        updated_files.append(str(output_path))
                        self.logger.info(f"✅ 创建结果文件: {output_path}")
                        
                except Exception as e:
                    self.logger.error(f"❌ 更新文件失败 {file_key}: {e}")
            
            # 隐藏进度条
            self.hide_progress()
            
            self.set_status(f"数据映射完成，处理了 {len(mappings)} 个映射")
            self.logger.info(f"数据映射完成，映射数: {len(mappings)}")
            
            # 显示结果
            if updated_files:
                files_info = '\n'.join(updated_files)
                QMessageBox.information(
                    self, "成功", 
                    f"数据映射执行完成！\n处理了 {len(mappings)} 个映射规则。\n\n更新的文件:\n{files_info}"
                )
            else:
                QMessageBox.information(
                    self, "成功", 
                    f"数据映射执行完成！\n处理了 {len(mappings)} 个映射规则。"
                )
            
        except Exception as e:
            self.hide_progress()
            self.logger.error(f"数据映射执行失败: {e}")
            QMessageBox.warning(self, "错误", f"数据映射执行失败: {str(e)}")
            self.set_status("数据映射执行失败")
    

        
    def export_result(self):
        """导出结果"""
        self.result_widget.export_results()
        
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            f"""
            <h2>{APP_NAME}</h2>
            <p>版本: {VERSION}</p>
            <p>一个专业的Excel数据筛选工具</p>
            <p>支持多文件数据源、复杂筛选条件和方案管理</p>
            """
        )
        
    def update_memory_usage(self):
        """更新内存使用显示"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            self.memory_label.setText(f"内存: {memory_mb:.0f}MB")
        except ImportError:
            # 如果没有psutil，不显示内存信息
            self.memory_label.setText("")
            self.memory_timer.stop()
        except Exception as e:
            self.logger.warning(f"更新内存使用失败: {e}")
            
    def show_progress(self, value: int, maximum: int = 100):
        """显示进度"""
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)
        self.progress_bar.setVisible(True)
        
    def hide_progress(self):
        """隐藏进度条"""
        self.progress_bar.setVisible(False)
        
    def set_status(self, message: str):
        """设置状态栏消息"""
        self.status_label.setText(message)
        self.logger.info(f"状态: {message}")
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.logger.info("应用程序关闭")
        event.accept() 