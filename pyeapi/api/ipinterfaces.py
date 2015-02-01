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
"""Module for working the logical IP interfaces in EOS

This module provides an API for configuring logical IP interfaces using
EOS and eAPI.

Parameters:
    name (string): The interface name the configuration is in reference
        to.  The interface name is the full interface identifier

    address (string): The interface IP address in the form of
        address/len.

    mtu (integer): The interface MTU value.  The MTU value accepts
        integers in the range of 68 to 65535 bytes
"""

import re

from pyeapi.api import EntityCollection


SWITCHPORT_RE = re.compile(r'^\s{3}switchport$', re.M)
IPADDR_RE = re.compile(r'(?<=\s{3}ip\saddress\s)(?P<value>.+)$', re.M)
MTU_RE = re.compile(r'(?<=\s{3}mtu\s)(?P<value>\d+)$', re.M)


class Ipinterfaces(EntityCollection):

    def get(self, name):
        """Returns the specific IP interface properties

        Example
            {
                "name": <string>,
                "address": <string>,
                "mtu": <integer>
            }

        Args:
            name (string): The interface identifier to retrieve the
                configuration for

        Return:
            A Python dictionary object of key/value pairs that represents
                the current configuration of the node.  If the specified
                interface does not exist then None is returned.
        """
        config = self.get_block('interface %s' % name)

        if SWITCHPORT_RE.search(config, re.M):
            return None

        resp = dict(name=name)

        value = lambda x,y: x.group('value') if x else y

        resp['address'] = value(IPADDR_RE.search(config, re.M), '0.0.0.0')
        resp['mtu'] = int(MTU_RE.search(config, re.M).group('value'))

        return resp

    def getall(self):
        """ Returns all of the IP interfaces found in the running-config

        Example:
            {
                'Ethernet1': {...},
                'Ethernet2': {...}
            }

        Returns:
            A Python dictionary object of key/value pairs keyed by interface
                name that represents all of the IP interfaces on
                the current node.
        """
        interfaces_re = re.compile(r'^interface\s(.+)', re.M)

        response = dict()
        for name in interfaces_re.findall(self.config):
            interface = self.get(name)
            if interface:
                response[name] = interface
        return response

    def create(self, name):
        """ Creates a new IP interface instance

        This method will create a new logical IP interface for the specified
        physical interface.   If a logical IP interface already exists then
        this operation will have no effect.

        Note:
            Configuring a logical IP interface on a physical interface will
            remove any existing logical switchports have have been created

        Args:
            name (string): The interface identifier to create the logical
                layer 3 IP interface for.  The name must be the full interface
                name and not an abbreviated interface name (eg Ethernet1, not
                Et1).

        Returns:
            True if the create operation succeeds otherwise False.  If the
                specified interface is already created the this method will
                have no effect but will still return True
        """
        commands = ['interface %s' % name, 'no switchport']
        return self.configure(commands)

    def delete(self, name):
        """ Deletes an IP interface instance from the running configuration

        This method will delete the logical IP interface for the specified
        physical interface.  If the interface does not have a logical
        IP interface defined, then this method will have no effect.

        Args:
            name (string): The interface identifier to create the logical
                layer 3 IP interface for.  The name must be the full interface
                name and not an abbreviated interface name (eg Ethernet1, not
                Et1).

        Returns:
            True if the delete operation succeeds otherwise False.

        """
        commands = ['interface %s' % name, 'no ip address', 'switchport']
        return self.configure(commands)

    def set_address(self, name, value=None, default=False):
        """ Configures the interface IP address

        Args:
            name (string): The interface identifier to apply the interface
                config to

            value (string): The IP address and mask to set the interface to.
                The value should be in the format of A.B.C.D/E

            default (bool): Configures the address parameter to its default
                value using the EOS CLI default command

        Returns:
            True if the operation succeeds otherwise False.

        """
        commands = ['interface %s' % name]
        if default:
            commands.append('default ip address')
        elif value is not None:
            commands.append('ip address %s' % value)
        else:
            commands.append('no ip address')
        return self.configure(commands)

    def set_mtu(self, name, value=None, default=False):
        """ Configures the interface IP MTU

        Args:
            name (string): The interface identifier to apply the interface
                config to

            value (integer): The MTU value to set the interface to.  Accepted
                values include 68 to 65535

            default (bool): Configures the mtu parameter to its default
                value using the EOS CLI default command

        Returns:
            True if the operation succeeds otherwise False.

        Raises:
            ValueError: If the value for MTU is not an integer value or
                outside of the allowable range

        """
        if value is not None:
            value = int(value)
            if not 68 <= value <= 65535:
                raise ValueError('invalid mtu value')

        commands = ['interface %s' % name]
        if default:
            commands.append('default mtu')
        elif value is not None:
            commands.append('mtu %s' % value)
        else:
            commands.append('no mtu')
        return self.configure(commands)

def instance(node):
    """Returns an instance of Ipinterfaces

    This method will create and return an instance of the Ipinterfaces object
    passing the value of node to the instance.  This function is required
    for the resource to be autoloaded by the Node object

    Args:
        node (Node): The node argument provides an instance of Node to
            the Ipinterfaces instance
    """
    return Ipinterfaces(node)
