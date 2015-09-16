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

from testlib import get_fixture, random_vlan, random_string, function
from testlib import EapiConfigUnitTest

import pyeapi.api.bgp

class TestApiBgp(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestApiBgp, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.bgp.instance(None)
        self.config = open(get_fixture('running_config.bgp')).read()

    def test_get(self):
        result = self.instance.get()
        keys = ['bgp_as', 'router_id', 'maximum_paths', 'maximum_ecmp_paths',
                'shutdown', 'neighbors', 'networks']
        self.assertEqual(sorted(keys), sorted(result.keys()))

    def test_create(self):
        for bgpas in ['65000', 65000]:
            func = function('create', bgpas)
            cmds = 'router bgp {}'.format(bgpas)
            self.eapi_positive_config_test(func, cmds)

    def test_create_invalid_as(self):
        for bgpas in ['66000', 66000]:
            with self.assertRaises(ValueError):
                self.instance.create(bgpas)

    def test_delete(self):
        func = function('delete')
        cmds = 'no router bgp 65000'
        self.eapi_positive_config_test(func, cmds)

    def test_default(self):
        func = function('default')
        cmds = 'default router bgp 65000'
        self.eapi_positive_config_test(func, cmds)

    def test_add_network(self):
        func = function('add_network', '172.16.10.1', '24', 'test')
        cmds = ['router bgp 65000', 'network 172.16.10.1/24 route-map test']
        self.eapi_positive_config_test(func, cmds)

    def test_remove_network(self):
        func = function('remove_network', '172.16.10.1', '24', 'test')
        cmds = ['router bgp 65000', 'no network 172.16.10.1/24 route-map test']
        self.eapi_positive_config_test(func, cmds)

    def test_set_router_id(self):
        for state in ['config', 'negate', 'default']:
            rid = '1.1.1.1'
            if state == 'config':
                cmds = ['router bgp 65000', 'router-id 1.1.1.1']
                func = function('set_router_id', rid)
            elif state == 'negate':
                cmds = ['router bgp 65000', 'no router-id']
                func = function('set_router_id')
            elif state == 'default':
                cmds = ['router bgp 65000', 'default router-id']
                func = function('set_router_id', rid, True)
            self.eapi_positive_config_test(func, cmds)

    def test_maximum_paths_just_max_path(self):
        for state in ['config', 'default']:
            max_paths = 20
            if state == 'config':
                cmds = ['router bgp 65000', 'maximum-paths 20']
                func = function('set_maximum_paths', max_paths)
            elif state == 'default':
                cmds = ['router bgp 65000', 'default maximum-paths']
                func = function('set_maximum_paths', default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_maximum_paths_max_path_and_ecmp(self):
        for state in ['config', 'default']:
            max_paths = 20
            max_ecmp_path = 20
            if state == 'config':
                cmds = ['router bgp 65000', 'maximum-paths 20 ecmp 20']
                func = function('set_maximum_paths', max_paths, max_ecmp_path)
            elif state == 'default':
                cmds = ['router bgp 65000', 'default maximum-paths']
                func = function('set_maximum_paths', default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_shutdown(self):
        for state in ['config', 'negate', 'default']:
            if state == 'config':
                cmds = ['router bgp 65000', 'shutdown']
                func = function('set_shutdown', True)
            elif state == 'negate':
                cmds = ['router bgp 65000', 'no shutdown']
                func = function('set_shutdown')
            elif state == 'default':
                cmds = ['router bgp 65000', 'default shutdown']
                func = function('set_shutdown', False, True)
            self.eapi_positive_config_test(func, cmds)

class TestApiBgpNeighbor(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestApiBgpNeighbor, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.bgp.BgpNeighbors(None)
        self.config = open(get_fixture('running_config.bgp')).read()

    def test_getall(self):
        result = self.instance.getall()
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 3)

    def test_get(self):
        result = self.instance.get('test')
        keys = ['name', 'send_community', 'shutdown', 'description',
                'remote_as', 'next_hop_self', 'route_map_in', 'route_map_out',
                'peer_group']
        self.assertEqual(sorted(keys), sorted(result.keys()))

    def test_delete(self):
        cmds = ['router bgp 65000', 'no neighbor test']
        func = function('delete', 'test')
        self.eapi_positive_config_test(func, cmds)

    def test_set_peer_group(self):
        for state in ['config', 'negate', 'default']:
            peer_group = 'test'
            name = '172.16.10.1'
            cmd = 'neighbor {} peer-group'.format(name)
            if state == 'config':
                cmds = ['router bgp 65000', '{} {}'.format(cmd, peer_group)]
                func = function('set_peer_group', name, peer_group)
            elif state == 'negate':
                cmds = ['router bgp 65000', 'no {}'.format(cmd)]
                func = function('set_peer_group', name)
            elif state == 'default':
                cmds = ['router bgp 65000', 'default {}'.format(cmd)]
                func = function('set_peer_group', name, peer_group, True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_remote_as(self):
        for state in ['config', 'negate', 'default']:
            remote_as = '65000'
            name = 'test'
            cmd = 'neighbor {} remote-as'.format(name)
            if state == 'config':
                cmds = ['router bgp 65000', '{} {}'.format(cmd, remote_as)]
                func = function('set_remote_as', name, remote_as)
            elif state == 'negate':
                cmds = ['router bgp 65000', 'no {}'.format(cmd)]
                func = function('set_remote_as', name)
            elif state == 'default':
                cmds = ['router bgp 65000', 'default {}'.format(cmd)]
                func = function('set_remote_as', name, remote_as, True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_shutdown(self):
        for state in ['config', 'negate', 'default']:
            name = 'test'
            cmd = 'neighbor {}'.format(name)
            if state == 'config':
                cmds = ['router bgp 65000', '{} shutdown'.format(cmd)]
                func = function('set_shutdown', name, True)
            elif state == 'negate':
                cmds = ['router bgp 65000', 'no {} shutdown'.format(cmd)]
                func = function('set_shutdown', name)
            elif state == 'default':
                cmds = ['router bgp 65000', 'default {} shutdown'.format(cmd)]
                func = function('set_shutdown', name, False, True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_send_community(self):
        for state in ['config', 'negate', 'default']:
            name = 'test'
            cmd = 'neighbor {}'.format(name)
            if state == 'config':
                cmds = ['router bgp 65000', '{} send-community'.format(cmd)]
                func = function('set_send_community', name, True)
            elif state == 'negate':
                cmds = ['router bgp 65000', 'no {} send-community'.format(cmd)]
                func = function('set_send_community', name)
            elif state == 'default':
                cmds = ['router bgp 65000', 'default {} send-community'.format(cmd)]
                func = function('set_send_community', name, False, True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_next_hop_self(self):
        for state in ['config', 'negate', 'default']:
            name = 'test'
            cmd = 'neighbor {}'.format(name)
            if state == 'config':
                cmds = ['router bgp 65000', '{} next-hop-self'.format(cmd)]
                func = function('set_next_hop_self', name, True)
            elif state == 'negate':
                cmds = ['router bgp 65000', 'no {} next-hop-self'.format(cmd)]
                func = function('set_next_hop_self', name)
            elif state == 'default':
                cmds = ['router bgp 65000', 'default {} next-hop-self'.format(cmd)]
                func = function('set_next_hop_self', name, False, True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_route_map_in(self):
        for state in ['config', 'negate', 'default']:
            route_map = 'TEST_RM'
            name = 'test'
            cmd = 'neighbor {} route-map'.format(name)
            if state == 'config':
                cmds = ['router bgp 65000', '{} {} in'.format(cmd, route_map)]
                func = function('set_route_map_in', name, route_map)
            elif state == 'negate':
                cmds = ['router bgp 65000', 'no {} in'.format(cmd)]
                func = function('set_route_map_in', name)
            elif state == 'default':
                cmds = ['router bgp 65000', 'default {} in'.format(cmd)]
                func = function('set_route_map_in', name, route_map, True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_route_map_out(self):
        for state in ['config', 'negate', 'default']:
            route_map = 'TEST_RM'
            name = 'test'
            cmd = 'neighbor {} route-map'.format(name)
            if state == 'config':
                cmds = ['router bgp 65000', '{} {} out'.format(cmd, route_map)]
                func = function('set_route_map_out', name, route_map)
            elif state == 'negate':
                cmds = ['router bgp 65000', 'no {} out'.format(cmd)]
                func = function('set_route_map_out', name)
            elif state == 'default':
                cmds = ['router bgp 65000', 'default {} out'.format(cmd)]
                func = function('set_route_map_out', name, route_map, True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_description(self):
        for state in ['config', 'negate', 'default']:
            value = 'this is a test'
            name = 'test'
            cmd = 'neighbor {} description'.format(name)
            if state == 'config':
                cmds = ['router bgp 65000', '{} {}'.format(cmd, value)]
                func = function('set_description', name, value)
            elif state == 'negate':
                cmds = ['router bgp 65000', 'no {}'.format(cmd)]
                func = function('set_description', name)
            elif state == 'default':
                cmds = ['router bgp 65000', 'default {}'.format(cmd)]
                func = function('set_description', name, value, True)
            self.eapi_positive_config_test(func, cmds)


if __name__ == '__main__':
    unittest.main()
