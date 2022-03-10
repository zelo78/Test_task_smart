# Клиент-серверное приложение

Тестовое задание компании _ООО "Смарт Текнолоджис"_

## Условие задания

### Сервер

Занимается приемом и выполнением задач. Выполнение задач производится строго по очереди и по одной за раз, последовательно.
Обработка клиентских запросов и выполнение задач должны производиться параллельно.

Предоставляет следующий интерфейс:
1. Получает тип задачи и данные и добавляет задачу в очередь на исполнение. Возвращает идентификатор задачи.
2. По идентификатору возвращает статус задачи (например: в очереди, выполняется, завершено)
3. По идентификатору возвращает результат выполнения задачи (предусмотреть что за результатом могут обратиться несколько раз).

Хранение задач (идентификаторов, данных и результатов) между запусками сервера не требуется.

Список задач (тип) предопределен, для имитации длительности задачи добавить указанную задержку во время ее выполнения:

1. Выполнить разворот строки. (`пример` -> `ремирп`). Задержка 2 сек.
2. Выполнить попарно перестановку четных и нечетных символов в строке (`пример` -> `рпмире`, `кот` -> `окт`). Задержка 5 сек.
3. Выполнить повтор символа в строке согласно его позиции (`пример` -> `прриииммммееееерррррр`). Задержка 7 сек.

### Клиент

Служит для выполнения запросов к серверу (рекомендуется использовать параметры командной строки).

Должен уметь:
1. Передать данные и тип задачи на сервер, отобразить идентификатор.
2. Запросить и вывести статус задачи по идентификатору.
3. Запросить и вывести результат выполнения задачи по идентификатору.
4. Возможность запуска в режиме (пакетный), когда клиент, получив тип задачи и данные:
   - отдает задачу на выполнение и выводит идентификатор
   - дожидается выполнения задачи (в ходе ожидания можно выводить текущий статус)
   - запрашивает и выводит результат выполнения задачи.
   - может прервать ожидание по `ctrl+c`
   
Протокол клиент-серверного взаимодействия на усмотрение разработчика.
Библиотеки и фреймворки на усмотрение разработчика, но предпочтительно использовать встроенные средства питона.
Версия питона (cpython) и ОС на усмотрение разработчика.

## Решение

Для связи между Клиентом и Сервером использован HTTP протокол.

### Сервер

Реализован в файле `server.py`. Этот файл необходимо запустить без каких-либо параметров в отдельной консоли.

### Клиент

Реализован в файле `client.py`. Использует параметры командной строки для выполнения запросов к серверу.

Варианты запуска:

- Получение помощи в командной строке

`client.py --help`

- Получение подробной помощи о конкретной команде в командной строке

`clietn.py <команда: task, status, result или wait> --help`

- Добавление задачи в очередь задач (возвращает <id задачи>)

`client.py task <код типа задачи (1, 2 или 3)> <обрабатываемая строка данных>`

- Запрос статуса задачи (отображает статус задачи)

`client.py status <id задачи>`

- Запрос результата выполнения задачи (отображает результат)

`client.py result <id задачи>`

- Добавление задачи в очередь и ожидание её выполнения

`client.py wait <код типа задачи (1, 2 или 3)> <обрабатываемая строка данных>`

### Использованные библиотеки

По условию задачи, использованы только стандартные библиотеки.

- [argparse](https://docs.python.org/3/library/argparse.html) - Парсер параметров командной строки
- [http.server](https://docs.python.org/3/library/http.server.html) - HTTP сервер
- [http.client](https://docs.python.org/3/library/http.client.html) - Клиент HTTP протокола
- [json](https://docs.python.org/3/library/json.html) - JSON энкодер/декодер
- [threading](https://docs.python.org/3/library/threading.html) - Параллелизм на основе потоков
