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
import os
import unittest

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))

from systestlib import DutSystemTest
from testlib import random_string


class TestApiRoutemaps(DutSystemTest):

    def test_get(self):
        for dut in self.duts:
            dut.config(['no route-map TEST deny 10',
                        'route-map TEST deny 10',
                        'set weight 100',
                        'match tag 50'])
            response = dut.api('routemaps').get('TEST')
            self.assertIsNotNone(response)

    def test_get_none(self):
        for dut in self.duts:
            dut.config('no route-map TEST deny 10')
            result = dut.api('routemaps').get('TEST')
            self.assertIsNone(result)

    def test_getall(self):
        for dut in self.duts:
            dut.config(['no route-map TEST deny 10',
                        'route-map TEST deny 10',
                        'set weight 100',
                        'no route-map TEST-2 permit 50',
                        'route-map TEST-2 permit 50',
                        'match tag 50'])
            result = dut.api('routemaps').getall()
            self.assertIn(('TEST'), result)
            self.assertIn(('TEST-2'), result)

    def test_create(self):
        for dut in self.duts:
            dut.config(['no route-map TEST deny 10'])
            api = dut.api('routemaps')
            self.assertIsNone(api.get('TEST'))
            result = dut.api('routemaps').create('TEST', 'deny', 10)
            self.assertTrue(result)
            self.assertIsNotNone(api.get('TEST'))
            dut.config(['no route-map TEST deny 10'])

    def test_create_with_hyphen(self):
        for dut in self.duts:
            dut.config(['no route-map TEST-1 deny 10'])
            api = dut.api('routemaps')
            self.assertIsNone(api.get('TEST-1'))
            result = dut.api('routemaps').create('TEST-1', 'deny', 10)
            self.assertTrue(result)
            self.assertIsNotNone(api.get('TEST-1'))
            dut.config(['no route-map TEST-1 deny 10'])

    def test_create_with_underscore(self):
        for dut in self.duts:
            dut.config(['no route-map TEST_1 deny 10'])
            api = dut.api('routemaps')
            self.assertIsNone(api.get('TEST_1'))
            result = dut.api('routemaps').create('TEST_1', 'deny', 10)
            self.assertTrue(result)
            self.assertIsNotNone(api.get('TEST_1'))
            dut.config(['no route-map TEST_1 deny 10'])

    def test_delete(self):
        for dut in self.duts:
            dut.config(['no route-map TEST deny 10',
                        'route-map TEST deny 10',
                        'set weight 100'])
            api = dut.api('routemaps')
            self.assertIsNotNone(api.get('TEST'))
            result = dut.api('routemaps').delete('TEST', 'deny', 10)
            self.assertTrue(result)
            self.assertIsNone(api.get('TEST'))

    def test_default(self):
        for dut in self.duts:
            dut.config(['no route-map TEST deny 10',
                        'route-map TEST deny 10',
                        'set weight 100'])
            api = dut.api('routemaps')
            self.assertIsNotNone(api.get('TEST'))
            result = dut.api('routemaps').default('TEST', 'deny', 10)
            self.assertTrue(result)
            self.assertIsNone(api.get('TEST'))

    def test_set_description(self):
        for dut in self.duts:
            text = random_string()
            dut.config(['no route-map TEST deny 10',
                        'route-map TEST deny 10'])
            api = dut.api('routemaps')
            self.assertNotIn('description %s' % text,
                             api.get_block('route-map TEST deny 10'))
            result = dut.api('routemaps').set_description('TEST', 'deny', 10,
                                                          text)
            self.assertTrue(result)
            self.assertIn('description %s' % text,
                          api.get_block('route-map TEST deny 10'))

    def test_set_match_statements(self):
        for dut in self.duts:
            dut.config(['no route-map TEST deny 10',
                        'route-map TEST deny 10'])
            api = dut.api('routemaps')
            self.assertNotIn('match as 100',
                             api.get_block('route-map TEST deny 10'))
            result = dut.api('routemaps').set_match_statements('TEST', 'deny',
                                                               10, ['as 100'])
            self.assertTrue(result)
            self.assertIn('match as 100',
                          api.get_block('route-map TEST deny 10'))

    def test_update_match_statement(self):
        for dut in self.duts:
            dut.config(['no route-map TEST deny 10',
                        'route-map TEST deny 10',
                        'match as 100'])
            api = dut.api('routemaps')
            self.assertIn('match as 100',
                          api.get_block('route-map TEST deny 10'))
            result = dut.api('routemaps').set_match_statements('TEST', 'deny',
                                                               10, ['as 200'])
            self.assertTrue(result)
            self.assertNotIn('match as 100',
                             api.get_block('route-map TEST deny 10'))
            self.assertIn('match as 200',
                          api.get_block('route-map TEST deny 10'))

    def test_remove_match_statement(self):
        for dut in self.duts:
            dut.config(['no route-map TEST deny 10',
                        'route-map TEST deny 10',
                        'match as 100'])
            api = dut.api('routemaps')
            self.assertIn('match as 100',
                          api.get_block('route-map TEST deny 10'))
            result = dut.api('routemaps').set_match_statements('TEST', 'deny',
                                                               10, ['tag 50'])
            self.assertTrue(result)
            self.assertNotIn('match as 100',
                             api.get_block('route-map TEST deny 10'))
            self.assertIn('match tag 50',
                          api.get_block('route-map TEST deny 10'))

    def test_set_set_statements(self):
        for dut in self.duts:
            dut.config(['no route-map TEST deny 10',
                        'route-map TEST deny 10'])
            api = dut.api('routemaps')
            self.assertNotIn('set weight 100',
                             api.get_block('route-map TEST deny 10'))
            result = dut.api('routemaps').set_set_statements('TEST', 'deny',
                                                             10, ['weight 100'])
            self.assertTrue(result)
            self.assertIn('set weight 100',
                          api.get_block('route-map TEST deny 10'))

    def test_update_set_statement(self):
        for dut in self.duts:
            dut.config(['no route-map TEST deny 10',
                        'route-map TEST deny 10',
                        'set weight 100'])
            api = dut.api('routemaps')
            self.assertIn('set weight 100',
                          api.get_block('route-map TEST deny 10'))
            result = dut.api('routemaps').set_set_statements('TEST', 'deny',
                                                             10, ['weight 200'])
            self.assertTrue(result)
            self.assertNotIn('set weight 100',
                             api.get_block('route-map TEST deny 10'))
            self.assertIn('set weight 200',
                          api.get_block('route-map TEST deny 10'))

    def test_remove_set_statement(self):
        for dut in self.duts:
            dut.config(['no route-map TEST deny 10',
                        'route-map TEST deny 10',
                        'set weight 100'])
            api = dut.api('routemaps')
            self.assertIn('set weight 100',
                          api.get_block('route-map TEST deny 10'))
            result = dut.api('routemaps').set_set_statements('TEST', 'deny',
                                                             10, ['tag 50'])
            self.assertTrue(result)
            self.assertNotIn('set weight 100',
                             api.get_block('route-map TEST deny 10'))
            self.assertIn('set tag 50',
                          api.get_block('route-map TEST deny 10'))

    def test_set_continue(self):
        for dut in self.duts:
            dut.config(['no route-map TEST deny 10',
                        'route-map TEST deny 10'])
            api = dut.api('routemaps')
            self.assertNotIn('continue',
                             api.get_block('route-map TEST deny 10'))
            result = dut.api('routemaps').set_continue('TEST', 'deny', 10, 100)
            self.assertTrue(result)
            self.assertEqual(100, api.get('TEST')['deny'][10]['continue'])

    def test_update_continue(self):
        for dut in self.duts:
            dut.config(['no route-map TEST deny 10',
                        'route-map TEST deny 10',
                        'continue 30'])
            api = dut.api('routemaps')
            self.assertIn('continue 30',
                          api.get_block('route-map TEST deny 10'))
            result = dut.api('routemaps').set_continue('TEST', 'deny', 10, 60)
            self.assertTrue(result)
            self.assertEqual(60, api.get('TEST')['deny'][10]['continue'])

    def test_default_continue(self):
        for dut in self.duts:
            dut.config(['no route-map TEST deny 10',
                        'route-map TEST deny 10',
                        'continue 100'])
            api = dut.api('routemaps')
            self.assertIn('continue 100',
                          api.get_block('route-map TEST deny 10'))
            result = dut.api('routemaps').set_continue('TEST', 'deny', 10,
                                                       default=True)
            self.assertTrue(result)
            self.assertEqual(None, api.get('TEST')['deny'][10]['continue'])

    def test_negate_continue(self):
        for dut in self.duts:
            dut.config(['no route-map TEST deny 10',
                        'route-map TEST deny 10',
                        'continue 100'])
            api = dut.api('routemaps')
            self.assertIn('continue 100',
                          api.get_block('route-map TEST deny 10'))
            result = dut.api('routemaps').set_continue('TEST', 'deny', 10,
                                                       disable=True)
            self.assertTrue(result)
            self.assertEqual(None, api.get('TEST')['deny'][10]['continue'])


if __name__ == '__main__':
    unittest.main()
