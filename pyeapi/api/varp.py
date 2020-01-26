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
"""Module for managing the VARP configuration in EOS

This module provides an API for configuring VARP resources using
EOS and eAPI.

Arguments:
    name (string): The interface name the configuration is in reference
        to.  The interface name is the full interface identifier

    address (string): The interface IP address in the form of
        address/len.

    mtu (integer): The interface MTU value.  The MTU value accepts
        integers in the range of 68 to 65535 bytes
"""

import re

from pyeapi.api import EntityCollection


class Varp(EntityCollection):

    def __init__(self, *args, **kwargs):
        super(Varp, self).__init__(*args, **kwargs)
        self._interfaces = None

    @property
    def interfaces(self):
        if self._interfaces is not None:
            return self._interfaces
        self._interfaces = VarpInterfaces(self.node)
        return self._interfaces

    def get(self):
        """Returns the current VARP configuration

        The Varp resource returns the following:

            * mac_address (str): The virtual-router mac address
            * interfaces (dict): A list of the interfaces that have a
                                 virtual-router address configured.

        Return:
            A Python dictionary object of key/value pairs that represents
            the current configuration of the node.  If the specified
            interface does not exist then None is returned::

                {
                    "mac_address": "aa:bb:cc:dd:ee:ff",
                    "interfaces": {
                        "Vlan100": {
                            "addresses": [ "1.1.1.1", "2.2.2.2"]
                        },
                        "Vlan200": [...]
                    }
                }
        """
        resource = dict()
        resource.update(self._parse_mac_address())
        resource.update(self._parse_interfaces())
        return resource

    def _parse_mac_address(self):
        mac_address_re = re.compile(r'^ip\svirtual-router\smac-address\s'
                                    r'((?:[a-f0-9]{2}:){5}[a-f0-9]{2})$', re.M)
        mac = mac_address_re.search(self.config)
        mac = mac.group(1) if mac else None
        return dict(mac_address=mac)

    def _parse_interfaces(self):
        interfaces = VarpInterfaces(self.node).getall()
        return dict(interfaces=interfaces)

    def set_mac_address(self, mac_address=None, default=False, disable=False):
        """ Sets the virtual-router mac address

        This method will set the switch virtual-router mac address. If a
        virtual-router mac address already exists it will be overwritten.

        Args:
            mac_address (string): The mac address that will be assigned as
                the virtual-router mac address. This should be in the format,
                aa:bb:cc:dd:ee:ff.
            default (bool): Sets the virtual-router mac address to the system
                default (which is to remove the configuration line).
            disable (bool): Negates the virtual-router mac address using
                the system no configuration command

        Returns:
            True if the set operation succeeds otherwise False.
        """
        base_command = 'ip virtual-router mac-address'
        if not default and not disable:
            if mac_address is not None:
                # Check to see if mac_address matches expected format
                if not re.match(r'(?:[a-f0-9]{2}:){5}[a-f0-9]{2}',
                                mac_address):
                    raise ValueError('mac_address must be formatted like:'
                                     'aa:bb:cc:dd:ee:ff')
            else:
                raise ValueError('mac_address must be a properly formatted '
                                 'address string')
        if default or disable and not mac_address:
            current_mac = self._parse_mac_address()
            if current_mac['mac_address']:
                base_command = base_command + ' ' + current_mac['mac_address']
        commands = self.command_builder(base_command, value=mac_address,
                                        default=default, disable=disable)
        return self.configure(commands)


class VarpInterfaces(EntityCollection):
    """The VarpInterfaces class helps manage interfaces with
    virtual-router configuration.
    """
    def get(self, name):
        interface_re = r'interface\s%s' % name
        config = self.get_block(interface_re)

        if not config:
            return None

        resource = dict(addresses=dict())
        resource.update(self._parse_virtual_addresses(config))
        return resource

    def getall(self):
        resources = dict()
        interfaces_re = re.compile(r'^interface\s(Vlan\d+)$', re.M)
        for name in interfaces_re.findall(self.config):
            interface_detail = self.get(name)
            if interface_detail:
                resources[name] = interface_detail
        return resources

    def set_addresses(self, name, addresses=None, default=False,
                      disable=False):

        commands = list()
        commands.append('interface %s' % name)

        if default:
            commands.append('default ip virtual-router address')
        elif disable:
            commands.append('no ip virtual-router address')
        elif addresses is not None:
            try:
                current_addresses = self.get(name)['addresses']
            except Exception:
                current_addresses = []

            # remove virtual-router addresses not present in addresses list
            for entry in set(current_addresses).difference(addresses):
                commands.append('no ip virtual-router address %s' % entry)

            # add new set virtual-router addresses that werent present
            for entry in set(addresses).difference(current_addresses):
                commands.append('ip virtual-router address %s' % entry)
        else:
            commands.append('no ip virtual-router address')

        return self.configure(commands) if commands else True

    def _parse_virtual_addresses(self, config):
        virt_ip_re = re.compile(r'^\s+ip\svirtual-router\saddress\s(\S+)$',
                                re.M)
        return dict(addresses=virt_ip_re.findall(config))


def instance(node):
    """Returns an instance of Ipinterfaces

    This method will create and return an instance of the Varp object
    passing the value of node to the instance.  This function is required
    for the resource to be autoloaded by the Node object

    Args:
        node (Node): The node argument provides an instance of Node to
            the Varp instance
    """
    return Varp(node)
