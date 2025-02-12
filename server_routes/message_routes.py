import json
import html
import hashlib

from bson import ObjectId
from pymongo import MongoClient

mongo_client = MongoClient("mongo")
db = mongo_client["cse312"]
chat_collection = db["chat"]
user_info_collection = db["user_info"]


def post_message(request, handler):
    message = json.loads(request.body)
    browser_token = str(message["browser_token"])
    message = str(message["message"])
    message = html.escape(message)
    username = "Guest"
    current_token = None
    response_headers = [
        "HTTP/1.1 200 OK",
        "Content-Type: application/json",
        "X-Content-Type-Options: nosniff",
        "Content-Length:0",
        "\r\n"
    ]
    flag = True
    # stores the username and token of the account with the message in the db
    if "token" in request.cookies:
        # print(browser_token)
        current_token = request.cookies["token"].encode("utf-8")
        current_token = hashlib.sha256(current_token).hexdigest()
        if user_info_collection.find_one({"token": current_token}) is not None:
            username = user_info_collection.find_one({"token": current_token})["username"]
            # print("final")
            # print(user_info_collection.find_one({"token": current_token}))
            if user_info_collection.find_one({"token": current_token})["xsrf_token"] != browser_token:
                response_headers = [
                    "HTTP/1.1 403 Forbidden",
                    "Content-Type: application/json",
                    "X-Content-Type-Options: nosniff",
                    "\r\n"
                ]
                flag = False
    if flag:
        chat_collection.insert_one({"username": username, "message": message, "userId": request.cookies["userId"]})

    # chat_collection.insert_one({"username": username, "message": message, "userId": request.cookies["userId"]})

    response_headers = "\r\n".join(response_headers).encode("utf-8")
    handler.request.sendall(response_headers)


def get_message(request, handler):
    message_history = chat_collection.find({})
    message_display = []
    for message in message_history:
        background_color = 'transparent'
        if "token" in request.cookies:
            if user_info_collection.find_one(
                    {"token": hashlib.sha256(request.cookies["token"].encode("utf-8")).hexdigest()}) is not None:
                if user_info_collection.find_one(
                        {"token": hashlib.sha256(request.cookies["token"].encode("utf-8")).hexdigest()})["username"] == \
                        message["username"]:
                    background_color = 'black'
        if message["userId"] == request.cookies["userId"]:
            background_color = 'black'
        message_display.append({
            "message": message["message"],
            "username": message["username"],
            "id": str(message["_id"]),
            "userId": message["userId"],
            "currentId": request.cookies["userId"],
            "color": background_color
        })

    message_display = json.dumps(message_display)
    message_display = message_display.encode("utf-8")

    response_headers = [
        "HTTP/1.1 200 OK",
        "Content-Type: application/json",
        "Content-Length: " + str(len(message_display)),
        "X-Content-Type-Options: nosniff",
        "\r\n"
    ]
    response_headers = "\r\n".join(response_headers).encode("utf-8")
    handler.request.sendall(response_headers + message_display)


def delete_message(request, handler):
    request_path = request.path
    message_id = ObjectId(request_path[15:len(request_path)])
    message = chat_collection.find_one({"_id": message_id})
    response_headers = [
        "HTTP/1.1 204 No Content",
        "X-Content-Type-Options: nosniff",
        "Content-Length:0",
        "\r\n"
    ]
    rejection = [
        "HTTP/1.1 403 Forbidden",
        "X-Content-Type-Options: nosniff",
        "Content-Length:0",
        "\r\n"
    ]
    if message["username"] == "Guest":
        if "token" in request.cookies:
            if request.cookies["token"] == "tokenLessBehavior":
                chat_collection.delete_one({"_id": message_id})
            else:
                response_headers = rejection
        else:
            chat_collection.delete_one({"_id": message_id})
    else:
        if request.cookies["token"] is not None:
            matched_token_account = user_info_collection.find_one(
                {"token": hashlib.sha256(request.cookies["token"].encode("utf-8")).hexdigest()})
            if matched_token_account is not None:
                if matched_token_account["username"] == message["username"]:
                    chat_collection.delete_one({"_id": message_id})
                else:
                    response_headers = rejection
            else:
                response_headers = rejection
        else:
            response_headers = rejection
    response_headers = "\r\n".join(response_headers)
    handler.request.sendall(response_headers.encode("utf-8"))
