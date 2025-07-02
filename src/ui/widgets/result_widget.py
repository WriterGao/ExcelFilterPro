#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结果展示组件
显示筛选和处理的结果
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QHeaderView,
    QFileDialog, QMessageBox, QProgressBar, QComboBox, QTabWidget
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
from ...core.enhanced_excel_processor import EnhancedExcelProcessor
from ...utils.logger import get_logger


class ExportThread(QThread):
    """导出线程"""
    
    progress_updated = Signal(int)
    export_finished = Signal(bool, str)
    
    def __init__(self, processor: EnhancedExcelProcessor, filtered_data: Dict[str, pd.DataFrame], 
                 template_path: str, output_path: str):
        super().__init__()
        self.processor = processor
        self.filtered_data = filtered_data
        self.template_path = template_path
        self.output_path = output_path
    
    def run(self):
        """执行导出"""
        try:
            self.progress_updated.emit(20)
            
            # 执行导出
            success = self.processor.write_to_template(
                self.template_path, 
                self.filtered_data, 
                self.output_path
            )
            
            self.progress_updated.emit(100)
            self.export_finished.emit(success, "导出成功" if success else "导出失败")
            
        except Exception as e:
            self.export_finished.emit(False, f"导出失败: {str(e)}")


class ResultWidget(QWidget):
    """结果预览组件"""
    
    export_requested = Signal(str)  # 导出请求信号
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.filtered_results: Dict[str, pd.DataFrame] = {}
        self.preview_data: Dict[str, Dict[str, Any]] = {}
        self.excel_processor: Optional[EnhancedExcelProcessor] = None
        self.template_path: str = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("预览结果")
        self.export_btn = QPushButton("导出Excel")
        self.clear_btn = QPushButton("清空结果")
        
        self.preview_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        
        toolbar_layout.addWidget(self.preview_btn)
        toolbar_layout.addWidget(self.export_btn)
        toolbar_layout.addWidget(self.clear_btn)
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # 结果显示区域
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 统计信息标签
        self.stats_label = QLabel("暂无结果")
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setStyleSheet("""
            QLabel {
                color: #666;
                padding: 20px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.stats_label)
        
        # 连接信号
        self.preview_btn.clicked.connect(self.preview_results)
        self.export_btn.clicked.connect(self.export_results)
        self.clear_btn.clicked.connect(self.clear_results)
    
    def set_components(self, processor: EnhancedExcelProcessor, template_path: str):
        """设置组件依赖"""
        self.excel_processor = processor
        self.template_path = template_path
        
        # 启用预览按钮
        can_preview = bool(processor and 
                          processor.data_frames and 
                          template_path)
        self.preview_btn.setEnabled(can_preview)
    
    def set_filtered_results(self, results: Dict[str, pd.DataFrame]):
        """设置筛选结果"""
        self.filtered_results = results.copy()
        self.update_results_display()
        
        # 启用导出按钮
        self.export_btn.setEnabled(bool(results) and bool(self.template_path))
    
    def preview_results(self):
        """预览结果"""
        if not self.filtered_results:
            QMessageBox.warning(self, "警告", "没有筛选结果可以预览")
            return
        
        self.show_results_in_tabs()
        self.update_statistics()
    
    def show_results_in_tabs(self):
        """在标签页中显示结果"""
        # 清空现有标签页
        self.tab_widget.clear()
        
        for column_name, df in self.filtered_results.items():
            # 创建表格
            table = QTableWidget()
            
            if not df.empty:
                # 设置表格数据
                table.setRowCount(min(100, len(df)))  # 最多显示100行
                table.setColumnCount(len(df.columns))
                table.setHorizontalHeaderLabels(df.columns.tolist())
                
                # 填充数据
                for row in range(min(100, len(df))):
                    for col in range(len(df.columns)):
                        value = str(df.iloc[row, col])
                        if len(value) > 50:  # 截断长文本
                            value = value[:47] + "..."
                        
                        item = QTableWidgetItem(value)
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        table.setItem(row, col, item)
                
                # 调整列宽
                table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            
            # 添加到标签页
            tab_title = f"{column_name} ({len(df)} 行)"
            self.tab_widget.addTab(table, tab_title)
        
        # 显示标签页
        if self.tab_widget.count() > 0:
            self.tab_widget.show()
            self.stats_label.hide()
        else:
            self.tab_widget.hide()
            self.stats_label.show()
            self.stats_label.setText("没有筛选结果")
    
    def update_statistics(self):
        """更新统计信息"""
        if not self.filtered_results:
            self.stats_label.setText("暂无结果")
            return
        
        total_rows = sum(len(df) for df in self.filtered_results.values())
        total_rules = len(self.filtered_results)
        
        stats_text = f"共 {total_rules} 个规则，筛选出 {total_rows} 行数据"
        
        # 详细统计
        details = []
        for column_name, df in self.filtered_results.items():
            details.append(f"{column_name}: {len(df)} 行")
        
        if details:
            stats_text += f"\n详细: {', '.join(details)}"
        
        self.stats_label.setText(stats_text)
    
    def update_results_display(self):
        """更新结果显示"""
        if self.filtered_results:
            self.show_results_in_tabs()
            self.update_statistics()
        else:
            self.tab_widget.clear()
            self.tab_widget.hide()
            self.stats_label.show()
            self.stats_label.setText("暂无结果")
    
    def export_results(self):
        """导出结果到Excel"""
        if not self.filtered_results:
            QMessageBox.warning(self, "警告", "没有结果可以导出")
            return
        
        if not self.template_path:
            QMessageBox.warning(self, "警告", "请先选择输出模板")
            return
        
        # 选择保存路径
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setNameFilter("Excel文件 (*.xlsx)")
        file_dialog.setDefaultSuffix("xlsx")
        file_dialog.selectFile("筛选结果.xlsx")
        
        if file_dialog.exec():
            output_path = file_dialog.selectedFiles()[0]
            
            # 开始导出
            self.start_export(output_path)
    
    def start_export(self, output_path: str):
        """开始导出"""
        if not self.excel_processor:
            QMessageBox.warning(self, "错误", "Excel处理器未初始化")
            return
        
        # 显示进度条
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        
        # 禁用按钮
        self.export_btn.setEnabled(False)
        
        # 创建导出线程
        self.export_thread = ExportThread(
            self.excel_processor,
            self.filtered_results,
            self.template_path,
            output_path
        )
        
        # 连接信号
        self.export_thread.progress_updated.connect(self.progress_bar.setValue)
        self.export_thread.export_finished.connect(self.on_export_finished)
        
        # 开始导出
        self.export_thread.start()
    
    def on_export_finished(self, success: bool, message: str):
        """导出完成处理"""
        # 隐藏进度条
        self.progress_bar.hide()
        
        # 启用按钮
        self.export_btn.setEnabled(True)
        
        # 显示结果
        if success:
            QMessageBox.information(self, "成功", message)
            self.logger.info("Excel导出成功")
        else:
            QMessageBox.warning(self, "失败", message)
            self.logger.error(f"Excel导出失败: {message}")
    
    def clear_results(self):
        """清空结果"""
        if self.filtered_results:
            reply = QMessageBox.question(
                self, "确认清空", "确定要清空所有结果吗？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.filtered_results.clear()
                self.update_results_display()
                self.export_btn.setEnabled(False)
                self.logger.info("清空筛选结果")
    
    def get_results_summary(self) -> Dict[str, Any]:
        """获取结果摘要"""
        if not self.filtered_results:
            return {}
        
        summary = {
            'total_rules': len(self.filtered_results),
            'total_rows': sum(len(df) for df in self.filtered_results.values()),
            'rules_detail': {}
        }
        
        for column_name, df in self.filtered_results.items():
            summary['rules_detail'][column_name] = {
                'rows': len(df),
                'columns': len(df.columns) if not df.empty else 0,
                'has_data': not df.empty
            }
        
        return summary
