#
# right (c) 2015, Arista Networks, Inc.
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

from testlib import get_fixture, function
from testlib import EapiConfigUnitTest

import pyeapi.api.vrrp

upd_intf = 'Vlan50'
upd_vrid = 10
upd_cmd = 'interface %s' % upd_intf
known_vrrps = {
    'Ethernet1': {
        10: {'priority': 175,
             'timers_advertise': 1,
             'mac_addr_adv_interval': 30,
             'preempt': True,
             'preempt_delay_min': 0,
             'preempt_delay_reload': 0,
             'delay_reload': 0,
             'primary_ip': '10.10.6.10',
             'secondary_ip': [],
             'description': 'vrrp 10 on Ethernet1',
             'enable': True,
             'track': [],
             'bfd_ip': '',
             'ip_version': 2}
    },
    'Port-Channel10': {
        10: {'priority': 150,
             'timers_advertise': 1,
             'mac_addr_adv_interval': 30,
             'preempt': True,
             'preempt_delay_min': 0,
             'preempt_delay_reload': 0,
             'delay_reload': 0,
             'primary_ip': '10.10.5.10',
             'secondary_ip': ['10.10.5.20'],
             'description': 'vrrp 10 on Port-Channel10',
             'enable': True,
             'track': [],
             'bfd_ip': '',
             'ip_version': 2}
    },
    'Vlan50': {
        10: {'priority': 200,
             'timers_advertise': 3,
             'mac_addr_adv_interval': 30,
             'preempt': True,
             'preempt_delay_min': 0,
             'preempt_delay_reload': 0,
             'delay_reload': 0,
             'primary_ip': '10.10.4.10',
             'secondary_ip': ['10.10.4.21', '10.10.4.22',
                              '10.10.4.23', '10.10.4.24'],
             'description': '',
             'enable': True,
             'track': [
                 {'name': 'Ethernet1', 'action': 'decrement', 'amount': 10},
                 {'name': 'Ethernet1', 'action': 'shutdown'},
                 {'name': 'Ethernet2', 'action': 'decrement', 'amount': 50},
                 {'name': 'Ethernet2', 'action': 'shutdown'},
                 {'name': 'Ethernet11', 'action': 'decrement', 'amount': 75},
                 {'name': 'Ethernet11', 'action': 'shutdown'},
             ],
             'bfd_ip': '',
             'ip_version': 2},
        20: {'priority': 100,
             'timers_advertise': 5,
             'mac_addr_adv_interval': 30,
             'preempt': False,
             'preempt_delay_min': 0,
             'preempt_delay_reload': 0,
             'delay_reload': 0,
             'primary_ip': '10.10.4.20',
             'secondary_ip': [],
             'description': '',
             'enable': False,
             'track': [
                 {'name': 'Ethernet1', 'action': 'shutdown'},
                 {'name': 'Ethernet2', 'action': 'decrement', 'amount': 1},
                 {'name': 'Ethernet2', 'action': 'shutdown'},
             ],
             'bfd_ip': '',
             'ip_version': 2},
        30: {'priority': 50,
             'timers_advertise': 1,
             'mac_addr_adv_interval': 30,
             'preempt': True,
             'preempt_delay_min': 0,
             'preempt_delay_reload': 0,
             'delay_reload': 0,
             'primary_ip': '10.10.4.30',
             'secondary_ip': [],
             'description': '',
             'enable': True,
             'track': [],
             'bfd_ip': '10.10.4.33',
             'ip_version': 2}
    }
}


