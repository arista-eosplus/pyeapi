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

    sflow (boolean): True if sFlow is enabled on the interface otherwise
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
MIN_LINKS_RE = re.compile(r'(?<=\s{3}min-links\s)(?P<value>.+)$', re.M)

INSTANCE_METHODS = ['create', 'delete', 'default']

DEFAULT_LACP_MODE = 'on'

VALID_INTERFACES = frozenset([
    'Ethernet',
    'Management',
    'Loopback',
    'Port-Channel',
    'Vlan',
    'Vxlan',
])

def isvalidinterface(value):
    match = re.match(r'([EPVLM][a-z-C]+)', value)
    return match and match.group() in VALID_INTERFACES


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
        response['description'] = self.value(DESCRIPTION_RE.search(config), '')
        return response

    def value(self, match, default=None):
        return match.group('value') if match else default

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
            name (string): The interface identifier.  It must be a full
                interface name (ie Ethernet, not Et)

            value (string): The value to set the description to.

            default (boolean): Specifies to default the interface description

        Returns:
            True if the operation succeeds otherwise False is returned
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
            name (string): The interface identifier.  It must be a full
                interface name (ie Ethernet, not Et)

            value (boolean): True if the interface should be in shutdown state
                otherwise False

            default (boolean): Specifies to default the interface description

        Returns:
            True if the operation succeeds otherwise False is returned
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
            name (string): the interface identifier to retrieve the from
                the configuration

        Returns:
            A Python dictionary object of key/value pairs that represent
            the current configuration for the specified node.  If the
            specified interface name does not exist, then None is returned.
        """
        config = self.get_block('^interface %s' % name)

        if not config:
            return None

        response = super(EthernetInterface, self).get(name)
        response.update(dict(name=name, type='ethernet'))

        response['sflow'] = SFLOW_RE.search(config) is None

        flowc_tx = FLOWC_TX_RE.search(config)
        response['flowcontrol_send'] = self.value(flowc_tx, 'off')

        flowc_rx = FLOWC_RX_RE.search(config)
        response['flowcontrol_receive'] = self.value(flowc_rx, 'off')

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
            name (string): The interface identifier.  It must be a full
                interface name (ie Ethernet, not Et)

            direction (string): one of either 'send' or 'receive'

            value (boolean): True if the interface should be in shutdown state
                          otherwise False
            default (boolean): Specifies to default the interface description

        Returns:
            True if the operation succeeds otherwise False is returned
        """
        return self.set_flowcontrol(name, 'send', value, default)

    def set_flowcontrol_receive(self, name, value=None, default=False):
        """Configures the interface flowcontrol receive value

        Args:
            name (string): The interface identifier.  It must be a full
                interface name (ie Ethernet, not Et)

            value (boolean): True if the interface should be in shutdown state
                          otherwise False

            default (boolean): Specifies to default the interface description

        Returns:
            True if the operation succeeds otherwise False is returned
        """
        return self.set_flowcontrol(name, 'receive', value, default)

    def set_flowcontrol(self, name, direction, value=None, default=False):
        """Configures the interface flowcontrol value

        Args:
            name (string): The interface identifier.  It must be a full
                interface name (ie Ethernet, not Et)

            direction (string): one of either 'send' or 'receive'

            value (boolean): True if the interface should be in shutdown state
                          otherwise False

            default (boolean): Specifies to default the interface description

        Returns:
            True if the operation succeeds otherwise False is returned
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
        """Configures the sFlow state on the interface

        Args:
            name (string): The interface identifier.  It must be a full
                interface name (ie Ethernet, not Et)

            value (boolean): True if sFlow should be enabled otherwise False

            default (boolean): Specifies the default value for sFlow

        Returns:
            True if the operation succeeds otherwise False is returned
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

