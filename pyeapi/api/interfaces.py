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
"""Module for working with interfaces in EOS

This module provides an API for pragmatically working with EOS interface
configurations.  Interfaces include any data or management plane interface
available in EOS.

Parameters:
    name (string): The name of the interface the configuration should be
        applied to.  The interface name is the full interface identifier.

    shutdown (boolean): True if the interface is administratively disabled,
        and False if the interface is administratively enable.  This value
        does not validate the interfaces operational state.

    description (string): The interface description string.  This value is
        an arbitrary operator defined value.

    sflow (boolean): True if sflow is enabled on the interface otherwise
        False

    flowcontrol_send (string): The flowcontrol send configuration value for
        the interface.  Valid values are on or off

    flowcontrol_receive (string): The flowcontrol receive configuration value
        for the interface.  Valid values are on or off

"""

import re

from pyeapi.api import EntityCollection
from pyeapi.utils import ProxyCall

DESCRIPTION_RE = re.compile(r'(?<=\s{3}description\s)(?P<value>.+)$', re.M)
SHUTDOWN_RE = re.compile(r'\s{3}(no\sshutdown)$', re.M)
SFLOW_RE = re.compile(r'(\s{3}no sflow)', re.M)
FLOWC_TX_RE = re.compile(r'(?<=\s{3}flowcontrol\ssend\s)(?P<value>.+)$', re.M)
FLOWC_RX_RE = re.compile(r'(?<=\s{3}flowcontrol\sreceive\s)(?P<value>.+)$',
                         re.M)

INSTANCE_METHODS = ['create', 'delete', 'default']

def isvalidinterface(value):
    matches = ['Ethernet', 'Management', 'Loopback', 'Port-Channel',
               'Vlan', 'Vxlan']
    match = re.match(r'([EPVLM][a-z-C]+)', value)
    if match:
        return match.group() in matches
    else:
        return False


class Interfaces(EntityCollection):

    def __init__(self, node, *args, **kwargs):
        super(Interfaces, self).__init__(node, *args, **kwargs)
        self._instances = dict()

    def get(self, name):
        return self.get_instance(name)[name]

    def getall(self):
        """Returns all interfaces in a dict object.

        Example:
            {
                "Ethernet1": {...},
                "Ethernet2": {...}
            }

        Returns:
            A Python dictionary object containing all interface
                configuration indexed by interface name
        """
        interfaces_re = re.compile(r'(?<=^interface\s)(.+)$', re.M)

        response = dict()
        for name in interfaces_re.findall(self.config):
            interface = self.get(name)
            if interface:
                response[name] = interface
        return response

    def __getattr__(self, name):
        if name.startswith('set_') or name in INSTANCE_METHODS:
            return ProxyCall(self.marshall, name)

    def get_instance(self, interface):
        cls = INTERFACE_CLASS_MAP.get(interface[0:2]) or BaseInterface
        if cls in self._instances:
            instance = self._instances[cls]
        else:
            instance = cls(self.node)
            self._instances[cls] = instance
        return instance

    def marshall(self, name, *args, **kwargs):
        interface = args[0]
        if not isvalidinterface(interface):
            raise ValueError('invalid interface {}'.format(interface))

        instance = self.get_instance(interface)
        method = getattr(instance, name)
        return method(*args, **kwargs)

class BaseInterface(EntityCollection):

    def get(self, name):
        config = self.get_block('^interface %s' % name)

        if not config:
            return None

        response = dict(name=name, type='generic')
        response['shutdown'] = SHUTDOWN_RE.search(config) is None

        value = lambda x, y: x.group('value') if x else y
        response['description'] = value(DESCRIPTION_RE.search(config), '')

        return response

    def create(self, name):
        """Creates a new interface on the node

        Note:
            This method will attempt to create the interface regardless
            if the interface exists or not.  If the interface already exists
            then this method will still return True

        Args:
            name (string): The full name of the interface.

        Returns:
            True if the interface could be created otherwise False (see Note)

        """
        return self.configure('interface %s' % name)

    def delete(self, name):
        """Deletes the interface from the node

        Note:
            This method will attempt to delete the interface from the nodes
            operational config.  If the interface does not exist then this
            method will not perform any changes but still return True

        Args:
            name (string): The full name of the interface

        Returns:
            True if the interface could be deleted otherwise False (see Node)

        """
        return self.configure('no interface %s' % name)

    def default(self, name):
        """Defaults an interface in the running configuration

        Args:
            name (string): The full name of the interface

        Returns:
            True if the command operation succeeds otherwise False
        """
        return self.configure('default interface %s' % name)

    def set_description(self, name, value=None, default=False):
        """Configures the interface description

        Args:
            name (string): The interface identifier.  It must be a full interface
               name (ie Ethernet, not Et)

            value (string): The value to set the description to.

            default (boolean): Specifies to default the interface description

        Returns:
            True if the operation succeeds otherwise Fals is returned
        """
        commands = ['interface %s' % name]
        if default:
            commands.append('default description')
        elif value is not None:
            commands.append('description %s' % value)
        else:
            commands.append('no description')
        return self.configure(commands)

    def set_shutdown(self, name, value=None, default=False):
        """Configures the interface shutdown state

        Args:
            name (string): The interface identifier.  It must be a full interface
                name (ie Ethernet, not Et)

            value (boolean): True if the interface should be in shutdown state
                otherwise False

            default (boolean): Specifies to default the interface description

        Returns:
            True if the operation succeeds otherwise Fals is returned
        """
        if value not in [True, False, None]:
            raise ValueError('invalid value for shutdown')

        commands = ['interface %s' % name]
        if default:
            commands.append('default shutdown')
        elif value:
            commands.append('shutdown')
        else:
            commands.append('no shutdown')
        return self.configure(commands)

