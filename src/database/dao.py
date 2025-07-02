"""
数据访问对象模块
"""

import json
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..utils.logger import get_logger
from ..database.models import FilterPlan, FilterRule, FilterCondition


class FilterPlanDAO:
    """筛选方案数据访问对象"""
    
    def __init__(self, connection: sqlite3.Connection):
        self.logger = get_logger(__name__)
        self.conn = connection
    
    def create(self, plan: FilterPlan) -> int:
        """创建筛选方案"""
        cursor = self.conn.cursor()
        
        # 插入方案记录
        cursor.execute("""
            INSERT INTO filter_plans (name, description, created_time, updated_time, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, (
            plan.name,
            plan.description,
            plan.created_time or datetime.now(),
            datetime.now(),
            plan.is_active
        ))
        
        plan_id = cursor.lastrowid
        
        # 插入规则记录
        for rule in plan.rules:
            rule.plan_id = plan_id
            self._create_rule(cursor, rule)
        
        self.conn.commit()
        self.logger.info(f"创建筛选方案: {plan.name} (ID: {plan_id})")
        return plan_id
    
    def get_by_id(self, plan_id: int) -> Optional[FilterPlan]:
        """根据ID获取方案"""
        cursor = self.conn.cursor()
        
        # 获取方案信息
        cursor.execute("""
            SELECT * FROM filter_plans WHERE id = ? AND is_active = TRUE
        """, (plan_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # 获取规则信息
        cursor.execute("""
            SELECT * FROM filter_rules WHERE plan_id = ? ORDER BY order_index
        """, (plan_id,))
        
        rule_rows = cursor.fetchall()
        rules = []
        
        for rule_row in rule_rows:
            conditions_data = json.loads(rule_row['conditions'])
            conditions = [FilterCondition.from_dict(c) for c in conditions_data]
            
            rule = FilterRule(
                id=rule_row['id'],
                plan_id=rule_row['plan_id'],
                name=rule_row['name'],
                conditions=conditions,
                target_column=rule_row['target_column'],
                order_index=rule_row['order_index'],
                is_enabled=bool(rule_row['is_enabled'])
            )
            rules.append(rule)
        
        # 创建方案对象
        plan = FilterPlan(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            rules=rules,
            created_time=datetime.fromisoformat(row['created_time']),
            updated_time=datetime.fromisoformat(row['updated_time']),
            is_active=bool(row['is_active'])
        )
        
        return plan
    
    def get_all(self) -> List[FilterPlan]:
        """获取所有方案"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT id FROM filter_plans WHERE is_active = TRUE
            ORDER BY updated_time DESC
        """)
        
        plan_ids = [row['id'] for row in cursor.fetchall()]
        plans = []
        
        for plan_id in plan_ids:
            plan = self.get_by_id(plan_id)
            if plan:
                plans.append(plan)
        
        return plans
    
    def update(self, plan: FilterPlan) -> bool:
        """更新方案"""
        cursor = self.conn.cursor()
        
        # 更新方案信息
        cursor.execute("""
            UPDATE filter_plans 
            SET name = ?, description = ?, updated_time = ?
            WHERE id = ?
        """, (
            plan.name,
            plan.description,
            datetime.now(),
            plan.id
        ))
        
        # 删除原有规则
        cursor.execute("DELETE FROM filter_rules WHERE plan_id = ?", (plan.id,))
        
        # 插入新规则
        for rule in plan.rules:
            rule.plan_id = plan.id
            self._create_rule(cursor, rule)
        
        self.conn.commit()
        self.logger.info(f"更新筛选方案: {plan.name}")
        return True
    
    def delete(self, plan_id: int) -> bool:
        """删除方案（软删除）"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            UPDATE filter_plans SET is_active = FALSE WHERE id = ?
        """, (plan_id,))
        
        self.conn.commit()
        self.logger.info(f"删除筛选方案ID: {plan_id}")
        return cursor.rowcount > 0
    
    def _create_rule(self, cursor: sqlite3.Cursor, rule: FilterRule):
        """创建规则记录"""
        conditions_json = json.dumps([c.to_dict() for c in rule.conditions])
        
        cursor.execute("""
            INSERT INTO filter_rules 
            (plan_id, name, conditions, target_column, order_index, is_enabled)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            rule.plan_id,
            rule.name,
            conditions_json,
            rule.target_column,
            rule.order_index,
            rule.is_enabled
        ))
