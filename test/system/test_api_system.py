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

from testlib import random_string
from systestlib import DutSystemTest


class TestApiSystem(DutSystemTest):

    def test_get(self):
        for dut in self.duts:
            dut.config('default hostname')
            response = dut.api('system').get()
            keys = ['hostname']
            self.assertEqual(keys, response.keys())
            self.assertEqual(response['hostname'], 'localhost')

    def test_get_check_hostname(self):
        for dut in self.duts:
            dut.config('hostname teststring')
            response = dut.api('system').get()
            self.assertEqual(response['hostname'], 'teststring')

    def test_set_hostname_with_value(self):
        for dut in self.duts:
            dut.config('default hostname')
            value = random_string()
            response = dut.api('system').set_hostname(value)
            self.assertTrue(response, 'dut=%s' % dut)
            value = 'hostname %s' % value
            self.assertIn(value, dut.running_config)

    def test_set_hostname_with_no_value(self):
        for dut in self.duts:
            dut.config('hostname test')
            response = dut.api('system').set_hostname()
            self.assertTrue(response, 'dut=%s' % dut)
            value = 'no hostname'
            self.assertIn(value, dut.running_config)

    def test_set_hostname_with_default(self):
        for dut in self.duts:
            dut.config('hostname test')
            response = dut.api('system').set_hostname(default=True)
            self.assertTrue(response, 'dut=%s' % dut)
            value = 'no hostname'
            self.assertIn(value, dut.running_config)

    def test_set_hostname_default_over_value(self):
        for dut in self.duts:
            dut.config('hostname test')
            response = dut.api('system').set_hostname(value='foo', default=True)
            self.assertTrue(response, 'dut=%s' % dut)
            value = 'no hostname'
            self.assertIn(value, dut.running_config)


if __name__ == '__main__':
    unittest.main()
