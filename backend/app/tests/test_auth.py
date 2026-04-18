"""
认证模块测试
"""
import pytest
from fastapi import status


class TestAuth:
    """认证测试类"""
    
    def test_register(self, client):
        """测试用户注册"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "newpass123",
                "full_name": "New User"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert "password" not in data  # 密码不应明文返回
    
    def test_register_duplicate_username(self, client, sample_user):
        """测试重复用户名注册"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",  # 已存在
                "email": "another@example.com",
                "password": "pass123"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_duplicate_email(self, client, sample_user):
        """测试重复邮箱注册"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "anotheruser",
                "email": "test@example.com",  # 已存在
                "password": "pass123"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_success(self, client, sample_user):
        """测试登录成功"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "testpass123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, sample_user):
        """测试错误密码登录"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, client):
        """测试不存在用户登录"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "password"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user(self, client, sample_user, auth_headers):
        """测试获取当前用户信息"""
        response = client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == sample_user.username
        assert data["email"] == sample_user.email
    
    def test_get_current_user_no_token(self, client):
        """测试无令牌获取用户信息"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_invalid_token(self, client):
        """测试无效令牌获取用户信息"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED