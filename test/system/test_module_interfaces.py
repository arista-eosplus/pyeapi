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

class TestModuleInterfaces(unittest.TestCase):

    def setUp(self):
        self.dut = pyeapi.client.connect('192.168.1.16', username='eapi',
                                         password='password', use_ssl=False)
        self.module = self.dut.module('interfaces')

    def test_get(self):
        self.dut.config(['default interface Ethernet1'])
        result = self.module.get('Ethernet1')
        self.assertIsInstance(result, dict)
        self.assertEqual(result['description'], '')
        self.assertFalse(result['shutdown'])
        self.assertEqual(result['flowcontrol_send'], 'off')
        self.assertEqual(result['flowcontrol_receive'], 'off')
        self.assertTrue(result['sflow'])

    def test_getall(self):
        self.dut.config(['default interface et1-7'])
        result = self.module.getall()
        self.assertIsInstance(result, dict)
        for intf in ['Ethernet1', 'Management1']:
            self.assertIn(intf, result)

    def test_create_and_return_true(self):
        self.dut.config('no interface Loopback0')
        result = self.module.create('Loopback0')
        self.assertTrue(result)
        config = self.dut.enable('show interfaces')
        self.assertIn('Loopback0', config[0]['interfaces'])

    def test_create_and_return_false(self):
        result = self.module.create('Ethernet1')
        self.assertFalse(result)

    def test_delete_and_return_true(self):
        self.dut.config('interface Loopback0')
        result = self.module.delete('Loopback0')
        self.assertTrue(result)
        config = self.dut.enable('show interfaces')
        self.assertNotIn('Loopback0', config[0]['interfaces'])

    def test_delete_and_return_false(self):
        result = self.module.delete('Ethernet1')
        self.assertFalse(result)

    def test_default(self):
        self.dut.config(['interface Ethernet1', 'shutdown'])
        result = self.module.default('Ethernet1')
        self.assertTrue(result)
        config = self.dut.enable('show interfaces Ethernet1')
        config = config[0]['interfaces']['Ethernet1']
        self.assertEqual(config['interfaceStatus'], 'connected')

    def test_set_description(self):
        text = random_string()
        result = self.module.set_description('Ethernet1', text)
        self.assertTrue(result)
        config = self.dut.enable('show interfaces Ethernet1')
        self.assertEqual(config[0]['interfaces']['Ethernet1']['description'],
                         text)

    def test_set_sflow_enable(self):
        self.dut.config(['interface Ethernet1', 'no sflow enable'])
        result = self.module.set_sflow('Ethernet1', True)
        self.assertTrue(result)
        config = self.dut.enable('show running-config interfaces Ethernet1',
                                 'text')
        self.assertNotIn('no sflow enable', config[0]['output'])

    def test_set_sflow_disable(self):
        self.dut.config('default interface Ethernet1')
        result = self.module.set_sflow('Ethernet1', False)
        self.assertTrue(result)
        config = self.dut.enable('show running-config interfaces Ethernet1',
                                 'text')
        self.assertIn('no sflow enable', config[0]['output'])














if __name__ == '__main__':
    unittest.main()
