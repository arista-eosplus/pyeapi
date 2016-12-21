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

from systestlib import DutSystemTest, random_interface


class TestApiSwitchports(DutSystemTest):

    def test_get(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config('default interface %s' % intf)
            result = dut.api('switchports').get(intf)
            self.assertIsInstance(result, dict)
            self.assertEqual(result['mode'], 'access')
            self.assertEqual(result['access_vlan'], '1')
            self.assertEqual(result['trunk_native_vlan'], '1')
            self.assertEqual(result['trunk_allowed_vlans'], '1-4094')

    def test_get_returns_none(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config(['default interface %s' % intf, 'interface %s' % intf,
                        'no switchport'])
            result = dut.api('switchports').get(intf)
            self.assertIsNone(result)

    def test_getall(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config('default interface %s' % intf)
            result = dut.api('switchports').getall()
            self.assertIsInstance(result, dict, 'dut=%s' % dut)
            self.assertIn(intf, result, 'dut=%s' % dut)

    def test_create_and_return_true(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config(['default interface %s' % intf, 'interface %s' % intf,
                        'no switchport'])
            result = dut.api('switchports').create(intf)
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show running-config interfaces %s' %
                                      intf, 'text')
            self.assertNotIn('no switchport', config[0]['output'],
                             'dut=%s' % dut)
            dut.config('default interface %s' % intf)

    def test_delete_and_return_true(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config('default interface %s' % intf)
            result = dut.api('switchports').delete(intf)
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show running-config interfaces %s' %
                                      intf, 'text')
            self.assertIn('no switchport', config[0]['output'], 'dut=%s' % dut)
            dut.config('default interface %s' % intf)

    def test_set_access_vlan_to_value(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config(['default interface %s' % intf, 'vlan 100'])
            resource = dut.api('switchports')
            result = resource.set_access_vlan(intf, '100')
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show running-config interfaces %s' %
                                      intf, 'text')
            self.assertIn('switchport access vlan 100', config[0]['output'],
                          'dut=%s' % dut)
            dut.config('default interface %s' % intf)

    def test_set_trunk_native_vlan(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config(['default interface %s' % intf, 'interface %s' % intf,
                        'switchport mode trunk', 'vlan 100'])
            resource = dut.api('switchports')
            result = resource.set_trunk_native_vlan(intf, '100')
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show running-config interfaces %s' %
                                      intf, 'text')
            self.assertIn('switchport trunk native vlan 100',
                          config[0]['output'], 'dut=%s' % dut)
            dut.config('default interface %s' % intf)

    def test_set_trunk_allowed_vlans(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config(['default interface %s' % intf, 'interface %s' % intf,
                        'switchport mode trunk'])
            resource = dut.api('switchports')
            result = resource.set_trunk_allowed_vlans(intf, '1,10,100')
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show running-config interfaces %s' %
                                      intf, 'text')
            self.assertIn('switchport trunk allowed vlan 1,10,100',
                          config[0]['output'], 'dut=%s' % dut)
            dut.config('default interface %s' % intf)


if __name__ == '__main__':
    unittest.main()
