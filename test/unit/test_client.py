#
# Copyright (c) 2014, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   Neither the name of Arista Networks nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
import sys
import os
import unittest
import imp

sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))

from mock import Mock, patch, call

from testlib import get_fixture, random_string, random_int

import pyeapi.client

DEFAULT_CONFIG = {'connection:localhost': dict(transport='socket')}


class TestNode(unittest.TestCase):

    def setUp(self):
        self.connection = Mock()
        self.node = pyeapi.client.Node(self.connection)

    def test_get_version_properties_match_version_number_no_match_model(self):
        self.node.enable = Mock()
        version = '4.17.1.1F-3512479.41711F (engineering build)'
        self.node.enable.return_value = [{'result': {'version': version,
                                                     'modelName': 'vEOS'}}]
        self.node._get_version_properties()
        self.assertEqual(self.node.version_number, '4.17.1.1')
        self.assertEqual(self.node.model, 'vEOS')

    def test_get_version_properties_no_match_version_number_match_model(self):
        self.node.enable = Mock()
        version = 'special-4.17.1.1F-3512479.41711F (engineering build)'
        model = 'DCS-7260QX-64-F'
        self.node.enable.return_value = [{'result': {'version': version,
                                                     'modelName': model}}]
        self.node._get_version_properties()
        self.assertEqual(self.node.version_number, version)
        self.assertEqual(self.node.model, '7260')

    def test_version_properties_populate(self):
        self.node.enable = Mock()
        version = '4.17.1.1F-3512479.41711F (engineering build)'
        self.node.enable.return_value = [{'result': {'version': version,
                                                     'modelName': 'vEOS'}}]
        self.node.version_number
        self.assertEqual(self.node.version_number, '4.17.1.1')
        self.assertEqual(self.node.version, version)
        self.assertEqual(self.node.model, 'vEOS')

    def test_enable_with_single_command(self):
        command = random_string()
        response = ['enable', command]

        self.connection.execute.return_value = {'result': list(response)}
        result = self.node.enable(command)

        self.connection.execute.assert_called_once_with(response, 'json')
        self.assertEqual(command, result[0]['result'])

    def test_enable_with_single_unicode_command(self):
        command = random_string()
        command = u'%s' % command
        response = ['enable', command]

        self.connection.execute.return_value = {'result': list(response)}
        result = self.node.enable(command)

        self.connection.execute.assert_called_once_with(response, 'json')
        self.assertEqual(command, result[0]['result'])

    def test_enable_with_single_extended_command(self):
        command = {'cmd': 'show cvx', 'revision': 2}
        response = ['enable', command]

        self.connection.execute.return_value = {'result': list(response)}
        result = self.node.enable(command)

        self.connection.execute.assert_called_once_with(response, 'json')
        self.assertEqual(command, result[0]['result'])

    def test_no_enable_with_single_command(self):
        command = random_string()
        response = [command]

        self.connection.execute.return_value = {'result': list(response)}
        result = self.node.enable(command, send_enable=False)

        self.connection.execute.assert_called_once_with(response, 'json')
        self.assertEqual(command, result[0]['result'])

    def test_enable_with_multiple_commands(self):
        commands = list()
        for i in range(0, random_int(2, 5)):
            commands.append(random_string())

        def execute_response(cmds, *args):
            return {'result': [x for x in cmds]}

        self.connection.execute.side_effect = execute_response

        responses = self.node.enable(commands)

        self.assertEqual(self.connection.execute.call_count, len(commands))

        expected_calls = [call(['enable', cmd], 'json') for cmd in commands]
        self.assertEqual(self.connection.execute.mock_calls, expected_calls)

        for index, response in enumerate(responses):
            self.assertEqual(commands[index], response['result'])

    def test_enable_with_multiple_unicode_commands(self):
        commands = list()
        for i in range(0, random_int(2, 5)):
            commands.append(u'%s' % random_string())

        def execute_response(cmds, *args):
            return {'result': [x for x in cmds]}

        self.connection.execute.side_effect = execute_response

        responses = self.node.enable(commands)

        self.assertEqual(self.connection.execute.call_count, len(commands))

        expected_calls = [call(['enable', cmd], 'json') for cmd in commands]
        self.assertEqual(self.connection.execute.mock_calls, expected_calls)

        for index, response in enumerate(responses):
            self.assertEqual(commands[index], response['result'])

    def test_config_with_single_command(self):
        command = random_string()
        self.node.run_commands = Mock(return_value=[{}, {}])
        result = self.node.config(command)
        self.assertEqual(result, [{}])

    def test_config_with_multiple_commands(self):
        commands = [random_string(), random_string()]
        self.node.run_commands = Mock(return_value=[{}, {}, {}])
        result = self.node.config(commands)
        self.assertEqual(result, [{}, {}])

    def test_config_with_single_multiline(self):
        command = ('banner login MULTILINE:This is a new banner\n'
                   'with different lines!!!')

        self.node.run_commands = Mock(return_value=[{}, {}])
        result = self.node.config(command)
        self.assertEqual(result, [{}])

    def test_config_with_multiple_multilines(self):
        commands = [random_string(),
                    ('banner login MULTILINE:This is a new banner\n'
                     'with different lines!!!'),
                    random_string()]

        self.node.run_commands = Mock(return_value=[{}, {}, {}, {}])
        result = self.node.config(commands)
        self.assertEqual(result, [{}, {}, {}])

    def test_get_config(self):
        config = [dict(output='test\nconfig')]
        self.node.run_commands = Mock(return_value=config)
        result = self.node.get_config()
        self.assertIsInstance(result, list)

    def test_get_config_as_string(self):
        config = [dict(output='test\nconfig')]
        self.node.run_commands = Mock(return_value=config)
        result = self.node.get_config(as_string=True)
        self.assertIsInstance(result, str)

    def test_get_config_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.node.get_config('invalid-config')

    def test_api_autoloader(self):
        result = self.node.api('system')
        self.assertIsNotNone(result)

    def test_enable_authentication(self):
        self.assertIsNone(self.node._enablepwd)
        self.node.enable_authentication('test')
        self.assertEqual(self.node._enablepwd, 'test')

    def test_enable_with_config_statement(self):
        cmds = ['show version', 'configure', 'hostname foo']
        with self.assertRaises(TypeError):
            self.node.enable(cmds)


