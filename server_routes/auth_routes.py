import base64
import hashlib
import os
import uuid

import requests
from pymongo import MongoClient

from util.auth import *

mongo_client = MongoClient("mongo")
db = mongo_client["cse312"]
chat_collection = db["chat"]
user_info_collection = db["user_info"]


def user_register(request, handler):
    info = extract_credentials(request)
    if validate_password(info[1]):
        encoded_password = info[1].encode("utf-8")
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(encoded_password, salt)
        user_info_collection.insert_one({"username": info[0], "password": hash, "token": None, "xsrf_token": None})
    response_headers = [
        "HTTP/1.1 302 Found",
        "Content-Length:0",
        "X-Content-Type-Options: nosniff",
        "Location: /",
        "\r\n"
    ]
    response_headers = "\r\n".join(response_headers)
    handler.request.sendall(response_headers.encode("utf-8"))


def user_login(request, handler):
    info = extract_credentials(request)
    input_password = info[1].encode("utf-8")
    user_account = user_info_collection.find_one({"username": info[0]})
    response_headers = [
        "HTTP/1.1 302 Found",
        "Content-Length:0",
        "X-Content-Type-Options: nosniff",
        "Location: /",
        "\r\n"
    ]
    if user_account is not None:
        if bcrypt.checkpw(input_password, user_account["password"]):
            token = str(uuid.uuid4())
            response_headers = [
                "HTTP/1.1 302 Found",
                "Content-Length:0",
                "X-Content-Type-Options: nosniff",
                "Location: /",
                f"Set-Cookie: token = {token}; Max-Age=3600; Secure; HttpOnly",
                "\r\n"
            ]
            token = token.encode("utf-8")
            token = hashlib.sha256(token).hexdigest()
            user_info_collection.update_one({"username": info[0]}, {"$set": {"token": token}})
    response_headers = "\r\n".join(response_headers)
    handler.request.sendall(response_headers.encode("utf-8"))


def user_logout(request, handler):
    response_headers = [
        "HTTP/1.1 302 Found",
        "Content-Length:0",
        "X-Content-Type-Options: nosniff",
        "Location: /",
        "\r\n"
    ]
    if "token" in request.cookies:
        user_info_collection.update_one({"token": hashlib.sha256(request.cookies["token"].encode('utf-8')).hexdigest()},
                                        {"$set": {"token": ""}})
        response_headers = [
            "HTTP/1.1 302 Found",
            "Content-Length:0",
            "X-Content-Type-Options: nosniff",
            "Location: /",
            "Set-Cookie: token=tokenLessBehavior; Expires=Tue, 11 Sep 1995 8:46 EST; Secure; HttpOnly",
            "\r\n"
        ]
    response_headers = "\r\n".join(response_headers)
    handler.request.sendall(response_headers.encode("utf-8"))


redirect_uri = "http://localhost:8080/spotify"
client_id = os.getenv("SPOTIFY_CLIENT_ID")  # change back to placeholder
client_secret = os.getenv("SPOTIFY_SECRET")  # change back to placeholder


def spotify_login(request, handler):
    scope = 'user-read-private user-read-email'
    auth_redirect = 'https://accounts.spotify.com/authorize?'
    queryString = {
        'response_type': 'code',
        'client_id': client_id,
        'scope': scope,
        'redirect_uri': redirect_uri
    }
    encoded_url = requests.Request('GET', auth_redirect, params=queryString).prepare().url
    response_headers = [
        "HTTP/1.1 302 Found",
        "Content-Length:0",
        "X-Content-Type-Options: nosniff",
        f"Location: {encoded_url}",
        "\r\n"
    ]
    response_headers = "\r\n".join(response_headers).encode("utf-8")
    handler.request.sendall(response_headers)


def spotify(request, handler):
    code = request.path.split('=')[1]
    credentials = f"{client_id}:{client_secret}"
    credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + credentials
    }
    data = {
        'code': code,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    response = requests.post(url, data=data, headers=headers)
    access_token = response.json()['access_token']
    endpoint = 'https://api.spotify.com/v1/me'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    data = requests.get(url=endpoint, headers=headers)
    username = data.json()['email']
    user_info_collection.insert_one(
        {"username": username, "token": hashlib.sha256(access_token.encode('utf-8')).hexdigest(), "xsrf_token": None})
    response_headers = [
        "HTTP/1.1 302 Found",
        "Content-Length:0",
        "X-Content-Type-Options: nosniff",
        "Location: /",
        f"Set-Cookie: token = {access_token}; Max-Age=3600; Secure; HttpOnly",
        "\r\n"
    ]
    response_headers = "\r\n".join(response_headers).encode("utf-8")
    handler.request.sendall(response_headers)
