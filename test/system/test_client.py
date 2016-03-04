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

from testlib import random_int, random_string, get_fixture

import pyeapi.client


class TestClient(unittest.TestCase):

    def setUp(self):
        pyeapi.client.load_config(filename=get_fixture('dut.conf'))
        config = pyeapi.client.config

        self.duts = list()
        for name in config.sections():
            if name.startswith('connection:') and 'localhost' not in name:
                name = name.split(':')[1]
                dut = pyeapi.client.connect_to(name)
                self.duts.append(dut)
                if dut._enablepwd is not None:
                    # If enable password defined for dut, set the
                    # enable password on the dut and clear it on tearDown
                    dut.config("enable secret %s" % dut._enablepwd)

    def test_enable_single_command(self):
        for dut in self.duts:
            result = dut.run_commands('show version')
            self.assertIsInstance(result, list, 'dut=%s' % dut)
            self.assertEqual(len(result), 1, 'dut=%s' % dut)

    def test_enable_multiple_commands(self):
        for dut in self.duts:
            commands = list()
            for i in range(1, random_int(10, 200)):
                commands.append('show version')
            result = dut.run_commands(commands[:])
            self.assertIsInstance(result, list, 'dut=%s' % dut)
            self.assertEqual(len(result), len(commands), 'dut=%s' % dut)

    def test_config_single_command(self):
        for dut in self.duts:
            hostname = 'hostname %s' % random_string(5, 50)
            result = dut.config(hostname)
            self.assertIsInstance(result, list, 'dut=%s' % dut)
            self.assertEqual(len(result), 1, 'dut=%s' % dut)
            self.assertEqual(result[0], {}, 'dut=%s' % dut)

            result = dut.run_commands('show running-config | include %s$' %
                                      hostname, 'text')
            self.assertEqual(result[0]['output'].strip(), hostname)

    def test_config_single_multiline_command(self):
        for dut in self.duts:
            # Clear any current banner
            dut.config('no banner login')

            banner = 'This is a new banner\nwith different lines!!!'
            cmd = 'banner login MULTILINE:%s' % banner
            result = dut.config(cmd)
            self.assertIsInstance(result, list, 'dut=%s' % dut)
            self.assertEqual(len(result), 1, 'dut=%s' % dut)
            self.assertEqual(result[0], {}, 'dut=%s' % dut)
            result = dut.run_commands('show banner login', 'text')
            self.assertEqual(result[0]['output'].strip().split('\n'),
                             banner.split('\n'))

    def test_config_multiple_commands(self):
        for dut in self.duts:
            commands = list()
            for i in range(1, random_int(10, 200)):
                commands.append('hostname %s' % random_string(5, 20))
            result = dut.config(commands[:])
            self.assertIsInstance(result, list, 'dut=%s' % dut)
            self.assertEqual(len(result), len(commands), 'dut=%s' % dut)

    def test_multiple_requests(self):
        for dut in self.duts:
            for i in range(1, random_int(10, 200)):
                result = dut.run_commands('show version')
                self.assertIsInstance(result, list, 'dut=%s' % dut)
                self.assertEqual(len(result), 1, 'dut=%s' % dut)

    def test_get_block(self):
        # Verify get_block using a config string returns correct value
        for dut in self.duts:
            api = dut.api('interfaces')
            config = api.config
            running = api.get_block('interface Ethernet1')
            txtstr = api.get_block('interface Ethernet1', config=config)
            self.assertEqual(running, txtstr)

    def test_get_block_none(self):
        # Verify get_block using a config string where match fails returns None
        for dut in self.duts:
            api = dut.api('interfaces')
            txtstr = api.get_block('interface Ethernet1', config='config')
            self.assertEqual(txtstr, None)

    def tearDown(self):
        for dut in self.duts:
            dut.config("no enable secret")


class TestNode(unittest.TestCase):

    def setUp(self):
        pyeapi.client.load_config(filename=get_fixture('dut.conf'))
        config = pyeapi.client.config

        self.duts = list()
        for name in config.sections():
            if name.startswith('connection:') and 'localhost' not in name:
                name = name.split(':')[1]
                self.duts.append(pyeapi.client.connect_to(name))

    def test_exception_trace(self):
        # Send commands that will return an error and validate the errors

        # General format of an error message:
        rfmt = r'Error \[%d\]: CLI command \d+ of \d+ \'.*\' failed: %s \[%s\]'
        # Design error tests
        cases = []
        # Send an incomplete command
        cases.append(('show run', rfmt
                      % (1002, 'invalid command',
                         'incomplete token \(at token \d+: \'.*\'\)')))
        # Send a mangled command
        cases.append(('shwo version', rfmt
                      % (1002, 'invalid command',
                         'Invalid input \(at token \d+: \'.*\'\)')))
        # Send a command that cannot be run through the api
        cases.append(('reload', rfmt
                      % (1004, 'incompatible command',
                         'Command not permitted via API access. To reload '
                         'the machine over the API, please use \'reload '
                         'now\' instead.')))
        # Send a continuous command that requires a break
        cases.append(('watch 10 show int e1 count rates', rfmt
                      % (1000, 'could not run command',
                         'init error \(cbreak\(\) returned ERR\)')))

        for dut in self.duts:
            for (cmd, regex) in cases:
                try:
                    # Insert the error in list of valid commands
                    dut.enable(['show version', cmd, 'show hostname'],
                               strict=True)
                    self.fail('A CommandError should have been raised')
                except pyeapi.eapilib.CommandError as exc:
                    # Validate the properties of the exception
                    self.assertEqual(len(exc.trace), 4)
                    self.assertIsNotNone(exc.command_error)
                    self.assertIsNotNone(exc.output)
                    self.assertIsNotNone(exc.commands)
                    self.assertRegexpMatches(exc.message, regex)


if __name__ == '__main__':
    unittest.main()
