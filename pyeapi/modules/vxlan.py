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

class Vxlan(object):

    def __init__(self, api):
        self.api = api

    def get(self):
        """Retrieves the vxlan interface from the running-config
        """
        result = self.api.enable('show interfaces vxlan1')
        result = result[0]['interfaces']['Vxlan1']
        return dict(name=result['name'],
                    multicast_group=result['floodMcastGrp'],
                    source_interface=result['srcIpIntf'])

    def create(self):
        """Creates a new vxlan interface instance
        """
        return self.api.config('interface vxlan1') == [{}]

    def delete(self):
        """Deletes the vxlan interface from the running configuration
        """
        return self.api.config('no interface vxlan1') == [{}]

    def default(self):
        """Defaults the vxlan interface in the running configuration
        """
        return self.api.config('default interface vxlan1') == [{}]

    def set_source_interface(self, value=None, default=False):
        """Configures the vlan source-interface value
        """
        commands = ['interface vxlan1']
        if default:
            commands.append('default vxlan source-interface')
        elif value is not None:
            commands.append('vxlan source-interface %s' % value)
        else:
            commands.append('no vxlan source-interface')
        return self.api.config(commands) == [{}, {}]

    def set_multicast_group(self, value=None, default=False):
        """Configures the vxlan interface multicast-group value
        """
        commands = ['interface vxlan1']
        if default:
            commands.append('default vxlan multicast-group')
        elif value:
            commands.append('vxlan multicast-group %s' % value)
        else:
            commands.append('no vxlan multicast-group')
        return self.api.config(commands) == [{}, {}]

def instance(api):
    return Vxlan(api)
