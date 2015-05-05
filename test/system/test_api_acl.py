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
import os
import unittest

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))

from systestlib import DutSystemTest


class TestApiStandardAcls(DutSystemTest):

    def test_get(self):
        for dut in self.duts:
            dut.config(['no ip access-list standard test',
                        'ip access-list standard test'])
            response = dut.api('acl').get('test')
            self.assertIsNotNone(response)

    def test_get_none(self):
        for dut in self.duts:
            dut.config('no ip access-list standard test')
            result = dut.api('acl').get('test')
            self.assertIsNone(result)

    def test_getall(self):
        for dut in self.duts:
            dut.config(['no ip access-list standard test',
                        'ip access-list standard test'])
            result = dut.api('acl').getall()
            self.assertIn('test', result)

    def test_create(self):
        for dut in self.duts:
            dut.config('no ip access-list standard test')
            api = dut.api('acl')
            self.assertIsNone(api.get('test'))
            result = dut.api('acl').create('test')
            self.assertTrue(result)
            self.assertIsNotNone(api.get('test'))

    def test_delete(self):
        for dut in self.duts:
            dut.config('ip access-list standard test')
            api = dut.api('acl')
            self.assertIsNotNone(api.get('test'))
            result = dut.api('acl').delete('test')
            self.assertTrue(result)
            self.assertIsNone(api.get('test'))

    def test_default(self):
        for dut in self.duts:
            dut.config('ip access-list standard test')
            api = dut.api('acl')
            self.assertIsNotNone(api.get('test'))
            result = dut.api('acl').default('test')
            self.assertTrue(result)
            self.assertIsNone(api.get('test'))

    def test_update_entry(self):
        for dut in self.duts:
            dut.config(['no ip access-list standard test',
                        'ip access-list standard test'])
            api = dut.api('acl')
            self.assertNotIn('10 permit any log',
                             api.get_block('ip access-list standard test'))
            result = dut.api('acl').update_entry('test', '10', 'permit',
                                                 '0.0.0.0', '0', True)
            self.assertTrue(result)
            self.assertIn('10 permit any log',
                          api.get_block('ip access-list standard test'))

    def test_update_entry_existing(self):
        for dut in self.duts:
            dut.config(['no ip access-list standard test',
                        'ip access-list standard test', '10 permit any log'])
            api = dut.api('acl')
            self.assertIn('10 permit any log',
                          api.get_block('ip access-list standard test'))
            result = dut.api('acl').update_entry('test', '10', 'deny',
                                                 '0.0.0.0', '0', True)
            self.assertTrue(result)
            self.assertIn('10 deny any log',
                          api.get_block('ip access-list standard test'))

    def test_add_entry(self):
        for dut in self.duts:
            dut.config(['no ip access-list standard test',
                        'ip access-list standard test'])
            api = dut.api('acl')
            self.assertNotIn('10 permit any log',
                             api.get_block('ip access-list standard test'))
            result = api.add_entry('test', 'permit', '0.0.0.0', '0', True)
            self.assertTrue(result)
            self.assertIn('10 permit any log',
                          api.get_block('ip access-list standard test'))

    def test_remove_entry(self):
        for dut in self.duts:
            dut.config(['no ip access-list standard test',
                        'ip access-list standard test', '10 permit any log'])
            api = dut.api('acl')
            self.assertIn('10 permit any log',
                          api.get_block('ip access-list standard test'))
            result = api.remove_entry('test', '10')
            self.assertTrue(result)
            self.assertNotIn('10 permit any log',
                             api.get_block('ip access-list standard test'))





if __name__ == '__main__':
    unittest.main()
