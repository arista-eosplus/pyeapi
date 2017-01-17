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

from testlib import get_fixture, function
from testlib import EapiConfigUnitTest

import pyeapi.api.varp


class TestApiVarp(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestApiVarp, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.varp.Varp(None)
        self.config = open(get_fixture('running_config.varp')).read()

    def test_instance(self):
        result = pyeapi.api.varp.instance(None)
        self.assertIsInstance(result, pyeapi.api.varp.Varp)

    def test_get(self):
        result = self.instance.get()
        keys = ['mac_address', 'interfaces']
        self.assertEqual(sorted(keys), sorted(result.keys()))
        self.assertIsNotNone(self.instance.get()['mac_address'])
        self.assertIsNotNone(self.instance.get()['interfaces'])

    def test_get_interfaces_none(self):
        self._interfaces = None
        result = self.instance.interfaces()
        self.assertIsNotNone(result)

    def test_get_interfaces_already_defined(self):
        self.instance.interfaces()
        result = self.instance.interfaces()
        self.assertIsNotNone(result)

    def test_set_mac_address_with_value(self):
        value = 'aa:bb:cc:dd:ee:ff'
        func = function('set_mac_address', mac_address=value)
        cmds = 'ip virtual-router mac-address %s' % value
        self.eapi_positive_config_test(func, cmds)

    def test_set_mac_address_with_positional_value(self):
        value = 'aa:bb:cc:dd:ee:ff'
        func = function('set_mac_address', value)
        cmds = 'ip virtual-router mac-address %s' % value
        self.eapi_positive_config_test(func, cmds)

    def test_set_mac_address_with_disable(self):
        func = function('set_mac_address', disable=True)
        cmds = 'no ip virtual-router mac-address 00:11:22:33:44:55'
        self.eapi_positive_config_test(func, cmds)

    def test_set_mac_address_with_no_value(self):
        with self.assertRaises(ValueError):
            self.instance.set_mac_address(mac_address=None)

    def test_set_mac_address_with_bad_value(self):
        with self.assertRaises(ValueError):
            self.instance.set_mac_address(mac_address='0011.2233.4455')

    def test_set_mac_address_with_default(self):
        func = function('set_mac_address', default=True)
        cmds = 'default ip virtual-router mac-address 00:11:22:33:44:55'
        self.eapi_positive_config_test(func, cmds)


class TestApiVarpInterfaces(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestApiVarpInterfaces, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.varp.VarpInterfaces(None)
        self.config = open(get_fixture('running_config.varp')).read()

    def test_get_with_no_interface(self):
        self.config = ""
        self.setUp()
        result = self.instance.get('Vlan1000')
        self.assertIsNone(result)

    def test_add_address_with_value(self):
        func = function('set_addresses', 'Vlan4001', addresses=['1.1.1.4'])
        cmds = ['interface Vlan4001', 'no ip virtual-router address 1.1.1.2',
                'ip virtual-router address 1.1.1.4']
        self.eapi_positive_config_test(func, cmds)

    def test_add_address_when_interface_does_not_exist(self):
        self.config = ""
        self.setUp()
        func = function('set_addresses', 'Vlan10', addresses=['1.1.1.4'])
        cmds = ['interface Vlan10', 'ip virtual-router address 1.1.1.4']
        self.eapi_positive_config_test(func, cmds)

    def test_add_address_with_no_value(self):
        func = function('set_addresses', 'Vlan4002')
        cmds = ['interface Vlan4002', 'no ip virtual-router address']
        self.eapi_positive_config_test(func, cmds)

    def test_add_address_with_empty_list(self):
        func = function('set_addresses', 'Vlan4001', addresses=[])
        cmds = ['interface Vlan4001', 'no ip virtual-router address 1.1.1.2']
        self.eapi_positive_config_test(func, cmds)

    def test_add_address_with_default(self):
        func = function('set_addresses', 'Vlan4001', default=True)
        cmds = ['interface Vlan4001', 'default ip virtual-router address']
        self.eapi_positive_config_test(func, cmds)

    def test_add_address_with_disable(self):
        func = function('set_addresses', 'Vlan4001', disable=True)
        cmds = ['interface Vlan4001', 'no ip virtual-router address']
        self.eapi_positive_config_test(func, cmds)


if __name__ == '__main__':
    unittest.main()
