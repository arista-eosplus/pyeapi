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
"""API module for Bgp
"""

import re

from collections import namedtuple

import netaddr

from pyeapi.api import Entity, EntityCollection
from pyeapi.utils import make_iterable

Network = namedtuple('Network', 'prefix length route_map')


class Bgp(Entity):
    """The Bgp class implements global BGP router configuration
    """

    def __init__(self, *args, **kwargs):
        super(Bgp, self).__init__(*args, **kwargs)
        self._neighbors = None

    @property
    def neighbors(self):
        if self._neighbors is not None:
            return self._neighbors
        self._neighbors = BgpNeighbors(self.node)
        return self._neighbors

    def get(self):
        """Returns the bgp routing configuration as a dict object
        """
        config = self.get_block('^router bgp .*')
        if not config:
            return None

        response = dict()
        response.update(self._parse_bgp_as(config))
        response.update(self._parse_router_id(config))
        response.update(self._parse_max_paths(config))
        response.update(self._parse_shutdown(config))
        response.update(self._parse_networks(config))

        response['neighbors'] = self.neighbors.getall()

        return response

    def _parse_bgp_as(self, config):
        match = re.search(r'^router bgp (\d+)', config)
        return dict(bgp_as=int(match.group(1)))

    def _parse_router_id(self, config):
        match = re.search(r'router-id ([^\s]+)', config)
        value = match.group(1) if match else None
        return dict(router_id=value)

    def _parse_max_paths(self, config):
        match = re.search(r'maximum-paths\s+(\d+)\s+ecmp\s+(\d+)', config)
        paths = int(match.group(1)) if match else None
        ecmp_paths = int(match.group(2)) if match else None
        return dict(maximum_paths=paths, maximum_ecmp_paths=ecmp_paths)

    def _parse_shutdown(self, config):
        value = 'no shutdown' in config
        return dict(shutdown=not value)

    def _parse_networks(self, config):
        networks = list()
        regexp = r'network (.+)/(\d+)(?: route-map (\w+))*'
        matches = re.findall(regexp, config)
        for (prefix, mask, rmap) in matches:
            rmap = None if rmap == '' else rmap
            networks.append(dict(prefix=prefix, masklen=mask, route_map=rmap))
        return dict(networks=networks)

    def configure_bgp(self, cmd):
        config = self.get()
        cmds = ['router bgp {}'.format(config['bgp_as'])]
        cmds.extend(make_iterable(cmd))
        return super(Bgp, self).configure(cmds)

    def create(self, bgp_as):
        value = int(bgp_as)
        if not 0 < value < 65536:
            raise ValueError('bgp as must be between 1 and 65535')
        command = 'router bgp {}'.format(bgp_as)
        return self.configure(command)

    def delete(self):
        config = self.get()
        if not config:
            return True
        command = 'no router bgp {}'.format(config['bgp_as'])
        return self.configure(command)

    def default(self):
        config = self.get()
        if not config:
            return True
        command = 'default router bgp {}'.format(config['bgp_as'])
        return self.configure(command)

    def set_router_id(self, value=None, default=False, disable=False):
        cmd = self.command_builder('router-id', value=value,
                                   default=default, disable=disable)
        return self.configure_bgp(cmd)

    def set_maximum_paths(self, max_path=None, max_ecmp_path=None,
                          default=False, disable=False):
        if not max_path and max_ecmp_path:
            raise TypeError('Cannot use maximum_ecmp_paths without '
                            'providing max_path')
        value = None
        if max_path:
            value = '{}'.format(max_path)
            if max_ecmp_path:
                value += ' ecmp {}'.format(max_ecmp_path)
        cmd = self.command_builder('maximum-paths', value=value,
                                   default=default, disable=disable)
        return self.configure_bgp(cmd)

    def set_shutdown(self, default=False, disable=True):
        # Default setting for BGP shutdown is disable=True,
        # meaning 'no shutdown'.
        # If both default and disable are false, BGP shutdown will
        # effectively be enabled.
        cmd = self.command_builder('shutdown', value=True, default=default,
                                   disable=disable)
        return self.configure_bgp(cmd)

    def add_network(self, prefix, length, route_map=None):
        if prefix == '' or length == '':
            raise ValueError('network prefix and length values '
                             'may not be empty')
        cmd = 'network {}/{}'.format(prefix, length)
        if route_map:
            cmd += ' route-map {}'.format(route_map)
        return self.configure_bgp(cmd)

    def remove_network(self, prefix, masklen, route_map=None):
        if prefix == '' or masklen == '':
            raise ValueError('network prefix and length values '
                             'may not be empty')
        cmd = 'no network {}/{}'.format(prefix, masklen)
        if route_map:
            cmd += ' route-map {}'.format(route_map)
        return self.configure_bgp(cmd)


