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
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))

from mock import patch

from testlib import get_fixture, random_string

import pyeapi.client

class TestClient(unittest.TestCase):

    def setUp(self):
        reload(pyeapi.client)
        self.assertEqual(pyeapi.client.config, dict())

    def test_load_config_for_connection_with_filename(self):
        conf = get_fixture('pyeapi.conf')
        result = pyeapi.client.load_config(filename=conf)
        cfg = pyeapi.client.config['connection:test1']
        self.assertEqual(cfg['host'], '192.168.1.16')
        self.assertEqual(cfg['username'], 'eapi')
        self.assertEqual(cfg['password'], 'password')

    def test_load_config_for_connection_with_env(self):
        os.environ['PYEAPI_CONF'] = get_fixture('pyeapi.conf')
        result = pyeapi.client.load_config()
        cfg = pyeapi.client.config['connection:test1']
        self.assertEqual(cfg['host'], '192.168.1.16')
        self.assertEqual(cfg['username'], 'eapi')
        self.assertEqual(cfg['password'], 'password')

    def test_load_config(self):
        conf = get_fixture('pyeapi.conf')
        result = pyeapi.client.load_config(conf)
        self.assertEqual(len(pyeapi.client.config), 3)
        for name in ['localhost', 'test1', 'test2']:
            name = 'connection:%s' % name
            self.assertIn(name, pyeapi.client.config)

    @patch('pyeapi.client.Connection')
    def test_connect(self, connection):
        result = pyeapi.client.connect()
        kwargs = dict(host='localhost', username='admin', password='',
                      enablepwd='', use_ssl=True, port=None)
        connection.assert_called_once_with(**kwargs)

    @patch('pyeapi.client.Connection')
    def test_connect_to_with_config(self, connection):
        conf = get_fixture('pyeapi.conf')
        pyeapi.client.load_config(filename=conf)
        result = pyeapi.client.connect_to('test1')
        kwargs = dict(host='192.168.1.16', username='eapi', password='password',
                      enablepwd='', use_ssl=False, port=None)
        connection.assert_called_once_with(**kwargs)



if __name__ == '__main__':
    unittest.main()
