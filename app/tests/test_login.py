import pytest
from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token
from flask.testing import FlaskClient

from app import create_app as app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_login_success(client: FlaskClient):
    """
    Test case for successful login with correct credentials
    """
    response = client.post('/login', json={
        'username': 'admin',
        'password': 'password'
    })
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'access_token' in json_data

def test_login_failure_invalid_username(client: FlaskClient):
    """
    Test case for login failure due to incorrect username
    """
    response = client.post('/login', json={
        'username': 'wronguser',
        'password': 'password'
    })
    
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['msg'] == 'Bad username or password'

def test_login_failure_invalid_password(client: FlaskClient):
    """
    Test case for login failure due to incorrect password
    """
    response = client.post('/login', json={
        'username': 'admin',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['msg'] == 'Bad username or password'

def test_login_missing_username(client: FlaskClient):
    """
    Test case for login failure due to missing username in payload
    """
    response = client.post('/login', json={
        'password': 'password'
    })
    
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['msg'] == 'Bad username or password'

def test_login_missing_password(client: FlaskClient):
    """
    Test case for login failure due to missing password in payload
    """
    response = client.post('/login', json={
        'username': 'admin'
    })
    
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['msg'] == 'Bad username or password'

def test_login_empty_payload(client: FlaskClient):
    """
    Test case for login failure due to empty JSON payload
    """
    response = client.post('/login', json={})
    
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['msg'] == 'Bad username or password'

def test_login_no_json_payload(client: FlaskClient):
    """
    Test case for login failure due to missing JSON payload (i.e., no body data)
    """
    response = client.post('/login')
    
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['msg'] == 'Bad username or password'
