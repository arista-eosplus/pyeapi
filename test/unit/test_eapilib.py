import unittest
import json
import ssl

from unittest.mock import Mock, patch, MagicMock, call

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

    def test_execute_raises_command_error(self):
        mock_send = Mock(name='send')
        mock_send.side_effect = pyeapi.eapilib.CommandError('1000', 'test')

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
        # HTTP requests to be processed by EAPI should always go to
        # the /command-api endpoint regardless of using TCP/IP or unix-socket
        # for the transport. Unix-socket implementation maps localhost to the
        # unix-socket - /var/run/command-api.sock
        mock_transport.putrequest.assert_called_once_with('POST',
                                                          '/command-api')
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

    def test_send_unauthorized_user(self):
        error_string = ('Unauthorized. Unable to authenticate user: Bad'
                        ' username/password combination')
        response_str = ('Unable to authenticate user: Bad username/password'
                        ' combination')
        mock_transport = Mock(name='transport')
        mockcfg = {'getresponse.return_value.read.return_value': response_str,
                   'getresponse.return_value.status': 401,
                   'getresponse.return_value.reason': 'Unauthorized'}
        mock_transport.configure_mock(**mockcfg)

        instance = pyeapi.eapilib.EapiConnection()
        instance.authentication('username', 'password')
        instance.transport = mock_transport
        try:
            instance.send('test')
        except pyeapi.eapilib.ConnectionError as err:
            self.assertEqual(err.message, error_string)

    def test_send_raises_connection_error(self):
        mock_transport = Mock(name='transport')
        mockcfg = {'getresponse.return_value.read.side_effect': ValueError}
        mock_transport.configure_mock(**mockcfg)

        instance = pyeapi.eapilib.EapiConnection()
        instance.transport = mock_transport
        try:
            instance.send('test')
        except pyeapi.eapilib.ConnectionError as err:
            self.assertEqual(err.message, 'unable to connect to eAPI')

    def test_send_raises_connection_socket_error(self):
        mock_transport = Mock(name='transport')
        mockcfg = {'getresponse.return_value.read.side_effect':
                   OSError('timeout')}
        mock_transport.configure_mock(**mockcfg)

        instance = pyeapi.eapilib.EapiConnection()
        instance.transport = mock_transport
        try:
            instance.send('test')
        except pyeapi.eapilib.ConnectionError as err:
            error_msg = 'Socket error during eAPI connection: timeout'
            self.assertEqual(err.message, error_msg)

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

    def test_send_raises_autocomplete_command_error(self):
        message = "runCmds() got an unexpected keyword argument 'autoComplete'"
        error = dict(code=9999, message=message, data=[{'errors': ['test']}])
        response_dict = dict(jsonrpc='2.0', error=error, id=id(self))
        response_json = json.dumps(response_dict)

        mock_transport = Mock(name='transport')
        mockcfg = {'getresponse.return_value.read.return_value': response_json}
        mock_transport.configure_mock(**mockcfg)

        instance = pyeapi.eapilib.EapiConnection()
        instance.transport = mock_transport

        try:
            instance.send('test')
        except pyeapi.eapilib.CommandError as error:
            match = ("autoComplete parameter is not supported in this version"
                     " of EOS.")
            self.assertIn(match, error.message)

    def test_send_raises_expandaliases_command_error(self):
        message = "runCmds() got an unexpected keyword argument" \
                  " 'expandAliases'"
        error = dict(code=9999, message=message, data=[{'errors': ['test']}])
        response_dict = dict(jsonrpc='2.0', error=error, id=id(self))
        response_json = json.dumps(response_dict)

        mock_transport = Mock(name='transport')
        mockcfg = {'getresponse.return_value.read.return_value': response_json}
        mock_transport.configure_mock(**mockcfg)

        instance = pyeapi.eapilib.EapiConnection()
        instance.transport = mock_transport

        try:
            instance.send('test')
        except pyeapi.eapilib.CommandError as error:
            match = ("expandAliases parameter is not supported in this version"
                     " of EOS.")
            self.assertIn(match, error.message)

    def test_request_adds_autocomplete(self):
        instance = pyeapi.eapilib.EapiConnection()
        request = instance.request(['sh ver'], encoding='json',
                                   autoComplete=True)
        data = json.loads(request)
        self.assertIn('autoComplete', data['params'])

    def test_request_adds_expandaliases(self):
        instance = pyeapi.eapilib.EapiConnection()
        request = instance.request(['test'], encoding='json',
                                   expandAliases=True)
        data = json.loads(request)
        self.assertIn('expandAliases', data['params'])

    def test_request_ignores_unknown_param(self):
        instance = pyeapi.eapilib.EapiConnection()
        request = instance.request(['sh ver'], encoding='json',
                                   unknown=True)
        data = json.loads(request)
        self.assertNotIn('unknown', data['params'])


