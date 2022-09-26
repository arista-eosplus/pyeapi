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
"""Module for working with EOS VLAN resources

The Vlans resource provides configuration of VLAN resources for an EOS
node.

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

VLAN_ID_RE = re.compile(r'(?:vlan\s)(?P<value>.*)$', re.M)
NAME_RE = re.compile(r'(?:name\s)(?P<value>.*)$', re.M)
STATE_RE = re.compile(r'(?:state\s)(?P<value>.*)$', re.M)
TRUNK_GROUP_RE = re.compile(r'(?:trunk\sgroup\s)(?P<value>.*)$', re.M)


def isvlan(value):
    """Checks if the argument is a valid VLAN

    A valid VLAN is an integer value in the range of 1 to 4094.  This
    function will test if the argument falls into the specified range and
    is considered a valid VLAN

    Args:
        value: The value to check if is a valid VLAN

    Returns:
        True if the supplied value is a valid VLAN otherwise False
    """
    try:
        value = int(value)
        return value in range(1, 4095)
    except ValueError:
        return False


class Vlans(EntityCollection):
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
        config = self.get_block('vlan %s' % value)
        if not config:
            return None

        response = dict(vlan_id=self._parse_vlan_id(config))
        response.update(self._parse_name(config))
        response.update(self._parse_state(config))
        response.update(self._parse_trunk_groups(config))

        return response

    def _parse_vlan_id(self, config):
        """ _parse_vlan_id scans the provided configuration block and extracts
        the vlan id.  The config block is expected to always return the
        vlan id.  The return dict is intended to be merged into the response
        dict.

        Args:
            config (str): The vlan configuration block from the nodes running
                configuration

        Returns:
            Str: vlan id (or range/list of vlan ids)
        """
        value = VLAN_ID_RE.search(config).group('value')
        return value

    def _parse_name(self, config):
        """ _parse_name scans the provided configuration block and extracts
        the vlan name.  The config block is expected to always return the
        vlan name.  The return dict is intended to be merged into the response
        dict.

        Args:
            config (str): The vlan configuration block from the nodes running
                configuration

        Returns:
            dict: resource dict attribute
        """
        value = NAME_RE.search(config).group('value')
        return dict(name=value)

    def _parse_state(self, config):
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
        value = STATE_RE.search(config).group('value')
        return dict(state=value)

    def _parse_trunk_groups(self, config):
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
        values = TRUNK_GROUP_RE.findall(config)
        return dict(trunk_groups=values)

    def getall(self):
        """Returns a dict object of all Vlans in the running-config

        Returns:
            A dict object of Vlan attributes

        """
        # RE to find standalone and grouped (ranged, enumerated) vlans (#197)
        vlans_re = re.compile(r'(?<=^vlan\s)[\d,\-]+', re.M)

        response = dict()
        for vid in vlans_re.findall(self.config):
            response[vid] = self.get(vid)
        return response

    def create(self, vid):
        """ Creates a new VLAN resource

        Args:
            vid (str): The VLAN ID to create

        Returns:
            True if create was successful otherwise False
        """
        command = 'vlan %s' % vid
        return self.configure(command) if isvlan(vid) else False

    def delete(self, vid):
        """ Deletes a VLAN from the running configuration

        Args:
            vid (str): The VLAN ID to delete

        Returns:
            True if the operation was successful otherwise False
        """
        command = 'no vlan %s' % vid
        return self.configure(command) if isvlan(vid) else False

    def default(self, vid):
        """ Defaults the VLAN configuration

        .. code-block:: none

            default vlan <vlanid>

        Args:
            vid (str): The VLAN ID to default

        Returns:
            True if the operation was successful otherwise False
        """
        command = 'default vlan %s' % vid
        return self.configure(command) if isvlan(vid) else False

    def configure_vlan(self, vid, commands):
        """ Configures the specified Vlan using commands

        Args:
            vid (str): The VLAN ID to configure
            commands: The list of commands to configure

        Returns:
            True if the commands completed successfully
        """
        commands = make_iterable(commands)
        commands.insert(0, 'vlan %s' % vid)
        return self.configure(commands)

    def set_name(self, vid, name=None, default=False, disable=False):
        """ Configures the VLAN name

        EosVersion:
            4.13.7M

        Args:
            vid (str): The VLAN ID to Configures
            name (str): The value to configure the vlan name
            default (bool): Defaults the VLAN ID name
            disable (bool): Negates the VLAN ID name

        Returns:
            True if the operation was successful otherwise False
        """
        cmds = self.command_builder('name', value=name, default=default,
                                    disable=disable)
        return self.configure_vlan(vid, cmds)

    def set_state(self, vid, value=None, default=False, disable=False):
        """ Configures the VLAN state

        EosVersion:
            4.13.7M

        Args:
            vid (str): The VLAN ID to configure
            value (str): The value to set the vlan state to
            default (bool): Configures the vlan state to its default value
            disable (bool): Negates the vlan state

        Returns:
            True if the operation was successful otherwise False
        """
        cmds = self.command_builder('state', value=value, default=default,
                                    disable=disable)
        return self.configure_vlan(vid, cmds)

    def set_trunk_groups(self, vid, value=None, default=False, disable=False):
        """ Configures the list of trunk groups support on a vlan

        This method handles configuring the vlan trunk group value to default
        if the default flag is set to True.  If the default flag is set
        to False, then this method will calculate the set of trunk
        group names to be added and to be removed.

        EosVersion:
            4.13.7M

        Args:
            vid (str): The VLAN ID to configure
            value (str): The list of trunk groups that should be configured
                for this vlan id.
            default (bool): Configures the trunk group value to default if
                this value is true
            disable (bool): Negates the trunk group value if set to true

        Returns:
            True if the operation was successful otherwise False

        """
        if default:
            return self.configure_vlan(vid, 'default trunk group')
        if disable:
            return self.configure_vlan(vid, 'no trunk group')

        current_value = self.get(vid)['trunk_groups']
        failure = False

        value = make_iterable(value)

        for name in set(value).difference(current_value):
            if not self.add_trunk_group(vid, name):
                failure = True

        for name in set(current_value).difference(value):
            if not self.remove_trunk_group(vid, name):
                failure = True

        return not failure

    def add_trunk_group(self, vid, name):
        """ Adds a new trunk group to the Vlan in the running-config

        EosVersion:
            4.13.7M

        Args:
            vid (str): The VLAN ID to configure
            name (str): The trunk group to add to the list

        Returns:
            True if the operation was successful otherwise False
        """
        return self.configure_vlan(vid, 'trunk group %s' % name)

    def remove_trunk_group(self, vid, name):
        """ Removes a trunk group from the list of configured trunk groups
        for the specified VLAN ID

        EosVersion:
            4.13.7M

        Args:
            vid (str): The VLAN ID to configure
            name (str): The trunk group to add to the list

        Returns:
            True if the operation was successful otherwise False
        """
        return self.configure_vlan(vid, 'no trunk group %s' % name)


def instance(node):
    """Returns an instance of Vlans

    This method will create and return an instance of the Vlans object passing
    the value of API to the object.  The instance method is required for the
    resource to be autoloaded by the Node object

    Args:
        node (Node): The node argument passes an instance of Node to the
            resource
    """
    return Vlans(node)
