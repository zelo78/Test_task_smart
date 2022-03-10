import argparse
import http.client
import json
from sys import exit
from typing import Optional
import time

HOST, PORT = "localhost", 8000


def main():
    """Программа использует параметру командной строки для выполнения запросов к серверу.
    Варианты запуска:

    Добавление задачи в очередь задач (возвращает id задачи)
    client.py task <код типа задачи (1, 2 или 3)> <обрабатываемая строка данных>

    Запрос статуса задачи (отображает статус задачи)
    client.py status <id задачи>

    Запрос результата выполнения задачи (отображает результат)
    client.py result <id задачи>

    Добавление задачи в очередь и ожидание её выполнения
    client.py wait <код типа задачи (1, 2 или 3)> <обрабатываемая строка данных>
    """

    # обрабатываем параметры командной строки
    # парсер добавляет нужную функцию-обработчик в объект args
    args = command_line_processing()
    # запускаем намеченную функцию-обработчик
    args.func(args)


def ask_server(method: str, data: dict) -> dict:
    """Соединяется с сервером методом `method`, передаём в теле запроса данные `data`.
    Читаем ответ, и возвращаем его в словаре
     {'status': код ответа сервера, 'reason': ответ сервера,
     'data': возвращенные данные}

     Все данные 'data' принимаются функцией и отдаются ею в виде объектов Python,
     функция сама выполняет требуемую сериализацию/десериализацию"""

    # поддерживаем только эти два метода
    assert method in ['POST', 'GET']

    # Пытаемся связаться с сервером
    try:
        connection = http.client.HTTPConnection(host=HOST, port=PORT)
        connection.request(
            method=method,
            url='/api/v1/task',  # заготовка для будущего развития
            headers={'Content-type': 'application/json'},
            body=json.dumps(data),
        )
        response = connection.getresponse()
    except ConnectionError:
        # В случае невозможности установить связь с сервером - сообщаем пользователю
        print('Ошибка соединения с сервером. Проверьте, запущен ли сервер!\nЗадача не была добавлена в очередь!')
        exit(1)
        response = None  # эта линия кода не будет выполнена никогда

    # Пытаемся провести десериализацию полученных данных
    try:
        received_data = json.loads(response.read().decode('utf-8'))
    except json.JSONDecodeError:
        # в случае неуспеха - сохраняем значение None в переменную
        received_data = None

    result = {
        'status': response.status,
        'reason': response.reason,
        'data': received_data,
    }
    connection.close()
    return result


def add_task(args, quiet: bool = False) -> Optional[int]:
    """Добавление задачи в очередь.

    Данные по задаче извлекаются из объекта args.
    Параметр quiet=True подавляет вывод данных на экран (по умолчанию False)
    Возвращает ID созданной задачи, или None в случае неуспеха"""

    # Подготовка данных
    data = {
        'task_type': args.task_type,
        'string': args.string,
    }
    result = ask_server('POST', data)

    if result['status'] == http.client.CREATED:
        identifier = result['data']['id']
        if not quiet:
            print(f'Создана новая задача с идентификатором {identifier}.')
        return identifier
    else:
        print(f'Ошибка, код ошибки {result["status"]}, описание ошибки {result["reason"]}.')
        return None  # возвращаем в случае ошибки


def show_task(args, quiet: bool = False) -> Optional[dict]:
    """Просмотр данных о задаче.

    Выводит статус или результат задачи (в зависимости от поля args.command).
    Параметр quiet=True подавляет вывод данных на экран (по умолчанию False)
    Возвращает словарь с данными о задаче"""

    # Запрос данных у сервера
    identifier = args.id
    response = ask_server('GET', {'id': identifier})

    if response is None:
        print('Ошибка получения данных')
        exit(1)

    if response['status'] == http.client.OK:
        task_information = response['data']
        # В "тихом" режиме - просто возвращаем данные
        if quiet:
            return task_information

        assert quiet is False  # здесь мы оказываемся только, если нужен вывод на экран

        if args.command == 'status':
            status = task_information['status']
            print(f'Задача с идентификатором {identifier} имеет статус {status}.')
        elif args.command == 'result':
            result = task_information['result']
            if result is None:
                print(f'Задача с идентификатором {identifier} пока не завершена.')
            else:
                print(f'Задача с идентификатором {identifier} получила результат {result}.')
        return task_information
    elif response['status'] == http.client.NOT_FOUND:
        print(f'Задача с идентификатором {identifier} в базе не найдена.')
    else:
        print(f'Ошибка, код ошибки {response["status"]}, описание ошибки {response["reason"]}.')

    return None  # возвращаем в случае ошибки


