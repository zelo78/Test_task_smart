import argparse
import http.client
import json

HOST, PORT = "localhost", 8000


def main():
    args = command_line_processing()
    args.func(args)


def ask_server(method: str, data: dict) -> dict:
    """Соединяется с сервером методом `method`, передаём в теле запроса данные `data`.
    Читаем ответ, и возвращаем его в словаре
     {'status': код ответа сервера, 'reason': ответ сервера,
     'data': возвращенные данные}"""

    assert method in ['POST', 'GET']

    connection = http.client.HTTPConnection(host=HOST, port=PORT)
    connection.request(
        method=method,
        url='/api/v1/task',
        headers={'Content-type': 'application/json'},
        body=json.dumps(data),
    )
    response = connection.getresponse()
    try:
        received_data = json.loads(response.read().decode('utf-8'))
    except json.JSONDecodeError:
        received_data = None

    result = {
        'status': response.status,
        'reason': response.reason,
        'data': received_data,
    }
    connection.close()
    return result


def add_task(args):
    """Добавление задачи в очередь"""
    # Подготовка данных
    data = {
        'task_type': args.task_type,
        'string': args.string,
    }
    result = ask_server('POST', data)

    if result['status'] == http.client.CREATED:
        identifier = result['data']['id']
        print(f'Создана новая задача с идентификатором {identifier}.')
    else:
        print(f'Ошибка, код ошибки {result["status"]}, описание ошибки {result["reason"]}.')


def show_task(args):
    """Просмотр данных о задаче. Выводит статус или результат задачи (в зависимости от поля args.command)"""
    # Подготовка данных
    identifier = args.id
    data = {'id': identifier}
    result = ask_server('GET', data)

    if result['status'] == http.client.OK:
        if args.command == 'status':
            status = result['data']['status']
            print(f'Задача с идентификатором {identifier} имеет статус {status}.')
        elif args.command == 'result':
            res = result['data']['result']
            if res is None:
                print(f'Задача с идентификатором {identifier} пока не завершена.')
            else:
                print(f'Задача с идентификатором {identifier} получила результат {res}.')
    elif result['status'] == http.client.NOT_FOUND:
        print(f'Задача с идентификатором {identifier} в базе не найдена.')
    else:
        print(f'Ошибка, код ошибки {result["status"]}, описание ошибки {result["reason"]}.')


def command_line_processing():
    """Создание и выполнение парсера параметров командной строки"""
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
        'source',
        help='Исходная строка',
        )
    # parser_wait.set_defaults(func=wait_for_task)

    parser_stop = subparsers.add_parser(
        'stop', 
        help='Остановить сервер и процесс выполнения задач',
        description='Останавливает сервер и процесс выполнения задач',
        )
    # parser_stop.set_defaults(func=stop_server)
    
    return parser.parse_args()


if __name__ == "__main__":
    main()
