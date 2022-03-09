import argparse
from urllib import request, parse

HOST, PORT = "http://localhost", 8000


def main():
    args = command_line_processing()

    if args.command == 'task':
        add_task(args)
    else:
        print(args)


def add_task(args):
    data = {
        'task_type': args.task_type,
        'string': args.string,
    }
    req = request.Request(
        url=f'{HOST}:{PORT}',
        data=parse.urlencode(data).encode('utf-8'),
        method='POST',
    )
    with request.urlopen(url=req) as f:
        print(f)


def command_line_processing():
    # create the top-level parser
    parser = argparse.ArgumentParser(
        description='Клиент тестового клиент-серверного приложения',
        epilog='Использованы модули argparse, ',
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

    parser_stop = subparsers.add_parser(
        'stop', 
        help='Остановить сервер и процесс выполнения задач',
        description='Останавливает сервер и процесс выполнения задач',
        )
    
    return parser.parse_args()


if __name__ == "__main__":
    main()
