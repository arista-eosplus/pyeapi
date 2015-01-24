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

from testlib import random_string, random_int
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
            config = dut.run_commands('show running-config interfaces %s' %
                                      intf, 'text')
            self.assertNotIn('no sflow enable', config[0]['output'])

    def test_set_sflow_disable(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config('default interface %s' % intf)
            result = dut.api('interfaces').set_sflow(intf, False)
            self.assertTrue(result)
            config = dut.run_commands('show running-config interfaces %s' %
                                      intf, 'text')
            self.assertIn('no sflow enable', config[0]['output'])


class TestPortchannelInterface(DutSystemTest):

    def test_get(self):
        for dut in self.duts:
            dut.config(['no interface Port-Channel1',
                        'interface Port-Channel1'])
            result = dut.api('interfaces').get('Port-Channel1')
            self.assertIsInstance(result, dict)
            self.assertEqual(result['type'], 'portchannel')
            self.assertEqual(result['name'], 'Port-Channel1')

    def test_get_lacp_mode_with_default(self):
        for dut in self.duts:
            dut.config(['no interface Port-Channel1',
                        'interface Port-Channel1'])
            instance = dut.api('interfaces').get_instance('Port-Channel1')
            result = instance.get_lacp_mode('Port-Channel1')
            self.assertEqual(result, 'on', 'dut=%s' % dut)

    def test_get_members_default(self):
        for dut in self.duts:
            dut.config(['no interface Port-Channel1',
                        'interface Port-Channel1'])
            instance = dut.api('interfaces').get_instance('Port-Channel1')
            result = instance.get_members('Port-Channel1')
            self.assertEqual(result, list(), 'dut=%s' % dut)

    def test_set_lacp_mode(self):
        for dut in self.duts:
            for mode in ['on', 'active', 'passive']:
                cfgmode = 'on' if mode != 'on' else 'active'
                dut.config(['no interface Port-Channel1',
                            'default interface Ethernet1',
                            'interface Ethernet1',
                            'channel-group 1 mode %s' % cfgmode])

                result = dut.api('interfaces').set_lacp_mode('Port-Channel1',
                                                             mode)
                self.assertTrue(result, 'dut=%s' % dut)
                commands = 'show running-config interfaces Ethernet1'
                config = dut.run_commands(commands, 'text')
                self.assertIn('channel-group 1 mode %s' % mode,
                              config[0]['output'], 'dut=%s' % dut)

    def test_set_lacp_mode_invalid_value(self):
        for dut in self.duts:
            mode = random_string()
            result = dut.api('interfaces').set_lacp_mode('Port-Channel1', mode)
            self.assertFalse(result)

    def test_set_members(self):
        for dut in self.duts:
            et1 = random_interface(dut)
            et2 = random_interface(dut, exclude=[et1])
            et3 = random_interface(dut, exclude=[et1, et2])

            dut.config(['no interface Port-Channel1',
                        'default interface %s' % et1,
                        'interface %s' % et1,
                        'channel-group 1 mode on',
                        'default interface %s' % et2,
                        'interface %s' % et2,
                        'channel-group 1 mode on',
                        'default interface %s' % et3])

            api = dut.api('interfaces')
            result = api.set_members('Port-Channel1', [et1, et3])
            self.assertTrue(result, 'dut=%s' % dut)

            cmd = 'show running-config interfaces %s'

            # check to make sure et1 is still in the lag and et3 was
            # added to the lag
            for interface in [et1, et3]:
                config = dut.run_commands(cmd % interface, 'text')
                self.assertIn('channel-group 1 mode on',
                              config[0]['output'], 'dut=%s' % dut)

            # checks to  make sure et2 was remvoved form the lag
            config = dut.run_commands(cmd % et2, 'text')
            self.assertNotIn('channel-group 1 mode on',
                             config[0]['output'], 'dut=%s' % dut)




    def test_minimum_links_valid(self):
        for dut in self.duts:
            minlinks = random_int(1, 16)
            dut.config(['no interface Port-Channel1',
                        'interface Port-Channel1'])
            result = dut.api('interfaces').set_minimum_links('Port-Channel1',
                                                             minlinks)
            self.assertTrue(result, 'dut=%s' % dut)
            commands = 'show running-config interfaces Port-Channel1'
            config = dut.run_commands(commands, 'text')
            self.assertIn('port-channel min-links %s' % minlinks,
                          config[0]['output'], 'dut=%s' % dut)

    def test_minimum_links_invalid_value(self):
        for dut in self.duts:
            minlinks = random_int(17, 128)
            result = dut.api('interfaces').set_minimum_links('Port-Channel1',
                                                             minlinks)
            self.assertFalse(result)

class TestApiVxlanInterface(DutSystemTest):

    def test_get(self):
        for dut in self.duts:
            dut.config(['no interface Vxlan1',
                        'interface Vxlan1'])
            result = dut.api('interfaces').get('Vxlan1')
            self.assertIsInstance(result, dict)
            self.assertEqual(result['type'], 'vxlan')
            self.assertEqual(result['name'], 'Vxlan1')
            self.assertFalse(result['shutdown'])
            self.assertEqual(result['description'], '')
            self.assertEqual(result['source_interface'], '')
            self.assertEqual(result['multicast_group'], '')

    def get_config(self, dut):
        cmd = 'show running-config all interfaces Vxlan1'
        config = dut.run_commands(cmd, 'text')
        return config[0]['output']

    def contains(self, text, dut):
        self.assertIn(text, self.get_config(dut), 'dut=%s' % dut)

    def test_set_source_interface(self):
        for dut in self.duts:
            dut.config(['no interface Vxlan1', 'interface Vxlan1'])
            api = dut.api('interfaces')
            instance = api.set_source_interface('Vxlan1', 'Loopback0')
            self.assertTrue(instance)
            self.contains('vxlan source-interface Loopback0', dut)

    def test_set_source_interface_default(self):
        for dut in self.duts:
            dut.config(['no interface Vxlan1', 'interface Vxlan1',
                        'vxlan source-interface Loopback0'])
            api = dut.api('interfaces')
            instance = api.set_source_interface('Vxlan1', default=True)
            self.assertTrue(instance)
            self.contains('no vxlan source-interface', dut)

    def test_set_source_interface_negate(self):
        for dut in self.duts:
            dut.config(['no interface Vxlan1', 'interface Vxlan1',
                        'vxlan source-interface Loopback0'])
            api = dut.api('interfaces')
            instance = api.set_source_interface('Vxlan1')
            self.assertTrue(instance)
            self.contains('no vxlan source-interface', dut)

    def test_set_multicast_group(self):
        for dut in self.duts:
            dut.config(['no interface Vxlan1', 'interface Vxlan1'])
            api = dut.api('interfaces')
            instance = api.set_multicast_group('Vxlan1', '239.10.10.10')
            self.assertTrue(instance)
            self.contains('vxlan multicast-group 239.10.10.10', dut)

    def test_set_multicast_group_default(self):
        for dut in self.duts:
            dut.config(['no interface Vxlan1', 'interface Vxlan1',
                        'vxlan multicast-group 239.10.10.10'])
            api = dut.api('interfaces')
            instance = api.set_multicast_group('Vxlan1', default=True)
            self.assertTrue(instance)
            self.contains('no vxlan multicast-group', dut)

    def test_set_multicast_group_negate(self):
        for dut in self.duts:
            dut.config(['no interface Vxlan1', 'interface Vxlan1',
                        'vxlan multicast-group 239.10.10.10'])
            api = dut.api('interfaces')
            instance = api.set_multicast_group('Vxlan1')
            self.assertTrue(instance)
            self.contains('no vxlan multicast-group', dut)


if __name__ == '__main__':
    unittest.main()
