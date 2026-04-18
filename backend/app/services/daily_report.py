"""
每日自动汇报服务
定时向谢总发送项目进度汇报
"""
import subprocess
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# 项目路径
PROJECT_PATH = Path(__file__).parent.parent.parent


def get_git_status():
    """获取 Git 状态"""
    try:
        # 最后一次提交
        result = subprocess.run(
            ['git', 'log', '-1', '--oneline', '--format=%h %s'],
            cwd=PROJECT_PATH,
            capture_output=True,
            text=True
        )
        last_commit = result.stdout.strip() if result.returncode == 0 else "无"
        
        # 提交次数
        result = subprocess.run(
            ['git', 'rev-list', '--count', 'HEAD'],
            cwd=PROJECT_PATH,
            capture_output=True,
            text=True
        )
        commit_count = result.stdout.strip() if result.returncode == 0 else "0"
        
        # 未提交更改
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=PROJECT_PATH,
            capture_output=True,
            text=True
        )
        has_changes = bool(result.stdout.strip())
        
        return {
            "last_commit": last_commit,
            "commit_count": commit_count,
            "has_uncommitted": has_changes,
            "uncommitted_files": len(result.stdout.strip().split('\n')) if has_changes else 0
        }
    except Exception as e:
        logger.error(f"获取Git状态失败: {e}")
        return {"error": str(e)}


def get_project_stats():
    """获取项目统计"""
    try:
        # 使用绝对路径
        backend_path = Path("/root/.openclaw/project-mgr/backend/app")
        frontend_path = Path("/root/.openclaw/project-mgr/frontend/src")
        
        backend_files = list(backend_path.glob("**/*.py")) if backend_path.exists() else []
        frontend_files = []
        if frontend_path.exists():
            frontend_files = list(frontend_path.glob("**/*.vue")) + \
                           list(frontend_path.glob("**/*.ts")) + \
                           list(frontend_path.glob("**/*.js"))
        
        backend_lines = 0
        for f in backend_files:
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    backend_lines += len(file.readlines())
            except:
                pass
        
        frontend_lines = 0
        for f in frontend_files:
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    frontend_lines += len(file.readlines())
            except:
                pass
        
        return {
            "backend_files": len(backend_files),
            "frontend_files": len(frontend_files),
            "backend_lines": backend_lines,
            "frontend_lines": frontend_lines,
            "total_lines": backend_lines + frontend_lines
        }
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"获取项目统计失败: {e}")
        return {}


def build_daily_report():
    """构建每日汇报消息"""
    git_status = get_git_status()
    stats = get_project_stats()
    
    # 检查是否有未提交的更改
    uncommitted_note = ""
    if git_status.get("has_uncommitted"):
        uncommitted_note = f"\n⚠️ **{git_status.get('uncommitted_files')}** 个文件未提交"
    
    message = f"""## 📅 每日进度汇报

**日期**: {datetime.now().strftime("%Y-%m-%d")}

### 🏗️ Git 状态
- 📝 最后提交: `{git_status.get('last_commit', 'N/A')}`
- 📊 总提交数: **{git_status.get('commit_count', '0')}**{uncommitted_note}

### 📈 项目统计
- 🔙 后端文件: **{stats.get('backend_files', 0)}** 个 ({stats.get('backend_lines', 0)} 行)
- 🔜 前端文件: **{stats.get('frontend_files', 0)}** 个 ({stats.get('frontend_lines', 0)} 行)
- 📊 总代码行数: **{stats.get('total_lines', 0)}** 行

### ✅ 今日完成
- Day 6: 定时任务调度器 + 通知系统

### ⏭️ 待处理
- 配置每日自动汇报
- 测试通知发送

---
*🤖 小e自动汇报*"""
    
    return message


def send_daily_report():
    """发送每日汇报 - 定时任务调用"""
    try:
        # 构建消息
        message = build_daily_report()
        
        # 尝试发送到企业微信
        # 这里使用项目内置的通知服务
        from app.services.notify import WeComNotifier
        
        notifier = WeComNotifier()
        success = notifier.send_markdown(message)
        
        if success:
            logger.info("每日汇报发送成功")
            return {"status": "success", "message": "汇报已发送"}
        else:
            logger.warning("每日汇报发送失败")
            return {"status": "failed", "message": "发送失败"}
            
    except Exception as e:
        logger.error(f"发送每日汇报异常: {e}")
        return {"status": "error", "message": str(e)}


# 直接执行时测试
if __name__ == "__main__":
    print(build_daily_report())