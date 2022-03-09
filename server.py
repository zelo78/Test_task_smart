from http.server import HTTPServer, BaseHTTPRequestHandler


DB = []


class Task:
    def __init__(self, type_code, string):
        self.type_code = type_code
        self.string = string
        self.state = 'pending'
        self.result = None


class RequestHandler(BaseHTTPRequestHandler):

    # определяем метод `do_GET`
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        print(body)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')


httpd = HTTPServer(('localhost', 8000), RequestHandler)
httpd.serve_forever()

# if __name__ == "__main__":
#     main()
