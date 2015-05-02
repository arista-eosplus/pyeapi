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


class TestApiUsers(DutSystemTest):

    def test_get(self):
        for dut in self.duts:
            dut.config(['no username test', 'username test nopassword'])
            result = dut.api('users').get('test')
            values = dict(nopassword=True, privilege='1', secret='',
                          role='', format='')

            result = self.sort_dict_by_keys(result)
            values = self.sort_dict_by_keys(values)

            self.assertEqual(values, result)

    def test_getall(self):
        for dut in self.duts:
            dut.config(['no username test', 'username test nopassword'])
            result = dut.api('users').getall()
            self.assertIsInstance(result, dict, 'dut=%s' % dut)
            self.assertIn('test', result, 'dut=%s' % dut)

    def test_create(self):
        for dut in self.duts:
            dut.config(['no username test', 'username test nopassword'])
            api = dut.api('users')
            result = api.create('test', nopassword=True)
            self.assertTrue(result)
            self.assertIn('username test privilege 1', api.config)

    def test_delete(self):
        for dut in self.duts:
            dut.config(['username test nopassword'])
            api = dut.api('users')
            self.assertIn('username test privilege 1 nopassword', api.config)
            result = api.delete('test')
            self.assertTrue(result)
            self.assertNotIn('username test privilege 1 nopassword', api.config)

    def test_default(self):
        for dut in self.duts:
            dut.config(['username test nopassword'])
            api = dut.api('users')
            self.assertIn('username test privilege 1 nopassword', api.config)
            result = api.default('test')
            self.assertTrue(result)
            self.assertNotIn('username test nopassword', api.config)

    def set_privilege_with_value(self):
        for dut in self.duts:
            dut.config(['no username test', 'username test nopassword'])
            api = dut.api('users')
            self.assertIn('username test nopassword', api.config)
            result = api.set_privilege('test', 8)
            self.assertTrue(result)
            self.assertNotIn('username test privilege 8', api.config)

    def set_privilege_with_no_value(self):
        for dut in self.duts:
            dut.config(['no username test',
                        'username test privilege 8 nopassword'])
            api = dut.api('users')
            self.assertIn('username test privilege 8', api.config)
            result = api.set_privilege('test')
            self.assertTrue(result)
            self.assertNotIn('username test privilege 1', api.config)


if __name__ == '__main__':
    unittest.main()
