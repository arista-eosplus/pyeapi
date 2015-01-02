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

DESCRIPTION_RE = re.compile(r'(?<=\s{3}description\s)(?P<value>.+)$', re.M)
SHUTDOWN_RE = re.compile(r'\s{3}(no\sshutdown)$', re.M)
SFLOW_RE = re.compile(r'(\s{3}no sflow)', re.M)
FLOWC_TX_RE = re.compile(r'(?<=\s{3}flowcontrol\ssend\s)(?P<value>.+)$', re.M)
FLOWC_RX_RE = re.compile(r'(?<=\s{3}flowcontrol\sreceive\s)(?P<value>.+)$', re.M)

class Interfaces(object):

    def __init__(self, api):
        self.api = api

    def get(self, name):
        """Returns an interface as a set of key/value pairs

        Example:
            {
                "name": <string>,
                "shutdown": [true, false],
                "description": <string>,
                "sflow": [true, false],
                "flowcontrol_send": [on, off],
                "flowcontrol_receive": [on, off]
            }

        Args:
            name (string): the iterface identifier to retrive the from
                the configuration

        Returns:
            dict: a dict of key/value pairs that represent the current
                running configuration from the node.  Returns None if
                the specified interface is not found in the current
                configuration
        """
        config = self.api.running_config.get_block('interface %s' % name)
        if not config:
            return None

        response = dict(name=name)
        response['shutdown'] = SHUTDOWN_RE.search(config) is None
        response['sflow'] = SFLOW_RE.search(config) is None

        value = lambda x, y: x.group('value') if x else y

        response['description'] = value(DESCRIPTION_RE.search(config), '')

        response['flowcontrol_send'] = value(FLOWC_TX_RE.search(config),
                                             'off')

        response['flowcontrol_receive'] = value(FLOWC_RX_RE.search(config),
                                                'off')

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
        interfaces_re = re.compile('(?<=^interface\s)(.+)$', re.M)

        response = dict()
        for name in interfaces_re.findall(self.api.running_config.text):
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




