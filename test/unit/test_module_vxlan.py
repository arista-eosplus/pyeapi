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

from mock import Mock

from testlib import get_fixture, random_vlan, function
from testlib import EapiConfigUnitTest

import pyeapi.modules.vxlan

class TestModuleVxlan(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestModuleVxlan, self).__init__(*args, **kwargs)
        self.instance = pyeapi.modules.vxlan

    def test_get(self):
        fixture = get_fixture('vxlan.json')
        self.eapi.enable.return_value = json.load(open(fixture))
        result = self.instance.get()
        self.eapi.enable.assert_called_with('show interfaces vxlan1')
        self.assertIsInstance(result, dict)

    def test_instance_functions(self):
        for name in ['create', 'delete', 'default']:
            if name == 'create':
                cmds = 'interface vxlan1'
            elif name == 'delete':
                cmds = 'no interface vxlan1'
            elif name == 'default':
                cmds = 'default interface vxlan1'
            self.eapi_positive_config_test(function(name), cmds)

    def test_set_source_interface(self):
        cmds = ['interface vxlan1', 'vxlan source-interface Loopback0']
        func = function('set_source_interface', 'Loopback0')
        self.eapi_positive_config_test(func, cmds)

    def test_set_source_interface_with_no_value(self):
        cmds = ['interface vxlan1', 'no vxlan source-interface']
        func = function('set_source_interface')
        self.eapi_positive_config_test(func, cmds)

    def test_set_source_interface_with_default(self):
        func = function('set_source_interface', default=True)
        cmds = ['interface vxlan1', 'default vxlan source-interface']
        self.eapi_positive_config_test(func, cmds)

    def test_multicast_group(self):
        cmds = ['interface vxlan1', 'vxlan multicast-group 239.1.1.1']
        func = function('set_multicast_group', '239.1.1.1')
        self.eapi_positive_config_test(func, cmds)

    def test_multicast_group_with_no_value(self):
        cmds = ['interface vxlan1', 'no vxlan multicast-group']
        func = function('set_multicast_group')
        self.eapi_positive_config_test(func, cmds)

    def test_multicast_group_with_default(self):
        cmds = ['interface vxlan1', 'default vxlan multicast-group']
        func = function('set_multicast_group', default=True)
        self.eapi_positive_config_test(func, cmds)

if __name__ == '__main__':
    unittest.main()


