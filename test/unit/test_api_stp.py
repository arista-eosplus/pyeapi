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

import pyeapi.api.stp

def get_running_config():
    return get_fixture('running_config.text')

class TestApiStp(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestApiStp, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.stp.Stp(None)
        self.config = open(get_running_config()).read()

    def test_instance(self):
        result = pyeapi.api.stp.instance(None)
        self.assertIsInstance(result, pyeapi.api.stp.Stp)

    def test_interfaces(self):
        result = self.instance.interfaces
        self.assertIsInstance(result, pyeapi.api.stp.StpInterfaces)

    def test_instances(self):
        result = self.instance.instances
        self.assertIsInstance(result, pyeapi.api.stp.StpInstances)

    def test_set_mode_with_value(self):
        for value in ['mstp', 'none']:
            cmds = 'spanning-tree mode %s' % value
            func = function('set_mode', value)
            self.eapi_positive_config_test(func, cmds)

    def test_set_mode_with_default(self):
        cmds = 'default spanning-tree mode'
        func = function('set_mode', default=True)
        self.eapi_positive_config_test(func, cmds)

    def test_set_mode_with_disable(self):
        cmds = 'no spanning-tree mode'
        func = function('set_mode', disable=True)
        self.eapi_positive_config_test(func, cmds)

    def test_set_mode_invalid_value_raises_value_error(self):
        value = random_string()
        func = function('set_mode', value)
        self.eapi_exception_config_test(func, ValueError)

class TestApiStpInterfaces(EapiConfigUnitTest):

    INTERFACES = ['Ethernet1', 'Ethernet1/1', 'Port-Channel1']

    def __init__(self, *args, **kwargs):
        super(TestApiStpInterfaces, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.stp.StpInterfaces(None)
        self.config = open(get_running_config()).read()

    def test_getall(self):
        result = self.instance.getall()
        self.assertIsInstance(result, dict)

    def test_set_portfast_type_with_value(self):
        for intf in self.INTERFACES:
            for value in ['edge', 'network', 'normal']:
                cmds = ['interface %s' % intf]
                cmds.append('spanning-tree portfast %s' % value)
                if value == 'edge':
                    cmds.append('spanning-tree portfast auto')
                func = function('set_portfast_type', intf, value)
                self.eapi_positive_config_test(func, cmds)

    def test_set_portfast_type_with_no_value(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'spanning-tree portfast normal']
            func = function('set_portfast_type', intf)
            self.eapi_positive_config_test(func, cmds)

    def test_set_portfast_type_invalid_value_raises_value_error(self):
        for intf in self.INTERFACES:
            value = random_string()
            func = function('set_portfast_type', intf, value)
            self.eapi_exception_config_test(func, ValueError)

    def test_set_portfast_type_invalid_intf_raises_value_error(self):
        intf = random_string()
        func = function('set_portfast_type', intf)
        self.eapi_exception_config_test(func, ValueError)

    def test_set_bpduguard_with_value(self):
        for intf in self.INTERFACES:
            for value in ['enable', 'disable']:
                cfgvalue = value == 'enable'
                cmds = ['interface %s' % intf,
                        'spanning-tree bpduguard %s' % value]
                func = function('set_bpduguard', intf, cfgvalue)
                self.eapi_positive_config_test(func, cmds)

    def test_set_bpduguard_with_no_value(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'spanning-tree bpduguard disable']
            func = function('set_bpduguard', intf)
            self.eapi_positive_config_test(func, cmds)

    def test_set_bpduguard_with_default(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'default spanning-tree bpduguard']
            func = function('set_bpduguard', intf, default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_bpduguard_with_disable(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'no spanning-tree bpduguard']
            func = function('set_bpduguard', intf, disable=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_bpduguard_invalid_intf_raises_value_error(self):
        intf = random_string()
        func = function('set_bpduguard', intf)
        self.eapi_exception_config_test(func, ValueError)

    def test_set_portfast_with_value(self):
        for intf in self.INTERFACES:
            for value in [True, False]:
                cmds = ['interface %s' % intf]
                if value:
                    cmds.append('spanning-tree portfast')
                else:
                    cmds.append('no spanning-tree portfast')
                func = function('set_portfast', intf, value)
                self.eapi_positive_config_test(func, cmds)

    def test_set_portfast_with_no_value(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'no spanning-tree portfast']
            func = function('set_portfast', intf, disable=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_portfast_with_default(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'default spanning-tree portfast']
            func = function('set_portfast', intf, default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_portfast_invalid_intf_raises_value_error(self):
        intf = random_string()
        func = function('set_portfast', intf)
        self.eapi_exception_config_test(func, ValueError)


if __name__ == '__main__':
    unittest.main()
