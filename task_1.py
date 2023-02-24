# Задание 1

# Реализуйте работу цикла событий и перехватывайте системные вызовы SIGINT и SIGTERM для корректного
# завершения работы. Используйте метод add_signal_handler() и модуль signal.

# Доработайте решение, чтобы через 3 секунды отобразились текущая дата и время.
# Для реализации используйте метод call_later().

import asyncio
import random
import signal
import time
import datetime
import functools


class GracefulExit(SystemExit):
    code = 1


def raise_graceful_exit():
    raise GracefulExit()


async def waiter(name: str):
    i = 0
    while (i := i + 1) > 0:
        r = random.random()
        await asyncio.sleep(r)
        print(f'[{name}] i={i}')


def waiter_2(name: str):
    i = 0
    while (i := i + 1) > 0:
        r = random.random()
        time.sleep(r)
        print(f'[{name}] i={i}')


def time_print():
    print(datetime.datetime.now())


if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, raise_graceful_exit)
    loop.add_signal_handler(signal.SIGTERM, raise_graceful_exit)
    loop.create_task(waiter('WAITER 1'))
    loop.create_task(waiter('WAITER 2'))
    loop.create_task(waiter('WAITER 3'))
    loop.create_task(waiter('WAITER 4'))
    loop.call_later(3, time_print)
    loop.run_in_executor(None, functools.partial(waiter_2, name='SPECIAL'))
    print('-' * 60)

    pending_tasks = asyncio.all_tasks(loop)
    tasks = asyncio.gather(*pending_tasks, return_exceptions=True)
    loop.run_until_complete(tasks)
    loop.close()

    try:
        loop.run_forever()
    except GracefulExit:
        pass
