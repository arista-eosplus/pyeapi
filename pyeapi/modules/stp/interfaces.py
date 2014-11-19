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

api = None

SCANNERS = {
    'bpduguard': re.compile(r'(?<=bpduguard\s)(?P<value>enable)$'),
    'portfast': re.compile(r'(?<=spanning-tree\s)(?P<value>portfast)$')
}

def _get_interface(name):
    result = api.enable('show running-config section %s' % name, 'text')
    output = result[0]['output']
    resp = dict(bpduguard=False, portfast=False)

    for attr, regex in SCANNERS.items():
        match = regex.search(output)
        resp[attr] = match is not None

    return resp

def getall():
    result = api.enable('show interfaces')
    resp = dict()
    for key, value in result[0]['interfaces'].items():
        if key.startswith('Et') and value['forwardingModel'] == 'bridged':
            resp[key] = _get_interface(key)
    return resp

def set_portfast(name, value=None, default=False):
    commands = ['interface %s' % name]
    if default:
        commands.append('default spanning-tree portfast')
    elif value in [None, 'disable']:
        commands.append('no spanning-tree portfast')
    elif value is 'enable':
        commands.append('spanning-tree portfast')
    return api.config(commands) == [{}, {}]

def set_bpduguard(name, value=None, default=False):
    commands = ['interface %s' % name]
    if default:
        commands.append('default spanning-tree bpdugard')
    elif value is None:
        commands.append('no spanning-tree bpduguard')
    else:
        commands.append('spanning-tree bpduguard %s' % value)
    return api.config(commands) == [{}, {}]
