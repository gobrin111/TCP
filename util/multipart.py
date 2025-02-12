from util.request import Request


class Multipart:
    def __init__(self):
        self.boundary = ""
        self.parts = []


class Part:
    def __init__(self):
        self.headers = {}
        self.name = ""
        self.content = b""


def parse_multipart(request: Request) -> Multipart:
    out = Multipart()
    size = int(request.headers.get('Content-Length'))
    boundary = request.headers["Content-Type"].split("boundary=")[1]
    out.boundary = boundary
    bounds = request.body.split(("--" + out.boundary + "\r\n").encode("utf-8"))
    i = 1

    for bound in bounds[1:len(bounds)]:
        headers_content = bound.split("\r\n\r\n".encode('utf-8'),1)
        part = Part()
        bound_headers = headers_content[0].decode("utf-8")
        content = headers_content[1]
        headers_arr = bound_headers.split("\r\n")

        for keyvalue in headers_arr:
            temp = keyvalue.split(': ')
            key = temp[0]
            value = temp[1]
            part.headers[key] = value
            if key == "Content-Disposition":
                temp = value.split("; ")
                for stuff in temp:
                    if stuff[0:4] == "name":
                        stuff = stuff.split("=")
                        part.name = stuff[1][1:len(stuff[1]) - 1]
                        break
        if i == len(bounds) - 1:
            content = content.rstrip("\r\n".encode('utf-8'))
            content = content.rstrip(("--" + out.boundary + "--").encode("utf-8"))
            content = content.rstrip("\r\n".encode('utf-8'))
        else:
            content = content.rstrip("\r\n".encode('utf-8'))
        part.content = content
        print(part.name)
        out.parts.append(part)
        i += 1
    return out


def test2():
    request = Request(
        b"POST /form-path HTTP/1.1\r\n"
        b"Content-Length: 9937\r\n"
        b"Content-Type: multipart/form-data; boundary=----WebKitFormBoundarycriD3u6M0UuPR1ia\r\n"
        b"\r\n"
        b"------WebKitFormBoundarycriD3u6M0UuPR1ia\r\n"
        b"Content-Disposition: form-data; name=\"commenter\"\r\n"
        b"\r\n"
        b"Jesse\r\n"
        b"------WebKitFormBoundarycriD3u6M0UuPR1ia\r\n"
        b"Content-Disposition: form-data; name=\"upload\"; filename=\"discord.png\"\r\n"
        b"Content-Type: image/png\r\n"
        b"\r\n"
        b"<bytes_of_\r\n\r\nthe_file>\r\n"
        b"------WebKitFormBoundarycriD3u6M0UuPR1ia--"
    )

    multipart_data = parse_multipart(request)
    assert multipart_data.boundary == "----WebKitFormBoundarycriD3u6M0UuPR1ia"
    print("=====================================")
    print(multipart_data.boundary)
    print("=====================================")
    for part in multipart_data.parts:
        print(part.headers)
        print(part.name)
        print(part.content)
        print("=====================================")


if __name__ == '__main__':
    # request = Request(b"POST /form-path HTTP/1.1\r\nContent-Length: 9937\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundarycriD3u6M0UuPR1ia\r\n\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia\r\nContent-Disposition: form-data; name='commenter'\r\n\r\nJesse\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia\r\nContent-Disposition: form-data; name='upload'; filename='discord.png'\r\nContent-Type: image/png\r\n\r\nwasd\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia--\r\n")
    # stuff = parse_multipart(request)
    # test2()
    # stuff = "----WebKitFormBoundarycriD3u6M0UuPR1ia"
    # temp = b"<bytes_of_\r\n\r\nthe_file>\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia--"
    # print(temp.rstrip("\r\n".encode('utf-8')).rstrip(("--" + stuff + "--").encode("utf-8")).rstrip("\r\n".encode('utf-8')))
    guess = b"12"
    print(len(guess))
