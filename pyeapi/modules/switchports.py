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

MODE_RE = re.compile(r'(?<=Operational Mode:\s)(?P<mode>.*)')
ACCESS_VLAN_RE = re.compile(r'(?<=Access Mode VLAN:\s)(?P<access_vlan>\d+)')
TRUNK_VLAN_RE = re.compile(r'(?<=Trunking Native Mode VLAN:\s)'
                           r'(?P<trunk_vlan>\d+)')
TRUNKING_VLANS_RE = re.compile(r'(?<=Trunking VLANs Enabled:\s)'
                               r'(?P<trunking_vlans>.*)')

api = None

def get(name):
    """Returns a dictionary object that represents a switchport
    """
    result = api.enable('show interfaces %s switchport' % name, 'text')
    output = result[0]['output']

    data = dict(name=name)

    match = MODE_RE.search(output)
    data['mode'] = \
        'access' if match.group('mode') == 'static access' else 'trunk'

    data['access_vlan'] = \
        ACCESS_VLAN_RE.search(output).group('access_vlan')

    data['trunk_native_vlan'] = \
        TRUNK_VLAN_RE.search(output).group('trunk_vlan')

    data['trunk_allowed_vlans'] = \
        TRUNKING_VLANS_RE.search(output).group('trunking_vlans')

    return data

def getall():
    """Returns a dictionary object that represents all configured switchports
    found in the running-config
    """
    result = api.enable('show interfaces')
    response = dict()
    for key, value in result[0]['interfaces'].items():
        if value['forwardingModel'] == 'bridged':
            response[key] = get(key)
    return response

def create(name):
    return api.config(['interface %s' % name, 'no ip address']) == [{}, {}]

def delete(name):
    return api.config(['interface %s' % name, 'no switchport']) == [{}, {}]

def default(name):
    return api.config(['interface %s' % name, 'default switchport']) == [{}, {}]

def set_mode(name, value=None, default=False):
    commands = ['interface %s' % name]
    if default:
        commands.append('default switchport mode')
    elif value is None:
        commands.append('no switchport mode')
    else:
        commands.append('switchport mode %s' % value)
    return api.config(commands) == [{}, {}]

def set_access_vlan(name, value=None, default=False):
    commands = ['interface %s' % name]
    if default:
        commands.append('default switchport access vlan')
    elif value is None:
        commands.append('no switchport access vlan')
    else:
        commands.append('switchport access vlan %s' % value)
    return api.config(commands) == [{}, {}]

def set_trunk_native_vlan(name, value=None, default=False):
    commands = ['interface %s' % name]
    if default:
        commands.append('default switchport trunk native vlan')
    elif value is None:
        commands.append('no switchport trunk native vlan')
    else:
        commands.append('switchport trunk native vlan %s' % value)
    return api.config(commands) == [{}, {}]

def set_trunk_allowed_vlans(name, value=None, default=False):
    commands = ['interface %s' % name]
    if default:
        commands.append('default switchport trunk allowed vlan')
    elif value is None:
        commands.append('no switchport trunk allowed vlan')
    else:
        commands.append('switchport trunk allowed vlan %s' % value)
    return api.config(commands) == [{}, {}]
