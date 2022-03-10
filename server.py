from http.server import HTTPServer, BaseHTTPRequestHandler
import http.client
import json
from threading import Lock, Thread
from time import sleep


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


def do_work(type_code, string):
    if type_code == 1:
        sleep(2)
        return string[::-1]
    elif type_code == 2:
        sleep(5)
        arr = list(string)
        res = arr[1:]
        res.append(arr[-1])
        for i in range(1, len(arr), 2):
            res[i] = arr[i-1]
        return ''.join(res)
    elif type_code == 3:
        sleep(7)
        res = []
        for i, c in enumerate(string):
            res.extend([c] * (i+1))
        return ''.join(res)


def worker():
    index = 0

    while True:
        with db_lock:
            # если есть очередная задача, то выбираем её
            if index < len(DB):
                task = DB[index]
                assert task.state == 'pending'
                task.state = 'processing'
            else:
                task = None  # пока нет необработанных задач
        if task is None:
            # все задачи завершены - ждём новой
            sleep(.1)
            continue

        print(f'PROCESSING {task}')
        result = do_work(task.type_code, task.string)
        with db_lock:
            task.state = 'done'
            task.result = result
            print(f'DONE {task}')
        index += 1


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
                'result': task.result,
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


def main():
    server = HTTPServer(('localhost', 8000), RequestHandler)
    server_thread = Thread(target=server.serve_forever)
    server_thread.start()
    worker_thread = Thread(target=worker)
    worker_thread.start()


if __name__ == "__main__":
    main()
