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
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))

from mock import Mock, call

from testlib import get_fixture, function, random_int
from testlib import EapiConfigUnitTest

import pyeapi.modules.spanningtree

class TestModuleStp(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestModuleStp, self).__init__(*args, **kwargs)
        self.instances = pyeapi.modules.spanningtree.Stp(None)



class TestModuleStpInterfaces(EapiConfigUnitTest):

    INTERFACES = ['Ethernet1', 'Ethernet1/1', 'Port-Channel1']

    def __init__(self, *args, **kwargs):
        super(TestModuleStpInterfaces, self).__init__(*args, **kwargs)
        self.instance = pyeapi.modules.spanningtree.StpInterfaces(None)

    def test_getall(self):

        def enable(*args):
            if args == ('show interfaces',):
                fixture = get_fixture('stp_interfaces_getall.json')
            elif args == ('show running-config section Ethernet2', 'text'):
                fixture = get_fixture('stp_interfaces_et2.json')
            return json.load(open(fixture))

        self.eapi.enable.side_effect = enable

        result = self.instance.getall()

        calls = [call.enable('show interfaces'),
                 call.enable('show running-config section Ethernet2', 'text')]
        self.eapi.assert_has_calls(calls)

        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 1)

    def test_set_portfast_with_value(self):
        for intf in self.INTERFACES:
            for value in ['edge', 'network', 'disable']:
                cmds = ['interface %s' % intf]
                if value is 'disable':
                    cmds.append('no spanning-tree portfast')
                else:
                    cmds.append('spanning-tree portfast')
                func = function('set_portfast', intf, value)
                self.eapi_positive_config_test(func, cmds)

    def test_set_portfast_with_no_value(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'no spanning-tree portfast']
            func = function('set_portfast', intf)
            self.eapi_positive_config_test(func, cmds)

    def test_set_portfast_with_default(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'default spanning-tree portfast']
            func = function('set_portfast', intf, default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_bpduguard_with_value(self):
        for intf in self.INTERFACES:
            for value in ['enable', 'disable']:
                cmds = ['interface %s' % intf,
                        'spanning-tree bpduguard %s' % value]
                func = function('set_bpduguard', intf, value)
                self.eapi_positive_config_test(func, cmds)

    def test_set_bpduguard_with_no_value(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'no spanning-tree bpduguard']
            func = function('set_bpduguard', intf)
            self.eapi_positive_config_test(func, cmds)

    def tset_set_bpduguard_with_default(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'no spanning-tree bpduguard']
            func = function('set_bpduguard', default=True)
            self.eapi_positive_config_test(func, cmds)


if __name__ == '__main__':
    unittest.main()


