#
# Copyright (c) 2016, Arista Networks, Inc.
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

from testlib import get_fixture, random_string, random_int, function
from testlib import EapiConfigUnitTest

import pyeapi.api.vrf

ALPHA = dict(name='alpha', description='vrf definition for alpha',
             admin='1', local='10')

BETA = dict(name='beta', description='the beta description',
            admin=None, local=None)

DELTA = dict(name='delta', description=None,
             admin=None, local=None)

GAMMA = dict(name='gamma', description='hello there everyone',
             admin='1000', local='5.2.2.2')

VRFS = (ALPHA, BETA, DELTA, GAMMA)

class TestApiVrf(EapiConfigUnitTest):
    '''Test class for VRF'''
    def __init__(self, *args, **kwargs):
        super(TestApiVrf, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.vrf.instance(None)
        self.config = open(get_fixture('running_config.text')).read()

    def test_get(self):
        result = self.instance.get(ALPHA['name'])
        self.assertDictEqual(ALPHA, result)

    def test_get_not_configured(self):
        self.assertIsNone(self.instance.get('missingvrf'))

    def test_getall(self):
        result = self.instance.getall()
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 4)
        for vrf in VRFS:
            self.assertDictEqual(vrf, result[vrf['name']])

    def test_vlan_functions(self):
        for fn in ['create', 'delete']:
            name = random_string()
            if fn == 'create':
                cmds = 'vrf definition %s' % name
            elif fn == 'delete':
                cmds = 'no vrf definition %s' % name
            func = function(fn, name)
            self.eapi_positive_config_test(func, cmds)

    def test_set_description(self):
        for state in ['config', 'default']:
            name = random_string(3, 30)
            desc = random_string(20, 80)
            if state == 'config':
                cmds = ['vrf definition %s' % name, 'description %s' % desc]
                func = function('set_description', name, desc)
            elif state == 'default':
                cmds = ['vrf definition %s' % name, 'default description']
                func = function('set_description', name, default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_rd(self):
        name = random_string(3, 30)
        admin = random_int(0, 65535)
        local = random_int(0, 65535)
        rd = '%s:%s' % (admin, local)

        cmds = ['vrf definition %s' % name, 'rd %s' % rd]
        func = function('set_rd', name, admin, local)

        self.eapi_positive_config_test(func, cmds)

if __name__ == '__main__':
    unittest.main()
