import json
import html

from pymongo import MongoClient
from util.websockets import *

mongo_client = MongoClient("mongo")
db = mongo_client["cse312"]
chat_collection = db["chat"]
user_info_collection = db["user_info"]
active_connections = {}


def receive_frame(handler):
    data = handler.request.recv(2)
    if not data:
        return None
    mask = (data[1] >> 7) & 0x01
    payload_length = 0
    if (data[1] & 0x7F) < 126:
        payload_length = data[1] & 0x7F
    elif (data[1] & 0x7F) == 126:
        data += handler.request.recv(2)
        payload_length = int.from_bytes(data[2:4], byteorder='big')
    else:
        data += handler.request.recv(8)
        payload_length = int.from_bytes(data[2:10], byteorder='big')
    print("before2")
    size = 0
    if payload_length <= 125:
        size = payload_length - (len(data) - 2)
    elif payload_length < 65536:
        size = payload_length - (len(data) - 4)
    else:
        size = payload_length - (len(data) - 10)
    if mask == 1:
        size += 4
    while size > 0:
        more_data = handler.request.recv(min(2048, size))
        if len(more_data) == 0:
            break
        size -= len(more_data)
        data += more_data
    print("number of bytes frame")
    print(len(data))
    frame = parse_ws_frame(data)
    return frame


def websocket(request, handler):
    accept_response = compute_accept(request.headers.get('Sec-WebSocket-Key'))
    response_headers = [
        "HTTP/1.1 101 Switching Protocols",
        "Content-Length:0",
        "Connection: Upgrade",
        f"Sec-WebSocket-Accept: {accept_response}",
        "Upgrade: websocket",
        "X-Content-Type-Options: nosniff",
        "\r\n"
    ]
    username = "Guest"
    if "token" in request.cookies:
        current_token = request.cookies["token"].encode("utf-8")
        current_token = hashlib.sha256(current_token).hexdigest()
        if user_info_collection.find_one({"token": current_token}) is not None:
            username = user_info_collection.find_one({"token": current_token})["username"]
    response_headers = "\r\n".join(response_headers).encode("utf-8")
    handler.request.sendall(response_headers)
    active_connections[id(handler)] = handler
    while True:
        frame = receive_frame(handler)
        if frame is None:
            print("None frame was sent")
            del active_connections[id(handler)]
            break
        # disconnects user by removing them from the active user list and closing the socket
        if frame.opcode == 8:
            del active_connections[id(handler)]
            break
        # parses the continous frames into one big payload
        message_data = frame.payload
        # if frame.fin_bit == 0 and frame.opcode == 1:
        if frame.fin_bit == 0:
            next_frame = receive_frame(handler)
            while next_frame.fin_bit != 1:
                message_data += next_frame.payload
                next_frame = receive_frame(handler)
            message_data += next_frame.payload
        # checks to see what messagetype is the payload
        message_payload = json.loads(message_data)
        messageType = message_payload['messageType']
        if messageType == 'chatMessage':
            message = html.escape(message_payload['message'])
            chat_collection.insert_one({"username": username, "message": message, "userId": request.cookies["userId"]})
            response = {
                'messageType': 'chatMessage',
                'username': username,
                'message': message,
                'id': str(chat_collection.find_one({"username": username, "message": message})["_id"])
            }
            response_frame = generate_ws_frame(json.dumps(response).encode())
            broadcast_message(response_frame)
        elif messageType[0:6] == 'webRTC':
            response_frame = generate_ws_frame(message_data)
            RTC_broadcast(response_frame, handler)


def RTC_broadcast(frame, current_handler):
    for conn_id in active_connections.keys():
        if conn_id != id(current_handler):
            active_connections[conn_id].request.sendall(frame)

def broadcast_message(response):
    for conn_id in active_connections.keys():
        current_handler = active_connections[conn_id]
        current_handler.request.sendall(response)