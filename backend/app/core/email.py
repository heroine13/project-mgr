"""
邮件通知服务模块
提供 SMTP 邮件发送功能，支持 HTML 模板
"""
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
from typing import Optional, List
import os
import jinja2
from datetime import datetime


class EmailService:
    """邮件服务类"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("SMTP_FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("SMTP_FROM_NAME", "Project Manager")
        self.use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        
        # Jinja2 模板引擎
        self.template_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "templates", "emails"
        )
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir)
        )
    
    def is_configured(self) -> bool:
        """检查邮件服务是否已配置"""
        return bool(self.smtp_user and self.smtp_password)
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None
    ) -> bool:
        """
        发送邮件
        
        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML 内容
            plain_content: 纯文本内容（可选）
        
        Returns:
            bool: 发送是否成功
        """
        if not self.is_configured():
            print(f"邮件服务未配置，跳过发送到 {to_email}")
            return False
        
        try:
            # 创建邮件消息
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
            
            # 添加纯文本版本
            if plain_content:
                msg.attach(MIMEText(plain_content, "plain", "utf-8"))
            
            # 添加 HTML 版本
            msg.attach(MIMEText(html_content, "html", "utf-8"))
            
            # 连接 SMTP 服务器并发送
            with SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            print(f"邮件发送成功: {to_email}")
            return True
            
        except Exception as e:
            print(f"邮件发送失败: {str(e)}")
            return False
    
    def render_template(self, template_name: str, context: dict) -> str:
        """
        渲染邮件模板
        
        Args:
            template_name: 模板文件名
            context: 模板上下文变量
        
        Returns:
            str: 渲染后的 HTML 内容
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except jinja2.TemplateNotFound:
            print(f"邮件模板不存在: {template_name}")
            return ""
        except Exception as e:
            print(f"模板渲染失败: {str(e)}")
            return ""


# 全局邮件服务实例
email_service = EmailService()


# === 便捷函数 ===

def send_task_notification(
    to_email: str,
    task_title: str,
    project_name: str,
    action: str,
    actor_name: str
) -> bool:
    """
    发送任务通知邮件
    
    Args:
        to_email: 收件人邮箱
        task_title: 任务标题
        project_name: 项目名称
        action: 操作类型 (created, updated, assigned, completed)
        actor_name: 操作人名称
    
    Returns:
        bool: 发送是否成功
    """
    action_verbs = {
        "created": "创建了",
        "updated": "更新了",
        "assigned": "分配了",
        "completed": "完成了",
        "commented": "评论了"
    }
    
    subject = f"[项目管理系统] 任务 {action_verbs.get(action, action)}: {task_title}"
    
    context = {
        "task_title": task_title,
        "project_name": project_name,
        "action": action,
        "action_verb": action_verbs.get(action, action),
        "actor_name": actor_name,
        "action_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "login_url": os.getenv("FRONTEND_URL", "http://localhost:5173")
    }
    
    html_content = email_service.render_template("task_notification.html", context)
    plain_content = f"""
任务 {action_verbs.get(action, action)}: {task_title}

项目: {project_name}
操作人: {actor_name}
时间: {context['action_time']}

请登录系统查看详情: {context['login_url']}
    """
    
    return email_service.send_email(to_email, subject, html_content, plain_content)


def send_project_notification(
    to_email: str,
    project_name: str,
    action: str,
    actor_name: str,
    description: str = ""
) -> bool:
    """
    发送项目通知邮件
    
    Args:
        to_email: 收件人邮箱
        project_name: 项目名称
        action: 操作类型
        actor_name: 操作人名称
        description: 描述信息
    
    Returns:
        bool: 发送是否成功
    """
    subject = f"[项目管理系统] 项目 {action}: {project_name}"
    
    context = {
        "project_name": project_name,
        "action": action,
        "actor_name": actor_name,
        "description": description,
        "action_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "login_url": os.getenv("FRONTEND_URL", "http://localhost:5173")
    }
    
    html_content = email_service.render_template("project_notification.html", context)
    plain_content = f"""
项目 {action}: {project_name}

操作人: {actor_name}
描述: {description}
时间: {context['action_time']}

请登录系统查看详情: {context['login_url']}
    """
    
    return email_service.send_email(to_email, subject, html_content, plain_content)


def send_welcome_email(to_email: str, username: str) -> bool:
    """
    发送欢迎邮件
    
    Args:
        to_email: 收件人邮箱
        username: 用户名
    
    Returns:
        bool: 发送是否成功
    """
    subject = "欢迎使用项目管理系统"
    
    context = {
        "username": username,
        "login_url": os.getenv("FRONTEND_URL", "http://localhost:5173"),
        "current_year": datetime.now().year
    }
    
    html_content = email_service.render_template("welcome.html", context)
    plain_content = f"""
欢迎使用项目管理系统, {username}!

请访问以下链接登录系统:
{context['login_url']}

祝您使用愉快！
    """
    
    return email_service.send_email(to_email, subject, html_content, plain_content)