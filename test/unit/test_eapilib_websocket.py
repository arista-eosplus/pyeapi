"""Tests for the websocket eAPI transport, driven through a fake websocket"""

from __future__ import annotations

import json
import logging
import queue
import random
import threading
import time
import unittest
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import websocket

import pyeapi.client
import pyeapi.eapilib
from pyeapi.eapilib import CommandError, ConnectionError
from pyeapi.eapilib import WebsocketEapiConnection

CLOSE = object()
EOS_VERSION = '4.30.0F'


def ok_response(request: dict) -> dict:
    """Echoes every command, so a response proves which request it answers"""
    result = [{'command': cmd, 'version': EOS_VERSION}
              for cmd in request['params']['cmds']]
    return {'jsonrpc': '2.0', 'id': request['id'], 'result': result}


class FakeWebSocket:
    """Stands in for websocket.WebSocket

    recv() blocks on a queue, like a socket.
    """

    def __init__(self, auth_status: str = 'success',
                 respond: Callable[[dict], dict] | None = ok_response,
                 reply_delay: Callable[[], float] | None = None) -> None:
        self.inbox: queue.Queue = queue.Queue()
        self.connected = True
        self.requests: list[dict] = []
        self.respond = respond
        self.reply_delay = reply_delay
        self.fail_send = False
        self.close_sent = False
        self.inbox.put(json.dumps({'authentication': {
            'status': auth_status, 'message': 'Bad credentials'}}))

    def send(self, payload: str) -> None:
        if self.fail_send or not self.connected:
            raise websocket.WebSocketConnectionClosedException(
                'socket is already closed.')
        message = json.loads(payload)
        if 'request' not in message:
            return
        request = message['request']
        self.requests.append(request)
        if self.respond is None:
            return
        reply = json.dumps({'response': self.respond(request)})
        if self.reply_delay is None:
            self.inbox.put(reply)
        else:
            threading.Timer(self.reply_delay(), self.inbox.put,
                            args=(reply,)).start()

    def push_response(self, response: dict) -> None:
        self.inbox.put(json.dumps({'response': response}))

    def server_drop(self) -> None:
        self.inbox.put(websocket.WebSocketConnectionClosedException(
            'Connection to remote host was lost.'))

    def recv(self) -> str:
        item = self.inbox.get()
        if item is CLOSE:
            self.connected = False
            return ''
        if isinstance(item, Exception):
            self.connected = False
            raise item
        return item

    def send_close(self) -> None:
        self.close_sent = True
        self.connected = False
        self.inbox.put(CLOSE)  # the server answers with its own close frame

    def abort(self) -> None:
        self.inbox.put(websocket.WebSocketConnectionClosedException('aborted'))

    def shutdown(self) -> None:
        self.connected = False

    def settimeout(self, timeout: float | None) -> None:
        pass


class FakeServer:
    """Hands out prepared FakeWebSockets, in order, from create_connection"""

    def __init__(self) -> None:
        self.prepared: list[FakeWebSocket] = []
        self.opened: list[FakeWebSocket] = []
        self.connect_kwargs: list[dict] = []

    def prepare(self, sock: FakeWebSocket) -> None:
        self.prepared.append(sock)

    def create_connection(self, *args, **kwargs) -> FakeWebSocket:
        sock = self.prepared.pop(0) if self.prepared else FakeWebSocket()
        self.opened.append(sock)
        self.connect_kwargs.append({'args': args, **kwargs})
        return sock