class EthernetInterface(BaseInterface):

    def get(self, name):
        """Returns an interface as a set of key/value pairs

        Example:
            {
                "name": <string>,
                "type": "ethernet",
                "sflow": [true, false],
                "flowcontrol_send": [on, off],
                "flowcontrol_receive": [on, off]
            }

        Args:
            name (string): the interface identifier to retrive the from
                the configuration

        Returns:
            A Python dictionary object of key/value pairs that respresent
            the current configuration for the specified node.  If the
            specified interface name does not exist, then None is returned.
        """
        config = self.get_block('^interface %s' % name)

        if not config:
            return None

        response = super(EthernetInterface, self).get(name)
        response.update(dict(name=name, type='ethernet'))

        value = lambda x, y: x.group('value') if x else y

        response['sflow'] = SFLOW_RE.search(config) is None

        response['flowcontrol_send'] = value(FLOWC_TX_RE.search(config),
                                             'off')
        response['flowcontrol_receive'] = value(FLOWC_RX_RE.search(config),
                                                'off')
        return response

    def create(self, name):
        """Creating Ethernet interfaces is currently not supported

        Args:
            name (string): The interface name

        Raises:
            NotImplementedError: creating Ethernet interfaces is not supported

        """
        raise NotImplementedError('creating Ethernet interfaces is '
                                  'not supported')

    def delete(self, name):
        """Deleting Ethernet interfaces is currently not supported

        Args:
            name (string): The interface name

        Raises:
            NotImplementedError: Deleting  Ethernet interfaces is not supported

        """
        raise NotImplementedError('deleting Ethernet interfaces is '
                                  'not supported')

    def set_flowcontrol_send(self, name, value=None, default=False):
        """Configures the interface flowcontrol send value

        Args:
            name (string): The interface identifier.  It must be a full interface
               name (ie Ethernet, not Et)

            direction (string): one of either 'send' or 'receive'

            value (boolean): True if the interface should be in shutdown state
                          otherwise False
            default (boolean): Specifies to default the interface description

        Returns:
            True if the operation succeeds otherwise Fals is returned

        """
        return self.set_flowcontrol(name, 'send', value, default)

    def set_flowcontrol_receive(self, name, value=None, default=False):
        """Configures the interface flowcontrol receive value

        Args:
            name (string): The interface identifier.  It must be a full interface
               name (ie Ethernet, not Et)

            value (boolean): True if the interface should be in shutdown state
                          otherwise False

            default (boolean): Specifies to default the interface description

        Returns:
            True if the operation succeeds otherwise Fals is returned

        """
        return self.set_flowcontrol(name, 'receive', value, default)

    def set_flowcontrol(self, name, direction, value=None, default=False):
        """Configures the interface flowcontrol value

        Args:
            name (string): The interface identifier.  It must be a full interface
               name (ie Ethernet, not Et)

            direction (string): one of either 'send' or 'receive'

            value (boolean): True if the interface should be in shutdown state
                          otherwise False

            default (boolean): Specifies to default the interface description

        Returns:
            True if the operation succeeds otherwise Fals is returned

        """
        if value is not None:
            if value not in ['on', 'off']:
                raise ValueError('invalid flowcontrol value')

        if direction not in ['send', 'receive']:
            raise ValueError('invalid direction specified')

        commands = ['interface %s' % name]
        if default:
            commands.append('default flowcontrol %s' % direction)
        elif value:
            commands.append('flowcontrol %s %s' % (direction, value))
        else:
            commands.append('no flowcontrol %s' % direction)
        return self.configure(commands)

    def set_sflow(self, name, value=None, default=False):
        """Configures the sflow state on the interface

        Args:
            name (string): The interface identifier.  It must be a full interface
               name (ie Ethernet, not Et)

            value (boolean): True if sflow should be enabled otherwise False

            default (boolean): Specifies the default value for sflow

        Returns:
            True if the operation succeeds otherwise Fals is returned

        """
        if value not in [True, False, None]:
            raise ValueError

        commands = ['interface %s' % name]
        if default:
            commands.append('default sflow')
        elif value:
            commands.append('sflow enable')
        else:
            commands.append('no sflow enable')
        return self.configure(commands)


INTERFACE_CLASS_MAP = {
    'Et': EthernetInterface
}


def instance(api):
    return Interfaces(api)




