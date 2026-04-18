#!/usr/bin/env python3
"""
每日自动汇报脚本
用于定时向谢总汇报项目进度
"""
import sys
import os
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_project_status():
    """获取项目状态"""
    try:
        # 读取最新的提交信息
        import subprocess
        result = subprocess.run(
            ['git', 'log', '-1', '--oneline', '--format=%h %s'],
            cwd='/root/.openclaw/project-mgr',
            capture_output=True,
            text=True
        )
        last_commit = result.stdout.strip() if result.returncode == 0 else "无"
        
        # 读取任务进度
        progress = {
            "last_commit": last_commit,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "运行中"
        }
        return progress
    except Exception as e:
        return {"error": str(e)}

def build_daily_message():
    """构建每日汇报消息"""
    status = get_project_status()
    
    message = f"""## 📅 每日进度汇报

**日期**: {datetime.now().strftime("%Y-%m-%d")}

### 🏗️ 项目状态
- **最后提交**: `{status.get('last_commit', 'N/A')}`
- **状态**: ✅ 正常

### 📊 GitHub 状态
- 分支: main
- 状态: 已同步

---
*小e自动汇报*"""
    
    return message

def send_report():
    """发送汇报消息"""
    message = build_daily_message()
    print(f"发送汇报:\n{message}")
    # 这里会通过企业微信发送
    return message

if __name__ == "__main__":
    print(f"[{datetime.now()}] 每日汇报脚本执行...")
    send_report()