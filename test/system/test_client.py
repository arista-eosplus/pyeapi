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
import os
import unittest

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))

from testlib import random_int, random_string

import pyeapi.client

class TestClient(unittest.TestCase):

    def test_enable_single_command(self):
        dut = pyeapi.client.connect('192.168.1.16', username='eapi',
                                    password='password', use_ssl=False)
        result = dut.enable('show version')
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

    def test_enable_multiple_commands(self):
        dut = pyeapi.client.connect('192.168.1.16', username='eapi',
                                    password='password', use_ssl=False)
        commands = list()
        for i in range(1, random_int(10, 200)):
            commands.append('show version')
        result = dut.enable(commands[:])
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), len(commands))

    def test_config_single_command(self):
        dut = pyeapi.client.connect('192.168.1.16', username='eapi',
                                    password='password', use_ssl=False)

        hostname = 'hostname %s' % random_string(5, 50)
        result = dut.config(hostname)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {})

        result = dut.enable('show running-config | include %s$' % hostname,
                            'text')
        self.assertEqual(result[0]['output'].strip(), hostname)

    def test_config_multiple_commands(self):
        dut = pyeapi.client.connect('192.168.1.16', username='eapi',
                                    password='password', use_ssl=False)

        commands = list()
        for i in range(1, random_int(10, 200)):
            commands.append('hostname %s' % random_string(5, 20))
        result = dut.config(commands[:])
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), len(commands))

    def test_multiple_requests(self):
        dut = pyeapi.client.connect('192.168.1.16', username='eapi',
                                    password='password', use_ssl=False)
        for i in range(1, random_int(10, 200)):
            result = dut.enable('show version')
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)


if __name__ == '__main__':
    unittest.main()