class PortchannelInterface(BaseInterface):

    def get(self, name):
        """Returns a Port-Channel interface as a set of key/value pairs

        Example:
            {
                "name": <string>,
                "type": "portchannel",
                "members": <arrary of interface names>,
                "minimum_links: <integer>,
                "lacp_mode": [on, active, passive]
            }

        Args:
            name (str): The interface identifier to retrieve from the
                running-configuration

        Returns:
            A Python dictionary object of key/value pairs that represents
                the interface configuration.  If the specified interface
                does not exist, then None is returned
        """
        config = self.get_block('^interface %s' % name)
        if not config:
            return None

        response = super(PortchannelInterface, self).get(name)
        response.update(dict(name=name, type='portchannel'))

        response['members'] = self.get_members(name)
        response['lacp_mode'] = self.get_lacp_mode(name)
        response['minimum_links'] = self.value(MIN_LINKS_RE.search(config), 0)
        return response

    def get_lacp_mode(self, name):
        """Returns the LACP mode for the specified Port-Channel interface

        Args:
            name(str): The Port-Channel interface name to return the LACP
                mode for from the configuration

        Returns:
            The configured LACP mode for the interface.  Valid mode values
                are 'on', 'passive', 'active'

        """
        members = self.get_members(name)
        if not members:
            return DEFAULT_LACP_MODE

        for member in self.get_members(name):
            match = re.search(r'channel-group\s\d+\smode\s(?P<value>.+)',
                              self.get_block('^interface %s' % member))
            return match.group('value')



    def get_members(self, name):
        """Returns the member interfaces for the specified Port-Channel

        Args:
            name(str): The Port-channel interface name to return the member
                interfaces for

        Returns:
            A list of physical interface names that belong to the specified
                interface
        """
        grpid = re.search(r'(\d+)', name).group()
        command = 'show port-channel %s all-ports' % grpid
        config = self.node.enable(command, 'text')
        return re.findall(r'Ethernet[\d/]*', config[0]['result']['output'])

    def set_members(self, name, members):
        """Configures the array of member interfaces for the Port-Channel

        Args:
            name(str): The Port-Channel interface name to configure the member
                interfaces

            members(list): The list of Ethernet interfaces that should be
                member interfaces

        Returns:
            True if the operation succeeds otherwise False
        """
        current_members = self.get_members(name)
        lacp_mode = self.get_lacp_mode(name)
        grpid = re.search(r'(\d+)', name).group()

        commands = list()

        # remove members from the current port-channel interface
        for member in set(current_members).difference(members):
            commands.append('interface %s' % member)
            commands.append('no channel-group %s' % grpid)

        # add new member interfaces to the port-channel interface
        for member in set(members).difference(current_members):
            commands.append('interface %s' % member)
            commands.append('channel-group %s mode %s' % (grpid, lacp_mode))

        return self.configure(commands) if commands else True

    def set_lacp_mode(self, name, mode):
        """Configures the LACP mode of the member interfaces

        Args:
            name(str): The Port-Channel interface name to configure the
                LACP mode

            mode(str): The LACP mode to configure the member interfaces to.
                Valid values are 'on, 'passive', 'active'

        Returns:
            True if the operation succeeds otherwise False
        """
        if mode not in ['on', 'passive', 'active']:
            return False

        grpid = re.search(r'(\d+)', name).group()

        remove_commands = list()
        add_commands = list()

        for member in self.get_members(name):
            remove_commands.append('interface %s' % member)
            remove_commands.append('no channel-group %s' % grpid)
            add_commands.append('interface %s' % member)
            add_commands.append('channel-group %s mode %s' % (grpid, mode))

        return self.configure(remove_commands + add_commands)

    def set_minimum_links(self, name, value=None, default=False):
        """Configures the Port-Channel min-links value

        Args:
            name(str): The Port-Channel interface name

            value(str): The value to configure the min-links

            default (bool): Specifies to default the interface description

        Returns:
            True if the operation succeeds otherwise False is returned
        """
        if value is not None:
            try:
                value = int(value)
                if not 0 <= value <= 16:
                    return False
            except ValueError:
                return False

        commands = ['interface %s' % name]
        if default:
            commands.append('default port-channel min-links')
        elif value is not None:
            commands.append('port-channel min-links %s' % value)
        else:
            commands.append('no port-channel min-links')

        return self.configure(commands)

class VxlanInterface(BaseInterface):

    SRC_INTF_RE = re.compile(r'(?<=\s{3}vxlan\ssource-interface\s)'
                             r'(?P<value>.+)$', re.M)
    MCAST_GRP_RE = re.compile(r'(?<=\s{3}vxlan\smulticast-group\s)'
                              r'(?P<value>.+)$', re.M)


    def get(self, name='Vxlan1'):
        """Returns a Vxlan interface as a set of key/value pairs

        Example:
            {
                "name": <string>,
                "type": "vxlan",
                "source_interface": <string>,
                "multicast_group": <string>
            }

        Args:
            name (str): The interface identifier to retrieve from the
                running-configuration

        Returns:
            A Python dictionary object of key/value pairs that represents
                the interface configuration.  If the specified interface
                does not exist, then None is returned
        """
        config = self.get_block('^interface %s' % name)
        if not config:
            return None

        response = super(VxlanInterface, self).get(name)
        response.update(dict(name=name, type='vxlan'))

        srcintf = self.value(self.SRC_INTF_RE.search(config), '')
        response['source_interface'] = srcintf

        mcastgrp = self.value(self.MCAST_GRP_RE.search(config), '')
        response['multicast_group'] = mcastgrp

        return response

    def set_source_interface(self, name='Vxlan1', value=None, default=False):
        """Configures the Vxlan source-interface value

        Args:
            name(str): The interface identifier to configure, defaults to
                Vxlan1
           value(str): The value to configure the source-interface to
           default(bool): Configures the source-interface value to default

        Returns:
            True if the operation succeeds otherwise False
        """
        commands = ['interface %s' % name]
        if default:
            commands.append('default vxlan source-interface')
        elif value is not None:
            commands.append('vxlan source-interface %s' % value)
        else:
            commands.append('no vxlan source-interface')

        return self.configure(commands)

    def set_multicast_group(self, name='Vxlan1', value=None, default=False):
        """Configures the Vxlan multicast-group value

        Args:
            name(str): The interface identifier to configure, defaults to
                Vxlan1
           value(str): The value to configure the multicast-group to
           default(bool): Configures the mulitcat-group value to default

        Returns:
            True if the operation succeeds otherwise False
        """
        commands = ['interface %s' % name]
        if default:
            commands.append('default vxlan multicast-group')
        elif value is not None:
            commands.append('vxlan multicast-group %s' % value)
        else:
            commands.append('no vxlan multicast-group')

        return self.configure(commands)







INTERFACE_CLASS_MAP = {
    'Et': EthernetInterface,
    'Po': PortchannelInterface,
    'Vx': VxlanInterface
}


def instance(api):
    return Interfaces(api)




