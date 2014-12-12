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

class Vlans(object):

    def __init__(self, api):
        self.api = api


    def _parse_get(self, vlan, trunkgroup):
        """Returns a vlan as a set of key/value pairs

        Example:
            {
                "name": <string>,
                "status": [active, suspend],
                "trunk_groups": [array]
            }

        Args:
            vlan (dict): set of attributes returned from eAPI
                         command "show vlans"
            trunkgroup (dict): set of attributes returned from eAPI
                               command "show vlan trunk group"

        Returns:
            dict: a dict object containing the vlan key/value pairs
        """
        response = dict()
        response['name'] = vlan['name']
        response['status'] = vlan['status']
        response['trunk_groups'] = trunkgroup['names']


    def getall(self):
        """Returns a dict object of all Vlans in the running-config

        Example:
            {
                "1": {...},
                "2": {...}
            }

        Returns:
            dict: a dict object of Vlan attributes
        """
        result = self.api.enable(['show vlan', 'show vlan trunk group'])
        response = dict()
        for vid in result[0]['vlans'].keys():
            response[vid] = self._parse_get(result[0]['vlans'][vid],
                                            result[1]['trunkGroups'][vid])
        return response


    def create(self, vid):
        """ Creates a new VLAN resource

        Args:
            vid (str): The VLAN ID to create

        Returns:
            bool: True if create was successful otherwise False
        """
        return self.api.config('vlan %s' % vid) == [{}]

    def delete(self, vid):
        """ Deletes a VLAN from the running configuration

        Args:
            vid (str): The VLAN ID to delete

        Returns:
            bool: True if the delete operation was successful otherwise False
        """
        return self.api.config('no vlan %s' % vid) == [{}]

    def default(self, vid):
        """ Defaults the VLAN configuration

        Args:
            vid (str): The VLAN ID to default

        Returns:
            bool: True if the delete operation was successful otherwise False
        """
        return self.api.config('default vlan %s' % vid) == [{}]

    def set_name(self, vid, name=None, default=False):
        """ Configures the VLAN name

        Args:
            vid (str): The VLAN ID to Configures
            name (str): The value to configure the vlan name
            default (bool): Defaults the VLAN ID name

        Returns:
            bool: True if the delete operation was successful otherwise False
        """
        commands = ['vlan %s' % vid]
        if default:
            commands.append('default name')
        elif name is not None:
            commands.append('name %s' % name)
        else:
            commands.append('no name')
        return self.api.config(commands) == [{}, {}]

    def set_state(self, vid, value=None, default=False):
        """ Configures the VLAN state

        Args:
            vid (str): The VLAN ID to configure
            value (str): The value to set the vlan state to
            default (bool): Configures the vlan state to its default value

        Returns:
            bool: True if the delete operation was successful otherwise False
        """
        commands = ['vlan %s' % vid]
        if default:
            commands.append('default state')
        elif value is not None:
            commands.append('state %s' % value)
        else:
            commands.append('no state')
        return self.api.config(commands) == [{}, {}]

    def add_trunk_group(self, vid, name):
        """ Adds a new trunk group to the Vlan in the running-config

        Args:
            vid (str): The VLAN ID to configure
            name (str): The trunk group to add to the list

        Returns:
            bool: Tre if the add operation was successful otherwise False
        """
        commands = ["vlan %s" % vid, "trunk group %s" % name]
        return self.api.config(commands) == [{}, {}]

    def remove_trunk_group(self, vid, name):
        """ Removes a trunk group from the list of configured trunk groups
        for the specified VLAN ID

        Args:
            vid (str): The VLAN ID to configure
            name (str): The trunk group to add to the list

        Returns:
            bool: Tre if the add operation was successful otherwise False
        """
        commands = ["vlan %s" % vid, "no trunk group %s" % name]
        return self.api.config(commands) == [{}, {}]

def instance(api):
    return Vlans(api)

