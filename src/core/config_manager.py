"""
配置管理模块
负责筛选方案的保存、加载和管理
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..utils.logger import get_logger
from ..utils.exceptions import ConfigurationError
from ..database.models import FilterPlan, FilterRule, FilterCondition


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, db_connection=None):
        self.logger = get_logger(__name__)
        self.db = db_connection
        self.plans: Dict[int, FilterPlan] = {}
        self.next_id = 1
        
    def save_filter_plan(self, plan: FilterPlan) -> int:
        """保存筛选方案"""
        if plan.id is None:
            plan.id = self.next_id
            self.next_id += 1
        
        plan.updated_time = datetime.now()
        if plan.created_time is None:
            plan.created_time = plan.updated_time
        
        self.plans[plan.id] = plan
        self.logger.info(f"保存筛选方案: {plan.name} (ID: {plan.id})")
        return plan.id
    
    def load_filter_plan(self, plan_id: int) -> Optional[FilterPlan]:
        """加载筛选方案"""
        plan = self.plans.get(plan_id)
        if plan:
            self.logger.info(f"加载筛选方案: {plan.name}")
        return plan
    
    def list_filter_plans(self) -> List[FilterPlan]:
        """获取所有筛选方案"""
        return list(self.plans.values())
    
    def delete_filter_plan(self, plan_id: int) -> bool:
        """删除筛选方案"""
        if plan_id in self.plans:
            plan_name = self.plans[plan_id].name
            del self.plans[plan_id]
            self.logger.info(f"删除筛选方案: {plan_name}")
            return True
        return False
    
    def export_plan(self, plan_id: int, file_path: str):
        """导出方案到文件"""
        plan = self.plans.get(plan_id)
        if not plan:
            raise ConfigurationError(f"方案ID {plan_id} 不存在")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(plan.to_dict(), f, ensure_ascii=False, indent=2)
            self.logger.info(f"方案导出到: {file_path}")
        except Exception as e:
            raise ConfigurationError(f"导出失败: {str(e)}")
    
    def import_plan(self, file_path: str) -> FilterPlan:
        """从文件导入方案"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            plan = FilterPlan.from_dict(data)
            plan.id = None  # 重新分配ID
            saved_id = self.save_filter_plan(plan)
            plan.id = saved_id
            
            self.logger.info(f"方案导入成功: {plan.name}")
            return plan
            
        except Exception as e:
            raise ConfigurationError(f"导入失败: {str(e)}")
    
    def create_sample_plan(self) -> FilterPlan:
        """创建示例方案"""
        # 创建示例条件
        condition1 = FilterCondition(
            field="年龄",
            operator=">",
            value=25,
            logic="AND"
        )
        
        condition2 = FilterCondition(
            field="部门",
            operator="=",
            value="销售部",
            logic="AND"
        )
        
        # 创建示例规则
        rule = FilterRule(
            id=1,
            name="优秀销售员",
            conditions=[condition1, condition2],
            target_column="A",
            is_enabled=True
        )
        
        # 创建示例方案
        plan = FilterPlan(
            name="销售部门分析",
            description="筛选年龄大于25岁的销售部员工",
            rules=[rule]
        )
        
        saved_id = self.save_filter_plan(plan)
        plan.id = saved_id
        return plan
