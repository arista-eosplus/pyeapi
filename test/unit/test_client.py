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

sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))

from mock import Mock, patch

from testlib import get_fixture, random_string, random_int

import pyeapi.client

DEFAULT_CONFIG = {'connection:localhost': dict(transport='socket')}


class TestNode(unittest.TestCase):

    def setUp(self):
        self.connection = Mock()
        self.node = pyeapi.client.Node(self.connection)

    def test_enable_with_single_command(self):
        command = random_string()
        response = ['enable', command]

        self.connection.execute.return_value = {'result': list(response)}
        result = self.node.enable(command)

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

        for cmd in commands:
            self.connection.execute.assert_call_with(['enable', cmd], 'json')

        for index, response in enumerate(responses):
            self.assertEqual(commands[index], response['result'])


class TestClient(unittest.TestCase):

    def setUp(self):
        if 'EAPI_CONF' in os.environ:
            del os.environ['EAPI_CONF']
        reload(pyeapi.client)

    def test_load_config_for_connection_with_filename(self):
        conf = get_fixture('eapi.conf')
        pyeapi.client.load_config(filename=conf)
        cfg = pyeapi.client.config.get_connection('test1')
        self.assertEqual(cfg['host'], '192.168.1.16')
        self.assertEqual(cfg['username'], 'eapi')
        self.assertEqual(cfg['password'], 'password')

    def test_load_config_for_connection_with_env(self):
        os.environ['EAPI_CONF'] = get_fixture('eapi.conf')
        pyeapi.client.load_config(random_string())
        cfg = pyeapi.client.config.get_connection('test1')
        self.assertEqual(cfg['host'], '192.168.1.16')
        self.assertEqual(cfg['username'], 'eapi')
        self.assertEqual(cfg['password'], 'password')

    def test_load_config(self):
        conf = get_fixture('eapi.conf')
        pyeapi.client.load_config(conf)
        self.assertEqual(len(pyeapi.client.config.sections()), 3)
        for name in ['localhost', 'test1', 'test2']:
            name = 'connection:%s' % name
            self.assertIn(name, pyeapi.client.config.sections())

    def test_config_for_replaces_host_w_name(self):
        conf = get_fixture('nohost.conf')
        pyeapi.client.load_config(conf)
        cfg = pyeapi.config_for('test')
        self.assertEqual(cfg['host'], 'test')

    @patch('pyeapi.client.make_connection')
    def test_connect_types(self, connection):
        transports = pyeapi.client.TRANSPORTS.keys()
        kwargs = dict(host='localhost', username='admin', password='',
                      port=None)

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
        config = open(get_fixture('running_config.text')).read()
        get_config_mock.return_value = config
        node.get_config = get_config_mock
        self.assertIsInstance(node.running_config, str)

    def test_node_returns_startup_config(self):
        node = pyeapi.client.Node(None)
        get_config_mock = Mock(name='get_config')
        config = open(get_fixture('running_config.text')).read()
        get_config_mock.return_value = config
        node.get_config = get_config_mock
        self.assertIsInstance(node.startup_config, str)

    def test_connect_default_type(self):
        transport = Mock()
        with patch.dict(pyeapi.client.TRANSPORTS, {'https': transport}):
            pyeapi.client.connect()
            kwargs = dict(host='localhost', username='admin', password='',
                          port=None)
            transport.assert_called_once_with(**kwargs)

    def test_connect_to_with_config(self):
        transport = Mock()
        with patch.dict(pyeapi.client.TRANSPORTS, {'https': transport}):
            conf = get_fixture('eapi.conf')
            pyeapi.client.load_config(filename=conf)
            pyeapi.client.connect_to('test1')
            kwargs = dict(host='192.168.1.16', username='eapi',
                          password='password', port=None)
            transport.assert_called_once_with(**kwargs)




if __name__ == '__main__':
    unittest.main()
