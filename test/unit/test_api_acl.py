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


class TestApiAcls(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestApiAcls, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.acl.Acls(None)
        self.config = open(get_fixture('running_config.text')).read()

    def test_instance(self):
        result = pyeapi.api.acl.instance(None)
        self.assertIsInstance(result, pyeapi.api.acl.Acls)

    def test_getall(self):
        result = self.instance.getall()
        self.assertIsInstance(result, dict)
        self.assertIn('exttest', result['extended'])
        self.assertIn('test', result['standard'])

    def test_get_not_configured(self):
        self.assertIsNone(self.instance.get('unconfigured'))

    def test_get(self):
        result = self.instance.get('test')
        keys = ['name', 'type', 'entries']
        self.assertEqual(sorted(keys), sorted(result.keys()))

    def test_get_instance(self):
        result = self.instance.get_instance('test')
        self.assertIsInstance(result, pyeapi.api.acl.StandardAcls)
        self.instance._instances['test'] = result
        result = self.instance.get_instance('exttest')
        self.assertIsInstance(result, pyeapi.api.acl.ExtendedAcls)
        result = self.instance.get_instance('unconfigured')
        self.assertIsInstance(result, dict)
        self.assertIsNone(result['unconfigured'])
        result = self.instance.get_instance('test')
        self.assertIsInstance(result, pyeapi.api.acl.StandardAcls)
        self.assertEqual(len(self.instance._instances), 2)

    def test_create_instance_standard(self):
        result = self.instance.create_instance('test', 'standard')
        self.assertIsInstance(result, pyeapi.api.acl.StandardAcls)
        self.assertEqual(len(self.instance._instances), 1)

    def test_create_instance_extended(self):
        result = self.instance.create_instance('exttest', 'extended')
        self.assertIsInstance(result, pyeapi.api.acl.ExtendedAcls)
        self.assertEqual(len(self.instance._instances), 1)

    def test_create_standard(self):
        cmds = 'ip access-list standard test'
        func = function('create', 'test')
        self.eapi_positive_config_test(func, cmds)

    def test_create_extended(self):
        cmds = 'ip access-list exttest'
        func = function('create', 'exttest', 'extended')
        self.eapi_positive_config_test(func, cmds)

    def test_create_unknown_type_creates_standard(self):
        cmds = 'ip access-list standard test'
        func = function('create', 'test', 'unknown')
        self.eapi_positive_config_test(func, cmds)

    def test_proxy_method_success(self):
        result = self.instance.remove_entry('test', '10')
        self.assertTrue(result)

    def test_proxy_method_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.instance.nonmethod('test', '10')


class TestApiStandardAcls(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestApiStandardAcls, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.acl.StandardAcls(None)
        self.config = open(get_fixture('running_config.text')).read()

    def test_get(self):
        result = self.instance.get('test')
        keys = ['name', 'type', 'entries']
        self.assertEqual(sorted(keys), sorted(result.keys()))
        self.assertEqual(result['type'], 'standard')

    def test_get_not_configured(self):
        self.assertIsNone(self.instance.get('unconfigured'))

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

    def test_update_entry_no_log(self):
        cmds = ['ip access-list standard test', 'no 10',
                '10 permit 0.0.0.0/32', 'exit']
        func = function('update_entry', 'test', '10', 'permit', '0.0.0.0',
                        '32')
        self.eapi_positive_config_test(func, cmds)

    def test_remove_entry(self):
        cmds = ['ip access-list standard test', 'no 10', 'exit']
        func = function('remove_entry', 'test', '10')
        self.eapi_positive_config_test(func, cmds)

    def test_add_entry(self):
        cmds = ['ip access-list standard test', 'permit 0.0.0.0/32 log',
                'exit']
        func = function('add_entry', 'test', 'permit', '0.0.0.0',
                        '32', True)
        self.eapi_positive_config_test(func, cmds)

    def test_add_entry_no_log(self):
        cmds = ['ip access-list standard test', 'permit 0.0.0.0/32',
                'exit']
        func = function('add_entry', 'test', 'permit', '0.0.0.0',
                        '32')
        self.eapi_positive_config_test(func, cmds)

    def test_add_entry_with_seqno(self):
        cmds = ['ip access-list standard test', '30 permit 0.0.0.0/32 log',
                'exit']
        func = function('add_entry', 'test', 'permit', '0.0.0.0',
                        '32', True, 30)
        self.eapi_positive_config_test(func, cmds)


class TestApiExtendedAcls(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestApiExtendedAcls, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.acl.ExtendedAcls(None)
        self.config = open(get_fixture('running_config.text')).read()

    def test_get(self):
        result = self.instance.get('exttest')
        keys = ['name', 'type', 'entries']
        self.assertEqual(sorted(keys), sorted(result.keys()))
        self.assertEqual(result['type'], 'extended')
        self.assertIn('entries', result)
        self.assertIn('50', result['entries'])
        entry = dict(action='permit', dstaddr='1.1.1.2', dstlen=None,
                     dstport=None, other=None, protocol='ip', srcaddr='any',
                     srclen=None, srcport=None)
        self.assertEqual(entry, result['entries']['50'])
        self.assertIn('70', result['entries'])
        entry = dict(action='permit', dstaddr='3.3.3.3', dstlen=None,
                     dstport='lt ipp', protocol='tcp', srcaddr='8.8.8.0',
                     other='urg ttl eq 24 fragments tracked log',
                     srclen='24', srcport='neq irc')
        self.assertEqual(entry, result['entries']['70'])

    def test_get_not_configured(self):
        self.assertIsNone(self.instance.get('unconfigured'))

    def test_acl_functions(self):
        for name in ['create', 'delete', 'default']:
            if name == 'create':
                cmds = 'ip access-list exttest'
            elif name == 'delete':
                cmds = 'no ip access-list exttest'
            elif name == 'default':
                cmds = 'default ip access-list exttest'
            func = function(name, 'exttest')
            self.eapi_positive_config_test(func, cmds)

    def test_update_entry(self):
        cmds = ['ip access-list exttest', 'no 10',
                '10 permit ip 0.0.0.0/32 1.1.1.1/32 log', 'exit']
        func = function('update_entry', 'exttest', '10', 'permit', 'ip',
                        '0.0.0.0', '32', '1.1.1.1', '32', True)
        self.eapi_positive_config_test(func, cmds)

    def test_update_entry_no_log(self):
        cmds = ['ip access-list exttest', 'no 10',
                '10 permit ip 0.0.0.0/32 1.1.1.1/32', 'exit']
        func = function('update_entry', 'exttest', '10', 'permit', 'ip',
                        '0.0.0.0', '32', '1.1.1.1', '32')
        self.eapi_positive_config_test(func, cmds)

    def test_remove_entry(self):
        cmds = ['ip access-list exttest', 'no 10', 'exit']
        func = function('remove_entry', 'exttest', '10')
        self.eapi_positive_config_test(func, cmds)

    def test_add_entry(self):
        cmds = ['ip access-list exttest',
                'permit ip 0.0.0.0/32 1.1.1.1/32 log', 'exit']
        func = function('add_entry', 'exttest', 'permit', 'ip', '0.0.0.0',
                        '32', '1.1.1.1', '32', True)
        self.eapi_positive_config_test(func, cmds)

    def test_add_entry_no_log(self):
        cmds = ['ip access-list exttest', 'permit ip 0.0.0.0/32 1.1.1.1/32',
                'exit']
        func = function('add_entry', 'exttest', 'permit', 'ip', '0.0.0.0',
                        '32', '1.1.1.1', '32')
        self.eapi_positive_config_test(func, cmds)

    def test_add_entry_with_seqno(self):
        cmds = ['ip access-list exttest',
                '30 permit ip 0.0.0.0/32 1.1.1.1/32 log', 'exit']
        func = function('add_entry', 'exttest', 'permit', 'ip', '0.0.0.0',
                        '32', '1.1.1.1', '32', True, 30)
        self.eapi_positive_config_test(func, cmds)


if __name__ == '__main__':
    unittest.main()