class TestClient(unittest.TestCase):

    def setUp(self):
        if 'EAPI_CONF' in os.environ:
            del os.environ['EAPI_CONF']
        imp.reload(pyeapi.client)

    def test_load_config_for_connection_with_filename(self):
        conf = get_fixture('eapi.conf')
        pyeapi.client.load_config(filename=conf)
        cfg = pyeapi.client.config.get_connection('test1')
        self.assertEqual(cfg['host'], '192.168.1.16')
        self.assertEqual(cfg['username'], 'eapi')
        self.assertEqual(cfg['password'], 'password')
        self.assertEqual(cfg['enablepwd'], 'enablepwd')

    def test_load_config_for_connection_with_env(self):
        os.environ['EAPI_CONF'] = get_fixture('eapi.conf')
        pyeapi.client.load_config(random_string())
        cfg = pyeapi.client.config.get_connection('test1')
        self.assertEqual(cfg['host'], '192.168.1.16')
        self.assertEqual(cfg['username'], 'eapi')
        self.assertEqual(cfg['password'], 'password')
        self.assertEqual(cfg['enablepwd'], 'enablepwd')

    def test_load_config(self):
        conf = get_fixture('eapi.conf')
        pyeapi.client.load_config(conf)
        self.assertEqual(len(pyeapi.client.config.sections()), 3)
        for name in ['localhost', 'test1', 'test2']:
            name = 'connection:%s' % name
            self.assertIn(name, pyeapi.client.config.sections())

    def test_load_config_empty_conf(self):
        conf = get_fixture('empty.conf')
        pyeapi.client.load_config(filename=conf)
        conns = pyeapi.client.config.connections
        self.assertEqual(conns, ['localhost'])

    def test_load_config_yaml(self):
        conf = get_fixture('eapi.conf.yaml')
        pyeapi.client.load_config(filename=conf)
        conns = pyeapi.client.config.connections
        self.assertEqual(conns, ['localhost'])

    def test_load_config_env_path(self):
        os.environ['EAPI_CONF'] = get_fixture('env_path.conf')
        pyeapi.client.config.autoload()
        self.assertIn('connection:env_path', pyeapi.client.config.sections())

    def test_config_always_has_default_connection(self):
        conf = '/invalid.conf'
        pyeapi.client.load_config(conf)
        self.assertEqual(len(pyeapi.client.config.sections()), 1)
        name = 'connection:localhost'
        self.assertIn(name, pyeapi.client.config.sections())

    def test_connections_property(self):
        conf = get_fixture('eapi.conf')
        pyeapi.client.load_config(conf)
        connections = ['test1', 'test2', 'localhost']
        result = pyeapi.client.config.connections
        self.assertEqual(sorted(connections), sorted(result))

    def test_missing_connection_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            pyeapi.client.connect_to('invalid')

    def test_config_for_replaces_host_w_name(self):
        conf = get_fixture('nohost.conf')
        pyeapi.client.load_config(conf)
        cfg = pyeapi.config_for('test')
        self.assertEqual(cfg['host'], 'test')

    def test_hosts_for_tag_returns_none(self):
        result = pyeapi.client.hosts_for_tag(random_string())
        self.assertIsNone(result)

    def test_hosts_for_tag_returns_names(self):
        conf = get_fixture('eapi.conf')
        pyeapi.client.load_config(conf)
        result = pyeapi.client.hosts_for_tag('tag1')
        self.assertEqual(sorted(['test1', 'test2']), sorted(result))

    @patch('pyeapi.client.make_connection')
    def test_connect_types(self, connection):
        transports = list(pyeapi.client.TRANSPORTS.keys())
        kwargs = dict(host='localhost', username='admin', password='',
                      port=None, key_file=None, cert_file=None,
                      ca_file=None, timeout=60, context=None)

        for transport in transports:
            pyeapi.client.connect(transport)
            connection.assert_called_with(transport, **kwargs)

    def test_make_connection_raises_typeerror(self):
        with self.assertRaises(TypeError):
            pyeapi.client.make_connection('invalid')

    def test_node_str_returns(self):
        node = pyeapi.client.Node(None)
        self.assertIsNotNone(str(node))

    def test_node_repr_returns(self):
        node = pyeapi.client.Node(None)
        self.assertIsNotNone(repr(node))

    def test_node_hasattr_connection(self):
        node = pyeapi.client.Node(None)
        self.assertTrue(hasattr(node, 'connection'))

    def test_node_returns_running_config(self):
        node = pyeapi.client.Node(None)
        get_config_mock = Mock(name='get_config')
        config_file = open(get_fixture('running_config.text'))
        config = config_file.read()
        config_file.close()
        get_config_mock.return_value = config
        node.get_config = get_config_mock
        self.assertIsInstance(node.running_config, str)

    def test_node_returns_startup_config(self):
        node = pyeapi.client.Node(None)
        get_config_mock = Mock(name='get_config')
        config_file = open(get_fixture('running_config.text'))
        config = config_file.read()
        config_file.close()
        get_config_mock.return_value = config
        node.get_config = get_config_mock
        self.assertIsInstance(node.startup_config, str)

    def test_node_returns_cached_startup_config(self):
        node = pyeapi.client.Node(None)
        config_file = open(get_fixture('running_config.text'))
        config = config_file.read()
        config_file.close()
        node._startup_config = config
        self.assertEqual(node.startup_config, config)

    def test_node_returns_version(self):
        node = pyeapi.client.Node(None)
        version = '4.17.1.1F-3512479.41711F (engineering build)'
        node.enable = Mock()
        node.enable.return_value = [{'result': {'version': version,
                                                'modelName': 'vEOS'}}]
        self.assertIsInstance(node.version, str)
        self.assertEqual(node.version, version)

    def test_node_returns_cached_version(self):
        node = pyeapi.client.Node(None)
        node._version = '4.16.7R'
        self.assertEqual(node.version, '4.16.7R')

    def test_node_returns_version_number(self):
        node = pyeapi.client.Node(None)
        version = '4.17.1.1F-3512479.41711F (engineering build)'
        node.enable = Mock()
        node.enable.return_value = [{'result': {'version': version,
                                                'modelName': 'vEOS'}}]
        self.assertIsInstance(node.version_number, str)
        self.assertIn(node.version_number, version)

    def test_node_returns_cached_version_number(self):
        node = pyeapi.client.Node(None)
        node._version_number = '4.16.7'
        self.assertEqual(node.version_number, '4.16.7')

    def test_node_returns_model(self):
        node = pyeapi.client.Node(None)
        version = '4.17.1.1F-3512479.41711F (engineering build)'
        model = 'DCS-7260QX-64-F'
        node.enable = Mock()
        node.enable.return_value = [{'result': {'version': version,
                                                'modelName': model}}]
        self.assertIsInstance(node.model, str)
        self.assertIn(node.model, model)

    def test_node_returns_cached_model(self):
        node = pyeapi.client.Node(None)
        node._model = '7777'
        self.assertEqual(node.model, '7777')

    def test_connect_default_type(self):
        transport = Mock()
        with patch.dict(pyeapi.client.TRANSPORTS, {'https': transport}):
            pyeapi.client.connect()
            kwargs = dict(host='localhost', username='admin', password='',
                          port=None, key_file=None, cert_file=None,
                          ca_file=None, timeout=60, context=None)
            transport.assert_called_once_with(**kwargs)

    def test_connect_return_node(self):
        transport = Mock()
        with patch.dict(pyeapi.client.TRANSPORTS, {'https': transport}):
            conf = get_fixture('eapi.conf')
            pyeapi.client.load_config(filename=conf)
            node = pyeapi.client.connect(host='192.168.1.16', username='eapi',
                                         password='password', port=None,
                                         timeout=60, return_node=True)
            kwargs = dict(host='192.168.1.16', username='eapi',
                          password='password', port=None, key_file=None,
                          cert_file=None, ca_file=None, timeout=60,
                          context=None)
            transport.assert_called_once_with(**kwargs)
            self.assertIsNone(node._enablepwd)

    def test_connect_return_node_enablepwd(self):
        transport = Mock()
        with patch.dict(pyeapi.client.TRANSPORTS, {'https': transport}):
            conf = get_fixture('eapi.conf')
            pyeapi.client.load_config(filename=conf)
            node = pyeapi.client.connect(host='192.168.1.16', username='eapi',
                                         password='password', port=None,
                                         timeout=60, enablepwd='enablepwd',
                                         return_node=True)
            kwargs = dict(host='192.168.1.16', username='eapi',
                          password='password', port=None, key_file=None,
                          cert_file=None, ca_file=None, timeout=60,
                          context=None)
            transport.assert_called_once_with(**kwargs)
            self.assertEqual(node._enablepwd, 'enablepwd')

    def test_connect_to_with_config(self):
        transport = Mock()
        with patch.dict(pyeapi.client.TRANSPORTS, {'https': transport}):
            conf = get_fixture('eapi.conf')
            pyeapi.client.load_config(filename=conf)
            node = pyeapi.client.connect_to('test1')
            kwargs = dict(host='192.168.1.16', username='eapi',
                          password='password', port=None, key_file=None,
                          cert_file=None, ca_file=None, timeout=60,
                          context=None)
            transport.assert_called_once_with(**kwargs)
            self.assertEqual(node._enablepwd, 'enablepwd')


if __name__ == '__main__':
    unittest.main()
