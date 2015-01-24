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
"""Module for working with spanning-tree in EOS

This module provides an API for working with spanning-tree configuration
in EOS.  This includes both global spanning-tree configuration as well as
interface config.

Global Parameters:
    mode (string): The spanning-tree operational mode.  Accepted values
        for this version are 'mstp' or 'none'.  This configuration
        parameter is not defaultable

    interfaces (StpInterfaces): The collection of STP enabled interfaces.

Interface Parameters:
    name (string): The name of the interface the STP configuration is in
        reference to.  The interface name is the full interface identifier

    portfast (string): The portfast configuration value for the interface.
        Accepted values are 'edge', 'network', or 'disabled'

    bpduguard (boolean): True if the BPDU Guard feature is enabled on the
        interface or False if it is disabled
"""

import re

from pyeapi.api import Entity, EntityCollection

class Stp(Entity):
    """The Stp class implements global configuration for spanning-tree

    The spanning-tree protocol provides both global and interface
    configuration options.  This class is the top-level class that provides
    access to all spanning-tree configuration options supported.

    Example:
        The below example demonstrates how to use the STP class to work
        with both global configuration and interface configuration.

        >>> import pyeapi.resources.stp
        >>> stp = pyeapi.resources.stp.instance(node)
        >>> stp.set_mode('mstp')
        True
        >>> stp.interfaces.set_bpduguard('Ethernet1', True)
        True

    Attributes:
        interfaces (StpInterfaces): An instance for configuration spanning-tree
            configuration interfaces

        instances (StpInstances): An instance object for working with
            spanning-tree global instances

    """

    def __init__(self, *args, **kwargs):
        super(Stp, self).__init__(*args, **kwargs)
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

        Note:
            See the individual classes for detailed message structures

        Returns:
            A Python dictionary object of key/value pairs the represent
                the entire supported spanning-tree configuration

        """
        return dict(interfaces=self.interfaces.getall(),
                    instances=self.instances.getall())

    @property
    def interfaces(self):
        if self._interfaces is not None:
            return self._interfaces
        self._interfaces = StpInterfaces(self.node)
        return self._interfaces

    @property
    def instances(self):
        if self._instances is not None:
            return self._instances
        self._instances = StpInstances(self.node)
        return self._instances

    def set_mode(self, value=None):
        """Configures the global spanning-tree mode

        Note:
            This configuration parameter is not defaultable

        Args:
            value (string): The value to configure the global spanning-tree
                mode of operation.  Valid values include 'mstp', 'none'

        Returns:
            True if the configuration operation succeeds otherwise False

        Raises:
            ValueError if the value is not in the accepted range
        """
        if value not in ['mstp', 'none', None]:
            raise ValueError("Specified value must be one of 'mstp', 'none'")
        if value is None:
            cmds = 'no spanning-tree mode'
        else:
            cmds = 'spanning-tree mode %s' % value
        return self.configure(cmds)

class StpInstances(EntityCollection):
    """Provides a configuration resource for spanning-tree instances

    This class provides an API for working with spanning-tree instances from
    the global configuration.  Spanning tree instances work with MST
    configuration
    """

    def getall(self):
        # TODO: (privateip, 20150106) stubbed out, needs implementation
        return dict()

class StpInterfaces(EntityCollection):
    """Provides a configuration resource for spanning-tree interfaces

    This class provides an API for working with spanning-tree interface
    configurations.  It provides access to managing specific interface
    spanning-tree configuration options.  Note that spanning-tree interfaces
    cannot be created or deleted.
    """

    def get(self, name):
        """Returns a dict object for the specified interface configuration

        Example
            {
                "name": <string>,
                "portfast": [network, edge, disable],
                "bpduguard": [true, false]
            }

        Args:
            name (string): The interface identifier to retrieve the config
                for.  Note: Spanning-tree interfaces are only supported on
                Ethernet and Port-Channel interfaces

        Returns:
            A Python dictionary object of key/value pairs that represent
                the spanning-tree interface configuration
            If the requested interface is not a valid spanning-tree
                interface, then None is returned
        """
        if not isvalidinterface(name):
            return None

        config = self.get_block(r'^interface\s%s$' % name)

        resp = dict()

        resp['bpduguard'] = 'spanning-tree bpduguard enable' in config

        if 'spanning-tree portfast network' in config:
            resp['portfast'] = 'network'
        elif 'spanning-tree portfast\n' in config:
            resp['portfast'] = 'edge'
        else:
            resp['portfast'] = 'disable'

        return resp

    def getall(self):
        """Returns a dict object of all spanning-tree interfaces

        This method will return all of the configured spanning-tree
        interfaces from the current nodes configuration.

        Example:
            {
                "Ethernet1": {...},
                "Ethernet2": {...}
            }

        Returns:
            A Python dictionary object that represents all configured
                spanning-tree interfaces indexed by interface name.
        """
        interfaces_re = re.compile(r'(?<=^interface\s)(.+)$', re.M)

        response = dict()
        for name in interfaces_re.findall(self.config):
            if name[0:2] in ['Et', 'Po']:
                interface = self.get(name)
                if interface:
                    response[name] = interface
        return response

    def set_portfast(self, name, value=None, default=False):
        """Configures the portfast value for the specified interface

        Args:
            name (string): The interface identifier to configure.  The name
                must be the full interface name (eg Ethernet1, not Et1).

            value (string): The value to configure the portfast setting to.
                Valid values include 'edge', 'network', 'none'

            default (bool): Configures the portfast parameter to its default
                value using the EOS CLI default configuration command

        Returns:
            True if the command succeeds, otherwise False

        Raises:
            ValueError: Raised if an invalid interface name or value is
                specified

        """
        if value not in ['network', 'edge', 'disable', None]:
            raise ValueError('invalid portfast value specified')

        if not isvalidinterface(name):
            raise ValueError('invalid interface value specified')

        commands = ['interface %s' % name]
        if default:
            commands.append('default spanning-tree portfast')
        elif value in [None, 'disable']:
            commands.append('no spanning-tree portfast')
        else:
            commands.append('spanning-tree portfast %s' % value)
        return self.configure(commands)

    def set_bpduguard(self, name, value=None, default=False):
        """Configures the bpduguard value for the specified interface

        Args:
            name (string): The interface identifier to configure.  The name
                must be the full interface name (eg Ethernet1, not Et1)

            value (bool): True if bpduguard is enabled otherwise False

            default (bool): Configures the bpduguard parameter to its default
                value using the EOS CLI default config command

        Returns:
            True if the command succeeds, otherwise False

        Raises:
            ValueError: Rasied if an invalid interface name is specified

            TypeError: Raised if the value keyword argument does not evaluate
                to a valid boolean

        """
        if not isvalidinterface(name):
            raise ValueError('invalid interface name specified')

        if value not in [True, False, None]:
            raise TypeError('value must be a boolean value')

        commands = ['interface %s' % name]
        if default:
            commands.append('default spanning-tree bpduguard')
        elif value is None:
            commands.append('no spanning-tree bpduguard')
        else:
            value = 'enable' if value else 'disable'
            commands.append('spanning-tree bpduguard %s' % value)
        return self.configure(commands)


def isvalidinterface(value):
    """Checks value to see if it could be a spanning-tree interface

    This function will check the value and return a boolean whether or not
    the interface could be a spanning-tree interface

    Note:
        This function only checks *if* the interface could be a spanning-tree
            interface but does not check if it *is* configured as a
            spanning-tree interface

    Args:
        value (string): The interface name to validate

    Returns:
        True if it could be a spanning-tree interface, otherwise False
    """
    return value[0:2] in ['Et', 'Po']

def instance(api):
    return Stp(api)
