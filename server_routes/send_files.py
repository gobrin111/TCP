import hashlib
import uuid

from pymongo import MongoClient

mongo_client = MongoClient("mongo")
db = mongo_client["cse312"]
chat_collection = db["chat"]
user_info_collection = db["user_info"]


def send_html(request, handler):
    new_xsrf = str(uuid.uuid4())
    with open("public/index.html", "rb") as f:
        html_file = f.read()
    html_file = html_file.decode("utf-8")
    if 'visits' in request.cookies:
        cookieCount = int(request.cookies["visits"]) + 1
        userId = request.cookies["userId"]
    else:
        cookieCount = 1
        userId = str(uuid.uuid4())
    cookieCount = str(cookieCount)
    # print(cookieCount)
    if "token" in request.cookies:
        user_account = user_info_collection.find_one(
            {"token": hashlib.sha256(request.cookies["token"].encode("utf-8")).hexdigest()})
        if user_account is not None:
            user_info_collection.update_one(
                {"token": hashlib.sha256(request.cookies["token"].encode('utf-8')).hexdigest()},
                {"$set": {"xsrf_token": new_xsrf}})
    html_file = html_file.replace('token-placeholder', new_xsrf)
    html_file = html_file.replace('{{visits}}', cookieCount)
    html_file = html_file.encode("utf-8")
    content_length = len(html_file)
    response_headers = [
        "HTTP/1.1 200 OK",
        "Content-Type: text/html; charset=utf-8",
        f"Content-Length: {content_length}",
        "X-Content-Type-Options: nosniff",
        f"Set-Cookie: visits ={cookieCount}; Max-Age=3600",
        f"Set-Cookie: userId={userId}; Max-Age=3600",
        "\r\n"
    ]
    response_headers = "\r\n".join(response_headers).encode("utf-8")
    handler.request.sendall(response_headers + html_file)


def send_css(request, handler):
    with open("public/style.css", "rb") as f:
        css_file = f.read()
    content_length = len(css_file)
    response_headers = [
        "HTTP/1.1 200 OK",
        "Content-Type: text/css; charset=utf-8",
        f"Content-Length: {content_length}",
        "X-Content-Type-Options: nosniff",
        "\r\n"
    ]
    response_headers = "\r\n".join(response_headers).encode("utf-8")
    handler.request.sendall(response_headers + css_file)


def send_img(request, handler):
    request_path = request.path
    # request_path = request_path[1:len(request_path)]
    i = request_path.find("public/image/")
    for char in request_path[i+13:]:
        if char == "/":
            response_headers = [
                "HTTP/1.1 403 Forbidden",
                "X-Content-Type-Options: nosniff",
                "Content-Length:0",
                "\r\n"
            ]
            response_headers = "\r\n".join(response_headers).encode("utf-8")
            handler.request.sendall(response_headers)
            return

    # jpg = b"\xff\xd8\xff"
    # png = b"\x89\x50\x4e"
    # gif1 = b"\x47\x49\x46\x38\x37\x61"
    # gif2 = b"\x47\x49\x46\x38\x39\x61"
    # mp41 = b"\x66\x74\x79\x70\x69"
    # mp42 = b"\x66\x74\x79\x70\x4d"
    # mp43 = b"\x00\x00\x00\x18"
    mimetype = "no"
    with open(f"/root/{request_path}", "rb") as f:
        content = f.read()
    # if content[0:len(jpg)] == jpg:
    #     mimetype = "image/jpeg"
    # elif content[0:len(png)] == png:
    #     mimetype = "image/png"
    # elif content[0:len(gif1)] == gif1 or content[0:len(gif2)] == gif2:
    #     mimetype = "image/gif"
    # elif content[0:len(mp41)] == mp41 or content[0:len(mp42)] == mp42 or content[0:len(mp43)] == mp43:
    #     mimetype = "video/mp4"

    if request_path[len(request_path) - 4:] == ".jpg" or request_path[len(request_path)-5:] == ".jpeg":
        mimetype = "image/jpeg"
    elif request_path[len(request_path) - 4:] == ".png":
        mimetype = "image/png"
    elif request_path[len(request_path)-4:] == ".gif":
        mimetype = "image/gif"
    elif request_path[len(request_path)-4:] == ".mp4":
        mimetype = "video/mp4"
    response_headers = [
        "HTTP/1.1 200 OK",
        f"Content-Type: {mimetype}",
        f"Content-Length: {len(content)}",
        "X-Content-Type-Options: nosniff",
        "\r\n"
    ]
    response_headers = "\r\n".join(response_headers).encode("utf-8")
    handler.request.sendall(response_headers + content)


def send_icon(request, handler):
    with open("public/favicon.ico", "rb") as f:
        icon_file = f.read()
    content_length = len(icon_file)
    response_headers = [
        "HTTP/1.1 200 OK",
        "Content-Type: image/vnd.microsoft.icon",
        f"Content-Length: {content_length}",
        "X-Content-Type-Options: nosniff",
        "\r\n"
    ]
    response_headers = "\r\n".join(response_headers).encode("utf-8")
    handler.request.sendall(response_headers + icon_file)


def send_js(request, handler):
    with open("public/functions.js", "rb") as f:
        js_file = f.read()
    content_length = len(js_file)
    response_headers = [
        "HTTP/1.1 200 OK",
        "Content-Type: text/javascript; charset=utf-8",
        f"Content-Length: {content_length}",
        "X-Content-Type-Options: nosniff",
        "\r\n"
    ]
    response_headers = "\r\n".join(response_headers).encode("utf-8")
    handler.request.sendall(response_headers + js_file)


def send_webJS(request, handler):
    with open("public/webrtc.js", "rb") as f:
        js_file = f.read()
    content_length = len(js_file)
    response_headers = [
        "HTTP/1.1 200 OK",
        "Content-Type: text/javascript; charset=utf-8",
        f"Content-Length: {content_length}",
        "X-Content-Type-Options: nosniff",
        "\r\n"
    ]
    response_headers = "\r\n".join(response_headers).encode("utf-8")
    handler.request.sendall(response_headers + js_file)