class TestApiVrrp(EapiConfigUnitTest):

    maxDiff = None

    def __init__(self, *args, **kwargs):
        super(TestApiVrrp, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.vrrp.Vrrp(None)
        self.config = open(get_fixture('running_config.vrrp')).read()

    def test_instance(self):
        result = pyeapi.api.vrrp.instance(None)
        self.assertIsInstance(result, pyeapi.api.vrrp.Vrrp)

    def test_get(self):
        # Request various sets of vrrp configurations
        for interface in known_vrrps:
            known = known_vrrps.get(interface)
            for vrid in known:
                known[vrid] = self.instance.vrconf_format(known[vrid])
            result = self.instance.get(interface)
            self.assertEqual(result, known)

    def test_get_non_existent_interface(self):
        # Request vrrp configuration for an interface that
        # is not defined
        result = self.instance.get('Vlan2000')
        self.assertIsNone(result)

    def test_get_invalid_parameters(self):
        # Pass empty, None, or other invalid parameters to get()
        with self.assertRaises(ValueError):
            self.instance.get('')
        with self.assertRaises(ValueError):
            self.instance.get(None)

    def test_getall(self):
        # Get all the vrrp configurations from the config
        result = self.instance.getall()
        self.assertEqual(result, known_vrrps)

    def test_create(self):
        interface = 'Ethernet1'
        vrid = 10

        # Test create with a normal configuration
        configuration = {
            'primary_ip': '10.10.60.10',
            'priority': 200,
            'description': 'modified vrrp 10 on Ethernet1',
            'secondary_ip': ['10.10.60.20', '10.10.60.30'],
            'ip_version': 3,
            'timers_advertise': 2,
            'mac_addr_adv_interval': 3,
            'preempt': True,
            'preempt_delay_min': 1,
            'preempt_delay_reload': 1,
            'delay_reload': 1,
            'track': [
                {'name': 'Ethernet1', 'action': 'decrement', 'amount': 1},
                {'name': 'Ethernet1', 'action': 'shutdown'},
                {'name': 'Ethernet2', 'action': 'decrement', 'amount': 1},
                {'name': 'Ethernet2', 'action': 'shutdown'},
            ],
            'bfd_ip': '10.10.60.30',
        }

        cmds = [
            'interface Ethernet1',
            'vrrp 10 shutdown',
            'vrrp 10 ip 10.10.60.10',
            'vrrp 10 priority 200',
            'vrrp 10 description modified vrrp 10 on Ethernet1',
            'vrrp 10 ip version 3',
            'vrrp 10 ip 10.10.60.20 secondary',
            'vrrp 10 ip 10.10.60.30 secondary',
            'vrrp 10 timers advertise 2',
            'vrrp 10 mac-address advertisement-interval 3',
            'vrrp 10 preempt',
            'vrrp 10 preempt delay minimum 1',
            'vrrp 10 preempt delay reload 1',
            'vrrp 10 delay reload 1',
            'vrrp 10 track Ethernet1 decrement 1',
            'vrrp 10 track Ethernet1 shutdown',
            'vrrp 10 track Ethernet2 decrement 1',
            'vrrp 10 track Ethernet2 shutdown',
            'vrrp 10 bfd ip 10.10.60.30',
        ]
        func = function('create', interface, vrid, **configuration)

        self.eapi_positive_config_test(func, cmds)

        # Test create setting possible parameters to 'no'
        configuration = {
            'primary_ip': 'no',
            'priority': 'no',
            'description': 'no',
            'secondary_ip': [],
            'ip_version': 'no',
            'timers_advertise': 'no',
            'mac_addr_adv_interval': 'no',
            'preempt': 'no',
            'preempt_delay_min': 'no',
            'preempt_delay_reload': 'no',
            'delay_reload': 'no',
            'track': [],
            'bfd_ip': 'no',
        }

        cmds = [
            'interface Ethernet1',
            'vrrp 10 shutdown',
            'no vrrp 10 ip 10.10.6.10',
            'no vrrp 10 priority',
            'no vrrp 10 description',
            'no vrrp 10 ip version',
            'no vrrp 10 timers advertise',
            'no vrrp 10 mac-address advertisement-interval',
            'no vrrp 10 preempt',
            'no vrrp 10 preempt delay minimum',
            'no vrrp 10 preempt delay reload',
            'no vrrp 10 delay reload',
            'no vrrp 10 bfd ip',
        ]
        func = function('create', interface, vrid, **configuration)

        self.eapi_positive_config_test(func, cmds)

        # Test create setting possible parameters to 'default'
        configuration = {
            'primary_ip': 'default',
            'priority': 'default',
            'description': 'default',
            'secondary_ip': [],
            'ip_version': 'default',
            'timers_advertise': 'default',
            'mac_addr_adv_interval': 'default',
            'preempt': 'default',
            'preempt_delay_min': 'default',
            'preempt_delay_reload': 'default',
            'delay_reload': 'default',
            'track': [],
            'bfd_ip': 'default',
        }

        cmds = [
            'interface Ethernet1',
            'vrrp 10 shutdown',
            'default vrrp 10 ip 10.10.6.10',
            'default vrrp 10 priority',
            'default vrrp 10 description',
            'default vrrp 10 ip version',
            'default vrrp 10 timers advertise',
            'default vrrp 10 mac-address advertisement-interval',
            'default vrrp 10 preempt',
            'default vrrp 10 preempt delay minimum',
            'default vrrp 10 preempt delay reload',
            'default vrrp 10 delay reload',
            'default vrrp 10 bfd ip',
        ]
        func = function('create', interface, vrid, **configuration)

        self.eapi_positive_config_test(func, cmds)

    def test_delete(self):
        interface = 'Ethernet1'
        vrid = 10

        cmds = [
            'interface Ethernet1',
            'no vrrp 10',
        ]

        func = function('delete', interface, vrid)

        self.eapi_positive_config_test(func, cmds)

    def test_default(self):
        interface = 'Ethernet1'
        vrid = 10

        cmds = [
            'interface Ethernet1',
            'default vrrp 10',
        ]

        func = function('default', interface, vrid)

        self.eapi_positive_config_test(func, cmds)

    def test_set_enable(self):
        # no vrrp 10 shutdown

        # Test set_enable gives properly formatted commands
        cases = [
            (False, 'vrrp %d shutdown' % upd_vrid),
            (True, 'no vrrp %d shutdown' % upd_vrid),
        ]

        for (enable, cmd) in cases:
            func = function('set_enable', upd_intf, upd_vrid, value=enable)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError from invalid parameters
        cases = ['a', 200]

        for enable in cases:
            func = function('set_enable', upd_intf, upd_vrid, value=enable)
            self.eapi_exception_config_test(func, ValueError)

    def test_set_primary_ip(self):
        # vrrp 10 ip 10.10.4.10

        # Test set_primary_ip gives properly formatted commands
        ip1 = '10.10.4.110'
        ipcurr = '10.10.4.10'
        cases = [
            (ip1, None, None, 'vrrp %d ip %s' % (upd_vrid, ip1)),
            (ip1, True, None, 'no vrrp %d ip %s' % (upd_vrid, ipcurr)),
            (ip1, None, True, 'default vrrp %d ip %s' % (upd_vrid, ipcurr)),
            (ip1, True, True, 'default vrrp %d ip %s' % (upd_vrid, ipcurr)),
        ]

        for (primary_ip, disable, default, cmd) in cases:
            func = function('set_primary_ip', upd_intf, upd_vrid,
                            value=primary_ip, disable=disable, default=default)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError from invalid parameters
        cases = ['abc', 500, '101.101']

        for primary_ip in cases:
            func = function('set_primary_ip', upd_intf, upd_vrid,
                            value=primary_ip)
            self.eapi_exception_config_test(func, ValueError)

    def test_set_priority(self):
        # vrrp 10 priority 200

        # Test set_primary_ip gives properly formatted commands
        cases = [
            (150, None, None, 'vrrp %d priority 150' % upd_vrid),
            (None, None, True, 'default vrrp %d priority' % upd_vrid),
            (None, True, True, 'default vrrp %d priority' % upd_vrid),
            (None, True, None, 'no vrrp %d priority' % upd_vrid),
        ]

        for (priority, disable, default, cmd) in cases:
            func = function('set_priority', upd_intf, upd_vrid,
                            value=priority, disable=disable, default=default)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError from invalid parameters
        cases = ['abc', 500, False]

        for priority in cases:
            func = function('set_priority', upd_intf, upd_vrid,
                            value=priority)
            self.eapi_exception_config_test(func, ValueError)

    def test_set_description(self):
        # no vrrp 10 description

        desc = 'test description'

        # Test set_description gives properly formatted commands
        cases = [
            (desc, None, None, 'vrrp %d description %s' % (upd_vrid, desc)),
            (None, None, True, 'default vrrp %d description' % upd_vrid),
            (None, True, True, 'default vrrp %d description' % upd_vrid),
            (None, True, None, 'no vrrp %d description' % upd_vrid),
        ]

        for (description, disable, default, cmd) in cases:
            func = function('set_description', upd_intf, upd_vrid,
                            value=description, disable=disable,
                            default=default)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

    def test_set_ip_version(self):
        # vrrp 10 ip version 2
        # Test set_description gives properly formatted commands
        cases = [
            (2, None, None, 'vrrp %d ip version 2' % upd_vrid),
            (None, None, True, 'default vrrp %d ip version' % upd_vrid),
            (None, True, True, 'default vrrp %d ip version' % upd_vrid),
            (None, True, None, 'no vrrp %d ip version' % upd_vrid),
        ]

        for (ip_version, disable, default, cmd) in cases:
            func = function('set_ip_version', upd_intf, upd_vrid,
                            value=ip_version, disable=disable, default=default)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError by entering invalid parameters
        cases = ['a', 5]

        for ip_version in cases:
            func = function('set_ip_version', upd_intf, upd_vrid,
                            value=ip_version)
            self.eapi_exception_config_test(func, ValueError)

    def test_set_secondary_ips(self):
        # vrrp 10 ip 10.10.4.21 secondary
        # vrrp 10 ip 10.10.4.22 secondary
        # vrrp 10 ip 10.10.4.23 secondary

        curr1 = '10.10.4.21'
        curr2 = '10.10.4.22'
        curr3 = '10.10.4.23'
        curr4 = '10.10.4.24'

        new1 = '10.10.4.31'
        new2 = '10.10.4.32'
        new3 = '10.10.4.33'
        new4 = curr4

        # Test set_secondary_ips gives properly formatted commands
        cases = [
            ([new1, new2, new3],
             {'add': [new1, new2, new3],
              'remove': [curr1, curr2, curr3, curr4]}),
            ([new1, new2, new4],
             {'add': [new1, new2],
              'remove': [curr1, curr2, curr3]}),
            ([],
             {'add': [],
              'remove': [curr1, curr2, curr3, curr4]}),
        ]

        for (secondary_ips, cmd_dict) in cases:
            cmds = []
            for sec_ip in cmd_dict['add']:
                cmds.append("vrrp %d ip %s secondary" % (upd_vrid, sec_ip))

            for sec_ip in cmd_dict['remove']:
                cmds.append("no vrrp %d ip %s secondary" % (upd_vrid, sec_ip))

            func = function('set_secondary_ips', upd_intf, upd_vrid,
                            secondary_ips)
            exp_cmds = [upd_cmd] + sorted(cmds)
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError by entering invalid parameters
        cases = [
            [new1, new2, 'abc'],
            [new1, new2, '10.10.10'],
            [new1, new2, True],
        ]

        for secondary_ips in cases:
            func = function('set_secondary_ips', upd_intf, upd_vrid,
                            secondary_ips)
            self.eapi_exception_config_test(func, ValueError)

    def test_set_timers_advertise(self):
        # vrrp 10 timers advertise 3

        # Test set_timers_advertise gives properly formatted commands
        cases = [
            (50, None, None, 'vrrp %d timers advertise 50' % upd_vrid),
            (None, None, True, 'default vrrp %d timers advertise' % upd_vrid),
            (None, True, True, 'default vrrp %d timers advertise' % upd_vrid),
            (None, True, None, 'no vrrp %d timers advertise' % upd_vrid),
        ]

        for (timers_advertise, disable, default, cmd) in cases:
            func = function('set_timers_advertise', upd_intf, upd_vrid,
                            value=timers_advertise, disable=disable,
                            default=default)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError by entering invalid parameters
        cases = [256, 0, 'a']

        for timers_advertise in cases:
            func = function('set_timers_advertise', upd_intf, upd_vrid,
                            value=timers_advertise)
            self.eapi_exception_config_test(func, ValueError)

    def test_set_mac_addr_adv_interval(self):
        # vrrp 10 mac-address advertisement-interval 30

        # Test set_timers_advertise gives properly formatted commands
        maadvint = 'mac-address advertisement-interval'
        cases = [
            (50, None, None, 'vrrp %d %s 50' % (upd_vrid, maadvint)),
            (None, None, True, 'default vrrp %d %s' % (upd_vrid, maadvint)),
            (None, True, True, 'default vrrp %d %s' % (upd_vrid, maadvint)),
            (None, True, None, 'no vrrp %d %s' % (upd_vrid, maadvint)),
        ]

        for (mac_addr_adv_interval, disable, default, cmd) in cases:
            func = function('set_mac_addr_adv_interval', upd_intf, upd_vrid,
                            value=mac_addr_adv_interval, disable=disable,
                            default=default)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError by entering invalid parameters
        cases = ['a', 10000]

        for mac_addr_adv_interval in cases:
            func = function('set_mac_addr_adv_interval', upd_intf, upd_vrid,
                            value=mac_addr_adv_interval)
            self.eapi_exception_config_test(func, ValueError)

    def test_set_preempt(self):
        # vrrp 10 preempt

        # Test set_description gives properly formatted commands
        cases = [
            (False, None, None, 'no vrrp %d preempt' % upd_vrid),
            (True, None, None, 'vrrp %d preempt' % upd_vrid),
            (None, None, True, 'default vrrp %d preempt' % upd_vrid),
            (None, True, True, 'default vrrp %d preempt' % upd_vrid),
            (None, True, None, 'no vrrp %d preempt' % upd_vrid),
        ]

        for (preempt, disable, default, cmd) in cases:
            func = function('set_preempt', upd_intf, upd_vrid,
                            value=preempt, disable=disable, default=default)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError by entering invalid parameters
        cases = ['a', 5]

        for preempt in cases:
            func = function('set_preempt', upd_intf, upd_vrid,
                            value=preempt)
            self.eapi_exception_config_test(func, ValueError)

    def test_set_preempt_delay_min(self):
        # vrrp 10 preempt delay minimum 0

        # Test set_preempt_delay_min gives properly formatted commands
        cases = [
            (2500, None, None,
             'vrrp %d preempt delay minimum 2500' % upd_vrid),
            (None, None, True,
             'default vrrp %d preempt delay minimum' % upd_vrid),
            (None, True, True,
             'default vrrp %d preempt delay minimum' % upd_vrid),
            (None, True, None, 'no vrrp %d preempt delay minimum' % upd_vrid),
        ]

        for (preempt_delay_min, disable, default, cmd) in cases:
            func = function('set_preempt_delay_min', upd_intf, upd_vrid,
                            value=preempt_delay_min, disable=disable,
                            default=default)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError by entering invalid parameters
        cases = ['a', 3601]

        for preempt_delay_min in cases:
            func = function('set_preempt_delay_min', upd_intf, upd_vrid,
                            value=preempt_delay_min)
            self.eapi_exception_config_test(func, ValueError)

    def test_set_preempt_delay_reload(self):
        # vrrp 10 preempt delay reload 0

        # Test set_preempt_delay_min gives properly formatted commands
        cases = [
            (1500, None, None,
             'vrrp %d preempt delay reload 1500' % upd_vrid),
            (None, None, True,
             'default vrrp %d preempt delay reload' % upd_vrid),
            (None, True, True,
             'default vrrp %d preempt delay reload' % upd_vrid),
            (None, True, None, 'no vrrp %d preempt delay reload' % upd_vrid),
        ]

        for (preempt_delay_reload, disable, default, cmd) in cases:
            func = function('set_preempt_delay_reload', upd_intf, upd_vrid,
                            value=preempt_delay_reload, disable=disable,
                            default=default)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError by entering invalid parameters
        cases = ['a', 3601]

        for preempt_delay_reload in cases:
            func = function('set_preempt_delay_reload', upd_intf, upd_vrid,
                            value=preempt_delay_reload)
            self.eapi_exception_config_test(func, ValueError)

    def test_set_delay_reload(self):
        # vrrp 10 delay reload 0

        # Test set_delay_min gives properly formatted commands
        cases = [
            (1750, None, None, 'vrrp %d delay reload 1750' % upd_vrid),
            (None, None, True, 'default vrrp %d delay reload' % upd_vrid),
            (None, True, True, 'default vrrp %d delay reload' % upd_vrid),
            (None, True, None, 'no vrrp %d delay reload' % upd_vrid),
        ]

        for (delay_reload, disable, default, cmd) in cases:
            func = function('set_delay_reload', upd_intf, upd_vrid,
                            value=delay_reload, disable=disable,
                            default=default)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError by entering invalid parameters
        cases = ['a', 3601]

        for delay_reload in cases:
            func = function('set_delay_reload', upd_intf, upd_vrid,
                            value=delay_reload)
            self.eapi_exception_config_test(func, ValueError)

    def test_set_tracks(self):
        # vrrp 10 track Ethernet1 decrement 10
        # vrrp 10 track Ethernet1 shutdown
        # vrrp 10 track Ethernet2 decrement 50
        # vrrp 10 track Ethernet2 shutdown
        # vrrp 10 track Ethernet11 decrement 75
        # vrrp 10 track Ethernet11 shutdown

        curr1 = {'name': 'Ethernet1', 'action': 'decrement', 'amount': 10}
        curr2 = {'name': 'Ethernet1', 'action': 'shutdown'}
        curr3 = {'name': 'Ethernet2', 'action': 'decrement', 'amount': 50}
        curr4 = {'name': 'Ethernet2', 'action': 'shutdown'}
        curr5 = {'name': 'Ethernet11', 'action': 'decrement', 'amount': 75}
        curr6 = {'name': 'Ethernet11', 'action': 'shutdown'}

        new1 = curr1
        new2 = {'name': 'Ethernet2', 'action': 'decrement', 'amount': 49}
        new3 = {'name': 'Ethernet3', 'action': 'shutdown'}
        new4 = {'name': 'Ethernet4', 'action': 'decrement', 'amount': 50}
        new5 = {'name': 'Ethernet5', 'action': 'shutdown'}
        new6 = {'name': 'Ethernet9', 'action': 'decrement', 'amount': 75}

        # Test set_track gives properly formatted commands
        cases = [
            ([curr6, curr5, new1, new2],
             {'add': [new2],
              'remove': [curr2, curr3, curr4]}),
            ([new2, new3, new4, new5, new6],
             {'add': [new2, new3, new4, new5, new6],
              'remove': [curr1, curr2, curr3, curr4, curr5, curr6]}),
            ([],
             {'add': [],
              'remove': [curr1, curr2, curr3, curr4, curr5, curr6]}),
        ]

        for (tracks, cmd_dict) in cases:
            cmds = []
            for add in cmd_dict['add']:
                tr_obj = add['name']
                action = add['action']
                amount = add['amount'] if 'amount' in add else ''
                cmd = ("vrrp %d track %s %s %s"
                       % (upd_vrid, tr_obj, action, amount))
                cmds.append(cmd.rstrip())

            for remove in cmd_dict['remove']:
                tr_obj = remove['name']
                action = remove['action']
                amount = remove['amount'] if 'amount' in remove else ''
                cmd = ("no vrrp %d track %s %s %s"
                       % (upd_vrid, tr_obj, action, amount))
                cmds.append(cmd.rstrip())

            func = function('set_tracks', upd_intf, upd_vrid, tracks)
            exp_cmds = [upd_cmd] + sorted(cmds)
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError by entering invalid parameters
        cases = [
            [{'name': 'Ethernet1', 'action': 'disable', 'amount': 10}],
            [{'name': 'Ethernet1', 'action': 'decrement', 'amount': True}],
            [{'name': 'Ethernet1', 'action': 'shutdown', 'amount': 10}],
            [{'action': 'decrement', 'amount': 10}],
            [{'name': 'Ethernet1', 'action': 'decrement',
              'amount': 10, 'bad': 1}],
        ]

        for tracks in cases:
            func = function('set_tracks', upd_intf, upd_vrid, tracks)
            self.eapi_exception_config_test(func, ValueError)

    def test_set_bfd_ip(self):
        # no vrrp 10 bfd ip

        bfd_addr = '10.10.4.101'

        # Test bfd_ip gives properly formatted commands
        cases = [
            (bfd_addr, None, None, 'vrrp %d bfd ip %s' % (upd_vrid, bfd_addr)),
            (None, True, None, 'no vrrp %d bfd ip' % upd_vrid),
            (None, None, True, 'default vrrp %d bfd ip' % upd_vrid),
            (None, True, True, 'default vrrp %d bfd ip' % upd_vrid),
        ]

        for (bfd_ip, disable, default, cmd) in cases:
            func = function('set_bfd_ip', upd_intf, upd_vrid,
                            value=bfd_ip, disable=disable, default=default)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError from invalid parameters
        cases = ['abc', 500, '101.101']

        for bfd_ip in cases:
            func = function('set_bfd_ip', upd_intf, upd_vrid,
                            value=bfd_ip)
            self.eapi_exception_config_test(func, ValueError)

    def test_vrconf_format(self):
        # Test the function to format a vrrp configuration to
        # match the output from get/getall
        vrconf = {
            'priority': None,
            'timers_advertise': None,
            'mac_addr_adv_interval': None,
            'preempt': 'default',
            'preempt_delay_min': None,
            'preempt_delay_reload': None,
            'delay_reload': None,
            'primary_ip': None,
            'secondary_ip': ['10.10.4.22', '10.10.4.21'],
            'description': None,
            'enable': True,
            'track': [
                {'name': 'Ethernet1', 'action': 'shutdown'},
                {'name': 'Ethernet1', 'action': 'decrement', 'amount': 10},
            ],
            'bfd_ip': None,
            'ip_version': None}

        fixed = {
            'priority': 100,
            'timers_advertise': 1,
            'mac_addr_adv_interval': 30,
            'preempt': False,
            'preempt_delay_min': 0,
            'preempt_delay_reload': 0,
            'delay_reload': 0,
            'primary_ip': '0.0.0.0',
            'secondary_ip': ['10.10.4.21', '10.10.4.22'],
            'description': None,
            'enable': True,
            'track': [
                {'name': 'Ethernet1', 'action': 'decrement', 'amount': 10},
                {'name': 'Ethernet1', 'action': 'shutdown'},
            ],
            'bfd_ip': '',
            'ip_version': 2}

        # Get the vrconf_format method from the library
        func = getattr(self.instance, 'vrconf_format')
        # Call the method with the vrconf dictionary
        result = func(vrconf)
        # And verify the result is a properly formatted dictionary
        self.assertEqual(fixed, result)


if __name__ == '__main__':
    unittest.main()
