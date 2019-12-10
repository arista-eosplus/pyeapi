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
import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))

from systestlib import DutSystemTest

IP_PREFIX = '10.10.10.'
VR_CONFIG = {
    'primary_ip': '10.10.10.2',
    'secondary_ip': [],
    'priority': 100,
    'description': '',
    'ip_version': 2,
    'timers_advertise': 1,
    'delay_reload': 1,
    'enable': False,
    'mac_addr_adv_interval': 30,
    'preempt': False,
    'preempt_delay_min': 1,
    'preempt_delay_reload': None,
    'primary_ipv4': '10.10.10.2',
    'priority_level': 200,
    'session_description': 'modified vrrp 10 on an interface',
    'secondary_ipv4': ['10.10.10.11'],
    'ipv4_version': 3,
    'advertisement_interval': 2,
    'timers_delay_reload': 1,
    'track': [
        {'name': 'Ethernet1', 'action': 'shutdown'},
        {'name': 'Ethernet2', 'action': 'decrement', 'amount': 10},
        {'name': 'Ethernet2', 'action': 'shutdown'},
    ],
    'tracked-object': [
        {'name': 'Ethernet1', 'action': 'shutdown'},
        {'name': 'Ethernet2', 'action': 'decrement', 'amount': 10},
        {'name': 'Ethernet2', 'action': 'shutdown'},
    ],
    'bfd_ip': '10.10.10.150',
}

