"""
任务管理模块测试
"""
import pytest
from fastapi import status


class TestTasks:
    """任务管理测试类"""
    
    def test_create_task(self, client, sample_project, auth_headers):
        """测试创建任务"""
        response = client.post(
            "/api/v1/tasks/",
            json={
                "title": "New Task",
                "description": "Task description",
                "project_id": sample_project.id,
                "priority": "high",
                "status": "todo"
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "New Task"
        assert data["project_id"] == sample_project.id
    
    def test_get_tasks(self, client, sample_task, auth_headers):
        """测试获取任务列表"""
        response = client.get(
            "/api/v1/tasks/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_task_by_id(self, client, sample_task, auth_headers):
        """测试获取单个任务"""
        response = client.get(
            f"/api/v1/tasks/{sample_task.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_task.id
        assert data["title"] == sample_task.title
    
    def test_update_task(self, client, sample_task, auth_headers):
        """测试更新任务"""
        response = client.put(
            f"/api/v1/tasks/{sample_task.id}",
            json={
                "title": "Updated Task",
                "status": "in_progress",
                "progress": 50
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["status"] == "in_progress"
        assert data["progress"] == 50
    
    def test_delete_task(self, client, sample_task, auth_headers):
        """测试删除任务"""
        response = client.delete(
            f"/api/v1/tasks/{sample_task.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        # 验证任务已被删除
        response = client.get(
            f"/api/v1/tasks/{sample_task.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_filter_tasks_by_status(self, client, sample_task, auth_headers):
        """测试按状态筛选任务"""
        response = client.get(
            "/api/v1/tasks/?status=todo",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(task["status"] == "todo" for task in data)
    
    def test_filter_tasks_by_project(self, client, sample_task, auth_headers):
        """测试按项目筛选任务"""
        response = client.get(
            f"/api/v1/tasks/?project_id={sample_task.project_id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(task["project_id"] == sample_task.project_id for task in data)
    
    def test_task_not_found(self, client, auth_headers):
        """测试任务不存在"""
        response = client.get(
            "/api/v1/tasks/99999",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_task_without_auth(self, client, sample_project):
        """测试无认证创建任务"""
        response = client.post(
            "/api/v1/tasks/",
            json={
                "title": "New Task",
                "project_id": sample_project.id
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTaskComments:
    """任务评论测试类"""
    
    def test_add_comment(self, client, sample_task, auth_headers):
        """测试添加评论"""
        response = client.post(
            f"/api/v1/tasks/{sample_task.id}/comments",
            json={"content": "This is a comment"},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["content"] == "This is a comment"
    
    def test_get_comments(self, client, sample_task, auth_headers):
        """测试获取评论列表"""
        # 先添加评论
        client.post(
            f"/api/v1/tasks/{sample_task.id}/comments",
            json={"content": "Test comment"},
            headers=auth_headers
        )
        
        # 获取评论
        response = client.get(
            f"/api/v1/tasks/{sample_task.id}/comments",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0