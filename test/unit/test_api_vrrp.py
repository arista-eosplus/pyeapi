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
             'authentication': '',
             'primary_ip': '10.10.6.10',
             'secondary_ip': {'exists': None},
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
             'authentication': '',
             'primary_ip': '10.10.5.10',
             'secondary_ip': {
                'exists': ['10.10.5.20']
             },
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
             'authentication': '',
             'primary_ip': '10.10.4.10',
             'secondary_ip': {
                'exists': ['10.10.4.21']
             },
             'description': '',
             'enable': True,
             'track': [
                {
                    'name': 'Ethernet1',
                    'track_action': 'shutdown',
                    'track_amount': None
                }
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
             'authentication': 'text 12345',
             'primary_ip': '10.10.4.20',
             'secondary_ip': {'exists': None},
             'description': '',
             'enable': False,
             'track': [
                {
                    'name': 'Ethernet1',
                    'track_action': 'shutdown',
                    'track_amount': None
                },
                {
                    'name': 'Ethernet2',
                    'track_action': 'decrement',
                    'track_amount': 1
                },
                {
                    'name': 'Ethernet2',
                    'track_action': 'shutdown',
                    'track_amount': None
                },
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
             'authentication':
             'ietf-md5 key-string 7 bu1yTgzm0RDgraNS0MNkaA==',
             'primary_ip': '10.10.4.30',
             'secondary_ip': {'exists': None},
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
        vrrp = ['Vlan50', 'Ethernet1', 'Port-Channel10']
        # vrrp = [('Vlan50', 10),
        #         ('Vlan50', 20),
        #         ('Ethernet1', 10),
        #         ('Port-Channel10', 10)]

        for interface in vrrp:
            known = known_vrrps.get(interface)
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
        configuration = {
            'primary_ip': '10.10.60.10',
            'priority': 200,
            'description': 'modified vrrp 10 on Ethernet1',
            'secondary_ip': {
                'add': ['10.10.60.20'],
                'remove': ['10.10.60.30'],
            },
            'ip_version': 3,
            'timers_advertise': 2,
            'mac_addr_adv_interval': 3,
            'preempt': False,
            'preempt_delay_min': 1,
            'preempt_delay_reload': 1,
            'delay_reload': 1,
            'authentication': '',
            'track': [
                {
                    'name': 'Ethernet1',
                    'track_action': 'decrement',
                    'track_amount': None
                },
                {
                    'name': 'Ethernet1',
                    'track_action': 'shutdown',
                    'track_amount': 1
                },
                {
                    'name': 'Ethernet2',
                    'track_action': 'decrement',
                    'track_amount': 1
                },
                {
                    'name': 'Ethernet2',
                    'track_action': 'shutdown',
                    'track_amount': 1
                },
            ],
            'bfd_ip': '10.10.60.30',
        }

        cmds = [
            'interface Ethernet1',
            'vrrp 10 ip 10.10.60.10',
            'vrrp 10 priority 200',
            'vrrp 10 description modified vrrp 10 on Ethernet1',
            'vrrp 10 ip 10.10.60.20 secondary',
            'no vrrp 10 ip 10.10.60.30 secondary',
            'vrrp 10 ip version 3',
            'vrrp 10 shutdown',
            'vrrp 10 timers advertise 2',
            'vrrp 10 mac-address advertisement-interval 3',
            'no vrrp 10 preempt',
            'vrrp 10 preempt delay minimum 1',
            'vrrp 10 preempt delay reload 1',
            'vrrp 10 delay reload 1',
            # 'no vrrp 10 authentication',
            'no vrrp 10 track Ethernet1 decrement',
            'vrrp 10 track Ethernet1 shutdown',
            'vrrp 10 track Ethernet2 decrement 1',
            'vrrp 10 track Ethernet2 shutdown',
            'vrrp 10 bfd ip 10.10.60.30',
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

    def test_update_primary_ip(self):
        # vrrp 10 ip 10.10.4.10
        ip1 = '10.10.4.110'
        ipcurr = '10.10.4.10'
        cases = [
            (ip1, 'vrrp %d ip %s' % (upd_vrid, ip1)),
            ('default', 'default vrrp %d ip %s' % (upd_vrid, ipcurr)),
            ('no', 'no vrrp %d ip %s' % (upd_vrid, ipcurr)),
            (None, 'no vrrp %d ip %s' % (upd_vrid, ipcurr)),
        ]

        for (primary_ip, cmd) in cases:
            func = function('update', upd_intf, upd_vrid,
                            primary_ip=primary_ip)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

    def test_update_priority(self):
        # vrrp 10 priority 200
        cases = [
            (150, 'vrrp %d priority 150' % upd_vrid),
            ('default', 'default vrrp %d priority' % upd_vrid),
            ('no', 'no vrrp %d priority' % upd_vrid),
            (None, 'no vrrp %d priority' % upd_vrid),
        ]

        for (priority, cmd) in cases:
            func = function('update', upd_intf, upd_vrid,
                            priority=priority)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

    def test_update_description(self):
        # no vrrp 10 description
        desc = 'test description'
        cases = [
            (desc, 'vrrp %d description %s' % (upd_vrid, desc)),
            ('default', 'default vrrp %d description' % upd_vrid),
            ('no', 'no vrrp %d description' % upd_vrid),
            (None, 'no vrrp %d description' % upd_vrid),
        ]

        for (description, cmd) in cases:
            func = function('update', upd_intf, upd_vrid,
                            description=description)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

    def test_update_secondary_ip(self):
        # vrrp 10 ip 10.10.4.21 secondary
        ip1 = '10.10.4.41'
        ip2 = '10.10.4.42'
        ipcurr = '10.10.4.21'
        cases = [
            (
                {'add': [ip1, ip2], 'remove': [ipcurr]},
                ['vrrp %d ip %s secondary' % (upd_vrid, ip1),
                 'vrrp %d ip %s secondary' % (upd_vrid, ip2),
                 'no vrrp %d ip %s secondary' % (upd_vrid, ipcurr)]
            ),
        ]

        for (secondary_ip, cmd) in cases:
            func = function('update', upd_intf, upd_vrid,
                            secondary_ip=secondary_ip)
            exp_cmds = [upd_cmd] + cmd
            self.eapi_positive_config_test(func, exp_cmds)

    def test_update_ip_version(self):
        # vrrp 10 ip version 2
        cases = [
            (3, 'vrrp %d ip version 3' % upd_vrid),
            ('default', 'default vrrp %d ip version' % upd_vrid),
            ('no', 'no vrrp %d ip version' % upd_vrid),
            (None, 'no vrrp %d ip version' % upd_vrid),
        ]

        for (ip_version, cmd) in cases:
            func = function('update', upd_intf, upd_vrid,
                            ip_version=ip_version)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError by entering invalid parameters
        cases = ['a', 5]

        for ip_version in cases:
            func = function('update', upd_intf, upd_vrid,
                            ip_version=ip_version)
            self.eapi_exception_config_test(func, ValueError)

    def test_update_enable(self):
        # Test when going from enabled to disabled
        # no vrrp 10 shutdown
        cases = [
            (False, 'vrrp %d shutdown' % upd_vrid),
            (True, None),
            ('no', 'no vrrp %d shutdown' % upd_vrid),
            ('default', 'default vrrp %d shutdown' % upd_vrid),
        ]

        for (enable, cmd) in cases:
            func = function('update', upd_intf, upd_vrid,
                            enable=enable)
            if cmd is not None:
                exp_cmds = [upd_cmd] + [cmd]
            else:
                exp_cmds = [upd_cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        # Test against vrrp 20 for going from disabled to enabled
        # vrrp 20 shutdown
        alt_vrid = 20
        cases = [
            (True, 'no vrrp %d shutdown' % alt_vrid),
            (False, None),
            ('no', 'no vrrp %d shutdown' % alt_vrid),
            ('default', 'default vrrp %d shutdown' % alt_vrid)
        ]

        for (enable, cmd) in cases:
            func = function('update', upd_intf, alt_vrid,
                            enable=enable)
            if cmd is not None:
                exp_cmds = [upd_cmd] + [cmd]
            else:
                exp_cmds = [upd_cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError by entering invalid parameters
        cases = ['a', 200]

        for enable in cases:
            func = function('update', upd_intf, upd_vrid,
                            enable=enable)
            self.eapi_exception_config_test(func, ValueError)

    def test_update_timers_advertise(self):
        # vrrp 10 timers advertise 3
        cases = [
            (255, 'vrrp %d timers advertise 255' % upd_vrid),
            ('default', 'default vrrp %d timers advertise' % upd_vrid),
            ('no', 'no vrrp %d timers advertise' % upd_vrid),
            (None, 'no vrrp %d timers advertise' % upd_vrid),
        ]

        for (timers_adv, cmd) in cases:
            func = function('update', upd_intf, upd_vrid,
                            timers_advertise=timers_adv)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        cases = [256, 0, 'a']

        for timers_adv in cases:
            func = function('update', upd_intf, upd_vrid,
                            timers_advertise=timers_adv)
            self.eapi_exception_config_test(func, ValueError)

    def test_update_mac_addr_adv_int(self):
        # vrrp 10 mac-address advertisement-interval 30
        cases = [
            (3, 'vrrp %d mac-address advertisement-interval 3' % upd_vrid),
            ('default', 'default vrrp %d mac-address advertisement-interval'
             % upd_vrid),
            ('no', 'no vrrp %d mac-address advertisement-interval' % upd_vrid),
            (None, 'no vrrp %d mac-address advertisement-interval' % upd_vrid),
        ]

        for (mac_add_adv_int, cmd) in cases:
            func = function('update', upd_intf, upd_vrid,
                            mac_addr_adv_interval=mac_add_adv_int)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError by entering invalid parameters
        cases = ['a', 10000]

        for mac_add_adv_int in cases:
            func = function('update', upd_intf, upd_vrid,
                            mac_addr_adv_interval=mac_add_adv_int)
            self.eapi_exception_config_test(func, ValueError)

    def test_update_preempt(self):
        # vrrp 10 preempt
        cases = [
            (False, 'no vrrp %d preempt' % upd_vrid),
            ('default', 'default vrrp %d preempt' % upd_vrid),
            ('no', 'no vrrp %d preempt' % upd_vrid),
        ]

        for (preempt, cmd) in cases:
            func = function('update', upd_intf, upd_vrid,
                            preempt=preempt)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        # Test turning on preempt
        # no vrrp 20 preempt
        alt_vrid = 20
        cases = [
            (True, 'vrrp %d preempt' % alt_vrid),
            ('default', 'default vrrp %d preempt' % alt_vrid),
            ('no', 'no vrrp %d preempt' % alt_vrid),
        ]

        for (preempt, cmd) in cases:
            func = function('update', upd_intf, alt_vrid,
                            preempt=preempt)
            if cmd is not None:
                exp_cmds = [upd_cmd] + [cmd]
            else:
                exp_cmds = [upd_cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError by entering invalid parameters
        cases = ['a', 5]

        for preempt in cases:
            func = function('update', upd_intf, upd_vrid,
                            preempt=preempt)
            self.eapi_exception_config_test(func, ValueError)

    def test_update_preempt_delay_min(self):
        # vrrp 10 preempt delay minimum 0
        cases = [
            (3, 'vrrp %d preempt delay minimum 3' % upd_vrid),
            ('default', 'default vrrp %d preempt delay minimum' % upd_vrid),
            ('no', 'no vrrp %d preempt delay minimum' % upd_vrid),
            (None, 'no vrrp %d preempt delay minimum' % upd_vrid),
        ]

        for (preempt_dly_min, cmd) in cases:
            func = function('update', upd_intf, upd_vrid,
                            preempt_delay_min=preempt_dly_min)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError by entering invalid parameters
        cases = ['a', 3601]

        for preempt_dly_min in cases:
            func = function('update', upd_intf, upd_vrid,
                            preempt_delay_min=preempt_dly_min)
            self.eapi_exception_config_test(func, ValueError)

    def test_update_preempt_delay_reload(self):
        # vrrp 10 preempt delay reload 0
        cases = [
            (3, 'vrrp %d preempt delay reload 3' % upd_vrid),
            ('default', 'default vrrp %d preempt delay reload' % upd_vrid),
            ('no', 'no vrrp %d preempt delay reload' % upd_vrid),
            (None, 'no vrrp %d preempt delay reload' % upd_vrid),
        ]

        for (preempt_dly_rld, cmd) in cases:
            func = function('update', upd_intf, upd_vrid,
                            preempt_delay_reload=preempt_dly_rld)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError by entering invalid parameters
        cases = ['a', 3601]

        for preempt_dly_rld in cases:
            func = function('update', upd_intf, upd_vrid,
                            preempt_delay_reload=preempt_dly_rld)
            self.eapi_exception_config_test(func, ValueError)

    def test_update_delay_reload(self):
        # vrrp 10 delay reload 0
        cases = [
            (3, 'vrrp %d delay reload 3' % upd_vrid),
            ('default', 'default vrrp %d delay reload' % upd_vrid),
            ('no', 'no vrrp %d delay reload' % upd_vrid),
            (None, 'no vrrp %d delay reload' % upd_vrid),
        ]

        for (delay_reload, cmd) in cases:
            func = function('update', upd_intf, upd_vrid,
                            delay_reload=delay_reload)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError by entering invalid parameters
        cases = ['a', 3601]

        for delay_reload in cases:
            func = function('update', upd_intf, upd_vrid,
                            delay_reload=delay_reload)
            self.eapi_exception_config_test(func, ValueError)

    # def test_update_authentication(self):
    #     # no vrrp 10 authentication
    #     cases = [
    #         # XXX fix test cases
    #     ]
    #
    #     for (authentication, cmd) in cases:
    #         func = function('update', upd_intf, upd_vrid,
    #                         authentication=authentication)
    #         exp_cmds = [upd_cmd] + [cmd]
    #         self.eapi_positive_config_test(func, exp_cmds)
    #
    #     # Test raising ValueError by entering invalid parameters
    #     cases = [
    #         # XXX fix test cases
    #     ]
    #
    #     for authentication in cases:
    #         func = function('update', upd_intf, upd_vrid,
    #                         authentication=authentication)
    #         self.eapi_exception_config_test(func, ValueError)

    def test_update_track(self):
        # vrrp 10 track Ethernet1 shutdown
        # Send various tracking commands in one go, then
        # send a command with no tracking specified and expect no commands
        cases = [
            (
                [{
                    'name': 'Ethernet2',
                    'track_action': 'shutdown',
                    'track_amount': 1
                 },
                 {
                    'name': 'Ethernet1',
                    'track_action': 'decrement',
                    'track_amount': 10
                 },
                 {
                    'name': 'Ethernet3',
                    'track_action': 'shutdown',
                    'track_amount': 'default'
                 },
                 {
                    'name': 'Ethernet2',
                    'track_action': 'decrement',
                    'track_amount': 'no'
                 },
                 {
                    'name': 'Ethernet1',
                    'track_action': 'shutdown',
                    'track_amount': None
                 }],
                ['vrrp %d track Ethernet2 shutdown' % upd_vrid,
                 'vrrp %d track Ethernet1 decrement 10' % upd_vrid,
                 'default vrrp %d track Ethernet3 shutdown' % upd_vrid,
                 'no vrrp %d track Ethernet2 decrement' % upd_vrid,
                 'no vrrp %d track Ethernet1 shutdown' % upd_vrid]
            ),
            ([], [])
        ]

        for (track, cmd) in cases:
            func = function('update', upd_intf, upd_vrid,
                            track=track)
            exp_cmds = [upd_cmd] + cmd
            self.eapi_positive_config_test(func, exp_cmds)

        # Test raising ValueError by entering invalid parameters
        cases = [
            [{
                'name': 'Ethernet1',
                'track_action': 'disable',
                'track_amount': 10
            }],
            [{
                'name': 'Ethernet1',
                'track_action': 'decrement',
                'track_amount': True
            }]
        ]

        for track in cases:
            func = function('update', upd_intf, upd_vrid,
                            track=track)
            self.eapi_exception_config_test(func, ValueError)

    def test_update_bfd_ip(self):
        # no vrrp 10 bfd ip
        bfd_addr = '10.10.4.101'
        cases = [
            (bfd_addr, 'vrrp %d bfd ip %s' % (upd_vrid, bfd_addr)),
            ('default', 'default vrrp %d bfd ip' % upd_vrid),
            ('no', 'no vrrp %d bfd ip' % upd_vrid),
            (None, 'no vrrp %d bfd ip' % upd_vrid),
        ]

        for (bfd_ip, cmd) in cases:
            func = function('update', upd_intf, upd_vrid,
                            bfd_ip=bfd_ip)
            exp_cmds = [upd_cmd] + [cmd]
            self.eapi_positive_config_test(func, exp_cmds)

    def test_update_invalid_vrid(self):
        # Test raising ValueError by updating a non-existent vrrp
        non_vrid = 1000
        params = {'priority': 100, 'enable': True}

        func = function('update', upd_intf, non_vrid, **params)
        self.eapi_exception_config_test(func, ValueError)

    def test_vrconf_format(self):
        # Test the function to format a vrrp configuration to
        # match the output from get/getall
        vrconf = {'priority': None,
                  'timers_advertise': None,
                  'mac_addr_adv_interval': None,
                  'preempt': 'default',
                  'preempt_delay_min': None,
                  'preempt_delay_reload': None,
                  'delay_reload': None,
                  'authentication': '',
                  'primary_ip': None,
                  'secondary_ip': {
                    'add': ['10.10.4.21'],
                    'remove': ['10.10.4.22']
                    },
                  'description': None,
                  'enable': True,
                  'track': [
                        {
                            'name': 'Ethernet1',
                            'track_action': 'shutdown',
                            'track_amount': None
                        },
                        {
                            'name': 'Ethernet1',
                            'track_action': 'decrement',
                            'track_amount': 10
                        },
                        {
                            'name': 'Ethernet2',
                            'track_action': 'shutdown',
                            'track_amount': 'on'
                        },
                  ],
                  'bfd_ip': None,
                  'ip_version': None}

        fixed = {'priority': 100,
                 'timers_advertise': 1,
                 'mac_addr_adv_interval': 30,
                 'preempt': False,
                 'preempt_delay_min': 0,
                 'preempt_delay_reload': 0,
                 'delay_reload': 0,
                 'authentication': '',
                 'primary_ip': '0.0.0.0',
                 'secondary_ip': {
                    'exists': ['10.10.4.21']
                 },
                 'description': None,
                 'enable': True,
                 'track': [
                    {
                        'name': 'Ethernet1',
                        'track_action': 'decrement',
                        'track_amount': 10
                    },
                    {
                        'name': 'Ethernet2',
                        'track_action': 'shutdown',
                        'track_amount': None
                    },
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
