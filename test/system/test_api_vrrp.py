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
from testlib import random_string

IP_PREFIX = '10.10.10.'
VR_CONFIG = {
    'primary_ip': '10.10.10.2',
    'priority': 200,
    'description': 'modified vrrp 10 on an interface',
    'secondary_ip': {
        'add': ['10.10.10.11'],
    },
    'ip_version': 3,
    'enable': False,
    'timers_advertise': 2,
    'mac_address_advertisement_interval': 3,
    'preempt': False,
    'preempt_delay_minimum': 1,
    'preempt_delay_reload': None,
    'delay_reload': 1,
    'authentication': '',
    'track': {
        ('Ethernet2', 'shutdown'): 1,
        ('Ethernet1', 'shutdown'): 1,
        ('Ethernet2', 'decrement'): 10,
    },
    'bfd_ip': '10.10.10.150',
}

# Define various test input
PRIMARY_IP = ['10.10.10.2', 'default', '10.10.10.3', 'no', '10.10.10.4', None]
PRIORITY = [200, 'default', 175, 'no', 190, None]
DESCRIPTION = ['1st modified vrrp', 'default', '2nd modified vrrp', 'no',
               '3rd modified vrrp', None]
SECONDARY_IP = [
    {'add': ['10.10.10.51', '10.10.10.52']},
    {'add': ['10.10.10.53', '10.10.10.54'],
     'remove': ['10.10.10.51', '10.10.10.52']},
]
IP_VERSION = [2, 3, 'default', 3, 'no', 3, None]
ENABLE = [True, False, True]
TIMERS_ADVERTISE = [10, 'default', 20, 'no', 30, None]
MAC_ADDR_ADV_INTVL = [50, 'default', 55, 'no', 60, None]
PREEMPT = [True, False, True]
PREEMPT_DELAY_MINIMUM = [3600, 'default', 500, 'no', 150, None]
PREEMPT_DELAY_RELOAD = [3600, 'default', 500, 'no', 150, None]
DELAY_RELOAD = [30, 'default', 25, 'no', 15, None]
TRACK = [
    {
        ('Ethernet2', 'shutdown'): 1,
        ('Ethernet1', 'shutdown'): 1,
        ('Ethernet2', 'decrement'): 10,
    },
    {
        ('Ethernet2', 'shutdown'): None,
        ('Ethernet1', 'shutdown'): 1,
        ('Ethernet2', 'decrement'): 'default',
    },
    {
        ('Ethernet2', 'shutdown'): 1,
        ('Ethernet1', 'shutdown'): 2,
        ('Ethernet2', 'decrement'): 20,
    },
    {
        ('Ethernet2', 'shutdown'): None,
        ('Ethernet1', 'shutdown'): 1,
        ('Ethernet2', 'decrement'): 'no',
    },
    {
        ('Ethernet2', 'shutdown'): 1,
        ('Ethernet1', 'shutdown'): 2,
        ('Ethernet2', 'decrement'): 20,
    },
    {
        ('Ethernet2', 'shutdown'): None,
        ('Ethernet1', 'shutdown'): 1,
        ('Ethernet2', 'decrement'): None,
    },
]
BFD_IP = ['10.10.10.160', 'default', '10.10.10.161', 'no',
          '10.10.10.162', None]


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
                        'vrrp %d shutdown' % vrid,
                        'exit'])
            response = dut.api('vrrp').get(interface)

            self.assertIsNotNone(response)

    def test_create(self):
        vrid = 99
        import copy
        vrrp_conf = copy.deepcopy(VR_CONFIG)
        # vrrp_conf = dict(VR_CONFIG)
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
                        'vrrp %d shutdown' % vrid,
                        'exit'])

            response = dut.api('vrrp').delete(interface, vrid)
            self.assertIs(response, True)

    def test_default(self):
        vrid = 102
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d shutdown' % vrid,
                        'exit'])

            response = dut.api('vrrp').delete(interface, vrid)
            self.assertIs(response, True)

    def test_update(self):
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
                'primary_ip': '10.10.10.12',
                'priority': 200,
                'description': 'updated vrrp 10 on an interface',
                'secondary_ip': {
                    'add': ['10.10.10.13', '10.10.10.23'],
                    'remove': ['10.10.10.11'],
                },
                'ip_version': 2,
                'enable': True,
                'timers_advertise': None,
                'mac_address_advertisement_interval': 'default',
                'preempt': True,
                'preempt_delay_minimum': 'default',
                'preempt_delay_reload': 'default',
                'delay_reload': 'default',
                'authentication': '',
                'track': {
                    ('Ethernet2', 'shutdown'): 1,
                    ('Ethernet1', 'shutdown'): None,
                    ('Ethernet2', 'decrement'): 1,
                },
                'bfd_ip': None,
            }

            response = dut.api('vrrp').update(interface, vrid, **vrrp_update)
            self.assertIs(response, True)
            vrrp_update = dut.api('vrrp').vrconf_format(vrrp_update)

            response = dut.api('vrrp').get(interface)[vrid]

            self.maxDiff = None
            self.assertEqual(response, vrrp_update)

    def test_update_primary_ip(self):
        vrid = 104
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d shutdown' % vrid,
                        'exit'])

            for p_ip in PRIMARY_IP:
                vrconfig = {'primary_ip': p_ip}
                response = dut.api('vrrp').update(interface, vrid, **vrconfig)
                self.assertIs(response, True)

    def test_update_priority(self):
        vrid = 104
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d shutdown' % vrid,
                        'exit'])

            for priority in PRIORITY:
                vrconfig = {'priority': priority}
                response = dut.api('vrrp').update(interface, vrid, **vrconfig)
                self.assertIs(response, True)

    def test_update_description(self):
        vrid = 104
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d shutdown' % vrid,
                        'exit'])

            for description in DESCRIPTION:
                vrconfig = {'description': description}
                response = dut.api('vrrp').update(interface, vrid, **vrconfig)
                self.assertIs(response, True)

    def test_update_secondary_ip(self):
        vrid = 104
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d shutdown' % vrid,
                        'exit'])

            for s_ip in SECONDARY_IP:
                vrconfig = {'secondary_ip': s_ip}
                response = dut.api('vrrp').update(interface, vrid, **vrconfig)
                self.assertIs(response, True)

    def test_update_ip_version(self):
        vrid = 104
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d shutdown' % vrid,
                        'exit'])

            for ip_version in IP_VERSION:
                vrconfig = {'ip_version': ip_version}
                response = dut.api('vrrp').update(interface, vrid, **vrconfig)
                self.assertIs(response, True)

    def test_update_timers_advertise(self):
        vrid = 104
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d shutdown' % vrid,
                        'exit'])

            for timers_advertise in TIMERS_ADVERTISE:
                vrconfig = {'timers_advertise': timers_advertise}
                response = dut.api('vrrp').update(interface, vrid, **vrconfig)
                self.assertIs(response, True)

    def test_update_mac_address_advertisement_interval(self):
        vrid = 104
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d shutdown' % vrid,
                        'exit'])

            for mac_addr_adv_intvl in MAC_ADDR_ADV_INTVL:
                vrconfig = {'mac_address_advertisement_interval':
                            mac_addr_adv_intvl}
                response = dut.api('vrrp').update(interface, vrid, **vrconfig)
                self.assertIs(response, True)

    def test_update_preempt(self):
        vrid = 104
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d shutdown' % vrid,
                        'exit'])

            for preempt in PREEMPT:
                vrconfig = {'preempt': preempt}
                response = dut.api('vrrp').update(interface, vrid, **vrconfig)
                self.assertIs(response, True)

    def test_update_preempt_delay_minimum(self):
        vrid = 104
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d shutdown' % vrid,
                        'exit'])

            for preempt_delay_minimum in PREEMPT_DELAY_MINIMUM:
                vrconfig = {'preempt_delay_minimum': preempt_delay_minimum}
                response = dut.api('vrrp').update(interface, vrid, **vrconfig)
                self.assertIs(response, True)

    def test_update_preempt_delay_reload(self):
        vrid = 104
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d shutdown' % vrid,
                        'exit'])

            for preempt_delay_reload in PREEMPT_DELAY_RELOAD:
                vrconfig = {'preempt_delay_reload': preempt_delay_reload}
                response = dut.api('vrrp').update(interface, vrid, **vrconfig)
                self.assertIs(response, True)

    def test_update_delay_reload(self):
        vrid = 104
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d shutdown' % vrid,
                        'exit'])

            for delay_reload in DELAY_RELOAD:
                vrconfig = {'delay_reload': delay_reload}
                response = dut.api('vrrp').update(interface, vrid, **vrconfig)
                self.assertIs(response, True)

    def test_update_track(self):
        vrid = 104
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d shutdown' % vrid,
                        'exit'])

            for track in TRACK:
                vrconfig = {'track': track}
                response = dut.api('vrrp').update(interface, vrid, **vrconfig)
                self.assertIs(response, True)

    def test_update_bfd_ip(self):
        vrid = 104
        for dut in self.duts:
            interface = self._vlan_setup(dut)
            dut.config(['interface %s' % interface,
                        'no vrrp %d' % vrid,
                        'vrrp %d shutdown' % vrid,
                        'exit'])

            for bfd_ip in BFD_IP:
                vrconfig = {'bfd_ip': bfd_ip}
                response = dut.api('vrrp').update(interface, vrid, **vrconfig)
                self.assertIs(response, True)


if __name__ == '__main__':
    unittest.main()