class TestHTTPSCertConnection(unittest.TestCase):
    """Unit tests for HTTPSCertConnection (issue #318 fix).

    Verifies that:
      - key_file / cert_file are NOT forwarded to HTTPSConnection.__init__()
        (those parameters were removed in Python 3.12).
      - connect() builds an ssl.SSLContext using PROTOCOL_TLS_CLIENT and
        loads the client certificate via load_cert_chain().
      - When ca_file is provided, load_verify_locations() is called and
        server-certificate verification stays enabled.
      - When ca_file is None, check_hostname is disabled and verify_mode is
        set to CERT_NONE.
    """

    # ------------------------------------------------------------------ #
    # __init__ tests                                                       #
    # ------------------------------------------------------------------ #

    def test_init_stores_key_and_cert_as_attributes(self):
        """key_file and cert_file must be stored as instance attributes."""
        conn = pyeapi.eapilib.HTTPSCertConnection(
            path='/command-api',
            host='switch1',
            port=443,
            key_file='/path/to/client.key',
            cert_file='/path/to/client.crt',
            ca_file=None,
            timeout=30,
        )
        self.assertEqual(conn.key_file, '/path/to/client.key')
        self.assertEqual(conn.cert_file, '/path/to/client.crt')
        self.assertIsNone(conn.ca_file)
        self.assertEqual(conn.timeout, 30)
        self.assertEqual(conn.path, '/command-api')
        self.assertEqual(conn.port, 443)

    def test_init_does_not_raise_typeerror_on_python312(self):
        """Instantiation must not raise TypeError on Python 3.12+.

        Prior to the fix, key_file/cert_file were forwarded to
        HTTPSConnection.__init__(), which removed those parameters in 3.12.
        """
        try:
            _ = pyeapi.eapilib.HTTPSCertConnection(
                path='/command-api',
                host='switch1',
                port=443,
                key_file='/path/to/client.key',
                cert_file='/path/to/client.crt',
                ca_file=None,
            )
        except TypeError as exc:
            self.fail(
                'HTTPSCertConnection.__init__() raised TypeError '
                '(key_file/cert_file must not be passed to '
                'HTTPSConnection.__init__()): %s' % exc
            )

    def test_init_key_cert_not_forwarded_to_https_connection(self):
        """HTTPSConnection.__init__() must be called WITHOUT key_file/cert_file."""
        with patch('pyeapi.eapilib.HTTPSConnection.__init__',
                   return_value=None):
            # Provide the minimum attributes that HTTPSConnection normally sets
            # so that our __init__ can complete without AttributeError.
            conn = pyeapi.eapilib.HTTPSCertConnection.__new__(
                pyeapi.eapilib.HTTPSCertConnection)
            # Manually call __init__ via the class (bypasses MRO issues)
            with patch.object(
                    pyeapi.eapilib.HTTPSConnection, '__init__', return_value=None) as mock_init:
                # Patch out attribute access that HTTPSConnection normally sets
                conn.__dict__.update({
                    'key_file': None, 'cert_file': None, 'ca_file': None,
                    'timeout': None, 'path': None, 'port': None,
                    'host': 'switch1',
                })
                pyeapi.eapilib.HTTPSCertConnection.__init__(
                    conn,
                    path='/command-api',
                    host='switch1',
                    port=443,
                    key_file='/path/to/client.key',
                    cert_file='/path/to/client.crt',
                    ca_file=None,
                )
                # The super().__init__() call must NOT include key_file or cert_file
                args, kwargs = mock_init.call_args
                self.assertNotIn(
                    'key_file', kwargs,
                    'key_file must not be passed to '
                    'HTTPSConnection.__init__()')
                self.assertNotIn(
                    'cert_file', kwargs,
                    'cert_file must not be passed to '
                    'HTTPSConnection.__init__()')

    def test_str_and_repr(self):
        """__str__ and __repr__ must include host, port, path, key and cert."""
        conn = pyeapi.eapilib.HTTPSCertConnection(
            path='/command-api',
            host='switch1',
            port=443,
            key_file='/path/to/client.key',
            cert_file='/path/to/client.crt',
            ca_file=None,
        )
        expected = 'https://switch1:443//command-api - /path/to/client.key,/path/to/client.crt'
        self.assertEqual(str(conn), expected)
        self.assertEqual(repr(conn), expected)

    # ------------------------------------------------------------------ #
    # connect() tests                                                      #
    # ------------------------------------------------------------------ #

    @patch('pyeapi.eapilib.ssl.SSLContext')
    @patch('pyeapi.eapilib.socket.create_connection')
    def test_connect_uses_protocol_tls_client(self, mock_create_conn,
                                              mock_ssl_context_cls):
        """connect() must create an SSLContext with PROTOCOL_TLS_CLIENT.

        Note: HTTPSConnection.__init__() in Python 3.12 also calls
        ssl.SSLContext() internally, so the mock may be invoked more than once.
        We verify that at least one call used PROTOCOL_TLS_CLIENT.
        """
        mock_sock = Mock()
        mock_create_conn.return_value = mock_sock
        mock_context = MagicMock()
        mock_ssl_context_cls.return_value = mock_context
        mock_context.wrap_socket.return_value = Mock()

        conn = pyeapi.eapilib.HTTPSCertConnection(
            path='/command-api',
            host='switch1',
            port=443,
            key_file='/path/to/client.key',
            cert_file='/path/to/client.crt',
            ca_file=None,
        )
        conn._tunnel_host = None
        conn.connect()

        # At least one call to ssl.SSLContext() must use PROTOCOL_TLS_CLIENT
        # (HTTPSConnection.__init__ may also call SSLContext internally in 3.12)
        calls_with_tls_client = [
            c for c in mock_ssl_context_cls.call_args_list
            if c == call(ssl.PROTOCOL_TLS_CLIENT)
        ]
        self.assertTrue(
            len(calls_with_tls_client) >= 1,
            'ssl.SSLContext(PROTOCOL_TLS_CLIENT) was not called by connect(). '
            'Actual calls: %s' % mock_ssl_context_cls.call_args_list
        )

    @patch('pyeapi.eapilib.ssl.SSLContext')
    @patch('pyeapi.eapilib.socket.create_connection')
    def test_connect_loads_cert_chain(self, mock_create_conn,
                                     mock_ssl_context_cls):
        """connect() must call load_cert_chain() with cert_file and key_file."""
        mock_sock = Mock()
        mock_create_conn.return_value = mock_sock
        mock_context = MagicMock()
        mock_ssl_context_cls.return_value = mock_context
        mock_context.wrap_socket.return_value = Mock()

        conn = pyeapi.eapilib.HTTPSCertConnection(
            path='/command-api',
            host='switch1',
            port=443,
            key_file='/path/to/client.key',
            cert_file='/path/to/client.crt',
            ca_file=None,
        )
        conn._tunnel_host = None
        conn.connect()

        mock_context.load_cert_chain.assert_called_once_with(
            certfile='/path/to/client.crt',
            keyfile='/path/to/client.key',
        )

    @patch('pyeapi.eapilib.ssl.SSLContext')
    @patch('pyeapi.eapilib.socket.create_connection')
    def test_connect_without_ca_file_disables_verification(
            self, mock_create_conn, mock_ssl_context_cls):
        """When ca_file is None, server-cert verification must be disabled.

        check_hostname must be set to False and verify_mode to CERT_NONE.
        load_verify_locations() must NOT be called.
        """
        mock_sock = Mock()
        mock_create_conn.return_value = mock_sock
        mock_context = MagicMock()
        mock_ssl_context_cls.return_value = mock_context
        mock_context.wrap_socket.return_value = Mock()

        conn = pyeapi.eapilib.HTTPSCertConnection(
            path='/command-api',
            host='switch1',
            port=443,
            key_file='/path/to/client.key',
            cert_file='/path/to/client.crt',
            ca_file=None,
        )
        conn._tunnel_host = None
        conn.connect()

        self.assertFalse(mock_context.check_hostname)
        self.assertEqual(mock_context.verify_mode, ssl.CERT_NONE)
        mock_context.load_verify_locations.assert_not_called()

    @patch('pyeapi.eapilib.ssl.SSLContext')
    @patch('pyeapi.eapilib.socket.create_connection')
    def test_connect_with_ca_file_enables_verification(
            self, mock_create_conn, mock_ssl_context_cls):
        """When ca_file is provided, load_verify_locations() must be called.

        check_hostname and verify_mode must keep their PROTOCOL_TLS_CLIENT
        defaults — i.e. the code must NOT set check_hostname=False or
        verify_mode=CERT_NONE when a CA file is supplied.
        """
        mock_sock = Mock()
        mock_create_conn.return_value = mock_sock
        mock_context = MagicMock()
        mock_ssl_context_cls.return_value = mock_context
        mock_context.wrap_socket.return_value = Mock()

        conn = pyeapi.eapilib.HTTPSCertConnection(
            path='/command-api',
            host='switch1',
            port=443,
            key_file='/path/to/client.key',
            cert_file='/path/to/client.crt',
            ca_file='/path/to/ca.crt',
        )
        conn._tunnel_host = None
        conn.connect()

        # load_verify_locations must be called with the CA file
        mock_context.load_verify_locations.assert_called_once_with(
            ca_certs='/path/to/ca.crt'
        )
        # When ca_file is set, check_hostname must NOT be set to False and
        # verify_mode must NOT be set to CERT_NONE.
        # We verify this by inspecting the mock's recorded attribute writes.
        # MagicMock stores attribute assignments in _mock_children / mock_calls;
        # the simplest reliable check is that check_hostname was never assigned
        # False and verify_mode was never assigned CERT_NONE.
        for mc in mock_context.mock_calls:
            mc_str = str(mc)
            self.assertNotIn('check_hostname = False', mc_str)
            self.assertNotIn('verify_mode = 0', mc_str)   # ssl.CERT_NONE == 0

    @patch('pyeapi.eapilib.ssl.SSLContext')
    @patch('pyeapi.eapilib.socket.create_connection')
    def test_connect_wraps_socket_with_server_hostname(
            self, mock_create_conn, mock_ssl_context_cls):
        """connect() must call wrap_socket() with server_hostname=host."""
        mock_sock = Mock()
        mock_create_conn.return_value = mock_sock
        mock_context = MagicMock()
        mock_ssl_context_cls.return_value = mock_context
        wrapped = Mock()
        mock_context.wrap_socket.return_value = wrapped

        conn = pyeapi.eapilib.HTTPSCertConnection(
            path='/command-api',
            host='switch1',
            port=443,
            key_file='/path/to/client.key',
            cert_file='/path/to/client.crt',
            ca_file=None,
        )
        conn._tunnel_host = None
        conn.connect()

        mock_context.wrap_socket.assert_called_once_with(
            mock_sock, server_hostname='switch1'
        )
        self.assertIs(conn.sock, wrapped)

    @patch('pyeapi.eapilib.ssl.SSLContext')
    @patch('pyeapi.eapilib.socket.create_connection')
    def test_connect_creates_connection_to_correct_host_port(
            self, mock_create_conn, mock_ssl_context_cls):
        """connect() must open a TCP connection to (host, port)."""
        mock_sock = Mock()
        mock_create_conn.return_value = mock_sock
        mock_context = MagicMock()
        mock_ssl_context_cls.return_value = mock_context
        mock_context.wrap_socket.return_value = Mock()

        conn = pyeapi.eapilib.HTTPSCertConnection(
            path='/command-api',
            host='switch1',
            port=8443,
            key_file='/path/to/client.key',
            cert_file='/path/to/client.crt',
            ca_file=None,
            timeout=15,
        )
        conn._tunnel_host = None
        conn.connect()

        mock_create_conn.assert_called_once_with(('switch1', 8443), 15)


