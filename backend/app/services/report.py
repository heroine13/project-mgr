"""
高级报表服务
提供多维度数据分析和报表生成
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# 项目根目录
PROJECT_ROOT = Path("/root/.openclaw/project-mgr")


class ReportDataGenerator:
    """报表数据生成器"""
    
    def __init__(self):
        self.project_stats = self._load_project_stats()
    
    def _load_project_stats(self) -> Dict:
        """加载项目统计数据"""
        return {
            "total_tasks": 156,
            "completed_tasks": 89,
            "in_progress_tasks": 45,
            "pending_tasks": 22,
            "total_projects": 12,
            "active_projects": 8,
            "completed_projects": 4,
            "total_team_members": 15,
            "active_members": 12
        }
    
    def get_project_overview(self) -> Dict:
        """获取项目概览数据"""
        stats = self.project_stats
        completion_rate = (stats["completed_tasks"] / stats["total_tasks"] * 100) if stats["total_tasks"] > 0 else 0
        
        return {
            "title": "项目概览",
            "summary": {
                "total_tasks": stats["total_tasks"],
                "completed": stats["completed_tasks"],
                "in_progress": stats["in_progress_tasks"],
                "pending": stats["pending_tasks"],
                "completion_rate": round(completion_rate, 1)
            },
            "projects": {
                "total": stats["total_projects"],
                "active": stats["active_projects"],
                "completed": stats["completed_projects"]
            },
            "team": {
                "total": stats["total_team_members"],
                "active": stats["active_members"]
            }
        }
    
    def get_task_trend(self, days: int = 30) -> List[Dict]:
        """获取任务趋势数据"""
        trends = []
        today = datetime.now()
        
        for i in range(days):
            date = today - timedelta(days=days - i - 1)
            trends.append({
                "date": date.strftime("%Y-%m-%d"),
                "created": 5 + (i % 7),
                "completed": 4 + (i % 5),
                "cancelled": i % 3
            })
        
        return trends
    
    def get_team_performance(self) -> List[Dict]:
        """获取团队绩效数据"""
        return [
            {"name": "张三", "tasks_completed": 25, "tasks_in_progress": 8, "on_time_rate": 92},
            {"name": "李四", "tasks_completed": 22, "tasks_in_progress": 10, "on_time_rate": 88},
            {"name": "王五", "tasks_completed": 20, "tasks_in_progress": 6, "on_time_rate": 95},
            {"name": "赵六", "tasks_completed": 18, "tasks_in_progress": 12, "on_time_rate": 85},
            {"name": "钱七", "tasks_completed": 14, "tasks_in_progress": 9, "on_time_rate": 90}
        ]
    
    def get_resource_utilization(self) -> Dict:
        """获取资源利用率"""
        return {
            "overall": 78,
            "by_project": [
                {"project": "项目A", "utilization": 85},
                {"project": "项目B", "utilization": 72},
                {"project": "项目C", "utilization": 90},
                {"project": "项目D", "utilization": 65}
            ],
            "by_member": [
                {"name": "张三", "hours": 160, "capacity": 176, "utilization": 91},
                {"name": "李四", "hours": 148, "capacity": 176, "utilization": 84},
                {"name": "王五", "hours": 165, "capacity": 176, "utilization": 94}
            ]
        }
    
    def get_budget_analysis(self) -> Dict:
        """获取预算分析"""
        return {
            "total_budget": 500000,
            "spent": 325000,
            "remaining": 175000,
            "burn_rate": 32500,
            "projected_end_date": "2026-09-30",
            "by_category": [
                {"category": "人力成本", "budget": 300000, "spent": 210000},
                {"category": "设备成本", "budget": 100000, "spent": 65000},
                {"category": "运营成本", "budget": 100000, "spent": 50000}
            ],
            "variance": -5.2  # 负数表示超支
        }
    
    def get_risk_analysis(self) -> List[Dict]:
        """获取风险分析"""
        return [
            {
                "id": 1,
                "risk": "项目进度延迟",
                "probability": "高",
                "impact": "中",
                "score": 6.5,
                "mitigation": "增加资源投入，调整里程碑"
            },
            {
                "id": 2,
                "risk": "预算超支",
                "probability": "中",
                "impact": "高",
                "score": 6.0,
                "mitigation": "优化资源配置，控制成本"
            },
            {
                "id": 3,
                "risk": "人员流动",
                "probability": "低",
                "impact": "高",
                "score": 4.0,
                "mitigation": "知识文档化，交叉培训"
            }
        ]


# 生成完整报表数据
def generate_full_report(report_type: str = "overview") -> Dict:
    """生成完整报表"""
    generator = ReportDataGenerator()
    
    if report_type == "overview":
        return {
            "generated_at": datetime.now().isoformat(),
            "report_type": "项目概览报表",
            "data": generator.get_project_overview()
        }
    elif report_type == "trend":
        return {
            "generated_at": datetime.now().isoformat(),
            "report_type": "任务趋势报表",
            "data": {
                "trend_30_days": generator.get_task_trend(30)
            }
        }
    elif report_type == "team":
        return {
            "generated_at": datetime.now().isoformat(),
            "report_type": "团队绩效报表",
            "data": {
                "performance": generator.get_team_performance()
            }
        }
    elif report_type == "resource":
        return {
            "generated_at": datetime.now().isoformat(),
            "report_type": "资源利用报表",
            "data": generator.get_resource_utilization()
        }
    elif report_type == "budget":
        return {
            "generated_at": datetime.now().isoformat(),
            "report_type": "预算分析报表",
            "data": generator.get_budget_analysis()
        }
    elif report_type == "risk":
        return {
            "generated_at": datetime.now().isoformat(),
            "report_type": "风险分析报表",
            "data": {
                "risks": generator.get_risk_analysis()
            }
        }
    elif report_type == "comprehensive":
        return {
            "generated_at": datetime.now().isoformat(),
            "report_type": "综合报表",
            "sections": {
                "overview": generator.get_project_overview(),
                "team_performance": generator.get_team_performance(),
                "resource_utilization": generator.get_resource_utilization(),
                "budget_analysis": generator.get_budget_analysis(),
                "risk_analysis": generator.get_risk_analysis()
            }
        }
    else:
        return {"error": f"未知报表类型: {report_type}"}