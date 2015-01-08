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

from systestlib import DutSystemTest


class TestResourceIpinterfaces(DutSystemTest):

    def test_get(self):
        for dut in self.duts:
            dut.config(['default interface Ethernet1', 'interface Ethernet1',
                        'no switchport', 'ip address 99.99.99.99/24',
                        'mtu 1800'])
            result = dut.api('ipinterfaces').get('Ethernet1')
            values = dict(name='Ethernet1', address='99.99.99.99/24',
                          mtu=1800)
            self.assertEqual(values, result, 'dut=%s' % dut)

    def test_getall(self):
        for dut in self.duts:
            dut.config(['default interface et1-7'])
            result = dut.api('interfaces').getall()
            self.assertIsInstance(result, dict)
            for intf in ['Management1']:
                self.assertIn(intf, result)

    def test_create_and_return_true(self):
        for dut in self.duts:
            dut.config('default interface Ethernet1')
            resource = dut.api('ipinterfaces')
            result = resource.create('Ethernet1')
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.enable('show running-config interfaces Ethernet1',
                                'text')
            self.assertIn('no switchport', config[0]['output'])

    def test_delete_and_return_true(self):
        for dut in self.duts:
            dut.config(['interface Ethernet1', 'ip address 199.1.1.1/24'])
            resource = dut.api('ipinterfaces')
            result = resource.delete('Ethernet1')
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.enable('show running-config interfaces Ethernet1',
                                'text')
            self.assertNotIn('ip address 199.1.1.1/24', config[0]['output'],
                             'dut=%s' % dut)

    def test_set_address(self):
        for dut in self.duts:
            dut.config(['default interface Ethernet1', 'interface Ethernet1',
                        'no switchport'])
            resource = dut.api('ipinterfaces')
            result = resource.set_address('Ethernet1', '111.111.111.111/24')
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.enable('show running-config interfaces Ethernet1',
                                'text')
            self.assertIn('ip address 111.111.111.111/24',
                          config[0]['output'], 'dut=%s' % dut)

    def test_set_mtu(self):
        for dut in self.duts:
            dut.config(['default interface Ethernet1', 'interface Ethernet1',
                        'ip address 111.111.111.111/24'])
            resource = dut.api('ipinterfaces')
            result = resource.set_mtu('Ethernet1', 2000)
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.enable('show running-config interfaces Ethernet1',
                                'text')
            self.assertIn('mtu 2000', config[0]['output'], 'dut=%s' % dut)

if __name__ == '__main__':
    unittest.main()
