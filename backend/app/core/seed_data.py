"""
数据库种子数据脚本 - 用于初始化测试数据
用法: cd backend && python3 -c "from app.core.seed_data import seed_database; seed_database()"
"""
import sys
import os
from datetime import datetime
import sqlite3
import json

# 优先使用 .env 中的 DATABASE_URL
DB_PATH = '/root/.openclaw/workspace/project-mgr/backend/test_db/project_mgr.db'

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def seed_database(db_path=DB_PATH):
    if not os.path.exists(db_path):
        print(f"Error: DB file not found at {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()
    
    # Clear existing seed data (but not system tables)
    tables_to_clear = ['projects', 'tasks', 'issues', 'documents', 'comments', 
                       'notifications', 'resources', 'workflow_templates']
    for table in tables_to_clear:
        cursor.execute(f"DELETE FROM {table}")
    conn.commit()

    # ========== 项目数据 ==========
    p1 = "INSERT INTO projects (name,description,code,status,owner_id,start_date,end_date,budget,actual_cost,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)"
    projects = [
        ("MES 生产制造管理系统", "公司核心产品，面向中小型工厂的生产制造管理解决方案", "MES", "active", 1, "2026-03-01", "2026-12-31", 500000, 200000, now, now),
        ("OA 办公自动化系统", "企业内部办公自动化系统，涵盖审批、考勤、文档等模块", "OA", "active", 1, "2026-04-01", "2026-11-30", 200000, 80000, now, now),
        ("CRM 客户关系管理", "完整的客户关系管理解决方案，支持销售全流程", "CRM", "PENDING", 3, "2026-06-01", "2026-10-31", 150000, 0, now, now),
        ("HR 人力资源管理系统", "涵盖招聘、考勤、薪酬、绩效的人力资源管理平台", "HR", "active", 3, "2026-02-01", "2026-08-31", 300000, 250000, now, now),
        ("WMS 仓储管理系统", "仓储进销存管理，支持条码扫描和PDA操作", "WMS", "COMPLETED", 4, "2025-10-01", "2026-03-31", 180000, 175000, now, now),
    ]
    for p in projects:
        cursor.execute(p1, p)
    conn.commit()

    # ========== 任务数据 ==========
    t1 = "INSERT INTO tasks (id,title,description,status,priority,assignee_id,project_id,due_date,estimated_hours,actual_hours,tags,created_by,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    tasks = [
        # MES 项目任务
        (1, "工单管理模块 - 需求分析", "完成工单创建、派发、跟踪的需求调研和分析", "COMPLETED", "HIGH", 1, 1, "2026-03-30", 40, 38, "需求,工单", 1, now, now),
        (2, "工单管理模块 - 前端开发", "开发工单列表、工单详情、工单创建的Vue页面", "IN_PROGRESS", "HIGH", 3, 1, "2026-04-30", 80, 45, "前端,工单", 1, now, now),
        (3, "工单管理模块 - 后端API", "开发工单CRUD、状态流转的FastAPI接口", "IN_PROGRESS", "HIGH", 1, 1, "2026-04-30", 60, 30, "后端,API", 1, now, now),
        (4, "质量管理模块 - 方案设计", "检验标准、质检流程、不合格品处理流程设计", "IN_PROGRESS", "MEDIUM", 3, 1, "2026-05-15", 30, 20, "质量,设计", 3, now, now),
        (5, "设备管理模块 - 数据库设计", "设备台账、维护保养、故障记录的表结构设计", "PENDING", "MEDIUM", 4, 1, "2026-05-20", 20, 0, "数据库,设备", 1, now, now),
        (6, "MES 系统集成测试", "MES系统与ERP、WMS的接口联调测试", "PENDING", "LOW", 4, 1, "2026-06-30", 50, 0, "测试,集成", 3, now, now),
        (7, "MES 用户手册编写", "整理MES各模块的操作手册和培训材料", "PENDING", "LOW", 4, 1, "2026-07-15", 15, 0, "文档", 3, now, now),
        # OA 项目任务
        (8, "流程审批 - 请假流程", "开发请假申请的在线提交流程和审批流", "COMPLETED", "HIGH", 3, 2, "2026-04-15", 30, 28, "OA,审批", 1, now, now),
        (9, "流程审批 - 报销流程", "开发费用报销流程，支持发票上传和审批", "IN_PROGRESS", "HIGH", 1, 2, "2026-05-10", 40, 20, "OA,审批", 1, now, now),
        (10, "考勤管理模块", "打卡记录、考勤统计、异常考勤处理功能", "IN_PROGRESS", "MEDIUM", 4, 2, "2026-05-20", 35, 15, "OA,考勤", 3, now, now),
        (11, "文档管理模块", "企业文档的上传、分类、检索功能", "PENDING", "LOW", 4, 2, "2026-06-01", 25, 0, "OA,文档", 1, now, now),
        # HR 项目任务
        (12, "招聘管理模块开发", "职位发布、简历管理、面试安排全流程", "COMPLETED", "MEDIUM", 3, 4, "2026-04-01", 35, 33, "HR,招聘", 3, now, now),
        (13, "薪酬计算模块", "薪资核算、社保公积金计算、工资条生成", "IN_PROGRESS", "HIGH", 1, 4, "2026-05-15", 50, 30, "HR,薪酬", 1, now, now),
        (14, "绩效考核模块", "KPI指标设定、绩效评分、绩效结果展示", "PENDING", "MEDIUM", 3, 4, "2026-06-15", 40, 0, "HR,绩效", 3, now, now),
        # CRM 项目任务
        (15, "CRM 客户信息管理", "客户档案、联系人、跟进记录管理", "PENDING", "HIGH", 1, 3, "2026-06-30", 30, 0, "CRM,客户", 3, now, now),
        (16, "CRM 销售漏斗", "销售阶段管理、商机预测、业绩统计", "PENDING", "MEDIUM", 4, 3, "2026-07-31", 25, 0, "CRM,销售", 1, now, now),
        # 补充任务
        (17, "MES 生产排程模块", "基于设备能力和工单优先级的智能排程", "PENDING", "HIGH", 1, 1, "2026-08-15", 45, 0, "MES,排程", 1, now, now),
        (18, "OA 会议室预订", "会议室资源管理、在线预订、冲突检测", "PENDING", "LOW", 4, 2, "2026-06-15", 20, 0, "OA,会议室", 3, now, now),
        (19, "HR 培训管理", "培训计划、课程管理、在线考试功能", "PENDING", "MEDIUM", 3, 4, "2026-07-01", 30, 0, "HR,培训", 1, now, now),
        (20, "系统安全加固", "权限校验、SQL注入防护、XSS过滤", "IN_PROGRESS", "HIGH", 1, 1, "2026-05-10", 25, 15, "安全,系统", 1, now, now),
    ]
    for t in tasks:
        cursor.execute(t1, t)
    conn.commit()

    # ========== 问题/缺陷数据 ==========
    i1 = "INSERT INTO issues (id,title,description,issue_type,status,priority,project_id,task_id,assignee_id,reporter_id,labels,is_resolved,resolved_at,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    issues = [
        (1, "MES工单创建校验缺失", "创建工单时未校验工单编号是否为空，导致重复编号", "BUG", "IN_PROGRESS", "HIGH", 1, 1, 1, 1, "bug,安全,校验", False, None, now, now),
        (2, "OA审批状态更新延迟", "审批通过后，流程状态在前端显示延迟约3秒", "BUG", "OPEN", "MEDIUM", 2, 3, 1, 1, "bug,性能", False, None, now, now),
        (3, "HR薪酬模块支持多币种", "当前只支持人民币，需要支持美元、欧元等", "FEATURE", "OPEN", "LOW", 4, None, 1, 1, "enhancement,国际化", False, None, now, now),
        (4, "WMS库存导入优化", "导入Excel大文件时内存占用过高，5000行以上可能崩溃", "BUG", "OPEN", "HIGH", 5, None, 4, 1, "bug,性能,内存", True, "2026-04-10", now, now),
        (5, "MES质量报表PDF导出", "当前只支持Excel导出，客户需要PDF格式", "FEATURE", "IN_PROGRESS", "MEDIUM", 1, None, 3, 3, "enhancement,报表", False, None, now, now),
        (6, "CRM客户搜索模糊匹配", "客户搜索只支持精确匹配，需要支持模糊搜索和拼音搜索", "FEATURE", "OPEN", "LOW", 3, None, 1, 1, "enhancement,搜索", False, None, now, now),
        (7, "OA报销附件大小限制", "当前附件限制5MB，财务需要支持20MB", "FEATURE", "OPEN", "MEDIUM", 2, None, 1, 4, "enhancement,附件", False, None, now, now),
        (8, "MES设备报修流程", "现场设备故障时无法快速报修", "FEATURE", "IN_PROGRESS", "HIGH", 1, None, 3, 4, "enhancement,移动端", False, None, now, now),
    ]
    for iss in issues:
        is_resolved = 1 if iss[11] else 0
        resolved_at = iss[12]
        cursor.execute(i1, (iss[0], iss[1], iss[2], iss[3], iss[4], iss[5], iss[6], iss[7], iss[8], iss[9], iss[10], is_resolved, resolved_at, iss[13], iss[14]))
    conn.commit()

    # ========== 文档数据 ==========
    d1 = "INSERT INTO documents (id,name,description,category_id,category_name,tags,project_id,current_version,is_public,created_at,updated_at,created_by) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
    docs = [
        (1, "MES系统需求规格说明书", "MES系统完整的需求规格说明书v2.0", 1, "需求文档", "需求,MES,规格", 1, 2, True, now, now, 1),
        (2, "MES数据库设计文档", "MES系统的数据库表结构、索引设计", None, "设计文档", "设计,MES,数据库", 1, 1, True, now, now, 1),
        (3, "OA系统API接口文档", "OA系统的RESTful API接口说明v1.5", None, "接口文档", "API,OA,接口", 2, 1, True, now, now, 3),
        (4, "项目周报模板", "每周项目进度汇报的模板文档", None, "模板", "模板,周报", None, 1, False, now, now, 1),
        (5, "HR系统用户手册", "HR系统的用户操作手册v1.0", None, "用户手册", "手册,HR,用户", 4, 1, True, now, now, 3),
        (6, "CRM产品演示PPT", "CRM系统的产品介绍和演示材料", None, "演示材料", "PPT,CRM,演示", None, 1, True, now, now, 1),
    ]
    for d in docs:
        cursor.execute(d1, d)
    conn.commit()

    # ========== 评论数据 ==========
    c1 = "INSERT INTO comments (id,task_id,project_id,user_id,content,mentions,created_at,updated_at,is_edited,parent_id) VALUES (?,?,?,?,?,?,?,?,?,?)"
    comments = [
        (1, 1, 1, 1, "需求已经评审通过，可以开始设计了", None, now, now, 0, None),
        (2, 2, 1, 3, "前端页面设计稿已完成，请查阅", None, now, now, 0, None),
        (3, 3, 1, 4, "工单编号校验逻辑已补充，待测试验证", None, now, now, 0, None),
        (4, 4, 2, 1, "审批流程的状态更新问题已定位到WebSocket连接延迟", None, now, now, 0, None),
        (5, 5, 2, 3, "修复方案：使用事件委托减少WebSocket消息处理开销", None, now, now, 0, None),
        (6, 6, 3, 1, "多币种需求已记录到产品 backlog，优先级待定", None, now, now, 0, None),
        (7, 7, 5, 4, "PDF导出功能需要引入PDF生成库，建议使用reportlab", None, now, now, 0, None),
        (8, 8, 5, 3, "已选用reportlab，正在测试中文字体嵌入", None, now, now, 0, None),
        (9, 10, 2, 1, "考勤模块需要对接企业微信的打卡API", None, now, now, 0, None),
        (10, 13, 4, 3, "薪酬计算需要支持个税专项附加扣除", None, now, now, 0, None),
    ]
    for c in comments:
        cursor.execute(c1, c)
    conn.commit()

    # ========== 通知数据 ==========
    n1 = "INSERT INTO notifications (id,user_id,type,title,content,related_data,link,is_read,is_deleted,created_at,read_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)"
    notifications = [
        (1, 1, "task_assigned", "新任务分配", "您被分配了任务：工单管理模块 - 前端开发", None, "/tasks", False, False, now, None),
        (2, 1, "task_completed", "任务完成", "任务工单管理模块 - 需求分析已完成", None, "/tasks", False, False, now, None),
        (3, 1, "project_updated", "项目更新", "MES生产制造管理系统进度更新至60%", None, "/projects", True, False, now, None),
        (4, 3, "task_assigned", "新任务分配", "您被分配了任务：质量方案设计", None, "/tasks", False, False, now, None),
        (5, 2, "comment_mentioned", "评论提及", "您在OA审批流程讨论中被提及", None, "/tasks", True, False, now, None),
        (6, 1, "issue_resolved", "问题已解决", "WMS库存盘点导入功能优化问题已解决", None, "/issues", True, False, now, None),
        (7, 3, "task_assigned", "新任务分配", "您被分配了任务：薪酬计算模块开发", None, "/tasks", False, False, now, None),
        (8, 1, "system", "系统维护通知", "系统将于5月20日凌晨2:00-4:00进行维护升级", None, "/settings", False, False, now, None),
        (9, 1, "task_comment", "任务评论", "您在工单管理模块任务上有新评论", None, "/tasks", False, False, now, None),
        (10, 4, "issue_assigned", "问题分配", "您被分配处理：MES工单创建校验缺失", None, "/issues", False, False, now, None),
    ]
    for n in notifications:
        cursor.execute(n1, n)
    conn.commit()

    # ========== 资源数据 ==========
    r1 = "INSERT INTO resources (id,name,resource_type,description,user_id,unit_cost,currency,is_available,max_capacity,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)"
    resources = [
        (1, "前端开发工位-A1", "workspace", "2楼A区-1号工位", 1, 0, "CNY", True, 1, now, now),
        (2, "后端开发工位-A2", "workspace", "2楼A区-2号工位", 1, 0, "CNY", True, 1, now, now),
        (3, "测试工位-B1", "workspace", "2楼B区-1号工位", 4, 0, "CNY", True, 1, now, now),
        (4, "产品经理工位-A3", "workspace", "2楼A区-3号工位", 3, 0, "CNY", True, 1, now, now),
        (5, "高性能开发服务器", "server", "用于后端开发和测试，32核64G", None, 500, "CNY", True, 1, now, now),
        (6, "测试环境服务器", "server", "用于部署测试环境，16核32G", None, 300, "CNY", True, 1, now, now),
        (7, "企业微信License", "license", "企业微信开发者许可证", None, 10000, "CNY", True, 1, now, now),
    ]
    for r in resources:
        cursor.execute(r1, r)
    conn.commit()

    # ========== 工作流模板 ==========
    w1 = "INSERT INTO workflow_templates (id,name,description,entity_type,steps,is_system,created_by,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)"
    wf1_config = json.dumps({"steps": [
        {"name": "提交", "type": "submit"},
        {"name": "主管审批", "type": "approval", "approver_role": "pm"},
        {"name": "执行", "type": "execute"},
        {"name": "验收", "type": "approval", "approver_role": "admin"}
    ]})
    wf2_config = json.dumps({"steps": [
        {"name": "提交请假申请", "type": "submit"},
        {"name": "主管审批", "type": "approval", "approver_role": "pm"},
        {"name": "HR备案", "type": "approval", "approver_role": "admin"}
    ]})
    workflows = [
        (1, "任务审批流程", "任务状态变更的审批流程", "task", wf1_config, False, 1, now, now),
        (2, "请假审批流程", "员工请假的审批流程", "attendance", wf2_config, False, 1, now, now),
    ]
    for w in workflows:
        cursor.execute(w1, w)
    conn.commit()

    # 角色分配
    cursor.execute("UPDATE users SET role_id = 1 WHERE id = 1")
    cursor.execute("UPDATE users SET role_id = 2 WHERE id = 3")
    cursor.execute("UPDATE users SET role_id = 3 WHERE id IN (2, 4)")
    conn.commit()

    print("种子数据填充完成！")
    for tbl in ['projects', 'tasks', 'issues', 'documents', 'comments', 'notifications', 'resources', 'workflow_templates']:
        count = cursor.execute(f'SELECT COUNT(*) FROM {tbl}').fetchone()[0]
        print(f"  {tbl}: {count}")
    conn.close()

if __name__ == '__main__':
    print("开始填充种子数据...")
    seed_database()
    print("所有数据已填充！")