class TestWebsocketEapiConnection(unittest.TestCase):

    def setUp(self) -> None:
        self.server = FakeServer()
        patcher = patch('pyeapi.eapilib.websocket.create_connection',
                        side_effect=self.server.create_connection)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.connections: list[WebsocketEapiConnection] = []
        self.addCleanup(self._close_connections)

    def _close_connections(self) -> None:
        for conn in self.connections:
            conn.close()

    def connect(self, timeout: float = 5,
                idle_timeout: float | None = None,
                **kwargs) -> WebsocketEapiConnection:
        conn = WebsocketEapiConnection('switch', username='admin',
                                       password='pwd', timeout=timeout,
                                       idle_timeout=idle_timeout, **kwargs)
        self.connections.append(conn)
        return conn

    def wait_until(self, condition: Callable[[], bool],
                   timeout: float = 2) -> None:
        deadline = time.monotonic() + timeout
        while not condition():
            self.assertLess(time.monotonic(), deadline,
                            'condition not reached')
            time.sleep(0.01)

    def test_init_runs_eapi_connection_init(self):
        conn = self.connect()
        self.assertIsNone(conn.error)
        self.assertIsNone(conn._auth)
        self.assertEqual(conn.is_alive(), {'is_alive': True})

    def test_only_websocket_keeps_cli_mode(self):
        self.assertIs(WebsocketEapiConnection.keeps_cli_mode, True)
        self.assertIs(pyeapi.eapilib.EapiConnection.keeps_cli_mode, False)

    def test_uri_defaults_to_wss_on_443(self):
        conn = self.connect()
        self.assertEqual(self.server.connect_kwargs[0]['args'],
                         ('wss://switch:443/command-api-websocket',))
        self.assertIn('wss://switch:443/command-api-websocket', str(conn))

    def test_config_file_strings_are_coerced(self):
        conn = self.connect(port='8443', timeout='7', idle_timeout='45',
                            path='/custom')
        self.assertEqual(self.server.connect_kwargs[0]['args'],
                         ('wss://switch:8443/custom',))
        self.assertEqual(conn._timeout, 7.0)
        self.assertEqual(conn._idle_timeout, 45.0)

    def test_unused_connect_kwargs_are_accepted(self):
        conn = self.connect(key_file=None, cert_file=None, ca_file=None)
        self.assertEqual(conn.is_alive(), {'is_alive': True})

    def test_make_connection_selects_websocket_transport(self):
        conn = pyeapi.client.make_connection(
            'websocket', host='switch', username='admin', password='pwd',
            idle_timeout=None)
        self.connections.append(conn)
        self.assertIsInstance(conn, WebsocketEapiConnection)

    def test_connect_selects_websocket_transport(self):
        conn = pyeapi.client.connect(transport='websocket', host='switch')
        self.connections.append(conn)
        self.assertIsInstance(conn, WebsocketEapiConnection)

    def test_auth_failure_raises_connection_error(self):
        self.server.prepare(FakeWebSocket(auth_status='failure'))
        with self.assertRaisesRegex(ConnectionError, 'Bad credentials'):
            WebsocketEapiConnection('switch', username='admin',
                                    password='wrong')

    def test_connect_failure_raises_connection_error(self):
        refused = ConnectionRefusedError(111, 'Connection refused')
        with patch('pyeapi.eapilib.websocket.create_connection',
                   side_effect=refused):
            with self.assertRaisesRegex(ConnectionError,
                                        'Unable to connect'):
                WebsocketEapiConnection('switch')

    def test_command_error(self):
        def error_response(request: dict) -> dict:
            return {'jsonrpc': '2.0', 'id': request['id'], 'error': {
                'code': 1002,
                'message': ("CLI command 1 of 1 'show bogus' failed: "
                            'invalid command')}}

        self.server.prepare(FakeWebSocket(respond=error_response))
        conn = self.connect()
        with self.assertRaisesRegex(CommandError, 'invalid command'):
            conn.execute(['show bogus'])

    def test_failed_request_sends_end_before_raising(self):
        def fail_bogus(request: dict) -> dict:
            if 'bogus' not in request['params']['cmds']:
                return ok_response(request)
            return {'jsonrpc': '2.0', 'id': request['id'], 'error': {
                'code': 1002,
                'message': ("CLI command 3 of 3 'bogus' failed: "
                            'invalid command'),
                'data': [{}, {}, {'errors': ['Invalid input']}]}}

        self.server.prepare(FakeWebSocket(respond=fail_bogus))
        conn = self.connect()
        with self.assertRaisesRegex(CommandError, 'invalid command'):
            conn.execute(['configure', 'interface Ethernet1', 'bogus'])
        sent = [request['params']['cmds']
                for request in self.server.opened[0].requests]
        self.assertEqual(sent, [['configure', 'interface Ethernet1', 'bogus'],
                                ['end']])
        # EOS rejects a request whose format is null
        self.assertEqual(self.server.opened[0].requests[1]['params']['format'],
                         'json')

    def test_rejected_end_is_not_retried(self):
        def reject_all(request: dict) -> dict:
            return {'jsonrpc': '2.0', 'id': request['id'], 'error': {
                'code': 1002, 'message': 'invalid command'}}

        self.server.prepare(FakeWebSocket(respond=reject_all))
        conn = self.connect()
        with self.assertRaises(CommandError):
            conn.execute(['show bogus'])
        sent = [request['params']['cmds']
                for request in self.server.opened[0].requests]
        self.assertEqual(sent, [['show bogus'], ['end']])

    def test_drop_while_leaving_config_mode_raises_original_error(self):
        server = self.server

        def fail_then_drop(request: dict) -> dict | None:
            if request['params']['cmds'] == ['end']:
                server.opened[0].server_drop()
                return None
            return {'jsonrpc': '2.0', 'id': request['id'], 'error': {
                'code': 1002, 'message': 'invalid command'}}

        class DroppingWebSocket(FakeWebSocket):
            def send(self, payload: str) -> None:
                message = json.loads(payload)
                if 'request' in message:
                    request = message['request']
                    self.requests.append(request)
                    reply = fail_then_drop(request)
                    if reply is not None:
                        self.push_response(reply)
                    return
                super().send(payload)

        self.server.prepare(DroppingWebSocket(respond=None))
        conn = self.connect()
        with self.assertLogs('pyeapi.eapilib', level='WARNING'):
            with self.assertRaisesRegex(CommandError, 'invalid command'):
                conn.execute(['configure', 'bogus'])

    def test_successful_request_sends_no_end(self):
        conn = self.connect()
        conn.execute(['configure', 'interface Ethernet1'])
        self.assertEqual(len(self.server.opened[0].requests), 1)

    def test_request_ids_are_unique(self):
        conn = self.connect()
        conn.execute(['show version'])
        conn.execute(['show version'])
        ids = [request['id'] for request in self.server.opened[0].requests]
        self.assertEqual(len(set(ids)), 2)

    def test_out_of_order_responses_reach_their_callers(self):
        self.server.prepare(FakeWebSocket(respond=None))
        conn = self.connect()
        sock = self.server.opened[0]

        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(conn.execute, ['show first'])
            self.wait_until(lambda: len(sock.requests) == 1)
            second = pool.submit(conn.execute, ['show second'])
            self.wait_until(lambda: len(sock.requests) == 2)
            for request in reversed(sock.requests):
                sock.push_response(ok_response(request))

            self.assertEqual(first.result()['result'][0]['command'],
                             'show first')
            self.assertEqual(second.result()['result'][0]['command'],
                             'show second')

    def test_response_with_unknown_id_is_dropped(self):
        self.server.prepare(FakeWebSocket(
            respond=lambda request: ok_response(
                {**request, 'id': 'someone-else'})))
        conn = self.connect(timeout=0.2)
        with self.assertLogs('pyeapi.eapilib', level='WARNING') as logs:
            with self.assertRaisesRegex(ConnectionError, 'No response'):
                conn.execute(['show version'])
        self.assertTrue(any('unknown id' in line for line in logs.output))
        self.assertEqual(conn.is_alive(), {'is_alive': False})

    def test_server_drop_fails_pending_requests_and_is_alive(self):
        self.server.prepare(FakeWebSocket(respond=None))
        conn = self.connect()
        sock = self.server.opened[0]

        with self.assertLogs('pyeapi.eapilib', level='WARNING') as logs:
            with ThreadPoolExecutor(max_workers=1) as pool:
                pending = pool.submit(conn.execute, ['show version'])
                self.wait_until(lambda: len(sock.requests) == 1)
                sock.server_drop()
                with self.assertRaisesRegex(ConnectionError,
                                            'Connection lost'):
                    pending.result()
        self.assertTrue(any('Connection lost' in line
                            for line in logs.output))
        self.assertEqual(conn.is_alive(), {'is_alive': False})

    def test_reconnects_before_sending_after_drop(self):
        conn = self.connect()
        first = conn.transport
        with self.assertLogs('pyeapi.eapilib', level='WARNING'):
            first.server_drop()
            self.wait_until(lambda: conn.is_alive() == {'is_alive': False})

        response = conn.execute(['show version'])

        self.assertEqual(len(self.server.opened), 2)
        self.assertIsNot(conn.transport, first)
        self.assertEqual(response['result'][0]['command'], 'show version')
        self.assertEqual(conn.is_alive(), {'is_alive': True})

    def test_send_failure_is_not_retried(self):
        conn = self.connect()
        self.server.opened[0].fail_send = True
        with self.assertRaisesRegex(ConnectionError, 'Send failed'):
            conn.execute(['configure session x commit'])
        self.assertEqual(len(self.server.opened), 1)
        self.assertEqual(conn.is_alive(), {'is_alive': False})

    def test_close_is_idempotent_and_refuses_new_requests(self):
        conn = self.connect()
        conn.close()
        conn.close()
        self.assertEqual(conn.is_alive(), {'is_alive': False})
        with self.assertRaisesRegex(ConnectionError, 'closed'):
            conn.execute(['show version'])

    def test_threads_sharing_a_connection_get_their_own_responses(self):
        self.server.prepare(FakeWebSocket(
            reply_delay=lambda: random.uniform(0, 0.005)))
        conn = self.connect()
        thread_count = 8
        requests_per_thread = 50

        def worker(thread_index: int) -> int:
            matched = 0
            for request_index in range(requests_per_thread):
                command = f'show thread {thread_index} request {request_index}'
                response = conn.execute([command])
                if response['result'][0]['command'] == command:
                    matched += 1
            return matched

        with ThreadPoolExecutor(max_workers=thread_count) as pool:
            matched = sum(pool.map(worker, range(thread_count)))
        self.assertEqual(matched, thread_count * requests_per_thread)

    def test_exclusive_holds_back_other_threads(self):
        conn = self.connect()
        sock = self.server.opened[0]
        with ThreadPoolExecutor(max_workers=1) as pool:
            with conn.exclusive():
                conn.execute(['show held'])
                other = pool.submit(conn.execute, ['show other'])
                time.sleep(0.1)
                self.assertEqual(len(sock.requests), 1)
                self.assertFalse(other.done())
            self.assertEqual(other.result()['result'][0]['command'],
                             'show other')

    def test_exclusive_is_a_no_op_on_other_transports(self):
        with pyeapi.eapilib.EapiConnection().exclusive():
            pass

    def test_shared_node_config_is_not_interleaved(self):
        self.server.prepare(FakeWebSocket(
            reply_delay=lambda: random.uniform(0, 0.002)))
        conn = self.connect()
        node = pyeapi.client.Node(conn)
        rounds = 50

        def configurer() -> None:
            for index in range(rounds):
                node.config(['interface Ethernet1', f'description {index}'])

        def reader() -> None:
            for _ in range(rounds * 3):
                node.run_commands(['show version'])

        with ThreadPoolExecutor(max_workers=2) as pool:
            for future in [pool.submit(configurer), pool.submit(reader)]:
                future.result()
        sent = [request['params']['cmds']
                for request in self.server.opened[0].requests]
        config_indexes = [index for index, cmds in enumerate(sent)
                          if 'configure terminal' in cmds]
        self.assertEqual(len(config_indexes), rounds)
        for index in config_indexes:
            self.assertEqual(sent[index + 1], ['end'])

    def test_idle_connection_closes_and_next_request_reconnects(self):
        conn = self.connect(idle_timeout=0.1)
        self.wait_until(lambda: conn.is_alive() == {'is_alive': False})
        self.assertTrue(self.server.opened[0].close_sent)

        response = conn.execute(['show version'])

        self.assertEqual(len(self.server.opened), 2)
        self.assertEqual(response['result'][0]['command'], 'show version')

    def test_pending_request_keeps_connection_open_past_idle_timeout(self):
        self.server.prepare(FakeWebSocket(respond=None))
        conn = self.connect(idle_timeout=0.1)
        sock = self.server.opened[0]

        with ThreadPoolExecutor(max_workers=1) as pool:
            pending = pool.submit(conn.execute, ['show slow'])
            self.wait_until(lambda: len(sock.requests) == 1)
            time.sleep(0.3)
            self.assertFalse(sock.close_sent)
            self.assertEqual(conn.is_alive(), {'is_alive': True})
            sock.push_response(ok_response(sock.requests[0]))
            self.assertEqual(pending.result()['result'][0]['command'],
                             'show slow')

        self.wait_until(lambda: sock.close_sent)

    def test_requests_more_often_than_idle_timeout_keep_connection_open(self):
        conn = self.connect(idle_timeout=0.2)
        for _ in range(6):
            conn.execute(['show version'])
            time.sleep(0.05)
        self.assertEqual(len(self.server.opened), 1)
        self.assertEqual(conn.is_alive(), {'is_alive': True})

    def test_idle_timeout_none_keeps_connection_open(self):
        conn = self.connect(idle_timeout=None)
        time.sleep(0.2)
        self.assertFalse(self.server.opened[0].close_sent)
        self.assertEqual(conn.is_alive(), {'is_alive': True})

    def test_idle_close_logs_at_info_not_warning(self):
        with self.assertLogs('pyeapi.eapilib', level='INFO') as logs:
            conn = self.connect(idle_timeout=0.1)
            self.wait_until(lambda: conn.is_alive() == {'is_alive': False})
            self.wait_until(lambda: self.server.opened[0].inbox.empty())
        levels = [(record.levelno, record.getMessage())
                  for record in logs.records]
        self.assertTrue(any(level == logging.INFO and 'idle' in message
                            for level, message in levels))
        self.assertEqual(
            [message for level, message in levels if level >= logging.WARNING],
            [])

    def test_timeout_resets_connection_and_fails_queued_requests(self):
        self.server.prepare(FakeWebSocket(respond=None))
        conn = self.connect(timeout=0.3)
        sock = self.server.opened[0]

        with ThreadPoolExecutor(max_workers=2) as pool:
            stuck = pool.submit(conn.execute, ['show stuck'])
            self.wait_until(lambda: len(sock.requests) == 1)
            queued = pool.submit(conn.execute, ['show queued'])
            self.wait_until(lambda: len(sock.requests) == 2)
            with self.assertRaisesRegex(ConnectionError, 'connection reset'):
                stuck.result()
            with self.assertRaises(ConnectionError):
                queued.result()

        self.assertEqual(conn.is_alive(), {'is_alive': False})
        response = conn.execute(['show version'])
        self.assertEqual(len(self.server.opened), 2)
        self.assertEqual(response['result'][0]['command'], 'show version')


if __name__ == '__main__':
    unittest.main()
