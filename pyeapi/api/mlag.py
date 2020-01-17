#
# Copyright (c) 2015, Arista Networks, Inc.
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
"""Module for working with EOS MLAG resources

The Mlag resource provides configuration management of global and interface
MLAG settings on an EOS node.

Parameters:

    config (dict): The global MLAG configuration values

    interfaces (dict): The configured MLAG interfaces

Config Parameters:
    domain_id (str): The domain_id parameter  is parsed from the nodes
        mlag configuration.  The domain id is an alphanumeric string that
        names the MLAG domain

    local_interface (str): The local VLAN interface used as the control
        plane endpoint between MLAG peers.  Valid values include any
        VLAN SVI

    peer_address (str): The IP address of the MLAG peer used to send MLAG
        control traffic.  The peer address must be reachable from the
        local interface.  Valid values include any IPv4 unicast address

    peer_link (str): The physical link that connects the node to its MLAG
        peer.  Valid values for the peer link include layer 2 Ethernet or
        Port-Channel interfaces

    shutdown (bool): The administrative state of the global MLAG process.

Interface Parameters:
    mlag_id (str): The interface mlag parameter parsed from the nodes
        interface configuration.  Valid values for the mlag id are in
        the range of 1 to 2000

"""

import re

from pyeapi.api import Entity


class Mlag(Entity):
    """The Mlag class provides management of the MLAG configuration

    The Mlag class is derived from Entity and provides an API for working
    with the nodes MLAG configuraiton.
    """

    def get(self):
        """Returns the Mlag configuration as a resource dict

        Returns:
            dict: A dict ojbect containing the Mlag resource attributes.
        """
        resource = dict()
        resource.update(self._parse_config())
        resource.update(self._parse_interfaces())

        return resource

    def _parse_config(self):
        """Parses the mlag global configuration

        Returns:
            dict: A dict object that is intended to be merged into the
                resource dict
        """
        config = self.get_block('mlag configuration')
        cfg = dict()
        cfg.update(self._parse_domain_id(config))
        cfg.update(self._parse_local_interface(config))
        cfg.update(self._parse_peer_address(config))
        cfg.update(self._parse_peer_link(config))
        cfg.update(self._parse_shutdown(config))
        return dict(config=cfg)

    def _parse_domain_id(self, config):
        """Scans the config block and parses the domain-id value

        Args:
            config (str): The config block to scan

        Returns:
            dict: A dict object that is intended to be merged into the
                resource dict
        """
        match = re.search(r'domain-id (.+)$', config)
        value = match.group(1) if match else None
        return dict(domain_id=value)

    def _parse_local_interface(self, config):
        """Scans the config block and parses the local-interface value

        Args:
            config (str): The config block to scan

        Returns:
            dict: A dict object that is intended to be merged into the
                resource dict
        """
        match = re.search(r'local-interface (\w+)', config)
        value = match.group(1) if match else None
        return dict(local_interface=value)

    def _parse_peer_address(self, config):
        """Scans the config block and parses the peer-address value

        Args:
            config (str): The config block to scan

        Returns:
            dict: A dict object that is intended to be merged into the
                resource dict
        """
        match = re.search(r'peer-address (\d+\.\d+\.\d+\.\d+)$', config)
        value = match.group(1) if match else None
        return dict(peer_address=value)

    def _parse_peer_link(self, config):
        """Scans the config block and parses the peer-link value

        Args:
            config (str): The config block to scan

        Returns:
            dict: A dict object that is intended to be merged into the
                resource dict
        """
        match = re.search(r'peer-link (\S+)', config)
        value = match.group(1) if match else None
        return dict(peer_link=value)

    def _parse_shutdown(self, config):
        """Scans the config block and parses the shutdown value

        Args:
            config (str): The config block to scan

        Returns:
            dict: A dict object that is intended to be merged into the
                resource dict
        """
        value = 'no shutdown' not in config
        return dict(shutdown=value)

    def _parse_interfaces(self):
        """Scans the global config and returns the configured interfaces

        Returns:
            dict: A dict object that is intended to be merged into the
                resource dict.
        """
        interfaces = dict()
        names = re.findall(r'^interface (Po.+)$', self.config, re.M)
        for name in names:
            config = self.get_block('interface %s' % name)
            match = re.search(r'mlag (\d+)', config)
            if match:
                interfaces[name] = dict(mlag_id=match.group(1))
        return dict(interfaces=interfaces)

    def _configure_mlag(self, string, value, default, disable):
        cfg = self.command_builder(string, value=value, default=default,
                                   disable=disable)
        cmds = ['mlag configuration', cfg]
        return super(Mlag, self).configure(cmds)

    def set_domain_id(self, value=None, default=False, disable=False):
        """Configures the mlag domain-id value

        Args:
            value (str): The value to configure the domain-id
            default (bool): Configures the domain-id using the default keyword
            disable (bool): Negates the domain-id using the no keyword

        Returns:
            bool: Returns True if the commands complete successfully
        """
        return self._configure_mlag('domain-id', value, default, disable)

    def set_local_interface(self, value=None, default=False, disable=False):
        """Configures the mlag local-interface value

        Args:
            value (str): The value to configure the local-interface
            default (bool): Configures the local-interface using the
                default keyword
            disable (bool): Negates the local-interface using the no keyword

        Returns:
            bool: Returns True if the commands complete successfully
        """
        return self._configure_mlag('local-interface', value, default, disable)

    def set_peer_address(self, value=None, default=False, disable=False):
        """Configures the mlag peer-address value

        Args:
            value (str): The value to configure the peer-address
            default (bool): Configures the peer-address using the
                default keyword
            disable (bool): Negates the peer-address using the no keyword

        Returns:
            bool: Returns True if the commands complete successfully
        """
        return self._configure_mlag('peer-address', value, default, disable)

    def set_peer_link(self, value=None, default=False, disable=False):
        """Configures the mlag peer-link value

        Args:
            value (str): The value to configure the peer-link
            default (bool): Configures the peer-link using the
                default keyword
            disable (bool): Negates the peer-link using the no keyword

        Returns:
            bool: Returns True if the commands complete successfully
        """
        return self._configure_mlag('peer-link', value, default, disable)

    def set_shutdown(self, default=False, disable=True):
        """Configures the mlag shutdown value

        Default setting for set_shutdown is disable=True, meaning
        'no shutdown'. Setting both default and disable to False will
        effectively enable shutdown.

        Args:
            default (bool): Configures the shutdown using the
                default keyword
            disable (bool): Negates shutdown using the no keyword

        Returns:
            bool: Returns True if the commands complete successfully
        """
        return self._configure_mlag('shutdown', True, default, disable)

    def set_mlag_id(self, name, value=None, default=False, disable=False):
        """Configures the interface mlag value for the specified interface

        Args:
            name (str): The interface to configure.  Valid values for the
                name arg include Port-Channel*
            value (str): The mlag identifier to cofigure on the interface
            default (bool): Configures the interface mlag value using the
                default keyword
            disable (bool): Negates the interface mlag value using the
                no keyword

        Returns:
            bool: Returns True if the commands complete successfully
        """
        cmd = self.command_builder('mlag', value=value, default=default,
                                   disable=disable)
        return self.configure_interface(name, cmd)


def instance(node):
    """Returns an instance of Mlag

    Args:
        node (Node): The node argument passes an instance of Node to the
            resource

    Returns:
        object: An instance of Mlag
    """
    return Mlag(node)
