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
import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))

from testlib import get_fixture, function
from testlib import EapiConfigUnitTest

import pyeapi.api.mlag

class TestApiMlag(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestApiMlag, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.mlag.instance(None)
        self.config = open(get_fixture('running_config.text')).read()

    def test_get(self):
        result = self.instance.get()

        keys = ['config', 'interfaces']

        intfkeys = ['mlag_id']
        interfaces = result['interfaces']['Port-Channel10']

        cfgkeys = ['domain_id', 'local_interface', 'peer_address',
                   'peer_link', 'shutdown']

        self.assertEqual(sorted(keys), sorted(result.keys()))
        self.assertEqual(sorted(cfgkeys), sorted(result['config'].keys()))
        self.assertEqual(sorted(intfkeys), sorted(interfaces.keys()))

    def test_set_domain_id(self):
        for state in ['config', 'negate', 'default']:
            cmds = ['mlag configuration']
            if state == 'config':
                cmds.append('domain-id test.dom-id string')
                func = function('set_domain_id', 'test.dom-id string')
            elif state == 'negate':
                cmds.append('no domain-id')
                func = function('set_domain_id', value='test', disable=True)
            elif state == 'default':
                cmds.append('default domain-id')
                func = function('set_domain_id', value='test', default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_local_interface(self):
        for state in ['config', 'negate', 'default']:
            cmds = ['mlag configuration']
            if state == 'config':
                cmds.append('local-interface Vlan1234')
                func = function('set_local_interface', 'Vlan1234')
            elif state == 'negate':
                cmds.append('no local-interface')
                func = function('set_local_interface', disable=True)
            elif state == 'default':
                cmds.append('default local-interface')
                func = function('set_local_interface', value='Vlan1234',
                                default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_peer_address(self):
        for state in ['config', 'negate', 'default']:
            cmds = ['mlag configuration']
            if state == 'config':
                cmds.append('peer-address 1.2.3.4')
                func = function('set_peer_address', '1.2.3.4')
            elif state == 'negate':
                cmds.append('no peer-address')
                func = function('set_peer_address', disable=True)
            elif state == 'default':
                cmds.append('default peer-address')
                func = function('set_peer_address', value='1.2.3.4',
                                default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_peer_link(self):
        for state in ['config', 'negate', 'default']:
            cmds = ['mlag configuration']
            if state == 'config':
                cmds.append('peer-link Ethernet1')
                func = function('set_peer_link', 'Ethernet1')
            elif state == 'negate':
                cmds.append('no peer-link')
                func = function('set_peer_link', disable=True)
            elif state == 'default':
                cmds.append('default peer-link')
                func = function('set_peer_link', value='Ethernet1',
                                default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_shutdown(self):
        for state in ['config', 'negate', 'default']:
            cmds = ['mlag configuration']
            if state == 'config':
                cmds.append('shutdown')
                func = function('set_shutdown', default=False, disable=False)
            elif state == 'negate':
                cmds.append('no shutdown')
                func = function('set_shutdown', disable=True)
            elif state == 'default':
                cmds.append('default shutdown')
                func = function('set_shutdown', default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_mlag_id(self):
        for state in ['config', 'negate', 'default']:
            if state == 'config':
                cmds = ['interface Ethernet1', 'mlag 1']
                func = function('set_mlag_id', 'Ethernet1', '1')
            elif state == 'negate':
                cmds = ['interface Ethernet1', 'no mlag']
                func = function('set_mlag_id', 'Ethernet1', disable=True)
            elif state == 'default':
                cmds = ['interface Ethernet1', 'default mlag']
                func = function('set_mlag_id', 'Ethernet1', value='1',
                                default=True)
            self.eapi_positive_config_test(func, cmds)


if __name__ == '__main__':
    unittest.main()