class BgpNeighbors(EntityCollection):

    def get(self, name):
        config = self.get_block('^router bgp .*')
        response = dict(name=name)
        response.update(self._parse_peer_group(config, name))
        response.update(self._parse_remote_as(config, name))
        response.update(self._parse_send_community(config, name))
        response.update(self._parse_shutdown(config, name))
        response.update(self._parse_description(config, name))
        response.update(self._parse_next_hop_self(config, name))
        response.update(self._parse_route_map_in(config, name))
        response.update(self._parse_route_map_out(config, name))
        return response

    def getall(self):
        config = self.get_block('^router bgp .*')
        if not config:
            return None

        collection = dict()
        for neighbor in re.findall(r'neighbor ([^\s]+)', config):
            collection[neighbor] = self.get(neighbor)
        return collection

    def _parse_peer_group(self, config, name):
        if self.version_number >= '4.23':
            regexp = r'neighbor {} peer group ([^\s]+)'.format(name)
        else:
            regexp = r'neighbor {} peer-group ([^\s]+)'.format(name)
        match = re.search(regexp, config)
        value = match.group(1) if match else None
        return dict(peer_group=value)

    def _parse_remote_as(self, config, name):
        regexp = r'neighbor {} remote-as (\d+)'.format(name)
        match = re.search(regexp, config)
        value = match.group(1) if match else None
        return dict(remote_as=value)

    def _parse_send_community(self, config, name):
        exp = 'no neighbor {} send-community'.format(name)
        value = exp in config
        return dict(send_community=not value)

    def _parse_shutdown(self, config, name):
        regexp = r'(?<!no )neighbor {} shutdown'.format(name)
        match = re.search(regexp, config, re.M)
        value = True if match else False
        return dict(shutdown=value)

    def _parse_description(self, config, name):
        regexp = r'neighbor {} description (.*)$'.format(name)
        match = re.search(regexp, config, re.M)
        value = match.group(1) if match else None
        return dict(description=value)

    def _parse_next_hop_self(self, config, name):
        exp = 'no neighbor {} next-hop-self'.format(name)
        value = exp in config
        return dict(next_hop_self=not value)

    def _parse_route_map_in(self, config, name):
        regexp = r'neighbor {} route-map ([^\s]+) in'.format(name)
        match = re.search(regexp, config, re.M)
        value = match.group(1) if match else None
        return dict(route_map_in=value)

    def _parse_route_map_out(self, config, name):
        regexp = r'neighbor {} route-map ([^\s]+) out'.format(name)
        match = re.search(regexp, config, re.M)
        value = match.group(1) if match else None
        return dict(route_map_out=value)

    def ispeergroup(self, name):
        try:
            netaddr.IPAddress(name)
            return False
        except netaddr.core.AddrFormatError:
            return True

    def create(self, name):
        return self.set_shutdown(name, default=False, disable=False)

    def delete(self, name):
        response = self.configure('no neighbor {}'.format(name))
        if not response:
            if self.version_number >= '4.23':
                response = self.configure('no neighbor {} '
                                          'peer group'.format(name))
            else:
                response = self.configure('no neighbor {} '
                                          'peer-group'.format(name))
        return response

    def configure(self, cmd):
        match = re.search(r'router bgp (\d+)', self.config)
        if not match:
            raise ValueError('bgp is not configured')
        cmds = ['router bgp {}'.format(match.group(1)), cmd]
        return super(BgpNeighbors, self).configure(cmds)

    def command_builder(self, name, cmd, value, default, disable):
        string = 'neighbor {} {}'.format(name, cmd)
        return super(BgpNeighbors, self).command_builder(string, value,
                                                         default, disable)

    def set_peer_group(self, name, value=None, default=False, disable=False):
        if not self.ispeergroup(name):
            if self.version_number >= '4.23':
                cmd = self.command_builder(name, 'peer group', value, default,
                                           disable)
            else:
                cmd = self.command_builder(name, 'peer-group', value, default,
                                           disable)
            return self.configure(cmd)
        return False

    def set_remote_as(self, name, value=None, default=False, disable=False):
        cmd = self.command_builder(name, 'remote-as', value, default, disable)
        return self.configure(cmd)

    def set_shutdown(self, name, default=False, disable=True):
        # Default setting for BGP neighbor shutdown is
        # disable=True, meaning 'no shutdown'
        # If both default and disable are false, BGP neighbor shutdown will
        # effectively be enabled.
        cmd = self.command_builder(name, 'shutdown', True, default, disable)
        return self.configure(cmd)

    def set_send_community(self, name, value=None, default=False,
                           disable=False):
        cmd = self.command_builder(name, 'send-community', value, default,
                                   disable)
        return self.configure(cmd)

    def set_next_hop_self(self, name, value=None, default=False,
                          disable=False):
        cmd = self.command_builder(name, 'next-hop-self', value, default,
                                   disable)
        return self.configure(cmd)

    def set_route_map_in(self, name, value=None, default=False, disable=False):
        cmd = self.command_builder(name, 'route-map', value, default, disable)
        cmd += ' in'
        return self.configure(cmd)

    def set_route_map_out(self, name, value=None, default=False,
                          disable=False):
        cmd = self.command_builder(name, 'route-map', value, default, disable)
        cmd += ' out'
        return self.configure(cmd)

    def set_description(self, name, value=None, default=False, disable=False):
        cmd = self.command_builder(name, 'description', value, default,
                                   disable)
        return self.configure(cmd)


def instance(api):
    return Bgp(api)
