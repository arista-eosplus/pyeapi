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
import re

MODE_RE = re.compile(r'(?<=\s{3}switchport\smode\s)(?P<value>.+)$', re.M)
ACCESS_VLAN_RE = re.compile(r'(?<=\s{3}switchport\saccess\svlan\s)'
                            r'(?P<value>\d+)$', re.M)
TRUNK_VLAN_RE = re.compile(r'(?<=\s{3}switchport\strunk\snative\svlan\s)'
                           r'(?P<value>\d+)$', re.M)
TRUNKING_VLANS_RE = re.compile(r'(?<=\s{3}switchport\strunk\sallowed\svlan\s)'
                               r'(?P<value>.*)$', re.M)


class Switchports(object):

    def __init__(self, api):
        self.api = api


    def get(self, name):
        """Returns a dictionary object that represents a switchport

        Example
            {
                "name": <string>,
                "mode": [access, trunk],
                "access_vlan": <string>
                "trunk_native_vlan": <string>,
                "trunk_allowed_vlans": <string>
            }

        Args:
            name (string): The interface identifer to get.  Note: Switchports
                are only supported on Ethernet and Port-Channel interfaces

        Returns:
            dict: The current interface configuration attributes as a
                dict object
        """
        config = self.api.running_config.get_block('interface %s' % name)

        if not re.match('\s{3}no\sswitchport', config, re.M):
            resp = dict(name=name)
            resp['mode'] = MODE_RE.search(config, re.M).group('value')
            resp['access_vlan'] = ACCESS_VLAN_RE.search(config, re.M).group('value')
            resp['trunk_native_vlan'] = \
                 TRUNK_VLAN_RE.search(config, re.M).group('value')
            resp['trunk_allowed_vlans'] = \
                TRUNKING_VLANS_RE.search(config, re.M).group('value')
            return resp

    def getall(self):
        """Returns a dictionary object that represents all configured
        switchports found in the running-config
        """
        interfaces_re = re.compile('(?<=^interface\s)([Et|Po].+)$', re.M)

        response = dict()
        for name in interfaces_re.findall(self.api.running_config.text):
            interface = self.get(name)
            if interface:
                response[name] = interface
        return response

    def create(self, name):
        command = ['interface %s' % name, 'no ip address',
                   'default switchport']
        return self.api.config(command) == [{}, {}, {}]

    def delete(self, name):
        command = ['interface %s' % name, 'no switchport']
        return self.api.config(command) == [{}, {}]

    def default(self, name):
        command = ['interface %s' % name, 'no ip address',
                   'default switchport']
        return self.api.config(command) == [{}, {}, {}]

    def set_mode(self, name, value=None, default=False):
        commands = ['interface %s' % name]
        if default:
            commands.append('default switchport mode')
        elif value is None:
            commands.append('no switchport mode')
        else:
            commands.append('switchport mode %s' % value)
        return self.api.config(commands) == [{}, {}]

    def set_access_vlan(self, name, value=None, default=False):
        commands = ['interface %s' % name]
        if default:
            commands.append('default switchport access vlan')
        elif value is None:
            commands.append('no switchport access vlan')
        else:
            commands.append('switchport access vlan %s' % value)
        return self.api.config(commands) == [{}, {}]

    def set_trunk_native_vlan(self, name, value=None, default=False):
        commands = ['interface %s' % name]
        if default:
            commands.append('default switchport trunk native vlan')
        elif value is None:
            commands.append('no switchport trunk native vlan')
        else:
            commands.append('switchport trunk native vlan %s' % value)
        return self.api.config(commands) == [{}, {}]

    def set_trunk_allowed_vlans(self, name, value=None, default=False):
        commands = ['interface %s' % name]
        if default:
            commands.append('default switchport trunk allowed vlan')
        elif value is None:
            commands.append('no switchport trunk allowed vlan')
        else:
            commands.append('switchport trunk allowed vlan %s' % value)
        return self.api.config(commands) == [{}, {}]


def instance(api):
    return Switchports(api)
