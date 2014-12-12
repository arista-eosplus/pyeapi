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

class Stp(object):

    def __init__(self, api):
        self.api = api
        self._interfaces = None
        self._instances = None

    def get(self):
        """Returns the spanning-tree configuration as a dict object

        The dictionary object represents the entire spanning-tree
        configuration derived from the nodes running config.  This
        includes both globally configuration attributes as well as
        interfaces and instances.  See the StpInterfaces and StpInstances
        classes for the key/value pair definitions.

        Example
            {
                "mode": [mstp, none],
                "interfaces": {...},
                "instances": {...}
            }

        Returns
            object: an instance of Stp
        """
        return dict(interfaces=self.interfaces.getall(),
                    instances=self.instances.getall())

    @property
    def interfaces(self):
        if self._interfaces is not None:
            return self._interfaces
        self._interfaces = StpInterfaces(self.api)
        return self._interfaces

# TODO: implement the StpInstances class
#    @property
#    def instances(self):
#        if self._instances is not None:
#            return self._instances
#        self._instances = StpInstances(self.api)
#        return self._instances

    def set_mode(self, value):
        if value not in ['mstp', 'none']:
            raise TypeError("Specified value must be one of ['mstp', 'none']")
        return self.api.config('spanning-tree mode %s' % value) == [{}]


class StpInterfaces(object):

    def __init__(self, api):
        self.api = api

    def _get_interface(self, name):
        result = self.api.enable('show running-config section %s' % name,
                                 'text')
        output = result[0]['output']
        resp = dict(bpduguard=False, portfast=False)

        if 'spanning-tree bpduguard enable' in output:
            resp['bpduguard'] = True
        else:
            resp['bpduguard'] = False

        if 'spanning-tree portfast network' in output:
            resp['portfast'] = 'network'
        elif 'spanning-tree portfast\n' in output:
            resp['portfast'] = 'edge'
        else:
            resp['portfast'] = 'disabled'

        return resp

    def getall(self):
        result = self.api.enable('show interfaces')
        resp = dict()
        for key, value in result[0]['interfaces'].items():
            if key.startswith('Et') and value['forwardingModel'] == 'bridged':
                resp[key] = self._get_interface(key)
        return resp

    def set_portfast(self, name, value=None, default=False):
        commands = ['interface %s' % name]
        if default:
            commands.append('default spanning-tree portfast')
        elif value in [None, 'disable']:
            commands.append('no spanning-tree portfast')
        else:
            commands.append('spanning-tree portfast %s' % value)
        return self.api.config(commands) == [{}, {}]

    def set_bpduguard(self, name, value=None, default=False):
        commands = ['interface %s' % name]
        if default:
            commands.append('default spanning-tree bpdugard')
        elif value is None:
            commands.append('no spanning-tree bpduguard')
        else:
            value = 'enable' if value else 'disable'
            commands.append('spanning-tree bpduguard %s' % value)
        return self.api.config(commands) == [{}, {}]


def instance(api):
    return Stp(api)
