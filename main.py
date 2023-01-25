#!/usr/bin/env python

import os
import asyncio
import websockets
import re
import urllib.parse

websocket_clients = set()

async def handle_socket_connection(websocket, path):
    """Handles the whole lifecycle of each client's websocket connection."""

    if websocket.user != "qlcplus":
        websocket_clients.add(websocket)

    print(f'New connection from: {websocket.remote_address} ({len(websocket_clients)} total)')
    try:
        # This loop will keep listening on the socket until its closed.
        async for raw_message in websocket:
            #print(f'Got: [{raw_message}] from socket [{id(websocket)}, {websocket.user}]')

            if websocket.user == "qlcplus":
                print("qlcplus =", raw_message)

                rgb = raw_message

                for c in websocket_clients:
                    print(f'Sending [{rgb}] to socket [{id(c)}]')
                    await c.send(rgb)

                await asyncio.sleep(0.1)


    except websockets.exceptions.ConnectionClosedError as cce:
        pass
    finally:
        print(f'Disconnected from socket [{id(websocket)}]...')
        websocket_clients.remove(websocket)


def get_query_param(path, key):
    query = urllib.parse.urlparse(path).query
    params = urllib.parse.parse_qs(query)
    values = params.get(key, [])
    if len(values) == 1:
        return values[0]


class QueryParamProtocol(websockets.WebSocketServerProtocol):
    async def process_request(self, path, headers):
        user = get_query_param(path, "user")
        if user is None:
            #return http.HTTPStatus.UNAUTHORIZED, [], b"Missing user\n"
            user = "other"

        self.user = user


async def query_param_handler(websocket):
    user = websocket.user

    await websocket.send(f"Hello {user}!")
    message = await websocket.recv()
    assert message == f"Goodbye {user}."



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        socket_server = websockets.serve(handle_socket_connection, 'localhost', 8000, create_protocol=QueryParamProtocol)
        print(f'Started socket server: {socket_server} ...')
        loop.run_until_complete(socket_server)
        loop.run_forever()
    finally:
        loop.close()
        print(f"Successfully shutdown [{loop}].")