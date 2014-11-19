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

def getall():
    """ Returns all of the IP interfaces found in the running-config

    Example:
        {
            'Ethernet1': {
                'address': <string>,
                'mtu': <int>
            }
        }

    Returns:
        dict: a dict object of IP interface attributes
    """
    result = api.enable('show ip interfaces')
    response = dict()
    for key, value in result[0]['interfaces'].items():
        address = '%s/%s' % \
            (value['interfaceAddress']['primaryIp']['address'],
             value['interfaceAddress']['primaryIp']['maskLen'])
        response[key] = dict(address=address, mtu=value['mtu'])
    return response

def create(name):
    """ Creates a new IP interface instance
    """
    return api.config(['interface %s' % name, 'no switchport']) == [{}, {}]

def delete(name):
    """ Deletes an IP interface instance from the running configuration
    """
    commands = ['interface %s' % name, 'no ip address', 'switchport']
    return api.config(commands)  == [{}, {}, {}]

def set_address(name, value=None, default=False):
    """ Configures the interface IP address
    """
    commands = ['interface %s' % name]
    if default:
        commands.append('default ip address')
    elif value is not None:
        commands.append('ip address %s' % value)
    else:
        commands.append('no ip address')
    return api.config(commands) == [{}, {}]

def set_mtu(name, value=None, default=False):
    """ Configures the interface IP MTU
    """
    commands = ['interface %s' % name]
    if default:
        commands.append('default mtu')
    elif value is not None:
        commands.append('mtu %s' % value)
    else:
        commands.append('no mtu')
    return api.config(commands) == [{}, {}]

