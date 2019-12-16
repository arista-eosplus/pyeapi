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

TEST_SSH_KEY = ('ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDKL1UtBALa4CvFUsHUipNym'
                'A04qCXuAtTwNcMj84bTUzUI+q7mdzRCTLkllXeVxKuBnaTm2PW7W67K5CVpl0'
                'EVCm6IY7FS7kc4nlnD/tFvTvShy/fzYQRAdM7ZfVtegW8sMSFJzBR/T/Y/sxI'
                '16Y/dQb8fC3la9T25XOrzsFrQiKRZmJGwg8d+0RLxpfMg0s/9ATwQKp6tPoLE'
                '4f3dKlAgSk5eENyVLA3RsypWADHpenHPcB7sa8D38e1TS+n+EUyAdb3Yov+5E'
                'SAbgLIJLd52Xv+FyYi0c2L49ByBjcRrupp4zfXn4DNRnEG4K6GcmswHuMEGZv'
                '5vjJ9OYaaaaaaa')

class TestApiUsers(DutSystemTest):

    def test_get(self):
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['no username test', 'username test nopassword',
                            'username test ssh-key %s' % TEST_SSH_KEY])
            else:
                dut.config(['no username test', 'username test nopassword',
                            'username test sshkey %s' % TEST_SSH_KEY])

            result = dut.api('users').get('test')
            if dut.version_number >= '4.23':
                values = dict(nopassword=True, privilege='1', secret='',
                              role='', format='')
                values["ssh-key"] = TEST_SSH_KEY
            else:
                values = dict(nopassword=True, privilege='1', secret='',
                              role='', format='', sshkey=TEST_SSH_KEY)
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

    def test_set_privilege_with_value(self):
        for dut in self.duts:
            dut.config(['no username test', 'username test nopassword'])
            api = dut.api('users')
            # EOS defaults to privilege 1
            self.assertIn('username test privilege 1 nopassword', api.config)
            result = api.set_privilege('test', 8)
            self.assertTrue(result)
            self.assertIn('username test privilege 8 nopassword', api.config)

    def test_set_privilege_with_no_value(self):
        for dut in self.duts:
            dut.config(['no username test',
                        'username test privilege 8 nopassword'])
            api = dut.api('users')
            self.assertIn('username test privilege 8', api.config)
            result = api.set_privilege('test')
            self.assertTrue(result)
            self.assertIn('username test privilege 1', api.config)

    def test_set_role_with_value(self):
        for dut in self.duts:
            dut.config(['no username test', 'username test nopassword'])
            api = dut.api('users')
            self.assertIn('username test privilege 1 nopassword', api.config)
            result = api.set_role('test', 'network-admin')
            self.assertTrue(result)
            self.assertIn('username test privilege 1 role network-admin nopassword', api.config)

    def test_set_role_with_no_value(self):
        for dut in self.duts:
            dut.config(['no username test',
                        'username test role network-admin nopassword'])
            api = dut.api('users')
            self.assertIn('username test privilege 1 role network-admin nopassword', api.config)
            result = api.set_role('test')
            self.assertTrue(result)
            self.assertNotIn('username test privilege 1 role network-admin nopassword', api.config)

    def test_set_sshkey_with_value(self):
        for dut in self.duts:
            dut.config(['no username test', 'username test nopassword'])
            api = dut.api('users')
            self.assertIn('username test privilege 1 nopassword', api.config)
            if dut.version_number >= '4.23':
                self.assertNotIn('username test ssh-key', api.config)
            else:
                self.assertNotIn('username test sshkey', api.config)
            result = api.set_sshkey('test', TEST_SSH_KEY)
            self.assertTrue(result)
            if dut.version_number >= '4.23':
                self.assertIn('username test ssh-key %s' % TEST_SSH_KEY, api.config)
            else:
                self.assertIn('username test sshkey %s' % TEST_SSH_KEY, api.config)

    def test_set_sshkey_with_empty_string(self):
        for dut in self.duts:
            dut.config(['no username test', 'username test nopassword'])
            api = dut.api('users')
            self.assertIn('username test privilege 1 nopassword', api.config)
            if dut.version_number >= '4.23':
                self.assertNotIn('username test ssh-key', api.config)
            else:
                self.assertNotIn('username test sshkey', api.config)
            result = api.set_sshkey('test', '')
            self.assertTrue(result)
            if dut.version_number >= '4.23':
                self.assertNotIn('username test ssh-key %s'
                                 % TEST_SSH_KEY, api.config)
            else:
                self.assertNotIn('username test sshkey %s'
                                 % TEST_SSH_KEY, api.config)

    def test_set_sshkey_with_None(self):
        for dut in self.duts:
            dut.config(['no username test', 'username test nopassword'])
            api = dut.api('users')
            self.assertIn('username test privilege 1 nopassword', api.config)
            if dut.version_number >= '4.23':
                self.assertNotIn('username test ssh-key', api.config)
            else:
                self.assertNotIn('username test sshkey', api.config)
            result = api.set_sshkey('test', None)
            self.assertTrue(result)
            if dut.version_number >= '4.23':
                self.assertNotIn('username test ssh-key %s'
                                 % TEST_SSH_KEY, api.config)
            else:
                self.assertNotIn('username test sshkey %s'
                                 % TEST_SSH_KEY, api.config)

    def test_set_sshkey_with_no_value(self):
        for dut in self.duts:
            dut.config(['no username test',
                        'username test nopassword'])
            api = dut.api('users')
            self.assertIn('username test privilege 1 nopassword', api.config)
            result = api.set_sshkey('test', disable=True)
            self.assertTrue(result)
            if dut.version_number >= '4.23':
                self.assertNotIn('username test ssh-key %s' % TEST_SSH_KEY,
                                 api.config)
            else:
                self.assertNotIn('username test sshkey %s' % TEST_SSH_KEY,
                                 api.config)


if __name__ == '__main__':
    unittest.main()
