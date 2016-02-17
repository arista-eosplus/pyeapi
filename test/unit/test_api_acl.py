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

import pyeapi.api.acl

class TestApiAclFunctions(unittest.TestCase):

    def test_mask_to_prefixlen(self):
        result = pyeapi.api.acl.mask_to_prefixlen('255.255.255.0')
        self.assertEqual(result, 24)

    def test_prefixlen_to_mask(self):
        result = pyeapi.api.acl.prefixlen_to_mask(24)
        self.assertEqual(result, '255.255.255.0')

class TestApiStandardAcls(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestApiStandardAcls, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.acl.StandardAcls(None)
        self.config = open(get_fixture('running_config.text')).read()

    def test_instance(self):
        result = pyeapi.api.acl.instance(None)
        self.assertIsInstance(result, pyeapi.api.acl.StandardAcls)

    def test_get(self):
        result = self.instance.get('test')
        keys = ['name', 'type', 'entries']
        self.assertEqual(sorted(keys), sorted(result.keys()))

    def test_get_not_configured(self):
        self.assertIsNone(self.instance.get('unconfigured'))

    def test_getall(self):
        result = self.instance.getall()
        self.assertIsInstance(result, dict)

    def test_acl_functions(self):
        for name in ['create', 'delete', 'default']:
            if name == 'create':
                cmds = 'ip access-list standard test'
            elif name == 'delete':
                cmds = 'no ip access-list standard test'
            elif name == 'default':
                cmds = 'default ip access-list standard test'
            func = function(name, 'test')
            self.eapi_positive_config_test(func, cmds)

    def test_update_entry(self):
        cmds = ['ip access-list standard test', 'no 10',
                '10 permit 0.0.0.0/32 log', 'exit']
        func = function('update_entry', 'test', '10', 'permit', '0.0.0.0',
                        '32', True)
        self.eapi_positive_config_test(func, cmds)

    def test_remove_entry(self):
        cmds = ['ip access-list standard test', 'no 10', 'exit']
        func = function('remove_entry', 'test', '10')
        self.eapi_positive_config_test(func, cmds)

    def test_add_entry(self):
        cmds = ['ip access-list standard test', 'permit 0.0.0.0/32 log', 'exit']
        func = function('add_entry', 'test', 'permit', '0.0.0.0',
                        '32', True)
        self.eapi_positive_config_test(func, cmds)

    def test_add_entry_with_seqno(self):
        cmds = ['ip access-list standard test', '30 permit 0.0.0.0/32 log', 'exit']
        func = function('add_entry', 'test', 'permit', '0.0.0.0',
                        '32', True, 30)
        self.eapi_positive_config_test(func, cmds)


if __name__ == '__main__':
    unittest.main()
