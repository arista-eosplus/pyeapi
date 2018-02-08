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

from testlib import get_fixture, function, random_string
from testlib import EapiConfigUnitTest

import pyeapi.api.routemaps


class TestApiRoutemaps(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestApiRoutemaps, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.routemaps.Routemaps(None)
        self.config = open(get_fixture('running_config.routemaps')).read()

    def test_instance(self):
        result = pyeapi.api.routemaps.instance(None)
        self.assertIsInstance(result, pyeapi.api.routemaps.Routemaps)

    def test_get(self):
        result = self.instance.get('TEST')
        keys = ['deny', 'permit']
        self.assertEqual(sorted(keys), sorted(result.keys()))

    def test_get_not_configured(self):
        self.assertIsNone(self.instance.get('blah'))

    def test_getall(self):
        # Review fixtures/running_config.routemaps to see the default
        # running-config that is the basis for this test
        result = self.instance.getall()
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result.keys()), 4)

    def test_routemaps_functions(self):
        for name in ['create', 'delete', 'default']:
            if name == 'create':
                cmds = 'route-map new permit 100'
            elif name == 'delete':
                cmds = 'no route-map new permit 100'
            elif name == 'default':
                cmds = 'default route-map new permit 100'
            func = function(name, 'new', 'permit', 100)
            self.eapi_positive_config_test(func, cmds)

    def test_set_set_statement_clean(self):
        cmds = ['route-map new permit 100', 'set weight 100']
        func = function('set_set_statements', 'new', 'permit', 100,
                        ['weight 100'])
        self.eapi_positive_config_test(func, cmds)

    def test_set_set_statement_remove_extraneous(self):
        # Review fixtures/running_config.routemaps to see the default
        # running-config that is the basis for this test
        cmds = ['route-map TEST permit 10', 'no set tag 50',
                'route-map TEST permit 10', 'set weight 100']
        func = function('set_set_statements', 'TEST', 'permit', 10,
                        ['weight 100'])
        self.eapi_positive_config_test(func, cmds)

    def test_set_match_statement_clean(self):
        cmds = ['route-map new permit 200', 'match as 100']
        func = function('set_match_statements', 'new', 'permit', 200,
                        ['as 100'])
        self.eapi_positive_config_test(func, cmds)

    def test_set_match_statement_remove_extraneous(self):
        # Review fixtures/running_config.routemaps to see the default
        # running-config that is the basis for this test
        cmds = ['route-map TEST permit 10', 'no match interface Ethernet1',
                'route-map TEST permit 10', 'match as 1000']
        func = function('set_match_statements', 'TEST', 'permit', 10,
                        ['as 1000'])
        self.eapi_positive_config_test(func, cmds)

    def test_set_continue(self):
        cmds = ['route-map TEST permit 10', 'continue 100']
        func = function('set_continue', 'TEST', 'permit', 10, 100)
        self.eapi_positive_config_test(func, cmds)

    def test_set_continue_with_invalid_integer(self):
        with self.assertRaises(ValueError):
            self.instance.set_continue('TEST', 'permit', 10, -1)

    def test_set_continue_with_invalid_string(self):
        with self.assertRaises(ValueError):
            self.instance.set_continue('TEST', 'permit', 10, 'invalid')

    def test_set_continue_to_default(self):
        cmds = ['route-map TEST permit 10', 'default continue']
        func = function('set_continue', 'TEST', 'permit', 10, default=True)
        self.eapi_positive_config_test(func, cmds)

    def test_negate_continue(self):
        cmds = ['route-map TEST permit 10', 'no continue']
        func = function('set_continue', 'TEST', 'permit', 10, disable=True)
        self.eapi_positive_config_test(func, cmds)

    def test_set_description_with_value(self):
        value = random_string()
        cmds = ['route-map TEST permit 10', 'no description',
                'description %s' % value]
        func = function('set_description', 'TEST', 'permit', 10, value)
        self.eapi_positive_config_test(func, cmds)

    def test_negate_description(self):
        cmds = ['route-map TEST permit 10', 'no description']
        func = function('set_description', 'TEST', 'permit', 10, disable=True)
        self.eapi_positive_config_test(func, cmds)

    def test_set_description_with_default(self):
        cmds = ['route-map TEST permit 10', 'default description']
        func = function('set_description', 'TEST', 'permit', 10, default=True)
        self.eapi_positive_config_test(func, cmds)

    def test_set_description_with_invalid_value(self):
        # with self.assertRaises(ValueError):
        #     self.instance.set_description('TEST', 'permit', 10, value=None)
        # If command_builder fails because value is None, uncomment
        # above lines and remove below lines.
        cmds = ['route-map TEST permit 10', 'no description']
        func = function('set_description', 'TEST', 'permit', 10, value=None)
        self.eapi_positive_config_test(func, cmds)


if __name__ == '__main__':
    unittest.main()
