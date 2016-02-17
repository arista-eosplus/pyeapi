#
# Copyright (c) 2015, Arista Networks, Inc.
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

from systestlib import DutSystemTest

VIRT_NULL = 'no ip virtual-router mac-address'
VIRT_ENTRY_A = 'ip virtual-router mac-address 00:11:22:33:44:55'
VIRT_ENTRY_B = 'ip virtual-router mac-address 00:11:22:33:44:56'
VIRT_ENTRY_C = 'ip virtual-router mac-address 00:11:22:33:44:57'
IP_CMD = 'ip virtual-router address'

class TestApiVarp(DutSystemTest):

    def test_basic_get(self):
        for dut in self.duts:
            dut.config([VIRT_NULL])
            response = dut.api('varp').get()
            self.assertIsNotNone(response)

    def test_get_with_value(self):
        for dut in self.duts:
            dut.config([VIRT_NULL, VIRT_ENTRY_A])
            response = dut.api('varp').get()
            self.assertIsNotNone(response)
            self.assertEqual(response['mac_address'], '00:11:22:33:44:55')

    def test_get_none(self):
        for dut in self.duts:
            dut.config([VIRT_NULL])
            response = dut.api('varp').get()
            self.assertIsNotNone(response)
            self.assertEqual(response['mac_address'], None)

    def test_set_mac_address_with_value(self):
        for dut in self.duts:
            dut.config([VIRT_NULL])
            api = dut.api('varp')
            self.assertNotIn(VIRT_ENTRY_A, api.config)
            result = dut.api('varp').set_mac_address('00:11:22:33:44:55')
            self.assertTrue(result)
            self.assertIn(VIRT_ENTRY_A, api.config)

    def test_change_mac_address(self):
        for dut in self.duts:
            dut.config([VIRT_NULL, VIRT_ENTRY_A])
            api = dut.api('varp')
            self.assertIn(VIRT_ENTRY_A, api.config)
            result = dut.api('varp').set_mac_address('00:11:22:33:44:56')
            self.assertTrue(result)
            self.assertIn(VIRT_ENTRY_B, api.config)

    def test_remove_mac_address(self):
        for dut in self.duts:
            dut.config([VIRT_NULL, VIRT_ENTRY_A])
            api = dut.api('varp')
            self.assertIn(VIRT_ENTRY_A, api.config)
            result = dut.api('varp').set_mac_address(disable=True)
            self.assertTrue(result)
            self.assertNotIn(VIRT_ENTRY_A, api.config)

    def test_set_mac_address_with_bad_value(self):
        for dut in self.duts:
            dut.config([VIRT_NULL])
            api = dut.api('varp')
            self.assertNotIn(VIRT_ENTRY_A, api.config)

            with self.assertRaises(ValueError):
                dut.api('varp').set_mac_address('0011.2233.4455')

