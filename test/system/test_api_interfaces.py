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

from testlib import random_string
from systestlib import DutSystemTest, random_interface


class TestResourceInterfaces(DutSystemTest):

    def test_get(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config(['default interface %s' % intf,
                        'interface %s' % intf,
                        'description this is a test',
                        'flowcontrol send off',
                        'flowcontrol receive on',
                        'no sflow enable'])
            result = dut.api('interfaces').get(intf)

            self.assertIsInstance(result, dict)
            self.assertEqual(result['description'], 'this is a test')
            self.assertFalse(result['shutdown'])
            self.assertEqual(result['flowcontrol_send'], 'off')
            self.assertEqual(result['flowcontrol_receive'], 'on')
            self.assertFalse(result['sflow'])

    def test_getall(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config(['default interface %s' % intf])
            result = dut.api('interfaces').getall()
            self.assertIsInstance(result, dict)
            for intf in [intf, 'Management1']:
                self.assertIn(intf, result)

    def test_create_and_return_true(self):
        for dut in self.duts:
            dut.config('no interface Loopback0')
            result = dut.api('interfaces').create('Loopback0')
            self.assertTrue(result)
            config = dut.run_commands('show interfaces')
            self.assertIn('Loopback0', config[0]['interfaces'])

    def test_create_ethernet_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            for dut in self.duts:
                dut.api('interfaces').create(random_interface(dut))

    def test_delete_and_return_true(self):
        for dut in self.duts:
            dut.config('interface Loopback0')
            result = dut.api('interfaces').delete('Loopback0')
            self.assertTrue(result)
            config = dut.run_commands('show interfaces')
            self.assertNotIn('Loopback0', config[0]['interfaces'])

    def test_delete_ethernet_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            for dut in self.duts:
                dut.api('interfaces').delete(random_interface(dut))

    def test_default(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config(['interface %s' % intf, 'shutdown'])
            result = dut.api('interfaces').default(intf)
            self.assertTrue(result)
            config = dut.run_commands('show interfaces %s' % intf)
            config = config[0]['interfaces'][intf]
            self.assertEqual(config['interfaceStatus'], 'connected')

    def test_set_description(self):
        for dut in self.duts:
            text = random_string()
            intf = random_interface(dut)
            result = dut.api('interfaces').set_description(intf, text)
            self.assertTrue(result)
            config = dut.run_commands('show interfaces %s' % intf)
            config = config[0]['interfaces'][intf]
            self.assertEqual(config['description'], text)

    def test_set_sflow_enable(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config(['interface %s' % intf, 'no sflow enable'])
            result = dut.api('interfaces').set_sflow(intf, True)
            self.assertTrue(result)
            config = dut.run_commands('show running-config interfaces %s' % intf,
                                'text')
            self.assertNotIn('no sflow enable', config[0]['output'])

    def test_set_sflow_disable(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config('default interface %s' % intf)
            result = dut.api('interfaces').set_sflow(intf, False)
            self.assertTrue(result)
            config = dut.run_commands('show running-config interfaces %s' % intf,
                                'text')
            self.assertIn('no sflow enable', config[0]['output'])

if __name__ == '__main__':
    unittest.main()
