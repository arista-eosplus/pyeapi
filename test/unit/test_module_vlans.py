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

from testlib import get_fixture, random_vlan, random_string, function
from testlib import EapiConfigUnitTest

import pyeapi.modules.vlans

class TestModuleVlans(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestModuleVlans, self).__init__(*args, **kwargs)
        self.instance = pyeapi.modules.vlans.instance(None)

    def test_getall(self):
        fixture = get_fixture('vlans_getall.json')
        self.eapi.enable.return_value = json.load(open(fixture))
        result = self.instance.getall()

        calls = call.enable(['show vlan', 'show vlan trunk group'])
        self.eapi.assert_has_calls(calls)

        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 4)

    def test_vlan_functions(self):
        for name in ['create', 'delete', 'default']:
            vid = random_vlan()
            if name == 'create':
                cmds = 'vlan %s' % vid
            elif name == 'delete':
                cmds = 'no vlan %s' % vid
            elif name == 'default':
                cmds = 'default vlan %s' % vid
            func = function(name, vid)
            self.eapi_positive_config_test(func, cmds)

    def test_set_name(self):
        for state in ['config', 'negate', 'default']:
            vid = random_vlan()
            name = random_string()
            if state == 'config':
                cmds = ['vlan %s' % vid, 'name %s' % name]
                func = function('set_name', vid, name)
            elif state == 'negate':
                cmds = ['vlan %s' % vid, 'no name']
                func = function('set_name', vid)
            elif state == 'default':
                cmds = ['vlan %s' % vid, 'default name']
                func = function('set_name', vid, default=True)
            self.eapi_positive_config_test(func, cmds)


    def test_set_state(self):
        for state in ['config', 'negate', 'default']:
            vid = random_vlan()
            name = random_string()
            if state == 'config':
                for value in ['active', 'suspend']:
                    cmds = ['vlan %s' % vid, 'state %s' % value]
                    func = function('set_state', vid, value)
                    self.eapi_positive_config_test(func, cmds)
            elif state == 'negate':
                cmds = ['vlan %s' % vid, 'no state']
                func = function('set_state', vid)
                self.eapi_positive_config_test(func, cmds)
            elif state == 'default':
                cmds = ['vlan %s' % vid, 'default state']
                func = function('set_state', vid, default=True)
                self.eapi_positive_config_test(func, cmds)

    def test_add_trunk_group(self):
        vid = random_vlan()
        tg = random_string()
        cmds = ['vlan %s' % vid, 'trunk group %s' % tg]
        func = function('add_trunk_group', vid, tg)
        self.eapi_positive_config_test(func, cmds)

    def test_remove_trunk_group(self):
        vid = random_vlan()
        tg = random_string()
        cmds = ['vlan %s' % vid, 'no trunk group %s' % tg]
        func = function('remove_trunk_group', vid, tg)
        self.eapi_positive_config_test(func, cmds)

if __name__ == '__main__':
    unittest.main()


