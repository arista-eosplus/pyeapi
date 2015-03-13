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

class TestApiStpInterfaces(DutSystemTest):

    def test_getall(self):
        for dut in self.duts:
            dut.config(['default interface Et1-7', 'interface Ethernet1',
                        'spanning-tree portfast edge', 'interface Ethernet2',
                        'spanning-tree portfast network', 'interface Ethernet3',
                        'spanning-tree bpduguard enable', 'interface Ethernet4',
                        'spanning-tree bpduguard disable'])
            result = dut.api('stp').interfaces.getall()
            self.assertIsInstance(result, dict)
            self.assertEqual('edge', result['Ethernet1']['portfast'])
            self.assertEqual('network', result['Ethernet2']['portfast'])
            self.assertTrue(result['Ethernet3']['bpduguard'])
            self.assertFalse(result['Ethernet4']['bpduguard'])


    def test_set_bpduguard_to_true(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config('default interface %s' % intf)
            resource = dut.api('stp').interfaces
            result = resource.set_bpduguard(intf, True)
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show running-config interfaces %s' %
                                      intf, 'text')
            self.assertIn('spanning-tree bpduguard enable',
                          config[0]['output'], 'dut=%s' % dut)

    def test_set_bpdugard_to_false(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config(['default interface %s' % intf, 'interface %s' % intf,
                        'spanning-tree bpduguard disable'])
            resource = dut.api('stp').interfaces
            result = resource.set_bpduguard('Ethernet1', False)
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show running-config interfaces %s' %
                                      intf, 'text')
            self.assertIn('spanning-tree bpduguard disable',
                          config[0]['output'], 'dut=%s' % dut)

    def test_set_portfast_to_edge(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config('default interface %s' % intf)
            resource = dut.api('stp').interfaces
            result = resource.set_portfast(intf, 'edge')
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show running-config interfaces %s' %
                                      intf, 'text')
            self.assertIn('spanning-tree portfast\n', config[0]['output'],
                          'dut=%s' % dut)

    def test_set_portfast_to_network(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config('default interface %s' % intf)
            resource = dut.api('stp').interfaces
            result = resource.set_portfast(intf, 'network')
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show running-config interfaces %s' %
                                      intf, 'text')
            self.assertIn('spanning-tree portfast network\n',
                          config[0]['output'], 'dut=%s' % dut)

    def test_set_portfast_to_disable(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config(['default interface %s' % intf, 'interface %s' % intf,
                        'spanning-tree portfast'])
            resource = dut.api('stp').interfaces
            result = resource.set_portfast(intf, 'disable')
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show running-config interfaces %s' %
                                      intf, 'text')
            self.assertNotIn('spanning-tree portfast', config[0]['output'],
                             'dut=%s' % dut)






if __name__ == '__main__':
    unittest.main()
