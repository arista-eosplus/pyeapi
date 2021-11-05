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
from mock import patch

import pyeapi.client
import pyeapi.eapilib


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
                    if dut.version_number >= '4.23':
                        dut.config("enable password %s" % dut._enablepwd)
                    else:
                        dut.config("enable secret %s" % dut._enablepwd)

    def test_unauthorized_user(self):
        error_string = ('Unauthorized. Unable to authenticate user: Bad'
                        ' username/password combination')
        for dut in self.duts:
            temp_node = pyeapi.connect(host=dut.settings['host'],
                                       transport=dut.settings['transport'],
                                       username='wrong', password='nope',
                                       port=dut.settings['port'],
                                       return_node=True)
            try:
                temp_node.run_commands('show version')
            except pyeapi.eapilib.ConnectionError as err:
                self.assertEqual(err.message, error_string)

    def test_populate_version_properties(self):
        for dut in self.duts:
            result = dut.run_commands('show version')
            self.assertEqual(dut.version, result[0]['version'])
            self.assertIn(dut.model, result[0]['modelName'])
            self.assertIn(dut.version_number, result[0]['version'])

    def test_enable_single_command(self):
        for dut in self.duts:
            result = dut.run_commands('show version')
            self.assertIsInstance(result, list, 'dut=%s' % dut)
            self.assertEqual(len(result), 1, 'dut=%s' % dut)

    def test_enable_single_extended_command(self):
        for dut in self.duts:
            result = dut.run_commands({'cmd': 'show cvx', 'revision': 1})
            self.assertIsInstance(result, list, 'dut=%s' % dut)
            self.assertEqual(len(result), 1, 'dut=%s' % dut)
            self.assertTrue('clusterMode' not in result[0].keys())

            result2 = dut.run_commands({'cmd': 'show cvx', 'revision': 2})
            self.assertIsInstance(result2, list, 'dut=%s' % dut)
            self.assertEqual(len(result2), 1, 'dut=%s' % dut)
            self.assertTrue('clusterMode' in result2[0].keys())

    def test_enable_single_unicode_command(self):
        for dut in self.duts:
            result = dut.run_commands(u'show version')
            self.assertIsInstance(result, list, 'dut=%s' % dut)
            self.assertEqual(len(result), 1, 'dut=%s' % dut)

    def test_no_enable_single_command(self):
        for dut in self.duts:
            result = dut.run_commands('show version', 'json', send_enable=False)
            self.assertIsInstance(result, list, 'dut=%s' % dut)
            self.assertEqual(len(result), 1, 'dut=%s' % dut)

    def test_no_enable_single_command_no_auth(self):
        for dut in self.duts:
            with self.assertRaises(pyeapi.eapilib.CommandError):
                dut.run_commands(['disable', 'show running-config'], 'json', send_enable=False)

    def test_enable_multiple_commands(self):
        for dut in self.duts:
            commands = list()
            for i in range(1, random_int(10, 200)):
                commands.append('show version')
            result = dut.run_commands(commands[:])
            self.assertIsInstance(result, list, 'dut=%s' % dut)
            self.assertEqual(len(result), len(commands), 'dut=%s' % dut)

    def test_enable_multiple_unicode_commands(self):
        for dut in self.duts:
            commands = list()
            for i in range(1, random_int(10, 200)):
                commands.append(u'show version')
            result = dut.enable(commands[:])
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

    def test_execute_with_autocomplete(self):
        # There are some versions of EOS before 4.17.x that have the
        # autocomplete feature available. If system tests are run on one of
        # those version of EOS this system test will fail.
        for dut in self.duts:
            version = self._dut_eos_version(dut)
            version = version.split('.')
            if int(version[0]) >= 4 and int(version[1]) >= 17:
                result = dut.connection.execute(['sh ver'], encoding='json',
                                                autoComplete=True)
                self.assertIn('version', result['result'][0])
            else:
                # Verify exception thrown for EOS version that does not
                # support autoComplete parameter with EAPI
                with self.assertRaises(pyeapi.eapilib.CommandError):
                    dut.connection.execute(['sh ver'], encoding='json',
                                           autoComplete=True)

    def test_execute_with_expandaliases(self):
        # There are some versions of EOS before 4.17.x that have the
        # expandaliases feature available. If system tests are run on one of
        # those version of EOS this system test will fail.
        for dut in self.duts:
            # configure an alias for show version command
            dut.config(['alias test show version'])
            version = self._dut_eos_version(dut)
            version = version.split('.')
            if int(version[0]) >= 4 and int(version[1]) >= 17:
                result = dut.connection.execute(['test'], encoding='json',
                                                expandAliases=True)
                self.assertIn('version', result['result'][0])
            else:
                # Verify exception thrown for EOS version that does not
                # support expandAliases parameter with EAPI
                with self.assertRaises(pyeapi.eapilib.CommandError):
                    dut.connection.execute(['test'], encoding='json',
                                           expandAliases=True)

    @patch('pyeapi.eapilib._LOGGER.exception')
    def test_execute_socket_timeout_error(self, logexception):
        for dut in self.duts:
            self.assertEqual(dut.connection.transport.timeout, 60)
            dut.connection.transport.timeout = 0.001
            try:
                dut.connection.execute(['show version'], encoding='json')
            except pyeapi.eapilib.ConnectionError as err:
                error_msg = 'Socket error during eAPI connection: timed out'
                self.assertEqual(err.message, error_msg)
            logexception.assert_called_once()
            dut.connection.transport.timeout = 60

    def _dut_eos_version(self, dut):
        result = dut.connection.execute(['show version'], encoding='json')
        return result['result'][0]['version']

    def tearDown(self):
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config("no enable password")
            else:
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

        if not hasattr(self, 'assertRegex'):
            self.assertRegex = self.assertRegexpMatches

    def test_exception_trace(self):
        # Send commands that will return an error and validate the errors

        # General format of an error message:
        rfmt = r'Error \[%d\]: CLI command \d+ of \d+ \'.*\' failed: %s \[%s\]'
        # Design error tests
        cases = []
        # Send an incomplete command
        cases.append(('show run', rfmt
                      % (1002, 'invalid command',
                         r'incomplete token \(at token \d+: \'.*\'\)')))
        # Send a mangled command
        cases.append(('shwo version', rfmt
                      % (1002, 'invalid command',
                         r'Invalid input \(at token \d+: \'.*\'\)')))
        # Send a command that cannot be run through the api
        # note the command for reload looks to change in new EOS
        # in 4.15 the  reload now is replaced with 'force' if you are
        # testing some DUT running older code and this test fails
        # change the error message to the following:
        # To reload the machine over the API, please use 'reload now' instead
        cases.append(('reload', rfmt
                      % (1004, 'incompatible command',
                         'Command not permitted via API access..*')))
        # Send a command that has insufficient priv
        cases.append(('show running-config', rfmt
                      % (1002, 'invalid command',
                         r'Invalid input \(privileged mode required\)')))

        for dut in self.duts:
            for (cmd, regex) in cases:
                try:
                    # Insert the error in list of valid commands
                    if cmd != "show running-config":
                        dut.enable(['show version', cmd, 'show hostname'],
                                   strict=True)
                    else:
                        dut.enable(['disable', 'show version', cmd],
                                   strict=True, send_enable=False)

                    self.fail('A CommandError should have been raised')
                except pyeapi.eapilib.CommandError as exc:
                    # Validate the properties of the exception
                    if cmd != 'show running-config':
                        self.assertEqual(len(exc.trace), 4)
                    else:
                        self.assertEqual(len(exc.trace), 3)
                    self.assertIsNotNone(exc.command_error)
                    self.assertIsNotNone(exc.output)
                    self.assertIsNotNone(exc.commands)
                    self.assertRegex(exc.message, regex)


if __name__ == '__main__':
    unittest.main()
