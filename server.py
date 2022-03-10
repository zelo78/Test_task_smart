from http.server import HTTPServer, BaseHTTPRequestHandler
import http.client
import json
from threading import Lock, Thread
from time import sleep


class Task:
    """Объект для хранения данных о задаче

    Параметры:
    type_code: код типа задачи
    string: строка, которую следует обработать
    Объект сохраняет также следующие данные:
    state: статус выполнения задачи (pending, processing, done)
    result: результат выполнения (строка). Пока задание не выполнено - None
    """

    def __init__(self, type_code: int, string: str):
        self.type_code = type_code
        self.string = string
        self.state = 'pending'
        self.result = None

    def __str__(self):
        """Строковое представление задачи в целях отладки"""

        return f'Task: type {self.type_code}, string {self.string}, state {self.state}, result {self.result}'


def do_work(type_code, string):
    """Функция, которая реально выполняет задачи.

    Данное выполнение вынесено в отдельную функцию во избежании коллизий"""

    if type_code == 1:
        # Выполнить разворот строки. (`пример` -> `ремирп`).
        # Задержка 2 сек.
        sleep(2)
        return string[::-1]
    elif type_code == 2:
        # Выполнить попарно перестановку четных и нечетных символов в строке
        # (`пример` -> `рпмире`, `кот` -> `окт`).
        # Задержка 5 сек.
        sleep(5)
        arr = list(string)
        res = arr[1:]
        res.append(arr[-1])
        for i in range(1, len(arr), 2):
            res[i] = arr[i-1]
        return ''.join(res)
    elif type_code == 3:
        # Выполнить повтор символа в строке согласно его позиции (`пример` -> `прриииммммееееерррррр`).
        # Задержка 7 сек.
        sleep(7)
        res = []
        for i, c in enumerate(string):
            res.extend([c] * (i+1))
        return ''.join(res)


def worker(db, db_lock):
    """Функция реализует Исполнителя, который обрабатывает очередь задач по одной за раз.

    Параметры:
    db - очередь задач. Предполагается, что реализована в виде списка
    db_lock - Замок (Lock), позволяющий избежать коллизий совместного доступа"""

    # указатель на текущую задачу в очереди
    index = 0

    while True:
        with db_lock:
            # если есть очередная задача, то выбираем её
            if index < len(db):
                task = db[index]
                assert task.state == 'pending'  # Задача точно должна иметь статус "Ожидает"
                task.state = 'processing'  # меняем его на "Выполняется"
            else:
                task = None  # пока нет необработанных задач
        if task is None:
            # все задачи завершены - ждём новой
            sleep(.1)
            continue

        # начинаем выполнять задачу
        print(f'PROCESSING {task}')
        result = do_work(task.type_code, task.string)
        with db_lock:
            task.state = 'done'  # Меняем статус задачи на "Выполнено"
            task.result = result  # Сохраняем результат
            print(f'DONE {task}')
        index += 1  # смещаем указатель на следующую задачу в очереди


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa
        content_length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(content_length))
        identifier = data['id']
        with self.server.db_lock:
            if 0 <= identifier < len(self.server.db):
                task = self.server.db[identifier]
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
        with self.server.db_lock:
            self.server.db.append(task)
            identifier = len(self.server.db) - 1

        print(f'{task} was added as #{identifier}')
        data = {'id': identifier}
        self.send_response(http.client.CREATED)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))


def main():
    """Серверная сторона программы.

    Создаём Сервер, Очередь и Исполнителя.
    Взаимодействуем с Сервером по HTTP протоколу.

    Метод POST - создание новой задачи в очереди.
    Метод GET - данные о текущей задаче в очереди.

    Используем JSON для сериализации обектов.

    Все входящие данные - в теле запроса.
    Все выходящие данные - в ответе."""

    # Очередь задач, реализована в виде списка
    db = []
    db_lock = Lock()  # Замок для исключения коллизий доступа

    # Создаём Сервер
    server = HTTPServer(('localhost', 8000), RequestHandler)
    # Сохраняем Очередь в аттрибутах Сервера
    server.db = db
    server.db_lock = db_lock

    # Поток выполнения Сервера
    server_thread = Thread(target=server.serve_forever)
    server_thread.start()

    # Поток Исполнителя
    worker_thread = Thread(target=worker, kwargs={'db': db, 'db_lock': db_lock})
    worker_thread.start()


if __name__ == "__main__":
    main()
