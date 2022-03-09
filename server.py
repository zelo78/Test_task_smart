from http.server import HTTPServer, BaseHTTPRequestHandler
import http.client
import json
from threading import Lock


DB = []
db_lock = Lock()


class Task:
    def __init__(self, type_code, string):
        self.type_code = type_code
        self.string = string
        self.state = 'pending'
        self.result = None

    def __str__(self):
        return f'Task: type {self.type_code}, string {self.string}, state {self.state}, result {self.result}'


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):  # noqa
        content_length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(content_length))
        identifier = data['id']
        with db_lock:
            if 0 <= identifier < len(DB):
                task = DB[identifier]
            else:
                task = None

        if task is None:
            self.send_response(http.client.NOT_FOUND)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
        else:
            data = {
                'status': task.state,
                'result' : task.result,
            }
            self.send_response(http.client.OK)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_POST(self):  # noqa
        content_length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(content_length))
        task = Task(type_code=data['task_type'], string=data['string'])
        with db_lock:
            DB.append(task)
            identifier = len(DB) - 1

        print(f'{task} was added as #{identifier}')
        data = {'id': identifier}
        self.send_response(http.client.CREATED)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))


httpd = HTTPServer(('localhost', 8000), RequestHandler)
httpd.serve_forever()

# if __name__ == "__main__":
#     main()
