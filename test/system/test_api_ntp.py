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
import itertools

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))

from systestlib import DutSystemTest


class TestApiNtp(DutSystemTest):

    def test_get(self):
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['ntp local-interface Ethernet1', 'ntp server 99.99.1.1'])
            else:
                dut.config(['ntp source Ethernet1', 'ntp server 99.99.1.1'])
            response = dut.api('ntp').get()
            self.assertIsNotNone(response)

    def test_create(self):
        intf = 'Ethernet1'
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['no ntp local-interface'])
            else:
                dut.config(['no ntp source'])
            response = dut.api('ntp').create(intf)
            self.assertTrue(response)
            response = dut.api('ntp').get()
            self.assertEqual(response['source_interface'], intf)

    def test_delete(self):
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['ntp local-interface Ethernet1'])
            else:
                dut.config(['ntp source Ethernet1'])
            response = dut.api('ntp').delete()
            self.assertTrue(response)
            response = dut.api('ntp').get()
            self.assertIsNone(response['source_interface'])

    def test_default(self):
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['ntp local-interface Ethernet1'])
            else:
                dut.config(['ntp source Ethernet1'])
            response = dut.api('ntp').default()
            self.assertTrue(response)
            response = dut.api('ntp').get()
            self.assertIsNone(response['source_interface'])

    def test_set_source_interface(self):
        intf = 'Ethernet1'
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['ntp local-interface Loopback0'])
            else:
                dut.config(['ntp source Loopback0'])
            response = dut.api('ntp').set_source_interface(intf)
            self.assertTrue(response)
            response = dut.api('ntp').get()
            self.assertEqual(response['source_interface'], intf)

    def test_add_server_single(self):
        server = '10.10.10.35'
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['ntp local-interface Ethernet1', 'no ntp'])
            else:
                dut.config(['ntp source Ethernet1', 'no ntp'])
            response = dut.api('ntp').add_server(server)
            self.assertTrue(response)
            response = dut.api('ntp').get()
            keys = [x.keys() for x in response['servers']]
            keys = list(itertools.chain.from_iterable(keys))
            self.assertListEqual(keys, [server])

    def test_add_server_multiple(self):
        servers = ['10.10.10.37', '10.10.10.36', '10.10.10.34']
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['ntp local-interface Ethernet1', 'no ntp'])
            else:
                dut.config(['ntp source Ethernet1', 'no ntp'])
            for server in servers:
                response = dut.api('ntp').add_server(server)
            self.assertTrue(response)
            response = dut.api('ntp').get()
            keys = [x.keys() for x in response['servers']]
            keys = list(itertools.chain.from_iterable(keys))
            self.assertListEqual(sorted(keys), sorted(servers))

    def test_add_server_prefer(self):
        server = '10.10.10.35'
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['ntp local-interface Ethernet1', 'no ntp'])
            else:
                dut.config(['ntp source Ethernet1', 'no ntp'])
            response = dut.api('ntp').add_server(server, prefer=False)
            self.assertTrue(response)
            response = dut.api('ntp').get()
            self.assertIsNone(response['servers'][0][server])

            response = dut.api('ntp').add_server(server, prefer=True)
            self.assertTrue(response)
            response = dut.api('ntp').get()
            self.assertEqual(response['servers'][0][server], 'prefer')

    def test_add_server_invalid(self):
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['ntp local-interface Ethernet1', 'no ntp'])
            else:
                dut.config(['ntp source Ethernet1', 'no ntp'])
            with self.assertRaises(ValueError):
                dut.api('ntp').add_server(None)
                dut.api('ntp').add_server('')
                dut.api('ntp').add_server(' ')

    def test_remove_server(self):
        server = '10.10.10.35'
        servers = ['10.10.10.37', '10.10.10.36', '10.10.10.34']
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['ntp local-interface Ethernet1', 'no ntp',
                            'ntp server %s' % server])
            else:
                dut.config(['ntp source Ethernet1', 'no ntp',
                            'ntp server %s' % server])
            for addserver in servers:
                dut.config(['ntp server %s' % addserver])
            response = dut.api('ntp').remove_server(server)
            self.assertTrue(response)
            response = dut.api('ntp').get()
            keys = [x.keys() for x in response['servers']]
            keys = list(itertools.chain.from_iterable(keys))
            self.assertListEqual(sorted(keys), sorted(servers))

    def test_remove_all_servers(self):
        servers = ['10.10.10.37', '10.10.10.36', '10.10.10.34']
        for dut in self.duts:
            if dut.version_number >= '4.23':
                dut.config(['ntp local-interface Ethernet1', 'no ntp'])
            else:
                dut.config(['ntp source Ethernet1', 'no ntp'])
            for addserver in servers:
                dut.config(['ntp server %s' % addserver])
            response = dut.api('ntp').remove_all_servers()
            self.assertTrue(response)
            response = dut.api('ntp').get()
            self.assertEqual(response['servers'], [])


if __name__ == '__main__':
    unittest.main()
