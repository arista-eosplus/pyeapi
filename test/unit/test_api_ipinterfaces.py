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


from testlib import get_fixture, function, random_int, random_string
from testlib import EapiConfigUnitTest

import pyeapi.api.ipinterfaces


class TestApiIpinterfaces(EapiConfigUnitTest):

    INTERFACES = ['Ethernet1', 'Ethernet1/1', 'Vlan1234', 'Management1',
                  'Port-Channel1']

    def __init__(self, *args, **kwargs):
        super(TestApiIpinterfaces, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.ipinterfaces.instance(None)
        self.config = open(get_fixture('running_config.text')).read()

    def test_get(self):
        result = self.instance.get('Loopback0')
        values = dict(name='Loopback0', address='1.1.1.1/32', mtu=1500)
        self.assertEqual(result, values)

    def test_getall(self):
        result = self.instance.getall()
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 3)

    def test_instance_functions(self):
        for intf in self.INTERFACES:
            for name in ['create', 'delete']:
                if name == 'create':
                    cmds = ['interface %s' % intf, 'no switchport']
                elif name == 'delete':
                    cmds = ['interface %s' % intf, 'no ip address',
                            'switchport']
                func = function(name, intf)
                self.eapi_positive_config_test(func, cmds)

    def test_set_address_with_value(self):
        for intf in self.INTERFACES:
            value = '1.2.3.4/5'
            cmds = ['interface %s' % intf, 'ip address 1.2.3.4/5']
            func = function('set_address', intf, value)
            self.eapi_positive_config_test(func, cmds)

    def test_set_address_with_no_value(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'no ip address']
            func = function('set_address', intf, disable=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_address_with_default(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'default ip address']
            func = function('set_address', intf, default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_address_invalid_value_raises_value_error(self):
        for intf in self.INTERFACES:
            # func = function('set_address', intf, None)
            # self.eapi_exception_config_test(func, ValueError)
            # If command_builder fails because value is None, uncomment
            # above lines and remove below lines.
            cmds = ['interface %s' % intf, 'no ip address']
            func = function('set_address', intf, value=None)
            self.eapi_positive_config_test(func, cmds)

    def test_set_mtu_with_values(self):
        for intf in self.INTERFACES:
            for value in [68, 65535, random_int(68, 65535)]:
                cmds = ['interface %s' % intf, 'mtu %s' % value]
                func = function('set_mtu', intf, value)
                self.eapi_positive_config_test(func, cmds)

    def test_set_mtu_with_no_value(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'no mtu']
            func = function('set_mtu', intf, disable=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_mtu_default(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'default mtu']
            func = function('set_mtu', intf, default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_mtu_invalid_value_raises_value_error(self):
        for intf in self.INTERFACES:
            for value in [67, 65536, 'a' + random_string()]:
                func = function('set_mtu', intf, value)
                self.eapi_exception_config_test(func, ValueError)
            for value in [None]:
                # If command_builder fails because value is None, put None
                # in the first loop to check for value error, and remove
                # this second loop
                cmds = ['interface %s' % intf, 'no mtu']
                func = function('set_mtu', intf, value)
                self.eapi_positive_config_test(func, cmds)


if __name__ == '__main__':
    unittest.main()