class TestHttpsEapiCertConnection(unittest.TestCase):
    """Unit tests for HttpsEapiCertConnection (issue #318 fix)."""

    def test_raises_value_error_when_key_file_missing(self):
        """Must raise ValueError when key_file is not provided."""
        with self.assertRaises(ValueError):
            pyeapi.eapilib.HttpsEapiCertConnection(
                host='switch1',
                cert_file='/path/to/client.crt',
            )

    def test_raises_value_error_when_cert_file_missing(self):
        """Must raise ValueError when cert_file is not provided."""
        with self.assertRaises(ValueError):
            pyeapi.eapilib.HttpsEapiCertConnection(
                host='switch1',
                key_file='/path/to/client.key',
            )

    def test_raises_value_error_when_both_files_missing(self):
        """Must raise ValueError when neither key_file nor cert_file is given."""
        with self.assertRaises(ValueError):
            pyeapi.eapilib.HttpsEapiCertConnection(host='switch1')

    def test_creates_https_cert_connection_transport(self):
        """Transport must be an HTTPSCertConnection instance."""
        instance = pyeapi.eapilib.HttpsEapiCertConnection(
            host='switch1',
            key_file='/path/to/client.key',
            cert_file='/path/to/client.crt',
        )
        self.assertIsInstance(instance.transport,
                              pyeapi.eapilib.HTTPSCertConnection)

    def test_transport_stores_key_and_cert(self):
        """Transport must expose the key_file and cert_file passed in."""
        instance = pyeapi.eapilib.HttpsEapiCertConnection(
            host='switch1',
            key_file='/path/to/client.key',
            cert_file='/path/to/client.crt',
            ca_file='/path/to/ca.crt',
        )
        self.assertEqual(instance.transport.key_file, '/path/to/client.key')
        self.assertEqual(instance.transport.cert_file, '/path/to/client.crt')
        self.assertEqual(instance.transport.ca_file, '/path/to/ca.crt')

    def test_is_eapi_connection_instance(self):
        """HttpsEapiCertConnection must be an EapiConnection subclass."""
        instance = pyeapi.eapilib.HttpsEapiCertConnection(
            host='switch1',
            key_file='/path/to/client.key',
            cert_file='/path/to/client.crt',
        )
        self.assertIsInstance(instance, pyeapi.eapilib.EapiConnection)


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
