#Клиент-серверное приложение

Тестовое задание компании _ООО "Смарт Текнолоджис"_

##Условие задания

###Сервер

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

###Клиент

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

##Решение

###Сервер

###Клиент

###Использованные библиотеки

- [argparse](https://docs.python.org/3/library/argparse.html) - Парсер параметров командной строки
- [urllib.request](https://docs.python.org/3/library/urllib.request.html) - Библиотека для открытия URL