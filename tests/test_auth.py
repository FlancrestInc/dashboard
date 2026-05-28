import os

from fastapi.testclient import TestClient

from app.main import app


def test_admin_login_accepts_surrounding_whitespace():
    client = TestClient(app)
    password = os.getenv("ADMIN_PASSWORD", "change-this-password")

    response = client.post(
        "/admin/login",
        data={"password": f" {password}\n"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/admin"
