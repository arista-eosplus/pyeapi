#
# Copyright (c) 2017, Arista Networks, Inc.
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

from testlib import random_string
from systestlib import DutSystemTest


class TestApiVrfs(DutSystemTest):

    def test_get(self):
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['no vrf instance blah', 'vrf instance blah',
                            'rd 10:10', 'description blah desc'])
            else:
                dut.config(['no vrf definition blah', 'vrf definition blah',
                            'rd 10:10', 'description blah desc'])
            response = dut.api('vrfs').get('blah')
            values = dict(rd='10:10', vrf_name='blah', description='blah desc',
                          ipv4_routing=False, ipv6_routing=False)
            self.assertEqual(values, response)
            if dut.version_number >= '4.23':
                dut.config(['no vrf instance blah'])
            else:
                dut.config(['no vrf definition blah'])

    def test_getall(self):
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['no vrf instance blah', 'vrf instance blah',
                            'no vrf instance second', 'vrf instance second'])
            else:
                dut.config(['no vrf definition blah', 'vrf definition blah',
                            'no vrf definition second', 'vrf definition second'])
            response = dut.api('vrfs').getall()
            self.assertIsInstance(response, dict, 'dut=%s' % dut)
            self.assertEqual(len(response), 2)
            for vrf_name in ['blah', 'second']:
                self.assertIn(vrf_name, response, 'dut=%s' % dut)
            if dut.version_number >= '4.23':
                dut.config(['no vrf instance blah', 'no vrf instance second'])
            else:
                dut.config(['no vrf definition blah', 'no vrf definition second'])

    def test_create_and_return_true(self):
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['no vrf instance blah', 'vrf instance blah'])
            else:
                dut.config(['no vrf definition blah', 'vrf definition blah'])
            result = dut.api('vrfs').create('blah')
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show vrf', encoding='text')
            self.assertIn('blah', config[0]['output'], 'dut=%s' % dut)
            if dut.version_number >= '4.23':
                dut.config(['no vrf instance blah'])
            else:
                dut.config(['no vrf definition blah'])

    def test_create_with_valid_rd(self):
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['no vrf instance blah', 'vrf instance blah'])
            else:
                dut.config(['no vrf definition blah', 'vrf definition blah'])
            result = dut.api('vrfs').create('blah', rd='10:10')
            self.assertTrue(result, 'dut=%s' % dut)
            command = 'show running-config section vrf'
            config = dut.run_commands(command, encoding='text')
            if dut.version_number >= '4.23':
                self.assertIn('vrf instance blah', config[0]['output'],
                              'dut=%s' % dut)
            else:
                self.assertIn('vrf definition blah', config[0]['output'],
                              'dut=%s' % dut)
            self.assertIn('rd 10:10', config[0]['output'], 'dut=%s' % dut)
            if dut.version_number >= '4.23':
                dut.config(['no vrf instance blah'])
            else:
                dut.config(['no vrf definition blah'])

    def test_create_and_return_false(self):
        for dut in self.duts:
            result = dut.api('vrfs').create('a%')
            self.assertFalse(result, 'dut=%s' % dut)

    def test_create_with_invalid_rd(self):
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['no vrf instance blah', 'vrf instance blah'])
            else:
                dut.config(['no vrf definition blah', 'vrf definition blah'])
            result = dut.api('vrfs').create('blah', rd='192.168.1.1:99999999')
            self.assertFalse(result, 'dut=%s' % dut)
            command = 'show running-config section vrf'
            config = dut.run_commands(command, encoding='text')
            if dut.version_number >= '4.23':
                self.assertIn('vrf instance blah', config[0]['output'],
                              'dut=%s' % dut)
            else:
                self.assertIn('vrf definition blah', config[0]['output'],
                              'dut=%s' % dut)
            self.assertNotIn('rd', config[0]['output'],
                             'dut=%s' % dut)
            if dut.version_number >= '4.23':
                dut.config(['no vrf instance blah'])
            else:
                dut.config(['no vrf definition blah'])

    def test_delete_and_return_true(self):
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config('vrf instance blah')
            else:
                dut.config('vrf definition blah')
            result = dut.api('vrfs').delete('blah')
            self.assertTrue(result, 'dut=%s' % dut)
            command = 'show running-config section vrf'
            config = dut.run_commands(command, encoding='text')
            if dut.version_number >= '4.23':
                self.assertNotIn('vrf instance blah', config[0]['output'],
                                 'dut=%s' % dut)
            else:
                self.assertNotIn('vrf definition blah', config[0]['output'],
                                 'dut=%s' % dut)

    def test_delete_and_return_false(self):
        for dut in self.duts:
            result = dut.api('vrfs').delete('a%')
            self.assertFalse(result, 'dut=%s' % dut)

    def test_default(self):
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['no vrf instance blah', 'vrf instance blah',
                            'description test desc'])
            else:
                dut.config(['no vrf definition blah', 'vrf definition blah',
                            'description test desc'])
            result = dut.api('vrfs').default('blah')
            self.assertTrue(result, 'dut=%s' % dut)
            command = 'show running-config section vrf'
            config = dut.run_commands(command, encoding='text')
            if dut.version_number >= '4.23':
                self.assertNotIn('vrf instance blah', config[0]['output'],
                                 'dut=%s' % dut)
                dut.config(['no vrf instance blah'])
            else:
                self.assertNotIn('vrf definition blah', config[0]['output'],
                                 'dut=%s' % dut)
                dut.config(['no vrf definition blah'])

    def test_set_rd(self):
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['no vrf instance blah', 'vrf instance blah'])
            else:
                dut.config(['no vrf definition blah', 'vrf definition blah'])
            result = dut.api('vrfs').set_rd('blah', '10:10')
            self.assertTrue(result, 'dut=%s' % dut)
            command = 'show running-config section vrf'
            config = dut.run_commands(command, encoding='text')
            self.assertIn('blah', config[0]['output'], 'dut=%s' % dut)
            self.assertIn('10:10', config[0]['output'], 'dut=%s' % dut)
            if dut.version_number >= '4.23':
                dut.config(['no vrf instance blah'])
            else:
                dut.config(['no vrf definition blah'])

    def test_set_description(self):
        for dut in self.duts:
            description = random_string()
            if dut.version_number >= '4.23':
                dut.config(['no vrf instance blah', 'vrf instance blah'])
            else:
                dut.config(['no vrf definition blah', 'vrf definition blah'])
            result = dut.api('vrfs').set_description('blah', description)
            self.assertTrue(result, 'dut=%s' % dut)
            command = 'show running-config section vrf'
            config = dut.run_commands(command, encoding='text')
            self.assertIn('description %s' % description, config[0]['output'],
                          'dut=%s' % dut)
            result = dut.api('vrfs').set_description('blah', default=True)
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands(command, encoding='text')
            self.assertNotIn('description %s' % description,
                             config[0]['output'], 'dut=%s' % dut)
            if dut.version_number >= '4.23':
                dut.config(['no vrf instance blah'])
            else:
                dut.config(['no vrf definition blah'])

    def test_set_ipv4_routing(self):
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['no vrf instance blah', 'vrf instance blah',
                            'rd 10:10', 'description test'])
            else:
                dut.config(['no vrf definition blah', 'vrf definition blah',
                            'rd 10:10', 'description test'])
            result = dut.api('vrfs').set_ipv4_routing('blah')
            self.assertTrue(result, 'dut=%s' % dut)
            command = 'show running-config section vrf'
            config = dut.run_commands(command, encoding='text')
            self.assertIn('ip routing vrf blah', config[0]['output'],
                          'dut=%s' % dut)
            result = dut.api('vrfs').set_ipv4_routing('blah', default=True)
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands(command, encoding='text')
            self.assertIn('no ip routing vrf blah', config[0]['output'],
                          'dut=%s' % dut)
            if dut.version_number >= '4.23':
                dut.config(['no vrf instance blah'])
            else:
                dut.config(['no vrf definition blah'])

    def test_set_ipv6_routing(self):
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['no vrf instance blah', 'vrf instance blah',
                            'rd 10:10', 'description test'])
            else:
                dut.config(['no vrf definition blah', 'vrf definition blah',
                            'rd 10:10', 'description test'])
            result = dut.api('vrfs').set_ipv6_routing('blah')
            self.assertTrue(result, 'dut=%s' % dut)
            command = 'show running-config all section vrf'
            config = dut.run_commands(command, encoding='text')
            self.assertIn('ipv6 unicast-routing vrf blah', config[0]['output'],
                          'dut=%s' % dut)
            result = dut.api('vrfs').set_ipv6_routing('blah', default=True)
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands(command, encoding='text')
            self.assertIn('no ipv6 unicast-routing vrf blah',
                          config[0]['output'], 'dut=%s' % dut)
            if dut.version_number >= '4.23':
                dut.config(['no vrf instance blah'])
            else:
                dut.config(['no vrf definition blah'])

    def test_set_interface(self):
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['no vrf instance blah', 'vrf instance blah',
                            'rd 10:10', 'default interface Ethernet1',
                            'interface Ethernet1', 'no switchport'])
            else:
                dut.config(['no vrf definition blah', 'vrf definition blah',
                            'rd 10:10', 'default interface Ethernet1',
                            'interface Ethernet1', 'no switchport'])
            result = dut.api('vrfs').set_interface('blah', 'Ethernet1')
            self.assertTrue(result, 'dut=%s' % dut)
            command = 'show running-config interfaces Ethernet1'
            config = dut.run_commands(command, encoding='text')
            if dut.version_number >= '4.23':
                self.assertIn('vrf blah', config[0]['output'],
                              'dut=%s' % dut)
            else:
                self.assertIn('vrf forwarding blah', config[0]['output'],
                              'dut=%s' % dut)
            result = dut.api('vrfs').set_interface('blah', 'Ethernet1',
                                                   disable=True)
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands(command, encoding='text')
            if dut.version_number >= '4.23':
                self.assertNotIn('vrf blah', config[0]['output'],
                                 'dut=%s' % dut)
                dut.config(['no vrf instance blah',
                            'default interface Ethernet1'])
            else:
                self.assertNotIn('vrf forwarding blah', config[0]['output'],
                                 'dut=%s' % dut)
                dut.config(['no vrf definition blah',
                            'default interface Ethernet1'])


if __name__ == '__main__':
    unittest.main()
