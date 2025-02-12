class Router:

    def __init__(self):
        self.routes = []

    def add_route(self, method, path, action, exact_path=False):
        dict = {
            'method': method,
            'path': path,
            'action': action,
            'exact_path': exact_path
        }
        self.routes.append(dict)

    def route_request(self, request, handler):
        for route in self.routes:
            if route['method'] == request.method:
                if route['exact_path']:  # if there needs to be exact path match
                    if route['path'] == request.path:
                        route['action'](request, handler)
                        return
                else:  # if exact_path is false, then only the beginning needs to match
                    # check that the beginning of route path matches with the request
                    if route['path'] == request.path[0:len(route['path'])]:
                        route['action'](request, handler)
                        return

        # if nothing gets processed then
        handler.request.sendall(b"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain; charset=utf-8;\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 13\r\n\r\n404 Not Found")
