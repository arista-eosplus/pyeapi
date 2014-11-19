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

api = None

def get():
    """ Returns all of the Vlans found in the running-config

    Example:
        {
            '1': {
                'dynamic': <boolean>,
                'interfaces': <dict>,
                'name': <string>,
                'status': [active, suspend]
            }
        }

    Returns:
        dict: a dict object of vlan attributes
    """
    result = api.enable('show vlan')
    return dict(vlans=result[0]['vlans'])

def trunk_groups():
    """Returns all of the trunk groups from the running-config

    Example:
        {
            'trunk_groups': {
                '1': {
                    'names': []
                }
            }
        }

    Returns:
        dict: a dict object of the trunk group attributes
    """
    result = api.enable('show vlan trunk group')
    return dict(trunk_groups=result[0]['trunkGroups'])

def create(vid):
    """ Creates a new VLAN resource

    Args:
        vid (str): The VLAN ID to create

    Returns:
        bool: True if create was successful otherwise False
    """
    return api.config('vlan %s' % vid) == [{}]

def delete(vid):
    """ Deletes a VLAN from the running configuration

    Args:
        vid (str): The VLAN ID to delete

    Returns:
        bool: True if the delete operation was successful otherwise False
    """
    return api.config('no vlan %s' % vid) == [{}]

def default(vid):
    """ Defaults the VLAN configuration

    Args:
        vid (str): The VLAN ID to default

    Returns:
        bool: True if the delete operation was successful otherwise False
    """
    return api.config('default vlan %s' % vid) == [{}]

def set_name(vid, name=None, default=False):
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
    return api.config(commands) == [{}, {}]

def set_state(vid, value=None, default=False):
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
    return api.config(commands) == [{}, {}]

def add_trunk_group(vid, name):
    """ Adds a new trunk group to the Vlan in the running-config

    Args:
        vid (str): The VLAN ID to configure
        name (str): The trunk group to add to the list

    Returns:
        bool: Tre if the add operation was successful otherwise False
    """
    commands = ["vlan %s" % vid, "trunk group %s" % name]
    return api.config(commands) == [{}, {}]

def remove_trunk_group(vid, name):
    """ Removes a trunk group from the list of configured trunk groups
    for the specified VLAN ID

    Args:
        vid (str): The VLAN ID to configure
        name (str): The trunk group to add to the list

    Returns:
        bool: Tre if the add operation was successful otherwise False
    """
    commands = ["vlan %s" % vid, "no trunk group %s" % name]
    return api.config(commands) == [{}, {}]


