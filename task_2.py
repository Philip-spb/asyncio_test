# Задание 2

# Создайте сервер на основе asyncio, который раз в 2 секунды отправляет подключённым клиентам текущий статус — время и
# количество подключённых клиентов. Для реализации используйте метод create_server().

# Доработайте решение, чтобы после 5 секунд неактивности клиент получал предупреждающее сообщение, а после 10 секунд
# неактивности сервер автоматически разрывал соединение с клиентом.

import asyncio
import datetime
from dataclasses import dataclass

HOST, PORT = '127.0.0.1', 8888

ALL_CONNECTIONS = []


@dataclass
class ConnectionItem:
    transport: type
    last_activity: datetime
    is_warning_send: bool = False


class ConnectionPool:

    def __init__(self):
        self.__pool = []

    @property
    def pool_len(self) -> int:
        return len(self.__pool)

    def get_transport_pool(self) -> list:
        return [item.transport for item in self.__pool]

    def get_pool(self) -> list:
        return self.__pool

    def _find_element(self, transport):
        filtered = filter(lambda x: x.transport == transport, self.__pool)
        return next(filtered)

    def add_to_pool(self, transport):
        self.__pool.append(ConnectionItem(transport=transport, last_activity=datetime.datetime.now()))

    def remove_item(self, transport):
        item = self._find_element(transport)
        self.__pool.remove(item)


CONNECTION_POOL = ConnectionPool()


class EchoServerClientProtocol(asyncio.Protocol):
    transport = None

    def connection_made(self, transport):
        self.transport = transport
        CONNECTION_POOL.add_to_pool(transport=transport)

    def connection_lost(self, exc):
        CONNECTION_POOL.remove_item(transport=self.transport)

    def data_received(self, data):
        for item in CONNECTION_POOL.get_pool():
            if item.transport != self.transport:
                item.transport.write(data)
            else:
                item.last_activity = datetime.datetime.now()
                item.is_warning_send = False


async def send_data_to_clients():
    while True:
        now = datetime.datetime.now()
        answer = f'[{now}] Total connections: {CONNECTION_POOL.pool_len}'
        for transport in CONNECTION_POOL.get_transport_pool():
            transport.write(f'{answer}\n'.encode())
        await asyncio.sleep(2)


async def send_warning():
    while True:
        now = datetime.datetime.now()
        warning = 'You are inactive too long'
        for item in CONNECTION_POOL.get_pool():
            if (now - item.last_activity).seconds >= 5 and not item.is_warning_send:
                item.transport.write(f'{warning}\n'.encode())
                item.is_warning_send = True
        await asyncio.sleep(0.1)


async def kick_from_server():
    while True:
        now = datetime.datetime.now()
        warning = 'KILL'
        for item in CONNECTION_POOL.get_pool():
            if (now - item.last_activity).seconds >= 10:
                item.transport.write(f'{warning}\n'.encode())
                item.transport.close()
        await asyncio.sleep(0.1)


loop = asyncio.get_event_loop()
coro = loop.create_server(EchoServerClientProtocol, HOST, PORT)
loop.create_task(send_data_to_clients())
loop.create_task(send_warning())
loop.create_task(kick_from_server())

server = loop.run_until_complete(coro)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
