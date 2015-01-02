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

from testlib import random_int, random_string, get_fixture
from systestlib import DutSystemTest

import pyeapi.client

class TestResourceInterfaces(DutSystemTest):

    def test_get(self):
        for dut in self.duts:
            dut.config(['default interface Ethernet1', 'interface Ethernet1',
                        'description this is a test',
                        'flowcontrol send off',
                        'flowcontrol receive on',
                        'no sflow enable'])
            result = dut.resource('interfaces').get('Ethernet1')
            self.assertIsInstance(result, dict)
            self.assertEqual(result['description'], 'this is a test')
            self.assertFalse(result['shutdown'])
            self.assertEqual(result['flowcontrol_send'], 'off')
            self.assertEqual(result['flowcontrol_receive'], 'on')
            self.assertFalse(result['sflow'])

    def test_getall(self):
        for dut in self.duts:
            dut.config(['default interface et1-7'])
            result = dut.resource('interfaces').getall()
            self.assertIsInstance(result, dict)
            for intf in ['Ethernet1', 'Management1']:
                self.assertIn(intf, result)

    def test_create_and_return_true(self):
        for dut in self.duts:
            dut.config('no interface Loopback0')
            result = dut.resource('interfaces').create('Loopback0')
            self.assertTrue(result)
            config = dut.enable('show interfaces')
            self.assertIn('Loopback0', config[0]['interfaces'])

    def test_create_and_return_false(self):
        for dut in self.duts:
            result = dut.resource('interfaces').create('Ethernet1')
            self.assertFalse(result)

    def test_delete_and_return_true(self):
        for dut in self.duts:
            dut.config('interface Loopback0')
            result = dut.resource('interfaces').delete('Loopback0')
            self.assertTrue(result)
            config = dut.enable('show interfaces')
            self.assertNotIn('Loopback0', config[0]['interfaces'])

    def test_delete_and_return_false(self):
        for dut in self.duts:
            result = dut.resource('interfaces').delete('Ethernet1')
            self.assertFalse(result)

    def test_default(self):
        for dut in self.duts:
            dut.config(['interface Ethernet1', 'shutdown'])
            result = dut.resource('interfaces').default('Ethernet1')
            self.assertTrue(result)
            config = dut.enable('show interfaces Ethernet1')
            config = config[0]['interfaces']['Ethernet1']
            self.assertEqual(config['interfaceStatus'], 'connected')

    def test_set_description(self):
        for dut in self.duts:
            text = random_string()
            result = dut.resource('interfaces').set_description('Ethernet1', text)
            self.assertTrue(result)
            config = dut.enable('show interfaces Ethernet1')
            self.assertEqual(config[0]['interfaces']['Ethernet1']['description'],
                            text)

    def test_set_sflow_enable(self):
        for dut in self.duts:
            dut.config(['interface Ethernet1', 'no sflow enable'])
            result = dut.resource('interfaces').set_sflow('Ethernet1', True)
            self.assertTrue(result)
            config = dut.enable('show running-config interfaces Ethernet1',
                                    'text')
            self.assertNotIn('no sflow enable', config[0]['output'])

    def test_set_sflow_disable(self):
        for dut in self.duts:
            dut.config('default interface Ethernet1')
            result = dut.resource('interfaces').set_sflow('Ethernet1', False)
            self.assertTrue(result)
            config = dut.enable('show running-config interfaces Ethernet1',
                                    'text')
            self.assertIn('no sflow enable', config[0]['output'])

if __name__ == '__main__':
    unittest.main()
