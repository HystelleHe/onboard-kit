import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db

# 测试数据库URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """创建测试数据库"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """创建测试客户端"""
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(client):
    """创建测试用户"""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "company": "Test Company"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture(scope="function")
def auth_headers(client, test_user):
    """获取认证头"""
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_check(client):
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root(client):
    """测试根端点"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_register_user(client):
    """测试用户注册"""
    user_data = {
        "email": "newuser@example.com",
        "password": "password123",
        "full_name": "New User"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client, test_user):
    """测试重复邮箱注册"""
    user_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login(client, test_user):
    """测试用户登录"""
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    """测试错误密码登录"""
    login_data = {
        "username": "test@example.com",
        "password": "wrongpassword"
    }
    response = client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401


def test_get_current_user(client, auth_headers):
    """测试获取当前用户"""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_create_guide(client, auth_headers):
    """测试创建引导"""
    guide_data = {
        "name": "Test Guide",
        "description": "Test Description",
        "target_url": "https://example.com",
        "config": {},
        "steps": [
            {
                "order": 1,
                "title": "Step 1",
                "description": "First step",
                "element_selector": "#step1",
                "position": "bottom",
                "config": {}
            }
        ]
    }
    response = client.post("/api/v1/guides/", json=guide_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == guide_data["name"]
    assert len(data["steps"]) == 1
    assert "id" in data


def test_list_guides(client, auth_headers):
    """测试获取引导列表"""
    response = client.get("/api/v1/guides/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_guide(client, auth_headers):
    """测试获取单个引导"""
    # 先创建引导
    guide_data = {
        "name": "Test Guide",
        "target_url": "https://example.com",
        "config": {},
        "steps": []
    }
    create_response = client.post("/api/v1/guides/", json=guide_data, headers=auth_headers)
    guide_id = create_response.json()["id"]

    # 获取引导
    response = client.get(f"/api/v1/guides/{guide_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == guide_id
    assert data["name"] == guide_data["name"]


def test_update_guide(client, auth_headers):
    """测试更新引导"""
    # 先创建引导
    guide_data = {
        "name": "Original Name",
        "target_url": "https://example.com",
        "config": {},
        "steps": []
    }
    create_response = client.post("/api/v1/guides/", json=guide_data, headers=auth_headers)
    guide_id = create_response.json()["id"]

    # 更新引导
    update_data = {
        "name": "Updated Name",
        "is_published": True
    }
    response = client.put(f"/api/v1/guides/{guide_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["is_published"] is True


def test_delete_guide(client, auth_headers):
    """测试删除引导"""
    # 先创建引导
    guide_data = {
        "name": "To Delete",
        "target_url": "https://example.com",
        "config": {},
        "steps": []
    }
    create_response = client.post("/api/v1/guides/", json=guide_data, headers=auth_headers)
    guide_id = create_response.json()["id"]

    # 删除引导
    response = client.delete(f"/api/v1/guides/{guide_id}", headers=auth_headers)
    assert response.status_code == 204

    # 验证已删除
    get_response = client.get(f"/api/v1/guides/{guide_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_unauthorized_access(client):
    """测试未授权访问"""
    response = client.get("/api/v1/guides/")
    assert response.status_code == 401


def test_invalid_token(client):
    """测试无效token"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
