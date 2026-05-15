"""
AI Service - 智能项目管理功能 (增强版)
支持: OpenAI GPT, Anthropic Claude, 本地模型
"""

import os
import json
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

# AI Provider Configuration
AI_PROVIDER = os.environ.get("AI_PROVIDER", "openai")  # openai, anthropic, local
AI_API_KEY = os.environ.get("AI_API_KEY", "")
AI_MODEL = os.environ.get("AI_MODEL", "gpt-4")
AI_BASE_URL = os.environ.get("AI_BASE_URL", "")  # 用于代理/本地模型

# OpenAI客户端初始化
openai_client = None
anthropic_client = None

if AI_API_KEY:
    try:
        import openai as openai_pkg
        openai_pkg.base_url = AI_BASE_URL if AI_BASE_URL else "https://api.openai.com/v1"
        openai_pkg.api_key = AI_API_KEY
        openai_client = openai_pkg.OpenAI(
            api_key=AI_API_KEY,
            base_url=AI_BASE_URL if AI_BASE_URL else None,
            timeout=60.0,
            max_retries=2
        )
        logger.info("OpenAI client initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize OpenAI client: {e}")

# Anthropic客户端初始化
if AI_PROVIDER == "anthropic" and AI_API_KEY:
    try:
        import anthropic
        anthropic_client = anthropic.Anthropic(
            api_key=AI_API_KEY,
            timeout=60.0
        )
        logger.info("Anthropic client initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize Anthropic client: {e}")


class AIService:
    """AI服务 - 智能项目管理功能"""
    
    # 系统提示词
    PROJECT_MANAGER_PROMPT = """你是一个专业的项目管理助手，专门帮助用户管理项目进度、协调团队任务、分析项目风险。

你的能力包括：
1. 任务管理建议 - 根据项目上下文提供任务优先级、资源分配建议
2. 进度分析 - 分析项目完成情况，识别潜在风险
3. 团队协作 - 提供团队绩效分析和改进建议
4. 问题解决 - 帮助识别和解决项目中的问题

请用中文回答，保持专业、简洁、有帮助。回答长度控制在200字以内，除非用户要求详细说明。"""

    @staticmethod
    async def call_ai_api(
        messages: List[Dict[str, str]],
        system_prompt: str = None
    ) -> str:
        """统一调用AI API"""
        
        if not AI_API_KEY:
            return "⚠️ AI服务未配置。请设置 AI_API_KEY 环境变量。"
        
        try:
            if AI_PROVIDER == "openai" and openai_client:
                # OpenAI 调用
                full_messages = [{"role": "system", "content": system_prompt or AIService.PROJECT_MANAGER_PROMPT}]
                full_messages.extend(messages)
                
                response = openai_client.chat.completions.create(
                    model=AI_MODEL,
                    messages=full_messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                return response.choices[0].message.content
                
            elif AI_PROVIDER == "anthropic" and anthropic_client:
                # Anthropic 调用
                system = system_prompt or AIService.PROJECT_MANAGER_PROMPT
                user_message = messages[-1]["content"] if messages else ""
                
                response = anthropic_client.messages.create(
                    model=AI_MODEL if AI_MODEL else "claude-3-sonnet-20240229",
                    max_tokens=1000,
                    system=system,
                    messages=[{"role": "user", "content": user_message}]
                )
                return response.content[0].text
                
            else:
                # 本地/自定义模型
                return await AIService._local_ai_response(messages, system_prompt)
                
        except Exception as e:
            logger.error(f"AI API call failed: {e}")
            return f"⚠️ AI服务调用失败: {str(e)}"
    
    @staticmethod
    async def _local_ai_response(messages: List[Dict], system_prompt: str) -> str:
        """本地AI响应（备用方案）"""
        return "⚠️ 请配置 AI_API_KEY 环境变量以启用AI功能。当前使用演示模式。"
    
    @staticmethod
    async def generate_task_suggestions(
        db: Session,
        project_id: int,
        user_id: int
    ) -> Dict:
        """AI智能任务建议"""
        
        # 获取项目数据
        from app.models.project import Project
        from app.models.task import Task
        
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {"error": "项目不存在"}
        
        tasks = db.query(Task).filter(Task.project_id == project_id).all()
        
        # 构建项目上下文
        tasks_summary = []
        for t in tasks:
            tasks_summary.append({
                "title": t.title,
                "status": str(t.status),
                "priority": str(t.priority),
                "due_date": str(t.due_date) if t.due_date else None
            })
        
        # 调用AI获取建议
        prompt = f"""请分析以下项目任务，提供智能建议：

项目名称: {project.name}
任务列表:
{json.dumps(tasks_summary, ensure_ascii=False, indent=2)}

请提供:
1. 任务优先级调整建议 (task_prioritization) - 列出需要调整优先级的任务和原因
2. 资源分配建议 (resource_allocation) - 建议如何分配团队成员
3. 风险识别 (risk_identification) - 识别可能的风险
4. 综合建议 (recommendations) - 其他改进建议

请用JSON格式返回，包含这4个分类。"""
        
        messages = [{"role": "user", "content": prompt}]
        ai_response = await AIService.call_ai_api(messages)
        
        # 尝试解析JSON响应
        try:
            # 尝试提取JSON部分
            import re
            json_match = re.search(r'\{[\s\S]*\}', ai_response)
            if json_match:
                suggestions = json.loads(json_match.group())
                return suggestions
        except:
            pass
        
        # 如果无法解析JSON，返回原始响应
        return {
            "task_prioritization": [],
            "resource_allocation": [],
            "risk_identification": [],
            "recommendations": [ai_response[:500]],
            "raw_response": ai_response[:500]
        }
    
    @staticmethod
    async def summarize_project_status(
        project_name: str,
        tasks: List[Dict],
        issues: List[Dict]
    ) -> str:
        """AI项目状态总结"""
        
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.get("status") == "completed")
        total_issues = len(issues)
        open_issues = sum(1 for i in issues if i.get("status") == "open")
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        prompt = f"""请为以下项目生成简洁的状态总结：

项目名称: {project_name}
任务统计: 总数 {total_tasks}, 已完成 {completed_tasks}, 完成率 {completion_rate:.1f}%
问题统计: 总数 {total_issues}, 开放问题 {open_issues}

请用2-3句话总结项目当前状态，并给出简短建议。"""
        
        messages = [{"role": "user", "content": prompt}]
        summary = await AIService.call_ai_api(messages)
        
        return summary
    
    @staticmethod
    async def generate_meeting_notes(
        project_name: str,
        recent_updates: List[str]
    ) -> str:
        """AI会议纪要生成"""
        
        prompt = f"""请为以下项目更新生成会议纪要：

项目名称: {project_name}
最近更新:
{chr(10).join(f"- {u}" for u in recent_updates)}

请生成格式良好的会议纪要，包含：
1. 会议主题
2. 最近进展
3. 待讨论事项
4. 下一步计划

使用中文，保持专业简洁。"""
        
        messages = [{"role": "user", "content": prompt}]
        notes = await AIService.call_ai_api(messages)
        
        return notes
    
    @staticmethod
    async def analyze_team_performance(
        team_members: List[Dict],
        tasks: List[Dict]
    ) -> Dict:
        """AI团队绩效分析"""
        
        # 计算基础统计数据
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
            }
        
        # 调用AI进行分析
        prompt = f"""请分析以下团队绩效数据，提供见解和建议：

团队成员绩效:
{json.dumps(member_performance, ensure_ascii=False, indent=2)}

请提供:
1. 最佳表现者 (top_performer)
2. 需要关注的成员 (needs_improvement)
3. 改进建议 (recommendations)

请用JSON格式返回。"""
        
        messages = [{"role": "user", "content": prompt}]
        ai_response = await AIService.call_ai_api(messages)
        
        # 尝试解析AI响应
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', ai_response)
            if json_match:
                analysis = json.loads(json_match.group())
                return {
                    "team_summary": analysis,
                    "individual_performance": member_performance,
                    "recommendations": analysis.get("recommendations", [])
                }
        except:
            pass
        
        return {
            "team_summary": {"ai_response": ai_response[:500]},
            "individual_performance": member_performance,
            "recommendations": ["请配置AI API以获取详细分析"]
        }
    
    @staticmethod
    async def suggest_task_dependencies(
        task_title: str,
        existing_tasks: List[Dict]
    ) -> List[Dict]:
        """AI任务依赖建议"""
        
        prompt = f"""请分析以下任务，推荐可能的依赖关系：

当前任务: {task_title}

现有任务:
{json.dumps([{"id": t.get("id"), "title": t.get("title"), "status": t.get("status")} for t in existing_tasks], ensure_ascii=False, indent=2)}

请分析哪些任务可能依赖于当前任务，或当前任务依赖于哪些任务。
请用JSON数组格式返回，每项包含 task_id, task_title, confidence(0-1), reason。"""
        
        messages = [{"role": "user", "content": prompt}]
        ai_response = await AIService.call_ai_api(messages)
        
        try:
            import re
            # 尝试匹配JSON数组
            json_match = re.search(r'\[[\s\S]*\]', ai_response)
            if json_match:
                suggestions = json.loads(json_match.group())
                return suggestions[:5]
        except:
            pass
        
        return []
    
    @staticmethod
    async def smart_reply(user_message: str, context: Dict = None) -> str:
        """智能回复功能"""
        
        context_info = ""
        if context:
            context_info = f"\n\n项目上下文:\n"
            for key, value in context.items():
                context_info += f"- {key}: {value}\n"
        
        prompt = f"""用户问题: {user_message}{context_info}

请给出专业、简洁的回答。"""
        
        messages = [{"role": "user", "content": prompt}]
        response = await AIService.call_ai_api(messages)
        
        return response


