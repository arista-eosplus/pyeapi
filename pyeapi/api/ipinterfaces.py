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
        to.  The interface name is the full interface identifier.

    address (string): The interface IP address in the form of
        address/len.

    mtu (integer): The interface MTU value.  The MTU value accepts
        integers in the range of 68 to 65535 bytes.  See RFC 791 and
        RFC 8200 for more information.
"""

import re

from pyeapi.api import EntityCollection
from pyeapi.utils import _interpolate_docstr

IP_MTU_MIN = 68
IP_MTU_MAX = 65535

SWITCHPORT_RE = re.compile(r'no switchport$', re.M)


class Ipinterfaces( EntityCollection ):

    def get( self, name ):
        """Returns the specific IP interface properties

        The Ipinterface resource returns the following:

            * name (str): The name of the interface
            * address (str): The IP address of the interface in the form
                of A.B.C.D/E (None if no ip configured)
            * secondary (list): The list of secondary IP addresses of the
                interface (if any configured)
            * mtu (int): The configured value for IP MTU.


        Args:
            name (string): The interface identifier to retrieve the
                configuration for

        Return:
            A Python dictionary object of key/value pairs that represents
                the current configuration of the node.  If the specified
                interface does not exist then None is returned.
        """
        config = self.get_block( 'interface %s' % name )
        if name[ 0:2 ] in [
                'Et', 'Po' ] and not SWITCHPORT_RE.search( config, re.M ):
            return None

        resource = dict( name=name )
        resource.update( self._parse_address(config) )
        resource.update( self._parse_mtu(config) )
        return resource

    def _parse_address( self, config ):
        """Parses the config block and returns the ip address value

        The provided configuration block is scanned and the configured value
        for the IP address is returned as a dict object. If the IP address
        value is not configured, then None is returned for the value

        Args:
            config (str): The interface configuration block to parse

        Return:
            dict: A dict object intended to be merged into the resource dict
        """
        match = re.findall( r'ip address ([^\s]+)', config, re.M )
        primary, secondary = ( match[0],
                match[1:] ) if match else ( None, None )
        return dict( address=primary,
         secondary=secondary ) if secondary else dict( address=primary )

    def _parse_mtu(self, config):
        """Parses the config block and returns the configured IP MTU value

        The provided configuration block is scanned and the configured value
        for the IP MTU is returned as a dict object.  The IP MTU value is
        expected to always be present in the provided config block

        Args:
            config (str): The interface configuration block to parse

        Return:
            dict: A dict object intended to be merged into the resource dict
        """
        match = re.search(r'mtu (\d+)', config)
        return dict( mtu=int(match.group( 1 )) if match else None )

    def getall(self):
        """ Returns all of the IP interfaces found in the running-config

        Returns:
            A Python dictionary object of key/value pairs keyed by interface
            name that represents all of the IP interfaces on
            the current node::

                {
                    'Ethernet1': {...},
                    'Ethernet2': {...}
                }
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

    def set_address(self, name, value=None, default=False, disable=False):
        """ Configures the interface IP address

        Args:
            name (string): The interface identifier to apply the interface
                config to

            value (string): The IP address and mask to set the interface to.
                The value should be in the format of A.B.C.D/E

            default (bool): Configures the address parameter to its default
                value using the EOS CLI default command

            disable (bool): Negates the address parameter value using the
                EOS CLI no command

        Returns:
            True if the operation succeeds otherwise False.

        """
        commands = ['interface %s' % name]
        commands.append(self.command_builder('ip address', value=value,
                                             default=default, disable=disable))
        return self.configure(commands)

    @_interpolate_docstr( 'IP_MTU_MIN', 'IP_MTU_MAX' )
    def set_mtu(self, name, value=None, default=False, disable=False):
        """ Configures the interface IP MTU

        Args:
            name (string): The interface identifier to apply the interface
                config to

            value (integer): The MTU value to set the interface to.  Accepted
                values include IP_MTU_MIN to IP_MTU_MAX

            default (bool): Configures the mtu parameter to its default
                value using the EOS CLI default command

            disable (bool); Negate the mtu parameter value using the EOS
                CLI no command

        Returns:
            True if the operation succeeds otherwise False.

        Raises:
            ValueError: If the value for MTU is not an integer value or
                outside of the allowable range

        """
        if value is not None:
            value = int(value)
            if not IP_MTU_MIN <= value <= IP_MTU_MAX:
                raise ValueError('invalid mtu value')

        commands = ['interface %s' % name]
        commands.append(self.command_builder('mtu', value=value,
                                             default=default, disable=disable))
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