class TestApiVrrp(DutSystemTest):

    def _vlan_setup(self, dut):
        dut.config(['no interface vlan 101',
                    'interface vlan 101',
                    'ip address %s1/24' % IP_PREFIX,
                    'exit'])
        return 'Vlan101'

    def test_get(self):
        vrid = 98
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'vrrp %d disabled' % vrid,
                        'exit'])
            response = dut.api('vrrp').get(interface)

            self.assertIsNotNone(response)

    def test_getall(self):
        vrid = 98
        vrid2 = 198
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'vrrp %d disabled' % vrid,
                        'exit',
                        'interface vlan $',
                        'vrrp %d disabled' % vrid,
                        'vrrp %d disabled' % vrid2,
                        'exit'])
            response = dut.api('vrrp').getall()

            self.assertIsNotNone(response)

    def test_create(self):
        vrid = 99
        import copy
        vrrp_conf = copy.deepcopy(VR_CONFIG)
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'exit'])

            response = dut.api('vrrp').create(interface, vrid, **vrrp_conf)
            self.assertIs(response, True)

            # Fix the configuration dict for proper output
            vrrp_conf = dut.api('vrrp').vrconf_format(vrrp_conf)

            response = dut.api('vrrp').get(interface)[vrid]

            self.maxDiff = None
            self.assertEqual(response, vrrp_conf)

    def test_delete(self):
        vrid = 101
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d disabled' % vrid,
                        'exit'])

            response = dut.api('vrrp').delete(interface, vrid)
            self.assertIs(response, True)

    def test_default(self):
        vrid = 102
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d disabled' % vrid,
                        'exit'])

            response = dut.api('vrrp').delete(interface, vrid)
            self.assertIs(response, True)

    def test_update_with_create(self):
        pass
        vrid = 103
        import copy
        vrrp_conf = copy.deepcopy(VR_CONFIG)
        # vrrp_conf = dict(VR_CONFIG)
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'exit'])

            # Create the inital vrrp on the interface
            response = dut.api('vrrp').create(interface, vrid, **vrrp_conf)
            self.assertIs(response, True)

            # Update some of the information on the vrrp
            vrrp_update = {
                'enable': True,
                'mac_addr_adv_interval': 'default',
                'preempt': True,
                'preempt_delay_min': 'default',
                'preempt_delay_reload': 'default',
                'primary_ip': '10.10.10.12',
                'primary_ipv4': '10.10.10.12',
                'priority_level': 200,
                'priority': 100,
                'description': '',
                'ip_version': None,
                'timers_advertise': 1,
                'delay_reload': 1,
                'session_description': 'updated vrrp 10 on an interface',
                'secondary_ipv4': ['10.10.10.13', '10.10.10.23'],
                'ipv4_version': 2,
                'advertisement_interval': None,
                'timers_delay_reload': 'default',
                'track': [
                    {'name': 'Ethernet2', 'action': 'shutdown'},
                    {'name': 'Ethernet2', 'action': 'decrement', 'amount': 1},
                ],
                'tracked_object': [
                    {'name': 'Ethernet2', 'action': 'shutdown'},
                    {'name': 'Ethernet2', 'action': 'decrement', 'amount': 1},
                ],
                'bfd_ip': None,
            }

            response = dut.api('vrrp').create(interface, vrid, **vrrp_update)
            self.assertIs(response, True)
            vrrp_update = dut.api('vrrp').vrconf_format(vrrp_update)

            response = dut.api('vrrp').get(interface)[vrid]

            self.maxDiff = None
            self.assertEqual(response, vrrp_update)

    def test_set_enable(self):
        vrid = 104
        enable_cases = [
            {'value': True},
            {'value': False},
            {'value': True},
            {'value': False},
        ]
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d disabled' % vrid,
                        'vrrp %d ipv4 10.10.10.2' % vrid,
                        'exit'])

            for enable in enable_cases:
                response = dut.api('vrrp').set_enable(
                    interface, vrid, **enable)
                self.assertIs(response, True)

    def test_set_primary_ipv4(self):
        vrid = 104
        primary_ipv4_cases = [
            {'value': '10.10.10.5'},
            {'default': True},
            {'value': '10.10.10.6'},
            {'disable': True},
            {'value': '10.10.10.7'},
        ]
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d disabled' % vrid,
                        'exit'])

            for p_ip in primary_ipv4_cases:
                response = dut.api('vrrp').set_primary_ipv4(
                    interface, vrid, **p_ip)
                self.assertIs(response, True)

    def test_set_priority_level(self):
        vrid = 104
        priority_cases = [
            {'value': 200},
            {'default': True},
            {'value': 175},
            {'disable': True},
            {'value': 190}
        ]
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d disabled' % vrid,
                        'exit'])

            for priority_level in priority_cases:
                response = dut.api('vrrp').set_priority_level(
                    interface, vrid, **priority_level)
                self.assertIs(response, True)

    def test_set_session_description(self):
        vrid = 104
        desc_cases = [
            {'value': '1st modified vrrp'},
            {'default': True},
            {'value': '2nd modified vrrp'},
            {'disable': True},
            {'value': '3rd modified vrrp'},
        ]
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d disabled' % vrid,
                        'exit'])

            for session_description in desc_cases:
                response = dut.api('vrrp').set_session_description(
                    interface, vrid, **session_description)
                self.assertIs(response, True)

    def test_set_secondary_ipv4s(self):
        vrid = 104
        secondary_ipv4_cases = [
            ['10.10.10.51', '10.10.10.52'],
            ['10.10.10.53', '10.10.10.54'],
            [],
        ]
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d disabled' % vrid,
                        'exit'])

            for s_ip_list in secondary_ipv4_cases:
                response = dut.api('vrrp').set_secondary_ipv4s(
                    interface, vrid, s_ip_list)
                self.assertIs(response, True)

    def test_set_ipv4_version(self):
        vrid = 104
        ip_version_cases = [
            {'value': 2},
            {'value': 3},
            {'default': True},
            {'value': 3},
            {'disable': True},
            {'value': 3},
        ]
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d disabled' % vrid,
                        'exit'])

            for ipv4_version in ip_version_cases:
                response = dut.api('vrrp').set_ipv4_version(
                    interface, vrid, **ipv4_version)
                self.assertIs(response, True)

    def test_set_advertisement_interval(self):
        vrid = 104
        timers_adv_cases = [
            {'value': 10},
            {'default': True},
            {'value': 20},
            {'disable': True},
            {'value': 30},
        ]
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d disabled' % vrid,
                        'exit'])

            for advertisement_interval in timers_adv_cases:
                response = dut.api('vrrp').set_advertisement_interval(
                    interface, vrid, **advertisement_interval)
                self.assertIs(response, True)

    def test_set_mac_addr_adv_interval(self):
        vrid = 104
        mac_addr_adv_int_cases = [
            {'value': 50},
            {'default': True},
            {'value': 55},
            {'disable': True},
            {'value': 60},
        ]
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d disabled' % vrid,
                        'exit'])

            for mac_addr_adv_intvl in mac_addr_adv_int_cases:
                response = dut.api('vrrp').set_mac_addr_adv_interval(
                    interface, vrid, **mac_addr_adv_intvl)
                self.assertIs(response, True)

    def test_set_preempt(self):
        vrid = 104
        preempt_cases = [
            {'value': True},
            {'default': True},
            {'value': True},
            {'disable': True},
            {'value': True},
            {'value': False},
        ]
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d disabled' % vrid,
                        'exit'])

            for preempt in preempt_cases:
                response = dut.api('vrrp').set_preempt(
                    interface, vrid, **preempt)
                self.assertIs(response, True)

    def test_set_preempt_delay_min(self):
        vrid = 104
        preempt_delay_min_cases = [
            {'value': 3600},
            {'default': True},
            {'value': 500},
            {'disable': True},
            {'value': 150},
        ]
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d disabled' % vrid,
                        'exit'])

            for preempt_delay_min in preempt_delay_min_cases:
                response = dut.api('vrrp').set_preempt_delay_min(
                    interface, vrid, **preempt_delay_min)
                self.assertIs(response, True)

    def test_set_preempt_delay_reload(self):
        vrid = 104
        preempt_delay_reload_cases = [
            {'value': 3600},
            {'default': True},
            {'value': 500},
            {'disable': True},
            {'value': 150},
        ]
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d disabled' % vrid,
                        'exit'])

            for preempt_delay_reload in preempt_delay_reload_cases:
                response = dut.api('vrrp').set_preempt_delay_reload(
                    interface, vrid, **preempt_delay_reload)
                self.assertIs(response, True)

    def test_set_timers_delay_reload(self):
        vrid = 104
        timers_delay_reload_cases = [
            {'value': 30},
            {'default': True},
            {'value': 25},
            {'disable': True},
            {'value': 15},
        ]
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d disabled' % vrid,
                        'exit'])

            for timers_delay_reload in timers_delay_reload_cases:
                response = dut.api('vrrp').set_timers_delay_reload(
                    interface, vrid, **timers_delay_reload)
                self.assertIs(response, True)

    def test_set_tracks(self):
        vrid = 104
        track_cases = [
            [
                {'name': 'Ethernet1', 'action': 'shutdown'},
                {'name': 'Ethernet2', 'action': 'decrement', 'amount': 10},
                {'name': 'Ethernet2', 'action': 'shutdown'},
            ],
            [
                {'name': 'Ethernet1', 'action': 'shutdown'},
            ],
            [
                {'name': 'Ethernet1', 'action': 'shutdown'},
                {'name': 'Ethernet2', 'action': 'decrement', 'amount': 20},
                {'name': 'Ethernet2', 'action': 'shutdown'},
            ],
            [
                {'name': 'Ethernet1', 'action': 'shutdown'},
            ],
            [],
        ]
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d disabled' % vrid,
                        'exit'])

            for track_list in track_cases:
                response = dut.api('vrrp').set_tracks(
                    interface, vrid, track_list)
                self.assertIs(response, True)

    def test_set_tracked_objects(self):
        vrid = 104
        track_cases = [
            [
                {'name': 'Ethernet1', 'action': 'shutdown'},
                {'name': 'Ethernet2', 'action': 'decrement', 'amount': 10},
                {'name': 'Ethernet2', 'action': 'shutdown'},
            ],
            [
                {'name': 'Ethernet1', 'action': 'shutdown'},
            ],
            [
                {'name': 'Ethernet1', 'action': 'shutdown'},
                {'name': 'Ethernet2', 'action': 'decrement', 'amount': 20},
                {'name': 'Ethernet2', 'action': 'shutdown'},
            ],
            [
                {'name': 'Ethernet1', 'action': 'shutdown'},
            ],
            [],
        ]
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d disabled' % vrid,
                        'exit'])

            for track_list in track_cases:
                response = dut.api('vrrp').set_tracked_objects(
                    interface, vrid, track_list)
                self.assertIs(response, True)

    def test_set_bfd_ip(self):
        vrid = 104
        bfd_ip_cases = [
            {'value': '10.10.10.160'},
            {'default': True},
            {'value': '10.10.10.161'},
            {'disable': True},
            {'value': '10.10.10.162'},
        ]
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d disabled' % vrid,
                        'exit'])

            for bfd_ip in bfd_ip_cases:
                response = dut.api('vrrp').set_bfd_ip(
                    interface, vrid, **bfd_ip)
                self.assertIs(response, True)


if __name__ == '__main__':
    unittest.main()
