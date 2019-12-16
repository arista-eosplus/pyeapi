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
            resp = dut.api('system').get()
            keys = ['hostname', 'iprouting', 'banner_motd', 'banner_login']
            self.assertEqual(sorted(keys), sorted(resp.keys()))


    def test_get_with_period(self):
        for dut in self.duts:
            dut.config('hostname host.domain.net')
            response = dut.api('system').get()
            self.assertEqual(response['hostname'], 'host.domain.net')

    def test_get_check_hostname(self):
        for dut in self.duts:
            dut.config('hostname teststring')
            response = dut.api('system').get()
            self.assertEqual(response['hostname'], 'teststring')

    def test_get_check_banners(self):
        for dut in self.duts:
            motd_banner_value = random_string() + "\n"
            login_banner_value = random_string() + "\n"
            dut.config([dict(cmd="banner motd", input=motd_banner_value)])
            dut.config([dict(cmd="banner login", input=login_banner_value)])
            resp = dut.api('system').get()
            self.assertEqual(resp['banner_login'], login_banner_value.rstrip())
            self.assertEqual(resp['banner_motd'], motd_banner_value.rstrip())

    def test_get_banner_with_EOF(self):
        for dut in self.duts:
            motd_banner_value = '!!!newlinebaner\nSecondLIneEOF!!!newlinebanner\n'
            dut.config([dict(cmd="banner motd", input=motd_banner_value)])
            resp = dut.api('system').get()
            self.assertEqual(resp['banner_motd'], motd_banner_value.rstrip())

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
            response = dut.api('system').set_hostname(disable=True)
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

    def test_set_iprouting_to_true(self):
        for dut in self.duts:
            dut.config('no ip routing')
            resp = dut.api('system').set_iprouting(True)
            self.assertTrue(resp, 'dut=%s' % dut)
            self.assertNotIn('no ip rotuing', dut.running_config)

    def test_set_iprouting_to_false(self):
        for dut in self.duts:
            dut.config('ip routing')
            resp = dut.api('system').set_iprouting(False)
            self.assertTrue(resp, 'dut=%s' % dut)
            self.assertIn('no ip routing', dut.running_config)

    def test_set_iprouting_to_no(self):
        for dut in self.duts:
            dut.config('ip routing')
            resp = dut.api('system').set_iprouting(disable=True)
            self.assertTrue(resp, 'dut=%s' % dut)
            self.assertIn('no ip routing', dut.running_config)

    def test_set_iprouting_to_default(self):
        for dut in self.duts:
            dut.config('ip routing')
            resp = dut.api('system').set_iprouting(default=True)
            self.assertTrue(resp, 'dut=%s' % dut)
            self.assertIn('no ip routing', dut.running_config)

    def test_set_hostname_with_period(self):
        for dut in self.duts:
            dut.config('hostname localhost')
            response = dut.api('system').set_hostname(value='host.domain.net')
            self.assertTrue(response, 'dut=%s' % dut)
            value = 'hostname host.domain.net'
            self.assertIn(value, dut.running_config)

    def test_set_banner_motd(self):
        for dut in self.duts:
            banner_value = random_string()
            dut.config([dict(cmd="banner motd",
                             input=banner_value)])
            self.assertIn(banner_value, dut.running_config)
            banner_api_value = random_string()
            resp = dut.api('system').set_banner("motd", banner_api_value)
            self.assertTrue(resp, 'dut=%s' % dut)
            self.assertIn(banner_api_value, dut.running_config)

    def test_set_banner_motd_donkey(self):
        for dut in self.duts:
            donkey_chicken = r"""
                                  /\          /\
                                 ( \\        // )
                                  \ \\      // /
                                   \_\\||||//_/
                                    \/ _  _ \
                                   \/|(o)(O)|
                                  \/ |      |
              ___________________\/  \      /
             //                //     |____|       Cluck cluck cluck!
            //                ||     /      \
           //|                \|     \ 0  0 /
          // \       )         V    / \____/
         //   \     /        (     /
        ""     \   /_________|  |_/
               /  /\   /     |  ||
              /  / /  /      \  ||
              | |  | |        | ||
              | |  | |        | ||
              |_|  |_|        |_||
               \_\  \_\        \_\\
            """

            resp = dut.api('system').set_banner("motd", donkey_chicken)
            self.assertTrue(resp, 'dut=%s' % dut)
            self.assertIn(donkey_chicken, dut.running_config)

    def test_set_banner_motd_default(self):
        for dut in self.duts:
            dut.config([dict(cmd="banner motd",
                             input="!!!!REMOVE BANNER TEST!!!!")])
            dut.api('system').set_banner('motd', None, True)
            self.assertIn('no banner motd', dut.running_config)

    def test_set_banner_login(self):
        for dut in self.duts:
            banner_value = random_string()
            dut.config([dict(cmd="banner login",
                             input=banner_value)])
            self.assertIn(banner_value, dut.running_config)
            banner_api_value = random_string()
            resp = dut.api('system').set_banner("login", banner_api_value)
            self.assertTrue(resp, 'dut=%s' % dut)
            self.assertIn(banner_api_value, dut.running_config)
            config_login_banner = dut.api('system').get()['banner_login']
            self.assertTrue(config_login_banner, banner_api_value.strip())

    def test_set_banner_login_default(self):
        for dut in self.duts:
            dut.config([dict(cmd="banner login",
                             input="!!!!REMOVE LOGIN BANNER TEST!!!!")])
            dut.api('system').set_banner('login', None, True)
            self.assertIn('no banner login', dut.running_config)

    def test_set_banner_login_negate(self):
        for dut in self.duts:
            dut.config([dict(cmd="banner login",
                             input="!!!!REMOVE LOGIN BANNER TEST!!!!")])
            dut.api('system').set_banner('login', None, False, True)
            self.assertIn('no banner login', dut.running_config)




if __name__ == '__main__':
    unittest.main()
