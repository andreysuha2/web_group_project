
from cgitb import text
import json

token = ""
refresh_token = ""


def test_signup(client, user):
    response = client.post(
        "/api/users/",
        json=user )
    assert response.status_code == 200, response.text


def test_signup_exist_user(client, user):
    response = client.post(
        "/api/users/",
        json=user )
    assert response.status_code == 409, response.text


def test_signup_wrong_email(client, user):
    response = client.post(
        "/api/users/",
        json={
            "username": "userna32me",
            "email": "usexample.com",
            "password": "string"
    } )
    assert response.status_code == 422, response.text


def test_login(client, user, session):
    response = client.post(
        "/api/session/",
        data= user)
    assert response.status_code == 200, response.text
    data = response.json()
    token = data["access_token"]
    refresh_token = data["refresh_token"]
    assert refresh_token != None
    assert token != None


def test_login_no_user(client, user, session):
    response = client.post(
        "/api/session/",
        data= { "username": "userwena32me",
                "email": "usexa@pedgle.com",
                "password": "string" } )
    assert response.status_code == 401


def test_users_all(client, user, session):
    response = client.get(
        "/api/users/all/",
        headers={
        "Authorization" : f"Bearer {token}" }
        )
    assert response.status_code == 200, response.text


# def test_refresh_token(client, user, session):
#     response = client.put(
#         "/api/session/",
#         headers={
#         "Authorization" : f"Bearer {refresh_token}" }
#         )
#     assert response.status_code == 200, response.text
#     data = response.json()
#     token = data["access_token"]
#     refresh_token = data["refresh_token"]
#     assert refresh_token != None
#     assert token != None


def test_users_id(client, user, session):
    response = client.get(
        "/api/users/1/",
        headers={
        "Authorization" : f"Bearer {token}" }
        )
    assert response.status_code == 200, response.text


def test_users_wrong_name(client, user, session):
    response = client.get(
        "/api/users/string/",
        headers={
        "Authorization" : f"Bearer {token}" }
        )
    assert response.status_code == 404, response.text


def test_users_name(client, user, session):
    response = client.get(
        "/api/users/username/",
        headers={
        "Authorization" : f"Bearer {token}" }
        )
    assert response.status_code == 200, response.text


def test_users_read_self_profile(client, user, session):
    response = client.get(
        "/api/profile/",
        headers={
        "Authorization" : f"Bearer {token}" }
        )
    assert response.status_code == 200, response.text
    result = response.json()
    assert result.get("username") == user.get("username")
    assert result.get("email") == user.get("email")



