import os
import pytest


@pytest.fixture()
def app():
    os.environ.update({
        "SQLALCHEMY_DATABASE_URI": "mysql+pymysql://movienotes:REDACTED@localhost/MovieDb",
        "CHROMADB_URI": "http://localhost:8000",
        "JWT_SECRET_KEY": "v3ry_s3cr3t_k3y"
    })

    from app import app

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_request_register_user(client):
    response = client.post('/register_user', json={
        "name": "John Tat",
        "email": "john.tat@etu.unige.ch",
        "password": "12345678"})
    assert response.status_code == 200
    response = client.post('/login', json={
        "email": "john.tat@etu.unige.ch",
        "password": "12345678",
    })
    assert  response.status_code == 200
    assert 'token' in response.json
    assert 'user_id' in response.json