def wait_for_task(args):
    """Добавление задачи в очередь и дожидается его выполнения.

    Данные по задаче извлекаются из объекта args."""

    ts_ns = time.time_ns()  # Время начала работы скрипта
    # добавляем задачу в очередь
    identifier = add_task(args, quiet=True)  # эта функция возвращает ID задачи
    args.id = identifier

    if identifier is None:
        print('Ошибка создания задачи. Задача не создана!')
        exit(1)

    print(f'[{(time.time_ns()-ts_ns)*1e-9:.5f}]: Создана задача #{identifier}')

    while True:
        task_information = show_task(args, quiet=True)
        status = task_information['status']
        if status == 'pending':
            print(f'[{(time.time_ns() - ts_ns) * 1e-9:.5f}]: Задача ожидает выполнения. Подождите немного. '
                  f'Вы можете прервать ожидание командой CTRL-C')
        elif status == 'processing':
            print(f'[{(time.time_ns() - ts_ns) * 1e-9:.5f}]: Задача уже выполняется. Потерпите немного. '
                  f'Вы можете прервать ожидание командой CTRL-C')
        elif status == 'done':
            print(f'[{(time.time_ns() - ts_ns) * 1e-9:.5f}]: Задача выполнена с результатом {task_information["result"]}')
            break
        time.sleep(.475)


def command_line_processing():
    """Создание и выполнение парсера параметров командной строки.

    Парсер сохраняет данные из командной строки в возвращаемом объекте,
    и также помещает туда функцию-обработчика команды."""

    # create the top-level parser
    parser = argparse.ArgumentParser(
        description='Клиент тестового клиент-серверного приложения',
        )
    subparsers = parser.add_subparsers(
        title='Команды',
        dest='command',
        required=True,
        description='Помощь по аргументам команды: %(prog)s `command` --help',
        )
    
    # create sub-parsers
    parser_task = subparsers.add_parser(
        'task',
        help='Добавить задачу; возвращает её идентификатор',
        description='Добавляет задачу в очередь и возвращает её идентификатор',
        )
    parser_task.add_argument(
        'task_type',
        choices=[1, 2, 3],
        type=int,
        help='Код типа задачи',
        )
    parser_task.add_argument(
        'string',
        help='Исходная строка',
        )
    parser_task.set_defaults(func=add_task)
    
    parser_status = subparsers.add_parser(
        'status', 
        help='Показать статус задачи (по идентификатору)',
        description='Запрашивает и выводит статус задачи по её идентификатору',
        )
    parser_status.add_argument(
        'id',
        type=int,
        help='Идентификатор задачи',
        )
    parser_status.set_defaults(func=show_task)

    parser_result = subparsers.add_parser(
        'result', 
        help='Показать результат выполнения задачи (по идентификатору)',
        description='Запрашивает и выводит результат задачи по её идентификатору',
        )
    parser_result.add_argument(
        'id',
        type=int,
        help='Идентификатор задачи',
        )
    parser_result.set_defaults(func=show_task)

    parser_wait = subparsers.add_parser(
        'wait', 
        help='Добавить задачу и дождаться её выполнения',
        description='Добавляет задачу и дожидается её выполнения',
        )
    parser_wait.add_argument(
        'task_type',
        choices=[1, 2, 3],
        type=int,
        help='Код типа задачи',
        )
    parser_wait.add_argument(
        'string',
        help='Исходная строка',
        )
    parser_wait.set_defaults(func=wait_for_task)

    # TODO Остановка сервера командой клиента
    # parser_stop = subparsers.add_parser(
    #     'stop',
    #     help='Остановить сервер и процесс выполнения задач',
    #     description='Останавливает сервер и процесс выполнения задач',
    #     )
    # parser_stop.set_defaults(func=stop_server)
    
    return parser.parse_args()


if __name__ == "__main__":
    main()
