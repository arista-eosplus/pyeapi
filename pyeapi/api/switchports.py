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
"""Module for working with logical layer 2 switchports in EOS

This module provides an API for working with logical layer 2 interfaces
(switchports) in EOS.  Switchports are interfaces built on top of
physical Ethernet and bundled Port-Channel interfaces.

Parameters:
    name (string): The name of interface the configuration is in reference
        to.  The interface name is the full interface identifier

    mode (string): The operating mode of the switchport.  Supported values
        are access or trunk.

    access_vlan (string): The VLAN identifier for untagged VLAN traffic when
        the interface is operating in 'access' mode

    trunk_native_vlan (string): The VLAN identifier for untagged VLAN traffic
        when the interface is operating in 'trunk' mode

    trunk_allowed_vlans (array): The list of VLAN identifiers that are allowed
        on the interface when the interface is in 'trunk' mode
"""

import re

from pyeapi.api import EntityCollection

MODE_RE = re.compile(r'(?<=\s{3}switchport\smode\s)(?P<value>.+)$', re.M)
ACCESS_VLAN_RE = re.compile(r'(?<=\s{3}switchport\saccess\svlan\s)'
                            r'(?P<value>\d+)$', re.M)
TRUNK_VLAN_RE = re.compile(r'(?<=\s{3}switchport\strunk\snative\svlan\s)'
                           r'(?P<value>\d+)$', re.M)
TRUNKING_VLANS_RE = re.compile(r'(?<=\s{3}switchport\strunk\sallowed\svlan\s)'
                               r'(?P<value>.*)$', re.M)


