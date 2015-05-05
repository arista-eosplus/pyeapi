import unittest
import json

from mock import Mock, patch

import pyeapi.eapilib


class TestEapiConnection(unittest.TestCase):

    def test_execute_valid_response(self):
        response_dict = dict(jsonrpc='2.0', result=[], id=id(self))
        mock_send = Mock(name='send')
        mock_send.return_value = json.dumps(response_dict)

        instance = pyeapi.eapilib.EapiConnection()
        instance.send = mock_send

        result = instance.execute(['command'])
        self.assertEqual(json.loads(result), response_dict)

    def test_execute_raises_type_error(self):
        instance = pyeapi.eapilib.EapiConnection()
        with self.assertRaises(TypeError):
            instance.execute(None, encoding='invalid')

    def test_execute_raises_connection_error(self):
        mock_send = Mock(name='send')
        mock_send.side_effect = pyeapi.eapilib.ConnectionError('test', 'test')

        instance = pyeapi.eapilib.EapiConnection()
        instance.send = mock_send

        with self.assertRaises(pyeapi.eapilib.ConnectionError):
            instance.execute('test')

    def test_execute_raises_comand_error(self):
        mock_send = Mock(name='send')
        mock_send.side_effect = pyeapi.eapilib.CommandError('test', 'test')

        instance = pyeapi.eapilib.EapiConnection()
        instance.send = mock_send

        with self.assertRaises(pyeapi.eapilib.CommandError):
            instance.execute('test')

    def test_create_socket_connection(self):
        instance = pyeapi.eapilib.SocketEapiConnection()
        self.assertIsInstance(instance, pyeapi.eapilib.EapiConnection)
        self.assertIsNotNone(str(instance.transport))

    @patch('pyeapi.eapilib.socket')
    def test_socket_connection_create(self, mock_socket):
        instance = pyeapi.eapilib.SocketConnection('/path/to/sock')
        instance.connect()
        mock_socket.socket.return_value.connect.assert_called_with('/path/to/sock')

    def test_create_http_local_connection(self):
        instance = pyeapi.eapilib.HttpLocalEapiConnection()
        self.assertIsInstance(instance, pyeapi.eapilib.EapiConnection)
        self.assertIsNotNone(str(instance.transport))

    def test_create_http_connection(self):
        instance = pyeapi.eapilib.HttpEapiConnection('localhost')
        self.assertIsInstance(instance, pyeapi.eapilib.EapiConnection)
        self.assertIsNotNone(str(instance.transport))

    def test_create_https_connection(self):
        instance = pyeapi.eapilib.HttpsEapiConnection('localhost')
        self.assertIsInstance(instance, pyeapi.eapilib.EapiConnection)
        self.assertIsNotNone(str(instance.transport))

    def test_send(self):
        response_dict = dict(jsonrpc='2.0', result=[{}], id=id(self))
        response_json = json.dumps(response_dict)

        mock_transport = Mock(name='transport')
        mockcfg = {'getresponse.return_value.read.return_value': response_json}
        mock_transport.configure_mock(**mockcfg)

        instance = pyeapi.eapilib.EapiConnection()
        instance.transport = mock_transport
        instance.send('test')

        self.assertTrue(mock_transport.close.called)

    def test_send_with_authentication(self):
        response_dict = dict(jsonrpc='2.0', result=[{}], id=id(self))
        response_json = json.dumps(response_dict)

        mock_transport = Mock(name='transport')
        mockcfg = {'getresponse.return_value.read.return_value': response_json}
        mock_transport.configure_mock(**mockcfg)

        instance = pyeapi.eapilib.EapiConnection()
        instance.authentication('username', 'password')
        instance.transport = mock_transport
        instance.send('test')

        self.assertTrue(mock_transport.close.called)

    def test_send_raises_connection_error(self):
        mock_transport = Mock(name='transport')
        mockcfg = {'getresponse.return_value.read.side_effect': ValueError}
        mock_transport.configure_mock(**mockcfg)

        instance = pyeapi.eapilib.EapiConnection()
        instance.transport = mock_transport

        with self.assertRaises(pyeapi.eapilib.ConnectionError):
            instance.send('test')


    def test_send_raises_command_error(self):
        error = dict(code=9999, message='test', data=[{'errors': ['test']}])
        response_dict = dict(jsonrpc='2.0', error=error, id=id(self))
        response_json = json.dumps(response_dict)

        mock_transport = Mock(name='transport')
        mockcfg = {'getresponse.return_value.read.return_value': response_json}
        mock_transport.configure_mock(**mockcfg)

        instance = pyeapi.eapilib.EapiConnection()
        instance.transport = mock_transport

        with self.assertRaises(pyeapi.eapilib.CommandError):
            instance.send('test')

class TestCommandError(unittest.TestCase):

    def test_create_command_error(self):
        result = pyeapi.eapilib.CommandError(9999, 'test')
        self.assertIsInstance(result, pyeapi.eapilib.EapiError)

    def test_command_error_trace(self):
        commands = ['test command', 'test command', 'test command']
        output = [{}, 'test output']
        result = pyeapi.eapilib.CommandError(9999, 'test', commands=commands,
                                             output=output)
        self.assertIsNotNone(result.trace)








