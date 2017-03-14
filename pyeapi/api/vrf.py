#
# Copyright (c) 2016, Arista Networks, Inc.
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

The VRF module provides methods to configure VRF definitions in EOS.

Parameters:

    name (string): The name parameter maps to the VLAN name in EOS.  Valid
        values include any consecutive sequence of numbers, letters and
        underscore up to the maximum number of characters.  This parameter
        is defaultable.
    state (string): The state parameter sets the operational state of
        the VLAN on the node.   It has two valid values: active or suspend.
        The state parameter is defaultable.
    trunk_groups (array): The trunk_groups parameter provides a list of
        trunk groups configured for this VLAN.  This parameter is
        defaultable.

"""

import re

from pyeapi.api import EntityCollection
from pyeapi.utils import make_iterable

DESC_RE = re.compile(r'description (?P<value>.+)$', re.M)
RD_RE = re.compile(r'(?:rd\s(?P<admin>\S+):(?P<local>\S+))$', re.M)


class Vrf(EntityCollection):
    """The Vlans class provides a configuration resource for VLANs

    The Vlans class is derived from ResourceBase a standard set of methods
    for working with VLAN configurations on an EOS node.

    """

    def get(self, value):
        """Returns the VLAN configuration as a resource dict.

        Args:
            vid (string): The vlan identifier to retrieve from the
                running configuration.  Valid values are in the range
                of 1 to 4095

        Returns:
            A Python dict object containing the VLAN attributes as
                key/value pairs.

        """
        config = self.get_block('vrf definition %s' % value)
        if not config:
            return None

        response = dict(name=value)
        response.update(self._parse_description(config))
        response.update(self._parse_rd(config))

        return response

    def _parse_description(self, config):
        """ _parse_state scans the provided configuration block and extracts
        the vlan state value.  The config block is expected to always return
        the vlan state config.  The return dict is inteded to be merged into
        the response dict.

        Args:
            config (str): The vlan configuration block from the nodes
                running configuration

        Returns:
            dict: resource dict attribute
        """
        desc = None
        value = DESC_RE.search(config)
        if value:
            desc = value.group('value')
        return dict(description=desc)

    def _parse_rd(self, config):
        """ _parse_trunk_groups scans the provided configuration block and
        extracts all the vlan trunk groups.  If no trunk groups are configured
        an empty List is returned as the vlaue.  The return dict is intended
        to be merged into the response dict.

        Args:
            config (str): The vlan configuration block form the node's
                running configuration

        Returns:
            dict: resource dict attribute
        """
        value = RD_RE.search(config)
        if value:
            return value.groupdict()
        return dict(admin=None, local=None)

    def getall(self):
        """Returns a dict object of all Vlans in the running-config

        Returns:
            A dict object of Vlan attributes

        """
        vrf_re = re.compile(r'(?<=^vrf\sdefinition\s)(\S+)', re.M)

        response = dict()
        for name in vrf_re.findall(self.config):
            response[name] = self.get(name)
        return response

    def create(self, name):
        """ Creates a VRF in the running configuration

        Args:
            name (str): The VRF definition name

        Returns:
            True if create was successful otherwise False
        """
        command = 'vrf definition %s' % name
        return self.configure(command)

    def delete(self, name):
        """ Deletes a VRF from the running configuration

        Args:
            name (str): The VRF definition name to delete

        Returns:
            True if the operation was successful otherwise False
        """
        command = 'no vrf definition %s' % name
        return self.configure(command)

    def configure_vrf(self, name, commands):
        """ Configures the specified Vlan using commands

        Args:
            name (str): The VRF to configure
            commands: The list of commands to configure

        Returns:
            True if the commands completed successfully
        """
        commands = make_iterable(commands)
        commands.insert(0, 'vrf definition %s' % name)
        return self.configure(commands)

    def set_description(self, name, value=None, default=False):
        """ Configures the VRF description

        EosVersion:
            4.13.7M

        Args:
            name (str): The VRF to configure
            value (str): The description for the VRF
            default (bool): Defaults the VRF description. In effect removing
                the description from the running-config.

        Returns:
            True if the operation was successful otherwise False
        """
        cmds = self.command_builder('description', value=value,
                                    default=default)
        return self.configure_vrf(name, cmds)

    def set_rd(self, name, admin, local):
        """ Configures the VRF Route Distinguisher

        EosVersion:
            4.13.7M

        Args:
            name (str): The VRF to configure
            admin (str): An AS number or globally assigned IPv4 address
                identifying the entity assigning the RD. This should be an
                IANA-assigned identifying number.
            local (str): A locally assigned number distinguishing the VRF.
                Values range from 0-65535 if the admin_ID is an IPv4 address,
                or from 0-4,294,967,295 if the admin_ID is an AS number. If the
                admin_ID is an AS number, the local_assignment can also be
                entered in the form of an IPv4 address.

        Returns:
            True if the operation was successful otherwise False
        """
        value = '%s:%s' % (admin, local)
        cmds = self.command_builder('rd', value=value)
        return self.configure_vrf(name, cmds)


def instance(node):
    """Returns an instance of Vlans

    This method will create and return an instance of the Vlans object passing
    the value of API to the object.  The instance method is required for the
    resource to be autoloaded by the Node object

    Args:
        node (Node): The node argument passes an instance of Node to the
            resource
    """
    return Vrf(node)