class Switchports(EntityCollection):
    """The Switchports class provides a configuration resource for swichports

    Logical layer 2 interfaces built on top of physical Ethernet and bundled
    Port-Channel interfaces can be configured and managed with an instance
    of Switchports.   The Switchports class is a resource collection and
    supports get and getall methods.  The Switchports class is derived from
    the BaseResource class

    """

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
            name (string): The interface identifier to get.  Note: Switchports
                are only supported on Ethernet and Port-Channel interfaces

        Returns:
            A Python dictionary object of key/value pairs that represent
                the switchport configuration for the interface specified
            If the specified argument is not a switchport then None is
                returned
        """
        config = self.get_block('interface %s' % name)

        if not re.search(r'\s{3}no\sswitchport$', config, re.M):
            resp = dict(name=name)
            resp['mode'] = MODE_RE.search(config, re.M).group('value')
            resp['access_vlan'] = \
                ACCESS_VLAN_RE.search(config, re.M).group('value')
            resp['trunk_native_vlan'] = \
                TRUNK_VLAN_RE.search(config, re.M).group('value')
            resp['trunk_allowed_vlans'] = \
                TRUNKING_VLANS_RE.search(config, re.M).group('value')
            return resp

    def getall(self):
        """Returns a dict object to all Switchports

        This method will return all of the configured switchports as a
        dictionary object keyed by the interface identifier.

        Returns:
            A Python dictionary object that represents all configured
                switchports in the current running configuration
        """
        interfaces_re = re.compile(r'(?<=^interface\s)([Et|Po].+)$', re.M)

        response = dict()
        for name in interfaces_re.findall(self.config):
            interface = self.get(name)
            if interface:
                response[name] = interface
        return response

    def create(self, name):
        """Creates a new logical layer 2 interface

        This method will create a new switchport for the interface specified
        in the arguments (name).  If the logical switchport already exists
        then this command will have no effect

        Args:
            name (string): The interface identifier to create the logical
                layer 2 switchport for.  The name must be the full interface
                name and not an abbreviated interface name (eg Ethernet1, not
                Et1)

        Returns:
            True if the create operation succeeds otherwise False.  If the
                interface specified in args is already a switchport then this
                method will have no effect but will still return True
        """
        commands = ['interface %s' % name, 'no ip address',
                    'switchport']
        return self.configure(commands)

    def delete(self, name):
        """Deletes the logical layer 2 interface

        This method will delete the logical switchport for the interface
        specified in the arguments.  If the interface doe not have a logical
        layer 2 interface defined, then this method will have no effect.

        Args:
            name (string): The interface identifier to create the logical
                layer 2 switchport for.  The name must be the full interface
                name and not an abbreviated interface name (eg Ethernet1, not
                Et1)

        Returns:
            True if the create operation succeeds otherwise False.  If the
                interface specified in args is already a switchport then this
                method will have no effect but will still return True
        """
        commands = ['interface %s' % name, 'no switchport']
        return self.configure(commands)

    def default(self, name):
        """Defaults the configuration of the switchport interface

        This method will default the configuration state of the logical
        layer 2 interface.

        Args:
            name (string): The interface identifier to create the logical
                layer 2 switchport for.  The name must be the full interface
                name and not an abbreviated interface name (eg Ethernet1, not
                Et1)

        Returns:
            True if the create operation succeeds otherwise False.  If the
                interface specified in args is already a switchport then this
                method will have no effect but will still return True
        """
        commands = ['interface %s' % name, 'no ip address',
                    'default switchport']
        return self.configure(commands)

    def set_mode(self, name, value=None, default=False):
        """Configures the switchport mode

        Args:
            name (string): The interface identifier to create the logical
                layer 2 switchport for.  The name must be the full interface
                name and not an abbreviated interface name (eg Ethernet1, not
                Et1)

            value (string): The value to set the mode to.  Accepted values
                for this argument are access or trunk

            default (bool): Configures the mode parameter to its default
                value using the EOS CLI

        Returns:
            True if the create operation succeeds otherwise False.
        """
        commands = ['interface %s' % name]
        if default:
            commands.append('default switchport mode')
        elif value is None:
            commands.append('no switchport mode')
        else:
            commands.append('switchport mode %s' % value)
        return self.configure(commands)

    def set_access_vlan(self, name, value=None, default=False):
        """Configures the switchport access vlan

        Args:
            name (string): The interface identifier to create the logical
                layer 2 switchport for.  The name must be the full interface
                name and not an abbreviated interface name (eg Ethernet1, not
                Et1)

            value (string): The value to set the access vlan to.  The value
                must be a valid VLAN ID in the range of 1 to 4094.

            default (bool): Configures the access vlan parameter to its default
                value using the EOS CLI

        Returns:
            True if the create operation succeeds otherwise False.
        """
        commands = ['interface %s' % name]
        if default:
            commands.append('default switchport access vlan')
        elif value is None:
            commands.append('no switchport access vlan')
        else:
            commands.append('switchport access vlan %s' % value)
        return self.configure(commands)

    def set_trunk_native_vlan(self, name, value=None, default=False):
        """Configures the switchport trunk native vlan value

        Args:
            name (string): The interface identifier to create the logical
                layer 2 switchport for.  The name must be the full interface
                name and not an abbreviated interface name (eg Ethernet1, not
                Et1)

            value (string): The value to set the trunk nativevlan to.  The
                value must be a valid VLAN ID in the range of 1 to 4094.

            default (bool): Configures the access vlan parameter to its default
                value using the EOS CLI

        Returns:
            True if the create operation succeeds otherwise False.
        """
        commands = ['interface %s' % name]
        if default:
            commands.append('default switchport trunk native vlan')
        elif value is None:
            commands.append('no switchport trunk native vlan')
        else:
            commands.append('switchport trunk native vlan %s' % value)
        return self.configure(commands)

    def set_trunk_allowed_vlans(self, name, value=None, default=False):
        """Configures the switchport trunk allowed vlans value

        Args:
            name (string): The interface identifier to create the logical
                layer 2 switchport for.  The name must be the full interface
                name and not an abbreviated interface name (eg Ethernet1, not
                Et1)

            value (string): The value to set the trunk allowed vlans to.  The
                value must be a valid VLAN ID in the range of 1 to 4094.

            default (bool): Configures the access vlan parameter to its default
                value using the EOS CLI

        Returns:
            True if the create operation succeeds otherwise False.
        """
        commands = ['interface %s' % name]
        if default:
            commands.append('default switchport trunk allowed vlan')
        elif value is None:
            commands.append('no switchport trunk allowed vlan')
        else:
            commands.append('switchport trunk allowed vlan %s' % value)
        return self.configure(commands)


def instance(node):
    """Returns an instance of Switchports

    This method will create and return an instance of the Switchports object
    passing the value of node to the instance.  The module method is
    required for the resource to be autoloaded by the Node object

    Args:
        node (Node): The node argument provides an instance of Node to the
            resource
    """
    return Switchports(node)