class TestApiVarpInterfaces(DutSystemTest):

    def test_set_virtual_addr_with_values_clean(self):
        for dut in self.duts:
            dut.config(['no interface Vlan1000', 'interface Vlan1000',
                        'ip address 1.1.1.1/24'])
            api = dut.api('varp')
            self.assertNotIn('ip virtual-router address 1.1.1.2',
                             api.get_block('interface Vlan1000'))
            result = dut.api('varp').interfaces.set_addresses('Vlan1000',
                                                              ['1.1.1.2',
                                                               '1.1.1.3'])
            self.assertTrue(result)
            self.assertIn('ip virtual-router address 1.1.1.2',
                          api.get_block('interface Vlan1000'))
            self.assertIn('ip virtual-router address 1.1.1.3',
                          api.get_block('interface Vlan1000'))

    def test_set_virtual_addr_with_values_dirty(self):
        for dut in self.duts:
            dut.config(['no interface Vlan1000', 'interface Vlan1000',
                        'ip address 1.1.1.1/24',
                        'ip virtual-router address 1.1.1.20'])
            api = dut.api('varp')
            self.assertIn('ip virtual-router address 1.1.1.20',
                          api.get_block('interface Vlan1000'))
            result = dut.api('varp').interfaces.set_addresses('Vlan1000',
                                                              ['1.1.1.2',
                                                               '1.1.1.3'])
            self.assertTrue(result)
            self.assertIn('ip virtual-router address 1.1.1.2',
                          api.get_block('interface Vlan1000'))
            self.assertIn('ip virtual-router address 1.1.1.3',
                          api.get_block('interface Vlan1000'))
            self.assertNotIn('ip virtual-router address 1.1.1.20',
                             api.get_block('interface Vlan1000'))

    def test_default_virtual_addrs(self):
        for dut in self.duts:
            dut.config(['no interface Vlan1000', 'interface Vlan1000',
                        'ip address 1.1.1.1/24',
                        'ip virtual-router address 1.1.1.20',
                        'ip virtual-router address 1.1.1.21'])
            api = dut.api('varp')
            self.assertIn('ip virtual-router address 1.1.1.20',
                          api.get_block('interface Vlan1000'))
            self.assertIn('ip virtual-router address 1.1.1.21',
                          api.get_block('interface Vlan1000'))
            result = dut.api('varp').interfaces.set_addresses('Vlan1000',
                                                              default=True)
            self.assertTrue(result)
            self.assertNotIn('ip virtual-router address 1.1.1.20',
                             api.get_block('interface Vlan1000'))
            self.assertNotIn('ip virtual-router address 1.1.1.21',
                             api.get_block('interface Vlan1000'))

    def test_negate_virtual_addrs(self):
        for dut in self.duts:
            dut.config(['no interface Vlan1000', 'interface Vlan1000',
                        'ip address 1.1.1.1/24',
                        'ip virtual-router address 1.1.1.20',
                        'ip virtual-router address 1.1.1.21'])
            api = dut.api('varp')
            self.assertIn('ip virtual-router address 1.1.1.20',
                          api.get_block('interface Vlan1000'))
            self.assertIn('ip virtual-router address 1.1.1.21',
                          api.get_block('interface Vlan1000'))
            result = dut.api('varp').interfaces.set_addresses('Vlan1000',
                                                              addresses=None)
            self.assertTrue(result)
            self.assertNotIn('ip virtual-router address 1.1.1.20',
                             api.get_block('interface Vlan1000'))
            self.assertNotIn('ip virtual-router address 1.1.1.21',
                             api.get_block('interface Vlan1000'))

    def test_negate_virtual_addrs_with_disable(self):
        for dut in self.duts:
            dut.config(['no interface Vlan1000', 'interface Vlan1000',
                        'ip address 1.1.1.1/24',
                        'ip virtual-router address 1.1.1.20',
                        'ip virtual-router address 1.1.1.21'])
            api = dut.api('varp')
            self.assertIn('ip virtual-router address 1.1.1.20',
                          api.get_block('interface Vlan1000'))
            self.assertIn('ip virtual-router address 1.1.1.21',
                          api.get_block('interface Vlan1000'))
            result = dut.api('varp').interfaces.set_addresses('Vlan1000',
                                                              disable=True)
            self.assertTrue(result)
            self.assertNotIn('ip virtual-router address 1.1.1.20',
                             api.get_block('interface Vlan1000'))
            self.assertNotIn('ip virtual-router address 1.1.1.21',
                             api.get_block('interface Vlan1000'))

    def test_empty_list_virtual_addrs(self):
        for dut in self.duts:
            dut.config(['no interface Vlan1000', 'interface Vlan1000',
                        'ip address 1.1.1.1/24',
                        'ip virtual-router address 1.1.1.20',
                        'ip virtual-router address 1.1.1.21'])
            api = dut.api('varp')
            self.assertIn('ip virtual-router address 1.1.1.20',
                          api.get_block('interface Vlan1000'))
            self.assertIn('ip virtual-router address 1.1.1.21',
                          api.get_block('interface Vlan1000'))
            result = dut.api('varp').interfaces.set_addresses('Vlan1000',
                                                              addresses=[])
            self.assertTrue(result)
            self.assertNotIn('ip virtual-router address 1.1.1.20',
                             api.get_block('interface Vlan1000'))
            self.assertNotIn('ip virtual-router address 1.1.1.21',
                             api.get_block('interface Vlan1000'))

    def test_no_attr_virtual_addrs(self):
        for dut in self.duts:
            dut.config(['no interface Vlan1000', 'interface Vlan1000',
                        'ip address 1.1.1.1/24',
                        'ip virtual-router address 1.1.1.20',
                        'ip virtual-router address 1.1.1.21'])
            api = dut.api('varp')
            self.assertIn('ip virtual-router address 1.1.1.20',
                          api.get_block('interface Vlan1000'))
            self.assertIn('ip virtual-router address 1.1.1.21',
                          api.get_block('interface Vlan1000'))
            result = dut.api('varp').interfaces.set_addresses('Vlan1000')
            self.assertTrue(result)
            self.assertNotIn('ip virtual-router address 1.1.1.20',
                             api.get_block('interface Vlan1000'))
            self.assertNotIn('ip virtual-router address 1.1.1.21',
                             api.get_block('interface Vlan1000'))

if __name__ == '__main__':
    unittest.main()
