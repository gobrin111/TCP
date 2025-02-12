class Request:
    def __init__(self, request: bytes):
        # TODO: parse the bytes of the request and populate the following instance variables

        self.body = b""
        self.method = ""
        self.path = ""
        self.http_version = ""
        self.headers = {}
        self.cookies = {}
        self.header_size = 0
        splitter = '\r\n\r\n'
        splitter = splitter.encode('utf-8')
        # decodes the request to a string
        headerBody = request.split(splitter, 1)
        self.header_size = len(headerBody[0]+b"\r\n\r\n")
        # real_body = request.split(headerBody[0]+splitter)[1]
        # self.body = real_body
        self.body = headerBody[1]

        allheaders = headerBody[0]
        allheaders = allheaders.decode('utf-8')
        allheaders = allheaders.split('\r\n') #array of all the headers
        method2version = allheaders[0]
        method2version = method2version.split(' ') #array of method, path, http_version
        # stores the method, path, and http_version
        self.method = method2version[0]
        self.path = method2version[1]
        self.http_version = method2version[2]
        allheaders = allheaders[1:len(allheaders)]
        # print(allheaders)
        for keyvalue in allheaders:
            temp = keyvalue.split(' ', 1)
            key = temp[0][0:len(temp[0])-1]
            value = temp[1]
            if key != 'Cookie':
                self.headers[key] = value
            else:
                self.headers[key] = keyvalue[8:len(keyvalue)]
                temp = keyvalue.split(' ')
                for cookiePair in temp[1:len(temp)]:
                    cookieTemp = cookiePair.split('=')
                    cookieKey = cookieTemp[0]
                    cookieValue = cookieTemp[1]
                    if cookieValue[len(cookieValue) - 1] == ';':
                        cookieValue = cookieValue[0:len(cookieValue)-1]
                    # print(cookieKey, cookieValue)
                    self.cookies[cookieKey] = cookieValue
        # print(self.headers["Content-Length"])



def test1():
    request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nCookie: session_id=abc123; theme=light; cart=3\r\n\r\n')
    assert request.method == "GET"
    assert "Host" in request.headers
    assert request.headers["Host"] == "localhost:8080"  # note: The leading space in the header value must be removed
    assert request.body == b""  # There is no body for this request.
    # When parsing POST requests, the body must be in bytes, not str
    assert "Cookie" in request.headers
    assert request.headers["Cookie"] == "session_id=abc123; theme=light; cart=3"
    assert "session_id" in request.cookies
    assert "theme" in request.cookies
    assert "cart" in request.cookies
    assert request.cookies["cart"] == "3"
    assert request.cookies["session_id"] == "abc123"
    assert request.cookies["theme"] == "light"
    # This is the start of a simple way (ie. no external libraries) to test your code.
    # It's recommended that you complete this test and add others, including at least one
    # test using a POST request. Also, ensure that the types of all values are correct
    # assert request.headers["Cookie"] == "session_id=abc123; theme=light; cart=3"

if __name__ == '__main__':
    test1()
    # response_headers = [
    #     "HTTP/1.1 200 OK",
    #     "Content-Type: text/css; charset=utf-8",
    #     f"Content-Length: 8",
    #     "X-Content-Type-Options: nosniff",
    #     "\r\n"
    # ]
    # request = Request(b"POST /form-path HTTP/1.1\r\nContent-Length: 9937\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundarycriD3u6M0UuPR1ia\r\n\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia\r\nContent-Disposition: form-data; name='commenter'\r\n\r\nJesse\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia--")
    # print(request.headers["Content-Type"])
    # print(request.body)