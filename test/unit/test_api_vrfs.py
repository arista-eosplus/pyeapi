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
import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))

from testlib import get_fixture, random_string, function
from testlib import EapiConfigUnitTest

import pyeapi.api.vrfs


class TestApiVrfs(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestApiVrfs, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.vrfs.instance(None)
        self.config = open(get_fixture('running_config.vrf')).read()

    def test_isrd_valid_value_number_number(self):
        self.assertTrue(pyeapi.api.vrfs.isrd('10:10'))

    def test_isrd_valid_value_ipaddress_number(self):
        self.assertTrue(pyeapi.api.vrfs.isrd('10.10.10.10:99'))

    def test_isrd_valid_value_number_ipaddress(self):
        self.assertTrue(pyeapi.api.vrfs.isrd('99:10.10.10.10'))

    def test_isrd_invalid_with_string(self):
        self.assertFalse(pyeapi.api.vrfs.isrd('a' + random_string()))

    def test_isrd_invalid_value_number_one_out_of_range(self):
        self.assertFalse(pyeapi.api.vrfs.isrd('70000:100'))

    def test_isrd_invalid_value_number_two_out_of_range(self):
        self.assertFalse(pyeapi.api.vrfs.isrd('5000:5000000000'))

    def test_isrd_invalid_first_ipaddress(self):
        self.assertFalse(pyeapi.api.vrfs.isrd('255.255.255.300:10'))

    def test_isrd_invalid_second_ipaddress(self):
        self.assertFalse(pyeapi.api.vrfs.isrd('10:355.255.255.0'))

    def test_isrd_invalid_ipaddress_number_two_out_of_range(self):
        self.assertFalse(pyeapi.api.vrfs.isrd('10.10.10.1:70000'))

    def test_isrd_invalid_ipaddress_ipaddress(self):
        self.assertFalse(pyeapi.api.vrfs.isrd('10.10.10.1:192.168.1.1'))

    def test_get(self):
        result = self.instance.get('blah')
        vrf = dict(rd='10:10', vrf_name='blah', description='blah desc',
                   ipv4routing=True, ipv6routing=False)
        self.assertEqual(vrf, result)

    def test_get_not_configured(self):
        self.assertIsNone(self.instance.get('notthere'))

    def test_getall(self):
        result = self.instance.getall()
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 2)

    def test_vrf_functions(self):
        for name in ['create', 'delete', 'default']:
            vrf_name = 'testvrf'
            if name == 'create':
                cmds = 'vrf definition %s' % vrf_name
            elif name == 'delete':
                cmds = 'no vrf definition %s' % vrf_name
            elif name == 'default':
                cmds = 'default vrf definition %s' % vrf_name
            func = function(name, vrf_name)
            self.eapi_positive_config_test(func, cmds)

    def test_set_rd(self):
        vrf_name = 'testrdvrf'
        rd = '10:10'
        cmds = ['vrf definition %s' % vrf_name, 'rd %s' % rd]
        func = function('set_rd', vrf_name, rd)
        self.eapi_positive_config_test(func, cmds)

    def test_set_description(self):
        for state in ['config', 'negate', 'default']:
            vrf_name = 'testdescvrf'
            if state == 'config':
                description = 'testing'
                cmds = ['vrf definition %s' % vrf_name,
                        'description %s' % description]
                func = function('set_description', vrf_name, description)
                self.eapi_positive_config_test(func, cmds)
            elif state == 'negate':
                cmds = ['vrf definition %s' % vrf_name, 'no description']
                func = function('set_description', vrf_name, disable=True)
                self.eapi_positive_config_test(func, cmds)
            elif state == 'default':
                cmds = ['vrf definition %s' % vrf_name, 'default description']
                func = function('set_description', vrf_name, default=True)
                self.eapi_positive_config_test(func, cmds)

    def test_set_ipv4_routing(self):
        for state in ['config', 'negate', 'default']:
            vrf_name = 'testipv4vrf'
            if state == 'config':
                cmds = ['ip routing vrf %s' % vrf_name]
                func = function('set_ipv4_routing', vrf_name)
                self.eapi_positive_config_test(func, cmds)
            elif state == 'negate':
                cmds = ['no ip routing vrf %s' % vrf_name]
                func = function('set_ipv4_routing', vrf_name, disable=True)
                self.eapi_positive_config_test(func, cmds)
            elif state == 'default':
                cmds = ['default ip routing vrf %s' % vrf_name]
                func = function('set_ipv4_routing', vrf_name, default=True)
                self.eapi_positive_config_test(func, cmds)

    def test_set_ipv6_routing(self):
        for state in ['config', 'negate', 'default']:
            vrf_name = 'testipv6vrf'
            if state == 'config':
                cmds = ['ipv6 unicast-routing vrf %s' % vrf_name]
                func = function('set_ipv6_routing', vrf_name)
                self.eapi_positive_config_test(func, cmds)
            elif state == 'negate':
                cmds = ['no ipv6 unicast-routing vrf %s' % vrf_name]
                func = function('set_ipv6_routing', vrf_name, disable=True)
                self.eapi_positive_config_test(func, cmds)
            elif state == 'default':
                cmds = ['default ipv6 unicast-routing vrf %s' % vrf_name]
                func = function('set_ipv6_routing', vrf_name, default=True)
                self.eapi_positive_config_test(func, cmds)

    def test_set_interface(self):
        for state in ['config', 'negate', 'default']:
            vrf_name = 'testintvrf'
            interface = 'Ethernet1'
            if state == 'config':
                cmds = ['interface %s' % interface,
                        'vrf forwarding %s' % vrf_name]
                func = function('set_interface', vrf_name, interface)
                self.eapi_positive_config_test(func, cmds)
            elif state == 'negate':
                cmds = ['interface %s' % interface, 'no vrf forwarding']
                func = function('set_interface', vrf_name, interface,
                                disable=True)
                self.eapi_positive_config_test(func, cmds)
            elif state == 'default':
                cmds = ['interface %s' % interface, 'default vrf forwarding']
                func = function('set_interface', vrf_name, interface,
                                default=True)
                self.eapi_positive_config_test(func, cmds)


if __name__ == '__main__':
    unittest.main()