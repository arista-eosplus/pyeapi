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

class Interfaces(object):

    def __init__(self, api):
        self.api = api

    def get(self, name):
        """Returns a single interface attribute dict as a set of
        key/value pairs

        The interface attributes are parsed with _parse_get function

        Example
            {
                "name": "Ethernet1",
                "description": <string>,
                "shutdown": [true, false],
                "sflow": [true, false],
                "flowcontrol_send": [on, off, desired],
                "flowcontrol_recieve": [on, off, desired]
            }

        Args:
            name (str): the name of the interface to retieve from
                        the running-config

        Returns:
            dict: a dict object that represents the single interface
        """
        config = self.api.running.get('interface %s' % name)
        config = '\n'.join(config)

        response = dict(name=name)

        # description
        match = re.search(r"(?<=\s{3}description\s)(.+)$", config, re.M)
        response['description'] = match.groups(1)[0] if match else ''

        # shutdown
        response['shutdown'] = 'no shutdown' in config

        # sflow
        response['sflow'] = 'no sflow' not in config

        # flowcontrol
        if name[0:2] in ['Et', 'Ma']:
            match = re.findall(r"(?<=flowcontrol\s)(send|receive)\s(.+)$",
                               config, re.M)

            send = receive = 'off'
            for token, value in match:
                if token == 'send':
                    send = value
                elif token == 'receive':
                    receive = value
        else:
            send = receive = 'unsupported'

        response['flowcontrol_send'] = send
        response['flowcontrol_receive'] = receive

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
        results  = self.api.enable('show interfaces')
        interfaces = results[0]['interfaces']

        response = dict()
        for name in interfaces:
            response[name] = self.get(name)

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