# AI Chat 服务 (简化为异步)
class AIChatService:
    """AI对话服务"""
    
    @staticmethod
    async def chat(
        user_message: str,
        project_context: Optional[Dict] = None
    ) -> str:
        """处理用户对话"""
        
        # 构建上下文
        context_info = ""
        if project_context:
            context_info = f"\n\n当前项目信息:\n"
            context_info += f"- 项目名称: {project_context.get('name', 'N/A')}\n"
            context_info += f"- 任务总数: {project_context.get('task_count', 0)}\n"
            context_info += f"- 完成率: {project_context.get('completion_rate', 0)}%\n"
        
        prompt = f"""用户: {user_message}{context_info}

请作为项目管理助手回答。"""
        
        messages = [{"role": "user", "content": prompt}]
        response = await AIService.call_ai_api(messages)
        
        return response


# 向后兼容的静态方法版本
class AIServiceSync:
    """同步版本的AI服务（用于兼容旧代码）"""
    
    @staticmethod
    def generate_task_suggestions(db: Session, project_id: int, user_id: int) -> Dict:
        """同步版本 - 推荐使用异步版本"""
        return {
            "task_prioritization": [],
            "resource_allocation": [],
            "risk_identification": [],
            "recommendations": ["请使用异步版本 AIService.generate_task_suggestions()"]
        }
    
    @staticmethod
    def summarize_project_status(project_name: str, tasks: List[Dict], issues: List[Dict]) -> str:
        """同步版本"""
        return "请使用异步版本 AIService.summarize_project_status()"
    
    @staticmethod
    def analyze_team_performance(team_members: List[Dict], tasks: List[Dict]) -> Dict:
        """同步版本"""
        return {"recommendations": ["请使用异步版本"]}
    
    @staticmethod
    def suggest_task_dependencies(task_title: str, existing_tasks: List[Dict]) -> List[Dict]:
        """同步版本"""
        return []

def reload_config():
    """重新加载AI配置（动态更新）"""
    global AI_PROVIDER, AI_API_KEY, AI_MODEL, AI_BASE_URL
    global openai_client, anthropic_client
    import os as _os
    
    AI_PROVIDER = _os.environ.get("AI_PROVIDER", "openai")
    AI_API_KEY = _os.environ.get("AI_API_KEY", "")
    AI_MODEL = _os.environ.get("AI_MODEL", "gpt-4")
    AI_BASE_URL = _os.environ.get("AI_BASE_URL", "")
    
    # Reset clients
    openai_client = None
    anthropic_client = None
    
    if AI_API_KEY:
        try:
            import openai as _openai_pkg
            _openai_pkg.base_url = AI_BASE_URL if AI_BASE_URL else "https://api.openai.com/v1"
            _openai_pkg.api_key = AI_API_KEY
            openai_client = _openai_pkg.OpenAI(
                api_key=AI_API_KEY,
                base_url=AI_BASE_URL if AI_BASE_URL else None,
                timeout=60.0,
                max_retries=2
            )
            logger.info(f"AI client reinitialized: provider={AI_PROVIDER}, model={AI_MODEL}")
        except Exception as e:
            logger.error(f"Failed to reinitialize AI client: {e}")
    
    if AI_PROVIDER == "anthropic" and AI_API_KEY:
        try:
            import anthropic as _anthropic
            anthropic_client = _anthropic.Anthropic(
                api_key=AI_API_KEY,
                timeout=60.0
            )
            logger.info("Anthropic client reinitialized")
        except Exception as e:
            logger.error(f"Failed to reinitialize Anthropic client: {e}")
