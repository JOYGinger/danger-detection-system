import os

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.services import history as history_service
from app.utils.crypto import generate_key

_TEST_KEY = generate_key()
_TEST_ENGINE = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
_TestSession = sessionmaker(autocommit=False, autoflush=False, bind=_TEST_ENGINE)


def _override_get_db():
    db = _TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_db():
    os.environ["ENCRYPTION_KEY"] = _TEST_KEY
    history_service._encryptor = None
    Base.metadata.create_all(bind=_TEST_ENGINE)
    app.dependency_overrides[get_db] = _override_get_db
    yield
    Base.metadata.drop_all(bind=_TEST_ENGINE)
    app.dependency_overrides.clear()
    if "ENCRYPTION_KEY" in os.environ:
        del os.environ["ENCRYPTION_KEY"]
    history_service._encryptor = None


@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_openapi_docs():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_openapi_json():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["info"]["title"] == "危险检测集成系统"
    assert "/health" in data["paths"]


@pytest.mark.asyncio
async def test_detect_sensitive_info():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/detect/text",
            json={
                "content": "密码：sk-proj-abc123def456ghi789jkl password=admin123",
                "detection_type": "sensitive_info",
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["result"]["type"] == "sensitive_info"
    assert data["result"]["risk_level"] == "high"
    assert data["result"]["details"]["count"] >= 2


@pytest.mark.asyncio
async def test_detect_all_types():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/detect/text",
            json={"content": "sk-proj-abc123def456ghi789jkl"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["results"] is not None
    assert "sensitive_info" in data["results"]
    assert "weak_password" in data["results"]


@pytest.mark.asyncio
async def test_detect_weak_password():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/detect/text",
            json={
                "content": "password123",
                "detection_type": "weak_password",
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["result"]["type"] == "weak_password"
    assert data["result"]["risk_level"] == "high"
    assert data["result"]["details"]["score"] <= 1


@pytest.mark.asyncio
async def test_detect_weak_password_strong():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/detect/text",
            json={
                "content": "Tr0ub4dor&3App!",
                "detection_type": "weak_password",
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["result"]["risk_level"] == "low"
    assert data["result"]["details"]["score"] >= 3


@pytest.mark.asyncio
async def test_detect_no_sensitive_info():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/detect/text",
            json={
                "content": "这是一段普通文本",
                "detection_type": "sensitive_info",
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["result"]["risk_level"] == "safe"


@pytest.mark.asyncio
async def test_detect_empty_content():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/detect/text",
            json={"content": ""},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_detect_invalid_type():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/detect/text",
            json={"content": "test", "detection_type": "invalid"},
        )
    assert response.status_code == 422


# --- 历史记录API测试 ---


@pytest.mark.asyncio
async def test_history_list_empty():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_history_after_detect():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/api/detect/text",
            json={
                "content": "sk-proj-abc123def456ghi789jkl",
                "detection_type": "sensitive_info",
            },
        )
        response = await client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    item = data["items"][0]
    assert item["detection_type"] == "sensitive_info"
    assert "input_content" not in item


@pytest.mark.asyncio
async def test_history_detail():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/api/detect/text",
            json={
                "content": "test content for detail",
                "detection_type": "sensitive_info",
            },
        )
        list_resp = await client.get("/api/history")
        record_id = list_resp.json()["items"][0]["id"]
        detail_resp = await client.get(f"/api/history/{record_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["input_content"] == "test content for detail"
    assert detail["detection_type"] == "sensitive_info"
    assert "result_detail" in detail


@pytest.mark.asyncio
async def test_history_detail_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/history/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_history_delete():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/api/detect/text",
            json={"content": "to be deleted", "detection_type": "sensitive_info"},
        )
        list_resp = await client.get("/api/history")
        record_id = list_resp.json()["items"][0]["id"]
        del_resp = await client.delete(f"/api/history/{record_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True


@pytest.mark.asyncio
async def test_history_delete_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete("/api/history/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_history_clear():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/api/detect/text",
            json={"content": "record 1", "detection_type": "sensitive_info"},
        )
        await client.post(
            "/api/detect/text",
            json={"content": "record 2"},
        )
        clear_resp = await client.delete("/api/history")
    assert clear_resp.status_code == 200
    assert clear_resp.json()["success"] is True
    assert clear_resp.json()["deleted_count"] >= 2


@pytest.mark.asyncio
async def test_history_pagination():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for i in range(5):
            await client.post(
                "/api/detect/text",
                json={"content": f"pagination test {i}", "detection_type": "sensitive_info"},
            )
        resp = await client.get("/api/history", params={"page": 1, "page_size": 3})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 3
    assert data["page_size"] == 3
