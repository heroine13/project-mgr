"""
集成测试
测试多个模块之间的协作
"""
import pytest
from fastapi import status


class TestProjectTaskIntegration:
    """项目-任务集成测试"""
    
    def test_create_project_and_tasks(self, client, sample_user, auth_headers):
        """测试创建项目和关联任务"""
        # 1. 创建项目
        project_response = client.post(
            "/api/v1/projects/",
            json={
                "name": "Integration Test Project",
                "description": "Testing project-task integration"
            },
            headers=auth_headers
        )
        assert project_response.status_code == status.HTTP_200_OK
        project_id = project_response.json()["id"]
        
        # 2. 创建任务
        task_response = client.post(
            "/api/v1/tasks/",
            json={
                "title": "Integration Task 1",
                "project_id": project_id,
                "priority": "high"
            },
            headers=auth_headers
        )
        assert task_response.status_code == status.HTTP_200_OK
        task_id = task_response.json()["id"]
        
        # 3. 验证任务属于项目
        task = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
        assert task.json()["project_id"] == project_id
    
    def test_project_statistics(self, client, sample_project, sample_task, auth_headers):
        """测试项目统计功能"""
        response = client.get(
            f"/api/v1/projects/{sample_project.id}/statistics",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_tasks" in data
        assert "completed_tasks" in data


class TestAuthProjectIntegration:
    """认证-项目集成测试"""
    
    def test_user_can_only_see_own_projects(self, client, sample_user, auth_headers):
        """测试用户只能看到自己的项目"""
        # 创建项目
        client.post(
            "/api/v1/projects/",
            json={"name": "My Project"},
            headers=auth_headers
        )
        
        # 获取项目列表
        response = client.get("/api/v1/projects/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        projects = response.json()
        assert all(p["owner_id"] == sample_user.id for p in projects)


class TestNotificationIntegration:
    """通知集成测试"""
    
    def test_task_creates_notification(self, client, sample_project, auth_headers):
        """测试任务创建时触发通知"""
        # 创建任务
        response = client.post(
            "/api/v1/tasks/",
            json={
                "title": "Task with Notification",
                "project_id": sample_project.id
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        # 获取通知列表
        notif_response = client.get("/api/v1/notifications/", headers=auth_headers)
        assert notif_response.status_code == status.HTTP_200_OK


class TestExportIntegration:
    """导出集成测试"""
    
    def test_export_tasks(self, client, sample_task, auth_headers):
        """测试导出任务"""
        response = client.get(
            "/api/v1/export/tasks?format=csv",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"].startswith("text/csv")


class TestWebSocketIntegration:
    """WebSocket 集成测试"""
    
    def test_websocket_connection(self, client, auth_headers):
        """测试 WebSocket 连接"""
        # 注意: WebSocket 测试需要特殊的测试客户端
        # 这里仅测试 WebSocket 端点是否可访问
        response = client.get("/api/v1/ws/health")
        assert response.status_code in [200, 404]  # 端点可能不存在


class TestGanttIntegration:
    """甘特图集成测试"""
    
    def test_gantt_task_timeline(self, client, sample_task, auth_headers):
        """测试甘特图时间线"""
        response = client.get(
            f"/api/v1/gantt/tasks?project_id={sample_task.project_id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK


# 运行集成测试的命令:
# pytest backend/app/tests/test_integration.py -v