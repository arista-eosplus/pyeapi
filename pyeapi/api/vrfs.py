#
# Copyright (c) 2017, Arista Networks, Inc.
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
"""Module for working with EOS VRF resources

The Vrfs resource provides configuration of VRF resources for an EOS
node.

Parameters:

    name (string): The name parameter maps to the VRF name in EOS.  Valid
        values include any consecutive sequence of numbers, letters and
        underscore up to the maximum number of characters.  This parameter
        is defaultable.
    description (string): The vrf description set by the user
    ipv4_routing (bool): Tells whether IPv4 routing is enabled on the VRF
    ipv6_routing (bool): Tells whether IPv6 unicast routing is enabled on the
        VRF

"""

import re

from pyeapi.api import EntityCollection
from pyeapi.utils import make_iterable

RD_RE = re.compile(r'(?:\srd\s)(?P<value>.*)$', re.M)
DESCRIPTION_RE = re.compile(r'(?:description\s)(?P<value>.*)$', re.M)


class Vrfs(EntityCollection):
    """The Vrfs class provides a configuration resource for VRFs

    The Vrfs class is derived from ResourceBase a standard set of methods
    for working with VRF configurations on an EOS node.

    """

    def get(self, value):
        """Returns the VRF configuration as a resource dict.

        Args:
            value (string): The vrf name to retrieve from the
                running configuration.

        Returns:
            A Python dict object containing the VRF attributes as
                key/value pairs.

        """
        if self.version_number >= '4.23':
            config = self.get_block('vrf instance %s' % value)
        else:
            config = self.get_block('vrf definition %s' % value)
        if not config:
            return None
        response = dict(vrf_name=value)
        response.update(self._parse_rd(config))
        response.update(self._parse_description(config))
        config = self.get_block('no ip routing vrf %s' % value)
        if config:
            response['ipv4_routing'] = False
        else:
            response['ipv4_routing'] = True
        config = self.get_block('no ipv6 unicast-routing vrf %s' % value)
        if config:
            response['ipv6_routing'] = False
        else:
            response['ipv6_routing'] = True

        return response

    def _parse_rd(self, config):
        """ _parse_rd scans the provided configuration block and extracts
        the vrf rd. The return dict is intended to be merged into the response
        dict.

        Args:
            config (str): The vrf configuration block from the nodes running
                configuration

        Returns:
            dict: resource dict attribute
        """
        match = RD_RE.search(config)
        if match:
            value = match.group('value')
        else:
            value = match
        return dict(rd=value)

    def _parse_description(self, config):
        """ _parse_description scans the provided configuration block and
        extracts the vrf description value. The return dict is intended to
        be merged into the response dict.

        Args:
            config (str): The vrf configuration block from the nodes
                running configuration

        Returns:
            dict: resource dict attribute
        """
        value = DESCRIPTION_RE.search(config).group('value')
        return dict(description=value)

    def getall(self):
        """Returns a dict object of all VRFs in the running-config

        Returns:
            A dict object of VRF attributes

        """
        if self.version_number >= '4.23':
            vrfs_re = re.compile(r'(?<=^vrf instance\s)(\w+)', re.M)
        else:
            vrfs_re = re.compile(r'(?<=^vrf definition\s)(\w+)', re.M)

        response = dict()
        for vrf in vrfs_re.findall(self.config):
            response[vrf] = self.get(vrf)
        return response

    def create(self, vrf_name, rd=None):
        """ Creates a new VRF resource

        Note: A valid RD has the following format admin_ID:local_assignment.
            The admin_ID can be an AS number or globally assigned IPv4 address.
            The local_assignment can be an integer between 0-65,535 if the
            admin_ID is an IPv4 address and can be between 0-4,294,967,295 if
            the admin_ID is an AS number. If the admin_ID is an AS number the
            local_assignment could also be in the form of an IPv4 address.

        Args:
            vrf_name (str): The VRF name to create
            rd (str): The value to configure the vrf rd

        Returns:
            True if create was successful otherwise False
        """
        if self.version_number >= '4.23':
            commands = ['vrf instance %s' % vrf_name]
        else:
            commands = ['vrf definition %s' % vrf_name]
        if rd:
            commands.append('rd %s' % rd)
        return self.configure(commands)

    def delete(self, vrf_name):
        """ Deletes a VRF from the running configuration

        Args:
            vrf_name (str): The VRF name to delete

        Returns:
            True if the operation was successful otherwise False
        """
        if self.version_number >= '4.23':
            command = 'no vrf instance %s' % vrf_name
        else:
            command = 'no vrf definition %s' % vrf_name
        return self.configure(command)

    def default(self, vrf_name):
        """ Defaults the VRF configuration for given name

        Args:
            vrf_name (str): The VRF name to default

        Returns:
            True if the operation was successful otherwise False
        """
        if self.version_number >= '4.23':
            command = 'default vrf instance %s' % vrf_name
        else:
            command = 'default vrf definition %s' % vrf_name
        return self.configure(command)

    def configure_vrf(self, vrf_name, commands):
        """ Configures the specified VRF using commands

        Args:
            vrf_name (str): The VRF name to configure
            commands: The list of commands to configure

        Returns:
            True if the commands completed successfully
        """
        commands = make_iterable(commands)
        if self.version_number >= '4.23':
            commands.insert(0, 'vrf instance %s' % vrf_name)
        else:
            commands.insert(0, 'vrf definition %s' % vrf_name)

        return self.configure(commands)

    def set_rd(self, vrf_name, rd):
        """ Configures the VRF rd (route distinguisher)

        Note: A valid RD has the following format admin_ID:local_assignment.
            The admin_ID can be an AS number or globally assigned IPv4 address.
            The local_assignment can be an integer between 0-65,535 if the
            admin_ID is an IPv4 address and can be between 0-4,294,967,295 if
            the admin_ID is an AS number. If the admin_ID is an AS number the
            local_assignment could also be in the form of an IPv4 address.

        Args:
            vrf_name (str): The VRF name to set rd for
            rd (str): The value to configure the vrf rd

        Returns:
            True if the operation was successful otherwise False
        """
        cmds = self.command_builder('rd', value=rd)
        return self.configure_vrf(vrf_name, cmds)

    def set_description(self, vrf_name, description=None, default=False,
                        disable=False):
        """ Configures the VRF description

        Args:
            vrf_name (str): The VRF name to configure
            description(str): The string to set the vrf description to
            default (bool): Configures the vrf description to its default value
            disable (bool): Negates the vrf description

        Returns:
            True if the operation was successful otherwise False
        """
        cmds = self.command_builder('description', value=description,
                                    default=default, disable=disable)
        return self.configure_vrf(vrf_name, cmds)

    def set_ipv4_routing(self, vrf_name, default=False, disable=False):
        """ Configures ipv4 routing for the vrf

        Args:
            vrf_name (str): The VRF name to configure
            default (bool): Configures ipv4 routing for the vrf value to
                default if this value is true
            disable (bool): Negates the ipv4 routing for the vrf if set to true

        Returns:
            True if the operation was successful otherwise False

        """
        cmd = 'ip routing vrf %s' % vrf_name
        if default:
            cmd = 'default %s' % cmd
        elif disable:
            cmd = 'no %s' % cmd
        cmd = make_iterable(cmd)
        return self.configure(cmd)

    def set_ipv6_routing(self, vrf_name, default=False, disable=False):
        """ Configures ipv6 unicast routing for the vrf

        Args:
            vrf_name (str): The VRF name to configure
            default (bool): Configures ipv6 unicast routing for the vrf value
                to default if this value is true
            disable (bool): Negates the ipv6 unicast routing for the vrf if set
                to true

        Returns:
            True if the operation was successful otherwise False

        """
        cmd = 'ipv6 unicast-routing vrf %s' % vrf_name
        if default:
            cmd = 'default %s' % cmd
        elif disable:
            cmd = 'no %s' % cmd
        cmd = make_iterable(cmd)
        return self.configure(cmd)

    def set_interface(self, vrf_name, interface, default=False, disable=False):
        """ Adds a VRF to an interface

        Notes:
            Requires interface to be in routed mode. Must apply ip address
            after VRF has been applied. This feature can also be accessed
            through the interfaces api.

        Args:
            vrf_name (str): The VRF name to configure
            interface (str): The interface to add the VRF too
            default (bool): Set interface VRF forwarding to default
            disable (bool): Negate interface VRF forwarding

        Returns:
            True if the operation was successful otherwise False
        """
        cmds = ['interface %s' % interface]
        if self.version_number >= '4.23':
            cmds.append(self.command_builder('vrf', value=vrf_name,
                        default=default, disable=disable))
        else:
            cmds.append(self.command_builder('vrf forwarding', value=vrf_name,
                        default=default, disable=disable))
        return self.configure(cmds)


def instance(node):
    """Returns an instance of Vrfs

    This method will create and return an instance of the Vrfs object passing
    the value of API to the object.  The instance method is required for the
    resource to be autoloaded by the Node object

    Args:
        node (Node): The node argument passes an instance of Node to the
            resource
    """
    return Vrfs(node)
