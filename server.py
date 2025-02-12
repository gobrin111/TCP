import socketserver
from collections import defaultdict

from bson import ObjectId
from pymongo import MongoClient
import html

from util.websockets import *
from server_routes.rtc_functions import *
from server_routes.media_upload import *
from server_routes.send_files import *
from server_routes.message_routes import *
from server_routes.auth_routes import *
from util.request import Request
from util.router import Router
from util.hello_path import hello_path
import json
import uuid
from util.auth import extract_credentials
from util.auth import validate_password
import bcrypt
import hashlib
import requests
import base64
import os
from util.multipart import parse_multipart
from PIL import Image, ImageSequence
import ffmpeg

mongo_client = MongoClient("mongo")
db = mongo_client["cse312"]
chat_collection = db["chat"]
user_info_collection = db["user_info"]

# mongo_client.drop_database("cse312")



class MyTCPHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        self.router = Router()
        self.router.add_route("GET", "/util/hello_path.py", hello_path, True)
        # TODO: Add your routes here
        self.router.add_route("GET", "/public/functions.js", send_js, True)
        self.router.add_route("GET", "/public/webrtc.js", send_webJS, True)
        self.router.add_route("GET", "/", send_html, True)
        self.router.add_route("GET", "/public/style.css", send_css, True)
        self.router.add_route("GET", "/public/image/", send_img, False)
        self.router.add_route("GET", "/public/favicon.ico", send_icon, True)

        self.router.add_route("POST", "/chat-messages", post_message, False)
        self.router.add_route("GET", "/chat-messages", get_message, False)
        self.router.add_route("DELETE", "/chat-messages/", delete_message, False)

        self.router.add_route("POST", "/register", user_register, True)
        self.router.add_route("POST", "/login", user_login, True)
        self.router.add_route("POST", "/logout", user_logout, True)

        self.router.add_route("GET", "/spotify-login", spotify_login, False)
        self.router.add_route("GET", "/spotify", spotify, False)  # callback with the auth code

        self.router.add_route("POST", "/media-uploads", media_upload, False)

        self.router.add_route("GET", "/websocket", websocket, False)
        # history = chat_collection.find_one({})
        # for key, value in history.items():
        #     print(f"{key}: {value}", flush=True)
        # self.router.add_route("GET", "/chat-messages",get_message, False)
        super().__init__(request, client_address, server)

    def handle(self):
        received_data = self.request.recv(2048)
        # # if (len(received_data) == 0):
        # #     print("No data received")
        # #     return
        print(self.client_address)
        print(f"{len(received_data)} bytes received")
        print("--- received data ---")
        print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)
        size = 0
        if "Content-Length" in request.headers:
            size = int(request.header_size) + int(request.headers["Content-Length"]) - len(received_data)
        else:
            size = int(request.header_size) - len(received_data)
        while size > 0:
            more_data = self.request.recv(2048)
            if len(more_data) == 0:
                break
            size -= len(more_data)
            received_data += more_data
        request = Request(received_data)

        self.router.route_request(request, self)


def main():
    host = "0.0.0.0"
    port = 8080
    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))
    server.serve_forever()


if __name__ == "__main__":
    main()
