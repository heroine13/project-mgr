"""
AI Service - Intelligent Features for Project Management
"""

import os
import json
from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.orm import Session

# AI Provider Configuration
AI_PROVIDER = os.environ.get("AI_PROVIDER", "openai")  # openai, anthropic, local
AI_API_KEY = os.environ.get("AI_API_KEY", "")
AI_MODEL = os.environ.get("AI_MODEL", "gpt-3.5-turbo")


class AIService:
    """AI service for intelligent project management features"""
    
    @staticmethod
    def generate_task_suggestions(
        db: Session,
        project_id: int,
        user_id: int
    ) -> Dict:
        """Generate AI-powered task suggestions based on project context"""
        
        # This is a simplified example - in production, you would:
        # 1. Fetch project data, tasks, and team performance
        # 2. Send to AI API for analysis
        # 3. Return intelligent suggestions
        
        suggestions = {
            "task_prioritization": [
                {"task_id": 1, "reason": "High impact on project milestone", "suggested_priority": "high"},
                {"task_id": 2, "reason": "Blocked by this task", "suggested_priority": "high"},
            ],
            "resource_allocation": [
                {"user_id": 1, "suggestion": "Assign to frontend tasks - high velocity", "capacity": "80%"},
                {"user_id": 2, "suggestion": "Better suited for testing tasks", "capacity": "60%"},
            ],
            "risk_identification": [
                {"risk": "Task #5 deadline may be missed", "likelihood": "high", "mitigation": "Consider rebalancing workload"},
                {"risk": "Resource bottleneck in week 3", "likelihood": "medium", "mitigation": "Start recruitment early"},
            ],
            "recommendations": [
                "Consider breaking down Task #8 into smaller tasks",
                "Team velocity suggests completing 3 more tasks this sprint",
                "Prioritize bug fixes before new feature development"
            ]
        }
        
        return suggestions
    
    @staticmethod
    def summarize_project_status(
        project_name: str,
        tasks: List[Dict],
        issues: List[Dict]
    ) -> str:
        """Generate AI-powered project status summary"""
        
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.get("status") == "completed")
        total_issues = len(issues)
        open_issues = sum(1 for i in issues if i.get("status") == "open")
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Generate summary based on metrics
        if completion_rate >= 80:
            status = "excellent"
            summary = f"'{project_name}' 项目进展顺利！已完成 {completion_rate:.1f}% 的任务。"
        elif completion_rate >= 50:
            status = "good"
            summary = f"'{project_name}' 项目正在进行中。已完成 {completion_rate:.1f}% 的任务。"
        else:
            status = "needs_attention"
            summary = f"'{project_name}' 项目需要关注。当前完成率为 {completion_rate:.1f}%。"
        
        if open_issues > 5:
            summary += f" 注意到有 {open_issues} 个开放的问题需要解决。"
        
        return summary
    
    @staticmethod
    def generate_meeting_notes(
        project_name: str,
        recent_updates: List[str]
    ) -> str:
        """Generate AI-powered meeting notes from project updates"""
        
        if not recent_updates:
            return f"# {project_name} 会议纪要\n\n暂无最新更新。"
        
        notes = f"# {project_name} 会议纪要\n\n"
        notes += f"**日期**: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        notes += "## 最近更新\n\n"
        
        for i, update in enumerate(recent_updates, 1):
            notes += f"{i}. {update}\n"
        
        notes += "\n## 待讨论事项\n\n"
        notes += "- 进度评估\n"
        notes += "- 风险识别\n"
        notes += "- 下一步计划\n"
        
        return notes
    
    @staticmethod
    def analyze_team_performance(
        team_members: List[Dict],
        tasks: List[Dict]
    ) -> Dict:
        """Analyze team performance and provide insights"""
        
        # Calculate metrics for each team member
        member_performance = {}
        
        for member in team_members:
            member_id = member.get("id")
            member_tasks = [t for t in tasks if t.get("assignee_id") == member_id]
            
            total = len(member_tasks)
            completed = sum(1 for t in member_tasks if t.get("status") == "completed")
            
            member_performance[member_id] = {
                "username": member.get("username"),
                "total_tasks": total,
                "completed": completed,
                "completion_rate": (completed / total * 100) if total > 0 else 0,
                "avg_hours": sum(t.get("actual_hours", 0) for t in member_tasks) / total if total > 0 else 0
            }
        
        # Generate insights
        insights = []
        
        # Top performer
        top_performer = max(member_performance.values(), key=lambda x: x["completion_rate"])
        insights.append(f"🏆 {top_performer['username']} 表现最佳，完成率 {top_performer['completion_rate']:.1f}%")
        
        # Needs improvement
        low_performers = [m for m in member_performance.values() if m["completion_rate"] < 50]
        if low_performers:
            names = ", ".join([m["username"] for m in low_performers])
            insights.append(f"⚠️ {names} 需要额外的支持来完成目标")
        
        return {
            "team_summary": insights,
            "individual_performance": member_performance,
            "recommendations": [
                "定期进行一对一交流，了解团队成员的需求",
                "分享最佳实践，促进知识共享",
                "考虑跨功能团队合作，提高效率"
            ]
        }
    
    @staticmethod
    def suggest_task_dependencies(
        task_title: str,
        existing_tasks: List[Dict]
    ) -> List[Dict]:
        """Suggest task dependencies based on AI analysis"""
        
        # Simple keyword-based dependency suggestion
        # In production, this would use NLP and project context
        
        suggestions = []
        task_keywords = set(task_title.lower().split())
        
        for existing_task in existing_tasks:
            existing_keywords = set(existing_task.get("title", "").lower().split())
            
            # Check for keyword overlap (indicating potential dependency)
            common_keywords = task_keywords & existing_keywords
            
            if common_keywords:
                suggestions.append({
                    "task_id": existing_task.get("id"),
                    "task_title": existing_task.get("title"),
                    "confidence": len(common_keywords) / len(task_keywords),
                    "reason": f"相关关键词: {', '.join(common_keywords)}"
                })
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        
        return suggestions[:5]  # Return top 5 suggestions


# AI Chat endpoint (simplified)
class AIChatService:
    """Simple AI chat for project management assistance"""
    
    SYSTEM_PROMPT = """你是一个专业的项目管理助手。请用中文回答关于项目管理的问题。

你可以帮助用户：
- 解答项目管理相关问题
- 提供任务管理建议
- 分析项目进度和风险
- 提供团队协作建议

请保持回答简洁、专业且有用。"""
    
    @staticmethod
    async def chat(
        user_message: str,
        project_context: Optional[Dict] = None
    ) -> str:
        """Process user chat message and return AI response"""
        
        # Build context from project data
        context_info = ""
        if project_context:
            context_info = f"\n\n项目上下文:\n"
            context_info += f"- 项目名称: {project_context.get('name', 'N/A')}\n"
            context_info += f"- 任务总数: {project_context.get('task_count', 0)}\n"
            context_info += f"- 完成率: {project_context.get('completion_rate', 0)}%\n"
        
        # In production, this would call actual AI API
        # For now, return a placeholder response
        response = f"感谢您的提问！这是关于项目管理的帮助信息。{context_info}\n\n"
        response += "如果您需要更具体的帮助，请告诉我您具体需要什么帮助。"
        
        return response