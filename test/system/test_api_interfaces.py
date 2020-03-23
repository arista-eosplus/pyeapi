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
            rintf = random_interface(dut)
            dut.config(['default interface %s' % rintf])
            result = dut.api('interfaces').getall()
            self.assertIsInstance(result, dict)
            for intf in [rintf, 'Management1']:
                self.assertIn(intf, result)

    def test_create_and_return_true(self):
        for dut in self.duts:
            dut.config('no interface Loopback0')
            result = dut.api('interfaces').create('Loopback0')
            self.assertTrue(result)
            config = dut.run_commands('show interfaces')
            self.assertIn('Loopback0', config[0]['interfaces'])

    def test_create_ethernet_raises_not_implemented_error(self):
        for dut in self.duts:
            with self.assertRaises(NotImplementedError):
                dut.api('interfaces').create(random_interface(dut))

    def test_delete_and_return_true(self):
        for dut in self.duts:
            dut.config('interface Loopback0')
            result = dut.api('interfaces').delete('Loopback0')
            self.assertTrue(result)
            config = dut.run_commands('show interfaces')
            self.assertNotIn('Loopback0', config[0]['interfaces'])

    def test_delete_ethernet_raises_not_implemented_error(self):
        for dut in self.duts:
            with self.assertRaises(NotImplementedError):
                dut.api('interfaces').delete(random_interface(dut))

    def test_create_and_delete_ethernet_sub_interface(self):
        for dut in self.duts:
            # Default Ethernet1
            dut.api('interfaces').default('Ethernet1')
            # Create subint Ethernet1.1
            res = dut.api('interfaces').create('Ethernet1.1')
            self.assertTrue(res)
            command = 'show running-config interfaces Ethernet1.1'
            output = dut.run_commands(command, encoding='text')
            self.assertIn('Ethernet1.1', output[0]['output'])
            # Delete subint Ethernet1.1
            res = dut.api('interfaces').delete('Ethernet1.1')
            self.assertTrue(res)
            output = dut.run_commands(command, encoding='text')
            self.assertEqual(output[0]['output'], '')

    def test_ethernet_set_and_unset_encapsulation(self):
        for dut in self.duts:
            # Default Ethernet1
            dut.api('interfaces').default('Ethernet1')
            # Create subint Ethernet1.1
            res = dut.api('interfaces').create('Ethernet1.1')
            self.assertTrue(res)
            # Set encapsulation
            res = dut.api('interfaces').set_encapsulation('Ethernet1.1', 4)
            self.assertTrue(res)
            command = 'show running-config interfaces Ethernet1.1'
            output = dut.run_commands(command, encoding='text')
            encap = 'encapsulation dot1q vlan 4'
            self.assertIn(encap, output[0]['output'])
            # Remove encapsulation
            res = dut.api('interfaces').set_encapsulation('Ethernet1.1', 4,
                                                          disable=True)
            self.assertTrue(res)
            output = dut.run_commands(command, encoding='text')
            self.assertNotIn(encap, output[0]['output'])
            # Delete subint Ethernet1.1
            res = dut.api('interfaces').delete('Ethernet1.1')
            self.assertTrue(res)

    def test_set_encapsulation_non_subintf_exception(self):
        for dut in self.duts:
            with self.assertRaises(NotImplementedError):
                dut.api('interfaces').set_encapsulation(random_interface(dut),
                                                        1)

    def test_set_encapsulation_non_supported_intf_exception(self):
        for dut in self.duts:
            with self.assertRaises(NotImplementedError):
                dut.api('interfaces').set_encapsulation('Vlan1234',
                                                        1)

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

    def test_set_description_negate(self):
        for dut in self.duts:
            text = random_string()
            intf = random_interface(dut)
            dut.config(['interface %s' % intf, 'description %s' % text])
            result = dut.api('interfaces').set_description(intf, disable=True)
            self.assertTrue(result)
            config = dut.run_commands('show interfaces %s' % intf)
            config = config[0]['interfaces'][intf]
            self.assertEqual(config['description'], '')

    def test_set_description_default(self):
        for dut in self.duts:
            text = random_string()
            intf = random_interface(dut)
            dut.config(['interface %s' % intf, 'description %s' % text])
            result = dut.api('interfaces').set_description(intf, default=True)
            self.assertTrue(result)
            config = dut.run_commands('show interfaces %s' % intf)
            config = config[0]['interfaces'][intf]
            self.assertEqual(config['description'], '')

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
            result = dut.api('interfaces').set_sflow(intf, disable=True)
            self.assertTrue(result)
            config = dut.run_commands('show running-config interfaces %s' %
                                      intf, 'text')
            self.assertIn('no sflow enable', config[0]['output'])

    def test_set_sflow_default(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config('default interface %s' % intf)
            result = dut.api('interfaces').set_sflow(intf, default=True)
            self.assertTrue(result)
            config = dut.run_commands('show running-config interfaces %s' %
                                      intf, 'text')
            self.assertNotIn('no sflow enable', config[0]['output'])

    def test_set_vrf(self):
        for dut in self.duts:
            intf = random_interface(dut)
            dut.config('default interface %s' % intf)
            # Verify set_vrf returns False if no vrf by name is configured
            result = dut.api('interfaces').set_vrf(intf, 'test')
            self.assertFalse(result)
            if dut.version_number >= '4.23':
                dut.config('vrf instance test')
            else:
                dut.config('vrf definition test')
            # Verify interface has vrf applied
            result = dut.api('interfaces').set_vrf(intf, 'test')
            self.assertTrue(result)
            config = dut.run_commands('show running-config interfaces %s' %
                                      intf, 'text')
            if dut.version_number >= '4.23':
                self.assertIn('vrf test', config[0]['output'])
            else:
                self.assertIn('vrf forwarding test', config[0]['output'])
            # Verify interface has vrf removed
            result = dut.api('interfaces').set_vrf(intf, 'test', disable=True)
            self.assertTrue(result)
            config = dut.run_commands('show running-config interfaces %s' %
                                      intf, 'text')
            if dut.version_number >= '4.23':
                self.assertIn('vrf test', config[0]['output'])
                # Remove test vrf
                dut.config('no vrf instance test')
            else:
                self.assertIn('vrf forwarding test', config[0]['output'])
                # Remove test vrf
                dut.config('no vrf definition test')


class TestPortchannelInterface(DutSystemTest):

    def test_get(self):
        for dut in self.duts:
            dut.config(['no interface Port-Channel1',
                        'interface Port-Channel1'])
            result = dut.api('interfaces').get('Port-Channel1')
            self.assertIsInstance(result, dict)
            self.assertEqual(result['type'], 'portchannel')
            self.assertEqual(result['name'], 'Port-Channel1')

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

    def test_set_members_with_mode(self):
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
            result = api.set_members('Port-Channel1', [et1, et3], mode='active')
            self.assertTrue(result, 'dut=%s' % dut)

            cmd = 'show running-config interfaces %s'

            # check to make sure et1 is still in the lag and et3 was
            # added to the lag
            for interface in [et1, et3]:
                config = dut.run_commands(cmd % interface, 'text')
                self.assertIn('channel-group 1 mode active',
                              config[0]['output'], 'dut=%s' % dut)

            # checks to  make sure et2 was remvoved form the lag
            config = dut.run_commands(cmd % et2, 'text')
            self.assertNotIn('channel-group 1 mode on',
                             config[0]['output'], 'dut=%s' % dut)

    def test_get_members_default(self):
        for dut in self.duts:
            dut.config(['no interface Port-Channel1',
                        'interface Port-Channel1'])
            instance = dut.api('interfaces').get_instance('Port-Channel1')
            result = instance.get_members('Port-Channel1')
            self.assertEqual(result, list(), 'dut=%s' % dut)

    def test_get_members_one_member(self):
        for dut in self.duts:
            dut.config(['no interface Port-Channel1',
                        'interface Port-Channel1',
                        'default interface Ethernet1',
                        'interface Ethernet1',
                        'channel-group 1 mode active'])
            instance = dut.api('interfaces').get_instance('Port-Channel1')
            result = instance.get_members('Port-Channel1')
            self.assertEqual(result, ['Ethernet1'], 'dut=%s' % dut)

    def test_get_members_two_members(self):
        for dut in self.duts:
            dut.config(['no interface Port-Channel1',
                        'interface Port-Channel1',
                        'default interface Ethernet1-2',
                        'interface Ethernet1-2',
                        'channel-group 1 mode active'])
            instance = dut.api('interfaces').get_instance('Port-Channel1')
            result = instance.get_members('Port-Channel1')
            self.assertEqual(result, ['Ethernet1', 'Ethernet2'], 'dut=%s' % dut)

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

    def test_get_lacp_mode_with_default(self):
        for dut in self.duts:
            dut.config(['no interface Port-Channel1',
                        'interface Port-Channel1'])
            instance = dut.api('interfaces').get_instance('Port-Channel1')
            result = instance.get_lacp_mode('Port-Channel1')
            self.assertEqual(result, 'on', 'dut=%s' % dut)

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

    def test_create_and_delete_portchannel_sub_interface(self):
        for dut in self.duts:
            et1 = random_interface(dut)
            et2 = random_interface(dut, exclude=[et1])

            dut.config(['no interface Port-Channel1',
                        'default interface %s' % et1,
                        'interface %s' % et1,
                        'channel-group 1 mode on',
                        'default interface %s' % et2,
                        'interface %s' % et2,
                        'channel-group 1 mode on'])
            # Create subint Port-Channel1.1
            api = dut.api('interfaces')
            result = api.create('Port-Channel1.1')
            self.assertTrue(result, 'dut=%s' % dut)
            command = 'show running-config interfaces Port-Channel1.1'
            output = dut.run_commands(command, encoding='text')
            self.assertIn('Port-Channel1.1', output[0]['output'])
            # Delete subint Port-Channel1.1
            result = dut.api('interfaces').delete('Port-Channel1.1')
            self.assertTrue(result)
            output = dut.run_commands(command, encoding='text')
            self.assertEqual(output[0]['output'], '')
            # Remove port-channel and default interfaces
            dut.config(['no interface Port-Channel1',
                        'default interface %s' % et1,
                        'default interface %s' % et2])

    def test_set_and_unset_portchannel_sub_intf_encapsulation(self):
        for dut in self.duts:
            et1 = random_interface(dut)
            et2 = random_interface(dut, exclude=[et1])

            dut.config(['no interface Port-Channel1',
                        'default interface %s' % et1,
                        'interface %s' % et1,
                        'channel-group 1 mode on',
                        'default interface %s' % et2,
                        'interface %s' % et2,
                        'channel-group 1 mode on'])
            # Create subint Port-Channel1.1
            api = dut.api('interfaces')
            result = api.create('Port-Channel1.1')
            self.assertTrue(result)
            # Set encapsulation
            result = api.set_encapsulation('Port-Channel1.1', 4)
            self.assertTrue(result)
            command = 'show running-config interfaces Port-Channel1.1'
            output = dut.run_commands(command, encoding='text')
            encap = 'encapsulation dot1q vlan 4'
            self.assertIn(encap, output[0]['output'])
            # Unset encapsulation
            result = api.set_encapsulation('Port-Channel1.1', 4, default=True)
            self.assertTrue(result)
            output = dut.run_commands(command, encoding='text')
            self.assertNotIn(encap, output[0]['output'])
            # Delete subint Port-Channel1.1
            result = dut.api('interfaces').delete('Port-Channel1.1')
            self.assertTrue(result)
            output = dut.run_commands(command, encoding='text')
            self.assertEqual(output[0]['output'], '')
            # Remove port-channel and default interfaces
            dut.config(['no interface Port-Channel1',
                        'default interface %s' % et1,
                        'default interface %s' % et2])


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
            self.assertEqual(result['description'], None)
            self.assertEqual(result['source_interface'], '')
            self.assertEqual(result['multicast_group'], '')
            self.assertEqual(result['multicast_decap'], False)


    def get_config(self, dut):
        cmd = 'show running-config all interfaces Vxlan1'
        config = dut.run_commands(cmd, 'text')
        return config[0]['output']

    def contains(self, text, dut):
        self.assertIn(text, self.get_config(dut), 'dut=%s' % dut)

    def notcontains(self, text, dut):
        self.assertNotIn(text, self.get_config(dut), 'dut=%s' % dut)

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
            instance = api.set_source_interface('Vxlan1', disable=True)
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
            instance = api.set_multicast_group('Vxlan1', disable=True)
            self.assertTrue(instance)
            self.contains('no vxlan multicast-group', dut)

    '''commenting this one out as it will only parse on a  trident based DUT
    def test_set_multicast_decap(self):
        for dut in self.duts:
            dut.config(['no interface Vxlan1', 'interface Vxlan1'])
            api = dut.api('interfaces')
            instance = api.set_multicast_decap('Vxlan1')
            self.assertTrue(instance)
            self.contains('vxlan multicast-group decap', dut)
    '''

    def test_set_udp_port(self):
        for dut in self.duts:
            dut.config(['no interface Vxlan1', 'interface Vxlan1',
                        'vxlan udp-port 1024'])
            api = dut.api('interfaces')
            instance = api.set_udp_port('Vxlan1', '1024')
            self.assertTrue(instance)
            self.contains('vxlan udp-port 1024', dut)

    def test_set_udp_port_default(self):
        for dut in self.duts:
            dut.config(['no interface Vxlan1', 'interface Vxlan1',
                        'vxlan udp-port 1024'])
            api = dut.api('interfaces')
            instance = api.set_udp_port('Vxlan1', default=True)
            self.assertTrue(instance)
            self.contains('vxlan udp-port 4789', dut)

    def test_set_udp_port_negate(self):
        for dut in self.duts:
            dut.config(['no interface Vxlan1', 'interface Vxlan1',
                        'vxlan udp-port 1024'])
            api = dut.api('interfaces')
            instance = api.set_udp_port('Vxlan1', disable=True)
            self.assertTrue(instance)
            self.contains('vxlan udp-port 4789', dut)

    def test_add_vtep(self):
        for dut in self.duts:
            dut.config(['no interface Vxlan1', 'interface Vxlan1'])
            api = dut.api('interfaces')
            instance = api.add_vtep('Vxlan1', '1.1.1.1')
            self.assertTrue(instance)
            self.contains('vxlan flood vtep 1.1.1.1', dut)

    def test_add_vtep_to_vlan(self):
        for dut in self.duts:
            dut.config(['no interface Vxlan1', 'interface Vxlan1'])
            api = dut.api('interfaces')
            instance = api.add_vtep('Vxlan1', '1.1.1.1', vlan='10')
            self.assertTrue(instance)
            self.contains('vxlan vlan 10 flood vtep 1.1.1.1', dut)

    def test_remove_vtep(self):
        for dut in self.duts:
            dut.config(['no interface Vxlan1', 'interface Vxlan1'])
            api = dut.api('interfaces')
            instance = api.remove_vtep('Vxlan1', '1.1.1.1')
            self.assertTrue(instance)
            self.contains('no vxlan flood vtep', dut)

    def test_remove_vtep_from_vlan(self):
        for dut in self.duts:
            dut.config(['no interface Vxlan1', 'interface Vxlan1'])
            api = dut.api('interfaces')
            instance = api.remove_vtep('Vxlan1', '1.1.1.1', vlan='10')
            self.assertTrue(instance)
            self.notcontains('vxlan vlan 10 flood vtep remove 1.1.1.1', dut)

    def test_update_vlan(self):
        for dut in self.duts:
            dut.config(['no interface Vxlan1', 'interface Vxlan1'])
            api = dut.api('interfaces')
            instance = api.update_vlan('Vxlan1', '10', '10')
            self.assertTrue(instance)
            self.contains('vxlan vlan add 10 vni 10', dut)

    def test_remove_vlan(self):
        for dut in self.duts:
            dut.config(['no interface Vxlan1', 'interface Vxlan1'])
            api = dut.api('interfaces')
            instance = api.remove_vlan('Vxlan1', '10')
            self.assertTrue(instance)
            self.notcontains('vxlan vlan remove 10 vni 10', dut)


if __name__ == '__main__':
    unittest.main()
