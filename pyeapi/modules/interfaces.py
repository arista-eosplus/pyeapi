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
import shlex

INTF_RE = re.compile(r'(?P<name>[a-zA-Z]*)(?P<index>.*)$')

class Interfaces(object):

    def __init__(self, api):
        self.api = api

    def _parse_interface(self, interface):
        """Returns an interface as a set of key/value pairs

        Example:
            {
                "description": <string>
                "shutdown": [true, false],
                "sflow": [true, false]
            }

        Args:
            interface (dict): set of attributes returned from eAPI command
                              "show interface <name>"

        Returns:
            dict: A dict object containing the interface key/value pairs
        """
        response = dict()
        response['description'] = interface['description']
        response['shutdown'] = interface['interfaceStatus'] == 'disabled'
        response['sflow'] = self._get_sflow_for(interface['name'])
        return response

    def _get_sflow_for(self, name):
        result = self.api.enable('show running-config interfaces %s' % name,
                                 'text')
        return 'no sflow enable' not in result[0]['output']


    def _parse_flowcontrol(self, name, flowcontrol):
        response = {}
        for line in flowcontrol.split('\n')[3:]:
            tokens = shlex.split(line)
            if tokens:
                if tokens[0] == name:
                    return (tokens[1], tokens[3])
        return (None, None)

    def _get_flowcontrol_for(self, name, flowcontrol):
        match = INTF_RE.match(name)
        if not match:
            return (None, None)

        idx = match.group('index')
        shortname = name[0:2] + idx
        if shortname not in flowcontrol:
            return (None, None)

        return self._parse_flowcontrol(shortname, flowcontrol)

    def get(self, name):
        """Returns a single interface attribute dict as a set of
        key/value pairs

        The interface attributes are parsed with _parse_get function

        Example
            {
                "Ethernet1": {...}
            }

        Args:
            name (str): the name of the interface to retieve from
                        the running-config

        Returns:
            dict: a dict object that represents the single interface
        """
        interface = self.api.enable('show interfaces')
        interface = interface[0]['interfaces'][name]

        flowcontrol = self.api.enable('show interfaces flowcontrol', 'text')
        flowcontrol = flowcontrol[0]['output']

        response = self._parse_interface(interface)
        (tx, rx) = self._get_flowcontrol_for(name, flowcontrol)
        response['flowcontrol_send'] = tx
        response['flowcontrol_receive'] = rx

        return response

    def getall(self):
        """Returns all interfaces in a dict object.

        The interface attributes are parsed with _parse_get function

        Example:
            {
                "Ethernet1": {...},
                "Ethernet2": {...}
            }

        Returns:
            dict: a dict object containing all interfaces and attributes
        """
        interfaces = self.api.enable('show interfaces')
        interfaces = interfaces[0]['interfaces']

        flowcontrol = self.api.enable('show interfaces flowcontrol', 'text')
        flowcontrol = flowcontrol[0]['output']

        response = dict()
        for name in interfaces:
            response[name] = self._parse_interface(interfaces[name])
            (tx, rx) = self._get_flowcontrol_for(name, flowcontrol)
            response[name]['flowcontrol_send'] = tx
            response[name]['flowcontrol_receive'] = rx

        return response

    def create(self, id):
        """Creates a new interface in EOS

        Args:
            id (str): The interface identifier.  It must be a full interface
                      name (ie Ethernet, not Et)

        Returns:
            bool: True if the create operation succeeds otherwise False
        """
        if id[0:2].upper() in ['ET', 'MA']:
            return False
        return self.api.config('interface %s' % id) == [{}]

    def delete(self, id):
        """Deletes an interface from the running configuration

        Args:
            id (str): The interface identifier.  It must be a full interface
                      name (ie Ethernet, not Et)

        Returns:
            bool: True if the delete operation succeeds otherwise False
        """
        if id[0:2].upper() in ['ET', 'MA']:
            return False
        return self.api.config('no interface %s' % id) == [{}]

    def default(self, id):
        """Defaults an interface in the running configuration

        Args:
            id (str): The interface identifier.  It must be a full interface
                      name (ie Ethernet, not Et)

        Returns:
            bool: True if the default operation succeeds otherwise False
        """
        return self.api.config('default interface %s' % id) == [{}]

    def set_description(self, id, value=None, default=False):
        """Configures the interface description

        Args:
            id (str): The interface identifier.  It must be a full interface
                      name (ie Ethernet, not Et)
            value (str): The value to set the description to.
            default (bool): Specifies to default the interface description

        Returns:
            bool: True if the delete operation succeeds otherwise False
        """
        commands = ['interface %s' % id]
        if default:
            commands.append('default description')
        elif value is not None:
            commands.append('description %s' % value)
        else:
            commands.append('no description')
        return self.api.config(commands) == [{}, {}]

    def set_shutdown(self, id, value=None, default=False):
        """Configures the interface shutdown state

        Args:
            id (str): The interface identifier.  It must be a full interface
                      name (ie Ethernet, not Et)
            value (bool): True if the interface should be in shutdown state
                          otherwise False
            default (bool): Specifies to default the interface description

        Returns:
            bool: True if the delete operation succeeds otherwise False
        """
        commands = ['interface %s' % id]
        if default:
            commands.append('default shutdown')
        elif value:
            commands.append('shutdown')
        else:
            commands.append('no shutdown')
        return self.api.config(commands) == [{}, {}]

    def set_flowcontrol(self, id, direction, value=None, default=False):
        """Configures the interface flowcontrol value

        Args:
            id (str): The interface identifier.  It must be a full interface
                      name (ie Ethernet, not Et)
            direction (str): one of either 'send' or 'receive'
            value (bool): True if the interface should be in shutdown state
                          otherwise False
            default (bool): Specifies to default the interface description

        Returns:
            bool: True if the delete operation succeeds otherwise False
        """
        if direction not in ['send', 'receive']:
            return False
        commands = ['interface %s' % id]
        if default:
            commands.append('default flowcontrol %s' % direction)
        elif value:
            commands.append('flowcontrol %s %s' % (direction, value))
        else:
            commands.append('no flowcontrol %s' % direction)
        return self.api.config(commands) == [{}, {}]

    def set_sflow(self, id, value=None, default=False):
        """Configures the sflow state on the interface

        Args:
            id (str): The interface identifier.  It must be a full interface
                      name (ie Ethernet, not Et)
            value (bool): True if sflow should be enabled otherwise False
            default (bool): Specifies the default value for sflow

        Returns:
            bool: True if the command succeeds otherwise False
        """
        commands = ['interface %s' % id]
        if default:
            commands.append('default sflow')
        elif value:
            commands.append('sflow enable')
        else:
            commands.append('no sflow enable')
        return self.api.config(commands) == [{}, {}]



def instance(api):
    return Interfaces(api)




