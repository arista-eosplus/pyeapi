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

from testlib import get_fixture, function
from testlib import EapiConfigUnitTest

import pyeapi.resources.spanningtree

class TestResourceStp(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestResourceStp, self).__init__(*args, **kwargs)
        self.instances = pyeapi.resources.spanningtree.Stp(None)


class TestResourceStpInterfaces(EapiConfigUnitTest):

    INTERFACES = ['Ethernet1', 'Ethernet1/1', 'Port-Channel1']

    def __init__(self, *args, **kwargs):
        super(TestResourceStpInterfaces, self).__init__(*args, **kwargs)
        self.instance = pyeapi.resources.spanningtree.StpInterfaces(None)
        self.running_config = open(get_fixture('running_config.text')).read()

    def test_getall(self):
        result = self.instance.getall()
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 7)

    def test_set_portfast_with_value(self):
        for intf in self.INTERFACES:
            for value in ['edge', 'network', 'disable']:
                cmds = ['interface %s' % intf]
                if value is 'disable':
                    cmds.append('no spanning-tree portfast')
                else:
                    cmds.append('spanning-tree portfast %s' % value)
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
                cfgvalue = value == 'enable'
                cmds = ['interface %s' % intf,
                        'spanning-tree bpduguard %s' % value]
                func = function('set_bpduguard', intf, cfgvalue)
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


