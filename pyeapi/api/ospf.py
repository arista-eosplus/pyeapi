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
'''
API module for Ospf
'''

import re

from pyeapi.api import Entity, EntityCollection
from pyeapi.utils import make_iterable


class Ospf(Entity):
    # The Ospf class implements global Ospf router configuration

    def __init__(self, *args, **kwargs):
        super(Ospf, self).__init__(*args, **kwargs)
        pass

    def get(self):
        # Returns the OSPF routing configuration as a dict object
        config = self.get_block('^router ospf .*')
        if not config:
            return None
    
        response = dict()
        response.update(self._parse_router_id(config))
        response.update(self._parse_networks(config))
        response.update(self._parse_ospf_process_id(config))
        response.update(self._parse_redistribution(config))
        response.update(self._parse_shutdown(config))

        return response

    def _parse_ospf_process_id(self, config):
        match = re.search(r'^router ospf (\d+)', config)
        return dict(ospf_process_id=int(match.group(1)))

    def _parse_router_id(self, config):
        match = re.search(r'router-id ([^\s]+)', config)
        value = match.group(1) if match else None
        return dict(router_id=value)

    def _parse_networks(self, config):
        networks = list()
        regexp = r'network (.+)/(\d+) area (\d+\.\d+\.\d+\.\d+)'
        matches = re.findall(regexp, config)
        for (network, netmask, area) in matches:
            networks.append(dict(network=network, netmask=netmask, area=area))
        return dict(networks=networks)

    def _parse_redistribution(self, config):
        redistributions = list()
        regexp = r'redistribute .*'
        matches = re.findall(regexp, config)
        for line in matches:
            ospf_redist = line.split()
            if len(ospf_redist) == 2:
                # simple redist: eg 'redistribute bgp'
                protocol = ospf_redist[1]
                redistributions.append(dict(protocol=protocol))
            if len(ospf_redist) == 4:
                # complex redist eg 'redistribute bgp route-map NYSE-RP-MAP'
                protocol = ospf_redist[1]
                route_map_name = ospf_redist[3]
                redistributions.append(dict(protocol=protocol, route_map=route_map_name))
        return dict(redistributions=redistributions)

    def _parse_shutdown(self, config):
        value = 'no shutdown' in config
        return dict(shutdown=not value)

    def set_shutdown(self):
        cmd = 'shutdown'
        return self.configure_ospf(cmd)

    def set_no_shutdown(self):
        cmd = 'no shutdown'
        return self.configure_ospf(cmd)

    def delete(self):
        config = self.get()
        if not config:
            return True
        command = 'no router ospf {}'.format(config['ospf_process_id'])
        return self.configure(command)

    def create(self, ospf_process_id):
        value = int(ospf_process_id)
        if not 0 < value < 65536:
            raise ValueError('ospf as must be between 1 and 65535')
        command = 'router ospf {}'.format(ospf_process_id)
        return self.configure(command)

    def configure_ospf(self, cmd):
        config = self.get()
        cmds = ['router ospf {}'.format(config['ospf_process_id'])]
        cmds.extend(make_iterable(cmd))
        return super(Ospf, self).configure(cmds)

    def set_router_id(self, value=None, default=False, disable=False):
        cmd = self.command_builder('router-id', value=value, default=default, disable=disable)
        return self.configure_ospf(cmd)
        
    def add_network(self, network, netmask, area=0):
        if network == '' or netmask == '':
            raise ValueError('network and mask values '
                             'may not be empty')
        cmd = 'network {}/{} area {}'.format(network, netmask, area)
        return self.configure_ospf(cmd)

    def remove_network(self, network, netmask, area=0):
        if network == '' or netmask == '':
            raise ValueError('network and mask values '
                             'may not be empty')
        cmd = 'no network {}/{} area {}'.format(network, netmask, area)
        return self.configure_ospf(cmd)

    def add_redistribution(self, protocol, route_map_name=None):
        protocols = ['bgp', 'rip', 'static', 'connected']
        if protocol not in protocols:
            raise ValueError('redistributed protocol must be'
                             'bgp, connected, rip or static')
        if route_map_name is None:
            cmd = 'redistribute {}'.format(protocol)
        else:
            cmd = 'redistribute {} route-map {}'.format(protocol, route_map_name)
        return self.configure_ospf(cmd)

    def remove_redistribution(self, protocol):
        protocols = ['bgp', 'rip', 'static', 'connected']
        if protocol not in protocols:
            raise ValueError('redistributed protocol must be'
                             'bgp, connected, rip or static')
        cmd = 'no redistribute {}'.format(protocol)        
        return self.configure_ospf(cmd)

def instance(api):
    return Ospf(api)
