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

from testlib import get_fixture, random_vlan, random_string, function
from testlib import EapiConfigUnitTest

import pyeapi.api.vlans


class TestApiVlans(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestApiVlans, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.vlans.instance(None)
        self.config = open(get_fixture('running_config.text')).read()

    def test_isvlan_with_string(self):
        self.assertFalse(pyeapi.api.vlans.isvlan('a' + random_string()))

    def test_isvlan_valid_value(self):
        self.assertTrue(pyeapi.api.vlans.isvlan('1234'))

    def test_isvlan_invalid_value(self):
        self.assertFalse(pyeapi.api.vlans.isvlan('5000'))

    def test_get(self):
        result = self.instance.get('1')
        vlan = dict(vlan_id='1', name='default', state='active',
                    trunk_groups=[])
        self.assertEqual(vlan, result)

        # ensure capturing grouppped vlans
        result = self.instance.get('200-.*')
        vlan = dict(vlan_id='200-202,204', name='grouping', state='active',
                    trunk_groups=[])
        self.assertEqual(vlan, result)

    def test_get_not_configured(self):
        self.assertIsNone(self.instance.get('1000'))

    def test_getall(self):
        result = self.instance.getall()
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 5)

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
                func = function('set_name', vid, disable=True)
            elif state == 'default':
                cmds = ['vlan %s' % vid, 'default name']
                func = function('set_name', vid, default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_state(self):
        for state in ['config', 'negate', 'default']:
            vid = random_vlan()
            if state == 'config':
                for value in ['active', 'suspend']:
                    cmds = ['vlan %s' % vid, 'state %s' % value]
                    func = function('set_state', vid, value)
                    self.eapi_positive_config_test(func, cmds)
            elif state == 'negate':
                cmds = ['vlan %s' % vid, 'no state']
                func = function('set_state', vid, disable=True)
                self.eapi_positive_config_test(func, cmds)
            elif state == 'default':
                cmds = ['vlan %s' % vid, 'default state']
                func = function('set_state', vid, default=True)
                self.eapi_positive_config_test(func, cmds)

    def test_set_trunk_groups_default(self):
        vid = random_vlan()
        cmds = ['vlan %s' % vid, 'default trunk group']
        func = function('set_trunk_groups', vid, default=True)
        self.eapi_positive_config_test(func, cmds)

    def test_set_trunk_groups_add_value(self):
        cmds = ['vlan 10', 'trunk group tg2']
        func = function('set_trunk_groups', '10', ['tg1', 'tg2'])
        self.eapi_positive_config_test(func, cmds)

    def test_set_trunk_groups_remove_value(self):
        cmds = ['vlan 10', 'no trunk group tg1']
        func = function('set_trunk_groups', '10', 'tg2')
        self.eapi_positive_config_test(func, cmds)

    def test_set_trunk_groups_remove_all(self):
        cmds = ['vlan 10', 'no trunk group']
        func = function('set_trunk_groups', '10', disable=True)
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
