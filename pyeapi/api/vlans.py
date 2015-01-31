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
        """Returns the VLAN configuration as key/value pairs

        Response Message

        .. code-block:: json

            {
                "name": <string>,
                "state": [active, suspend],
                "trunk_groups": [array]
            }

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

        response = dict(vlan_id=value)
        response['name'] = NAME_RE.search(config).group('value')
        response['state'] = STATE_RE.search(config).group('value')
        response['trunk_groups'] = TRUNK_GROUP_RE.findall(config)

        return response

    def getall(self):
        """Returns a dict object of all Vlans in the running-config

        Response Message

        .. code-block:: json

            {
                "1": {...},
                "2": {...}
            }

        Returns:
            A dict object of Vlan attributes

        """
        vlans_re = re.compile(r'(?<=^vlan\s)(\d+)', re.M)

        response = dict()
        for vid in vlans_re.findall(self.config):
            response[vid] = self.get(vid)
        return response

    def create(self, vid):
        """ Creates a new VLAN resource

        .. code-block:: none

            vlan <vlanid>

        Args:
            vid (str): The VLAN ID to create

        Returns:
            True if create was successful otherwise False
        """
        command = 'vlan %s' % vid
        return self.configure(command) if isvlan(vid) else False

    def delete(self, vid):
        """ Deletes a VLAN from the running configuration

        .. code-block:: none

            no vlan <vlanid>

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

    def set_name(self, vid, name=None, default=False):
        """ Configures the VLAN name

        .. code-block:: none

            vlan <vlanid>
            [no] [default] name <name>

        Args:
            vid (str): The VLAN ID to Configures
            name (str): The value to configure the vlan name
            default (bool): Defaults the VLAN ID name

        Returns:
            True if the operation was successful otherwise False
        """
        commands = ['vlan %s' % vid]
        if default:
            commands.append('default name')
        elif name is not None:
            commands.append('name %s' % name)
        else:
            commands.append('no name')
        return self.configure(commands)

    def set_state(self, vid, value=None, default=False):
        """ Configures the VLAN state

        .. code-block:: none

            vlan <vlanid>
            [no] [default] state [suspect, active]

        Args:
            vid (str): The VLAN ID to configure
            value (str): The value to set the vlan state to
            default (bool): Configures the vlan state to its default value

        Returns:
            True if the operation was successful otherwise False
        """
        commands = ['vlan %s' % vid]
        if default:
            commands.append('default state')
        elif value is not None:
            commands.append('state %s' % value)
        else:
            commands.append('no state')
        return self.configure(commands)

    def set_trunk_groups(self, vid, value=None, default=False):
        """ Configures the list of trunk groups support on a vlan

        This method handles configuring the vlan trunk group value to default
        if the default flag is set to True.  If the default flag is set
        to False, then this method will calculate the set of trunk
        group names to be added and to be removed.

        .. code-block:: none

            vlan <vid.
            default trunk group

        Args:
            vid (str): The VLAN ID to configure
            value (str): The list of trunk groups that should be configured
                for this vlan id.
            default (bool): Configures the trunk group value to default if
                this value is true

        Returns:
            True if the operation was successful otherwise False

        """
        if default:
            return self.configure(['vlan %s' % vid, 'default trunk group'])

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

        .. code-block:: none

            vlan <vlanid>
            trunk group <name>

        Args:
            vid (str): The VLAN ID to configure
            name (str): The trunk group to add to the list

        Returns:
            True if the operation was successful otherwise False
        """
        commands = ["vlan %s" % vid, "trunk group %s" % name]
        return self.configure(commands)

    def remove_trunk_group(self, vid, name):
        """ Removes a trunk group from the list of configured trunk groups
        for the specified VLAN ID

        .. code-block:: none

            vlan <vlanid>
            no trunk group <name>

        Args:
            vid (str): The VLAN ID to configure
            name (str): The trunk group to add to the list

        Returns:
            True if the operation was successful otherwise False
        """
        commands = ["vlan %s" % vid, "no trunk group %s" % name]
        return self.configure(commands)

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

