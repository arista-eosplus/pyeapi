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


class TestApiMlag(DutSystemTest):

    def test_get(self):
        for dut in self.duts:
            dut.config(['no interface Port-Channel1-2000',
                        'default mlag configuration'])
            response = dut.api('mlag').get()
            config = dict(domain_id=None, local_interface=None,
                          peer_link=None, peer_address=None, shutdown=False)
            values = dict(config=config, interfaces=dict())
            self.assertEqual(values, response)

    def test_set_domain_id_with_value(self):
        for dut in self.duts:
            dut.config('default mlag configuration')
            api = dut.api('mlag')
            self.assertIn('no domain-id', api.get_block('mlag configuration'))
            for domid in ['test_domain_id', 'test.dom-id', 'test domain id']:
                result = dut.api('mlag').set_domain_id(domid)
                self.assertTrue(result)
                self.assertIn('domain-id %s' % domid, api.get_block('mlag configuration'))

    def test_set_domain_id_with_no_value(self):
        for dut in self.duts:
            dut.config(['mlag configuration', 'domain-id test'])
            api = dut.api('mlag')
            self.assertIn('domain-id test', api.get_block('mlag configuration'))
            result = dut.api('mlag').set_domain_id(disable=True)
            self.assertTrue(result)
            self.assertIn('no domain-id', api.get_block('mlag configuration'))

    def test_set_domain_id_with_default(self):
        for dut in self.duts:
            dut.config(['mlag configuration', 'domain-id test'])
            api = dut.api('mlag')
            self.assertIn('domain-id test', api.get_block('mlag configuration'))
            result = dut.api('mlag').set_domain_id(default=True)
            self.assertTrue(result)
            self.assertIn('no domain-id', api.get_block('mlag configuration'))

    def test_set_local_interface_with_value(self):
        for dut in self.duts:
            dut.config('default mlag configuration')
            api = dut.api('mlag')
            self.assertIn('no local-interface', api.get_block('mlag configuration'))
            result = dut.api('mlag').set_local_interface('Vlan1234')
            self.assertTrue(result)
            self.assertIn('local-interface Vlan1234', api.get_block('mlag configuration'))

    def test_set_local_interface_with_no_value(self):
        for dut in self.duts:
            dut.config(['interface Vlan1234', 'mlag configuration', 'local-interface Vlan1234'])
            api = dut.api('mlag')
            self.assertIn('local-interface Vlan1234', api.get_block('mlag configuration'))
            result = api.set_local_interface(disable=True)
            self.assertTrue(result)
            self.assertIn('no local-interface', api.get_block('mlag configuration'))

    def test_set_local_interface_with_default(self):
        for dut in self.duts:
            dut.config(['interface Vlan1234', 'mlag configuration', 'local-interface Vlan1234'])
            api = dut.api('mlag')
            self.assertIn('local-interface Vlan1234', api.get_block('mlag configuration'))
            result = api.set_local_interface(default=True)
            self.assertTrue(result)
            self.assertIn('no local-interface', api.get_block('mlag configuration'))

    def test_set_peer_address_with_value(self):
        for dut in self.duts:
            dut.config('default mlag configuration')
            api = dut.api('mlag')
            self.assertIn('no peer-address', api.get_block('mlag configuration'))
            result = dut.api('mlag').set_peer_address('1.2.3.4')
            self.assertTrue(result)
            self.assertIn('peer-address 1.2.3.4', api.get_block('mlag configuration'))

    def test_set_peer_address_with_no_value(self):
        for dut in self.duts:
            dut.config(['interface Vlan1234', 'ip address 1.2.3.1/24',
                        'mlag configuration', 'peer-address 1.2.3.4'])
            api = dut.api('mlag')
            self.assertIn('peer-address 1.2.3.4',
                          api.get_block('mlag configuration'))
            result = api.set_peer_address(disable=True)
            self.assertTrue(result)
            self.assertIn('no peer-address',
                          api.get_block('mlag configuration'))

    def test_set_peer_address_with_default(self):
        for dut in self.duts:
            dut.config(['interface Vlan1234', 'ip address 1.2.3.1/24',
                        'mlag configuration', 'peer-address 1.2.3.4'])
            api = dut.api('mlag')
            self.assertIn('peer-address 1.2.3.4',
                          api.get_block('mlag configuration'))
            result = api.set_peer_address(default=True)
            self.assertTrue(result)
            self.assertIn('no peer-address',
                          api.get_block('mlag configuration'))

    def test_set_peer_link_with_value(self):
        for dut in self.duts:
            dut.config('default mlag configuration')
            api = dut.api('mlag')
            self.assertIn('no peer-link', api.get_block('mlag configuration'))
            result = dut.api('mlag').set_peer_link('Ethernet1')
            self.assertTrue(result)
            self.assertIn('peer-link Ethernet1',
                          api.get_block('mlag configuration'))

    def test_set_peer_link_with_value_portchannel(self):
        for dut in self.duts:
            dut.config(['default mlag configuration',
                        'interface Port-Channel5'])
            api = dut.api('mlag')
            self.assertIn('no peer-link', api.get_block('mlag configuration'))
            result = dut.api('mlag').set_peer_link('Port-Channel5')
            self.assertTrue(result)
            self.assertIn('peer-link Port-Channel5', api.get_block('mlag configuration'))

    def test_set_peer_link_with_no_value(self):
        for dut in self.duts:
            dut.config(['mlag configuration', 'peer-link Ethernet1'])
            api = dut.api('mlag')
            self.assertIn('peer-link Ethernet1', api.get_block('mlag configuration'))
            result = api.set_peer_link(disable=True)
            self.assertTrue(result)
            self.assertIn('no peer-link', api.get_block('mlag configuration'))

    def test_set_peer_link_with_default(self):
        for dut in self.duts:
            dut.config(['mlag configuration', 'peer-link Ethernet1'])
            api = dut.api('mlag')
            self.assertIn('peer-link Ethernet1',
                          api.get_block('mlag configuration'))
            result = api.set_peer_link(default=True)
            self.assertTrue(result)
            self.assertIn('no peer-link', api.get_block('mlag configuration'))

    def test_set_shutdown_with_true(self):
        for dut in self.duts:
            dut.config('default mlag configuration')
            api = dut.api('mlag')
            self.assertIn('no shutdown', api.get_block('mlag configuration'))
            result = api.set_shutdown(True)
            self.assertTrue(result)
            self.assertIn('shutdown', api.get_block('mlag configuration'))

    def test_set_shutdown_with_false(self):
        for dut in self.duts:
            dut.config(['mlag configuration', 'shutdown'])
            api = dut.api('mlag')
            self.assertIn('shutdown', api.get_block('mlag configuration'))
            result = api.set_shutdown(False)
            self.assertTrue(result)
            self.assertIn('no shutdown', api.get_block('mlag configuration'))

    def test_set_shutdown_with_no_value(self):
        for dut in self.duts:
            dut.config(['mlag configuration', 'shutdown'])
            api = dut.api('mlag')
            self.assertIn('shutdown', api.get_block('mlag configuration'))
            result = api.set_shutdown(disable=True)
            self.assertTrue(result)
            self.assertIn('no shutdown', api.get_block('mlag configuration'))

    def test_set_shutdown_with_default(self):
        for dut in self.duts:
            dut.config(['mlag configuration', 'shutdown'])
            api = dut.api('mlag')
            self.assertIn('shutdown', api.get_block('mlag configuration'))
            result = api.set_shutdown(default=True)
            self.assertTrue(result)
            self.assertIn('no shutdown', api.get_block('mlag configuration'))

    def test_set_mlag_id_with_value(self):
        for dut in self.duts:
            dut.config('no interface Port-Channel10')
            api = dut.api('mlag')
            self.assertIsNone(api.get_block('interface Port-Channel10'))
            result = api.set_mlag_id('Port-Channel10', '100')
            self.assertTrue(result)
            self.assertIn('mlag 100', api.get_block('interface Port-Channel10'))

    def test_set_mlag_id_with_no_value(self):
        for dut in self.duts:
            dut.config(['no interface Port-Channel10',
                        'interface Port-Channel10', 'mlag 100'])
            api = dut.api('mlag')
            self.assertIn('mlag 100',
                          api.get_block('interface Port-Channel10'))
            result = api.set_mlag_id('Port-Channel10', disable=True)
            self.assertTrue(result)
            self.assertIn('no mlag', api.get_block('interface Port-Channel10'))

    def test_set_mlag_id_with_default(self):
        for dut in self.duts:
            dut.config(['no interface Port-Channel10',
                        'interface Port-Channel10', 'mlag 100'])
            api = dut.api('mlag')
            self.assertIn('mlag 100',
                          api.get_block('interface Port-Channel10'))
            result = api.set_mlag_id('Port-Channel10', default=True)
            self.assertTrue(result)
            self.assertIn('no mlag', api.get_block('interface Port-Channel10'))


if __name__ == '__main__':
    unittest.main()
