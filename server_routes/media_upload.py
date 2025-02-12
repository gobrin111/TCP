import hashlib
import os
import uuid

import ffmpeg
from PIL import Image, ImageSequence
from pymongo import MongoClient

from util.multipart import parse_multipart

mongo_client = MongoClient("mongo")
db = mongo_client["cse312"]
chat_collection = db["chat"]
user_info_collection = db["user_info"]
def media_upload_resize(media_path, if_video, if_gif):
    max_size = (240, 240)

    if if_video:
        i = media_path.find("public/image/")
        filename = media_path[i + 13:]
        video_data = ffmpeg.probe(media_path)
        stream = next((stream for stream in video_data['streams'] if stream['codec_type'] == 'video'), None)
        width = int(stream['width'])
        height = int(stream['height'])

        other_path = os.path.abspath(f"public/image/resized_{filename}")
        # ffmpeg.input(media_path).filter('scale', max_size[0], max_size[1]).output(other_path, acodec='copy').run()
        # print("gaydar")
        ratio = min(240 / width, 240 / height)
        width = int(width * ratio)
        height = int(height * ratio)
        if width % 2 == 1:
            width -= 1
        if height % 2 == 1:
            height -= 1
        ffmpeg.input(media_path).output(other_path, acodec='copy', **{'vf': f'scale={width}:{height}', 'c:a': 'copy', 'c:s': 'copy'}).run()
    else:
        with Image.open(media_path) as img:
            if if_gif:
                frames = []
                for frame in ImageSequence.Iterator(img):
                    # Resize the frame to max_size while maintaining aspect ratio
                    frame = frame.copy()
                    frame.thumbnail(max_size)
                    frames.append(frame)
                frames[0].save(
                    media_path,
                    save_all=True,
                    append_images=frames[1:],
                    loop=0,
                    duration=100
                )
            else:
                img.thumbnail(max_size)
                img.save(media_path)


def media_upload(request, handler):
    multiPart = parse_multipart(request)
    username = "Guest"
    response_headers = [
        "HTTP/1.1 302 Found",
        "Content-Length:0",
        "X-Content-Type-Options: nosniff",
        "Location: /",
        "\r\n"
    ]
    # stores the username and token of the account with the message in the db
    if "token" in request.cookies:
        current_token = request.cookies["token"].encode("utf-8")
        current_token = hashlib.sha256(current_token).hexdigest()
        if user_info_collection.find_one({"token": current_token}) is not None:
            username = user_info_collection.find_one({"token": current_token})["username"]
    for part in multiPart.parts:
        # if "Content-Type" in part.headers:
        # if part.headers["Content-Type"] == "image/jpeg":
        #     image_content = part.content
        #     filename = f"{uuid.uuid4()}.jpeg"
        #     image_message = f"<img src=\"public/image/{filename}\">"
        #     print(image_message)
        #     path = os.path.abspath(f"public/image/{filename}")
        #     print(path)
        #     with open(path, "wb") as writer:
        #         writer.write(image_content)
        #     chat_collection.insert_one(
        #         {"username": username, "message": image_message, "userId": request.cookies["userId"]})
        if part.name == "upload":
            content = part.content
            jpg = b"\xff\xd8\xff"
            png = b"\x89\x50\x4e"
            gif1 = b"\x47\x49\x46\x38\x37\x61"
            gif2 = b"\x47\x49\x46\x38\x39\x61"
            mp41 = b"\x66\x74\x79\x70\x69"
            mp42 = b"\x66\x74\x79\x70\x4d"
            mp43 = b"\x00\x00\x00\x18"
            # mp44 = b"\x66\x74\x79\x70\x4D\x53\x4E\x56"
            filename = str(uuid.uuid4())
            message = f"<img src=\"public/image/{filename}\">"
            video = False
            gif = False
            if content[0:len(jpg)] == jpg:
                filename += ".jpeg"
                message = f"<img src=\"public/image/{filename}\">"
            elif content[0:len(png)] == png:
                filename += ".png"
                message = f"<img src=\"public/image/{filename}\">"
            elif content[0:len(gif1)] == gif1 or content[0:len(gif2)] == gif2:
                gif = True
                filename += ".gif"
                message = f"<img src=\"public/image/{filename}\">"
            else:
                video = True
                filename += ".mp4"
                message = f"<video  controls autoplay muted><source src=\"public/image/resized_{filename}\" type=\"video/mp4\"></video>"

            path = os.path.abspath(f"public/image/{filename}")
            with open(path, "wb") as writer:
                writer.write(content)
            media_upload_resize(path, video, gif)
            chat_collection.insert_one(
                {"username": username, "message": message, "userId": request.cookies["userId"]})

    response_headers = "\r\n".join(response_headers).encode("utf-8")
    handler.request.sendall(response_headers)