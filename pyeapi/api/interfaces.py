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
"""Module for working with interfaces in EOS

This module provides an API for pragmatically working with EOS interface
configurations.  Interfaces include any data or management plane interface
available in EOS.

Parameters:
    name (string): The name of the interface the configuration should be
        applied to.  The interface name is the full interface identifier.

    shutdown (boolean): True if the interface is administratively disabled,
        and False if the interface is administratively enable.  This value
        does not validate the interfaces operational state.

    description (string): The interface description string.  This value is
        an arbitrary operator defined value.

    sflow (boolean): True if sFlow is enabled on the interface otherwise
        False

    flowcontrol_send (string): The flowcontrol send configuration value for
        the interface.  Valid values are on or off

    flowcontrol_receive (string): The flowcontrol receive configuration value
        for the interface.  Valid values are on or off

"""

import re

from pyeapi.api import EntityCollection
from pyeapi.utils import ProxyCall, CliVariants

MIN_LINKS_RE = re.compile(r'(?<=\s{3}min-links\s)(?P<value>.+)$', re.M)

DEFAULT_LACP_MODE = 'on'
DEFAULT_LACP_FALLBACK = 'disabled'
DEFAULT_LACP_FALLBACK_TIMEOUT = 90

VALID_INTERFACES = frozenset([
    'Ethernet',
    'Management',
    'Loopback',
    'Port-Channel',
    'Vlan',
    'Vxlan',
])


def isvalidinterface(value):
    match = re.match(r'([EPVLM][a-z-C]+)', value)
    return match and match.group() in VALID_INTERFACES


class Interfaces(EntityCollection):

    def __init__(self, node, *args, **kwargs):
        super(Interfaces, self).__init__(node, *args, **kwargs)
        self._instances = dict()

    def get(self, name):
        return self.get_instance(name)[name]

    def getall(self):
        """Returns all interfaces in a dict object.

        Returns:
            A Python dictionary object containing all interface
            configuration indexed by interface name::

                {
                    "Ethernet1": {...},
                    "Ethernet2": {...}
                }

        """
        interfaces_re = re.compile(r'(?<=^interface\s)(.+)$', re.M)

        response = dict()
        for name in interfaces_re.findall(self.config):
            interface = self.get(name)
            if interface:
                response[name] = interface
        return response

    def __getattr__(self, name):
        return ProxyCall(self.marshall, name)

    def get_instance(self, interface):
        cls = INTERFACE_CLASS_MAP.get(interface[0:2]) or BaseInterface
        if cls in self._instances:
            instance = self._instances[cls]
        else:
            instance = cls(self.node)
            self._instances[cls] = instance
        return instance

    def marshall(self, name, *args, **kwargs):
        interface = args[0]
        if not isvalidinterface(interface):
            raise ValueError('invalid interface {}'.format(interface))

        instance = self.get_instance(interface)
        if not hasattr(instance, name):
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (instance, name))
        method = getattr(instance, name)
        return method(*args, **kwargs)


class BaseInterface(EntityCollection):

    def __str__(self):
        return 'Interface'

    def get(self, name):
        """Returns a generic interface as a set of key/value pairs

        This class is should normally serve as a  base class for building more
        specific interface resources.  The attributes of this resource are
        common to all interfaces regardless of type in EOS.

        The generic interface resource returns the following:

            * name (str): The name of the interface
            * type (str): Always returns 'generic'
            * shutdown (bool): True if the interface is shutdown
            * description (str): The interface description value

        Args:
            name (str): The interface identifier to retrieve from the
                running-configuration

        Returns:
            A Python dictionary object of key/value pairs that represents
                the interface configuration.  If the specified interface
                does not exist, then None is returned
        """
        config = self.get_block('^interface %s' % name)
        if not config:
            return None

        resource = dict(name=name, type='generic')
        resource.update(self._parse_shutdown(config))
        resource.update(self._parse_description(config))
        return resource

    def _parse_shutdown(self, config):
        """Scans the specified config block and returns the shutdown value

        Args:
            config (str): The interface config block to scan

        Returns:
            dict: Returns a dict object with the shutdown value retrieved
                from the config block.  The returned dict object is intended
                to be merged into the interface resource dict
        """
        value = 'no shutdown' not in config
        return dict(shutdown=value)

    def _parse_description(self, config):
        """Scans the specified config block and returns the description value

        Args:
            config (str): The interface config block to scan

        Returns:
            dict: Returns a dict object with the description value retrieved
                from the config block.  If the description value is not
                configured, None is returned as the value.  The returned dict
                is intended to be merged into the interface resource dict.
        """
        value = None
        match = re.search(r'description (.+)$', config, re.M)
        if match:
            value = match.group(1)
        return dict(description=value)

    def create(self, name):
        """Creates a new interface on the node

        Note:
            This method will attempt to create the interface regardless
            if the interface exists or not.  If the interface already exists
            then this method will still return True

        Args:
            name (string): The full name of the interface.

        Returns:
            True if the interface could be created otherwise False (see Note)

        """
        return self.configure('interface %s' % name)

    def delete(self, name):
        """Deletes the interface from the node

        Note:
            This method will attempt to delete the interface from the nodes
            operational config.  If the interface does not exist then this
            method will not perform any changes but still return True

        Args:
            name (string): The full name of the interface

        Returns:
            True if the interface could be deleted otherwise False (see Node)

        """
        return self.configure('no interface %s' % name)

    def default(self, name):
        """Defaults an interface in the running configuration

        Args:
            name (string): The full name of the interface

        Returns:
            True if the command operation succeeds otherwise False
        """
        return self.configure('default interface %s' % name)

    def set_encapsulation(self, name, vid, default=False, disable=False):
        """Configures the subinterface encapsulation value

        Args:
            name (string): The interface identifier.  It must be a full
                interface name (ie Ethernet, not Et)
            vid (int): The vlan id number
            default (boolean): Specifies to default the subinterface
                encapsulation
            disable (boolean): Specifies to disable the subinterface
                encapsulation

        Returns:
            True if the operation succeeds otherwise False is returned
        """
        if '.' not in name:
            raise NotImplementedError('parameter encapsulation can only be'
                                      ' set on subinterfaces')
        if name[0:2] not in ['Et', 'Po']:
            raise NotImplementedError('parameter encapsulation can only be'
                                      ' set on Ethernet and Port-Channel'
                                      ' subinterfaces')
        commands = ['interface %s' % name]
        commands.append(self.command_builder('encapsulation dot1q vlan',
                                             str(vid), default=default,
                                             disable=disable))
        return self.configure(commands)

    def set_description(self, name, value=None, default=False, disable=False):
        """Configures the interface description

        EosVersion:
            4.13.7M

        Args:
            name (string): The interface identifier.  It must be a full
                interface name (ie Ethernet, not Et)
            value (string): The value to set the description to.
            default (boolean): Specifies to default the interface description
            disable (boolean): Specifies to negate the interface description

        Returns:
            True if the operation succeeds otherwise False
        """
        string = 'description'
        commands = self.command_builder(string, value=value, default=default,
                                        disable=disable)
        return self.configure_interface(name, commands)

    def set_shutdown(self, name, default=False, disable=True):
        """Configures the interface shutdown state

        Default configuration for set_shutdown is disable=True, meaning
        'no shutdown'. Setting both default and disable to False will
        effectively enable shutdown on the interface.

        Args:
            name (string): The interface identifier.  It must be a full
                interface name (ie Ethernet, not Et)

            default (boolean): Specifies to default the interface shutdown

            disable (boolean): Specifies to disable interface shutdown, i.e.
                disable=True => no shutdown

        Returns:
            True if the operation succeeds otherwise False is returned
        """
        commands = ['interface %s' % name]
        commands.append(self.command_builder('shutdown', value=True,
                                             default=default, disable=disable))
        return self.configure(commands)


class EthernetInterface(BaseInterface):

    def __str__(self):
        return 'EthernetInterface'

    def get(self, name):
        """Returns an interface as a set of key/value pairs

        Args:
            name (string): the interface identifier to retrieve the from
                the configuration

        Returns:
            A Python dictionary object of key/value pairs that represent
            the current configuration for the specified node.  If the
            specified interface name does not exist, then None is returned::

                {
                    "name": <string>,
                    "type": "ethernet",
                    "sflow": [true, false],
                    "flowcontrol_send": [on, off],
                    "flowcontrol_receive": [on, off]
                }
        """
        config = self.get_block('^interface %s' % name)

        if not config:
            return None

        resource = super(EthernetInterface, self).get(name)
        resource.update(dict(name=name, type='ethernet'))
        resource.update(self._parse_sflow(config))
        resource.update(self._parse_flowcontrol_send(config))
        resource.update(self._parse_flowcontrol_receive(config))
        return resource

    def _parse_sflow(self, config):
        """Scans the specified config block and returns the sflow value

        Args:
            config (str): The interface config block to scan

        Returns:
            dict: Returns a dict object with the sflow value retrieved
                from the config block.  The returned dict object is intended
                to be merged into the interface resource dict
        """
        value = 'no sflow' not in config
        return dict(sflow=value)

    def _parse_flowcontrol_send(self, config):
        """Scans the config block and returns the flowcontrol send value

        Args:
            config (str): The interface config block to scan

        Returns:
            dict: Returns a dict object with the flowcontrol send value
                retrieved from the config block.  The returned dict object
                is intended to be merged into the interface resource dict
        """
        value = 'off'
        match = re.search(r'flowcontrol send (\w+)$', config, re.M)
        if match:
            value = match.group(1)
        return dict(flowcontrol_send=value)

    def _parse_flowcontrol_receive(self, config):
        """Scans the config block and returns the flowcontrol receive value

        Args:
            config (str): The interface config block to scan

        Returns:
            dict: Returns a dict object with the flowcontrol receive value
                retrieved from the config block.  The returned dict object
                is intended to be merged into the interface resource dict
        """
        value = 'off'
        match = re.search(r'flowcontrol receive (\w+)$', config, re.M)
        if match:
            value = match.group(1)
        return dict(flowcontrol_receive=value)

    def create(self, name):
        """Create an Ethernet subinterface

        Args:
            name (string): The subinterface name. Ex: Ethernet1.1

        Raises:
            NotImplementedError: creating physical Ethernet interfaces is not
            supported. Only subinterfaces can be created.
        """
        if '.' not in name:
            raise NotImplementedError('creating physical Ethernet interfaces'
                                      ' is not supported. Only subinterfaces'
                                      ' can be created')
        return self.configure(['interface %s' % name])

    def delete(self, name):
        """Delete an Ethernet subinterfaces

        Args:
            name (string): The subinterface name. Ex: Ethernet1.1

        Raises:
            NotImplementedError: creating physical Ethernet interfaces is not
            supported. Only subinterfaces can be created.
        """
        if '.' not in name:
            raise NotImplementedError('deleting physical Ethernet interfaces'
                                      ' is not supported. Only subinterfaces'
                                      ' can be created')
        return self.configure(['no interface %s' % name])

    def set_flowcontrol_send(self, name, value=None, default=False,
                             disable=False):
        """Configures the interface flowcontrol send value

        Args:
            name (string): The interface identifier.  It must be a full
                interface name (ie Ethernet, not Et)

            value (boolean): True if the interface should enable sending flow
                control packets, otherwise False

            default (boolean): Specifies to default the interface flow
                control send value

            disable (boolean): Specifies to disable the interface flow
                control send value

        Returns:
            True if the operation succeeds otherwise False is returned
        """
        return self.set_flowcontrol(name, 'send', value, default, disable)

    def set_flowcontrol_receive(self, name, value=None, default=False,
                                disable=False):
        """Configures the interface flowcontrol receive value

        Args:
            name (string): The interface identifier.  It must be a full
                interface name (ie Ethernet, not Et)

            value (boolean): True if the interface should enable receiving
                flow control packets, otherwise False

            default (boolean): Specifies to default the interface flow
                control receive value

            disable (boolean): Specifies to disable the interface flow
                control receive value

        Returns:
            True if the operation succeeds otherwise False is returned
        """
        return self.set_flowcontrol(name, 'receive', value, default, disable)

    def set_flowcontrol(self, name, direction, value=None, default=False,
                        disable=False):
        """Configures the interface flowcontrol value

        Args:
            name (string): The interface identifier.  It must be a full
                interface name (ie Ethernet, not Et)

            direction (string): one of either 'send' or 'receive'

            value (boolean): True if the interface should enable flow control
                packet handling, otherwise False

            default (boolean): Specifies to default the interface flow control
                send or receive value

            disable (boolean): Specifies to disable the interface flow control
                send or receive value

        Returns:
            True if the operation succeeds otherwise False is returned
        """
        if value is not None:
            if value not in ['on', 'off']:
                raise ValueError('invalid flowcontrol value')

        if direction not in ['send', 'receive']:
            raise ValueError('invalid direction specified')

        commands = ['interface %s' % name]
        commands.append(self.command_builder('flowcontrol %s' % direction,
                                             value=value, default=default,
                                             disable=disable))
        return self.configure(commands)

    def set_sflow(self, name, value=None, default=False, disable=False):
        """Configures the sFlow state on the interface

        Args:
            name (string): The interface identifier.  It must be a full
                interface name (ie Ethernet, not Et)

            value (boolean): True if sFlow should be enabled otherwise False

            default (boolean): Specifies the default value for sFlow

            disable (boolean): Specifies to disable sFlow

        Returns:
            True if the operation succeeds otherwise False is returned
        """
        if value not in [True, False, None]:
            raise ValueError

        commands = ['interface %s' % name]
        commands.append(self.command_builder('sflow enable', value=value,
                                             default=default, disable=disable))
        return self.configure(commands)

    def set_vrf(self, name, vrf, default=False, disable=False):
        """Applies a VRF to the interface

           Note: VRF being applied to interface must already exist in switch
               config. Ethernet port must be in routed mode. This functionality
               can also be handled in the VRF api.

           Args:
               name (str): The interface identifier.  It must be a full
                   interface name (ie Ethernet, not Et)
               vrf (str): The vrf name to be applied to the interface
               default (bool): Specifies the default value for VRF
               disable (bool): Specifies to disable VRF

           Returns:
               True if the operation succeeds otherwise False is returned
        """
        commands = ['interface %s' % name]
        if self.version_number >= '4.23':
            commands.append(self.command_builder('vrf', vrf,
                                                 default=default,
                                                 disable=disable))
        else:
            commands.append(self.command_builder('vrf forwarding', vrf,
                                                 default=default,
                                                 disable=disable))
        return self.configure(commands)

class PortchannelInterface(BaseInterface):

    def __str__(self):
        return 'PortchannelInterface'

    def get(self, name):
        """Returns a Port-Channel interface as a set of key/value pairs

        Args:
            name (str): The interface identifier to retrieve from the
                running-configuration

        Returns:
            A Python dictionary object of key/value pairs that represents
            the interface configuration.  If the specified interface
            does not exist, then None is returned::

                {
                    "name": <string>,
                    "type": "portchannel",
                    "members": <arrary of interface names>,
                    "minimum_links: <integer>,
                    "lacp_mode": [on, active, passive]
                }

        """
        config = self.get_block('^interface %s' % name)
        if not config:
            return None

        response = super(PortchannelInterface, self).get(name)
        response.update(dict(name=name, type='portchannel'))

        response['members'] = self.get_members(name)
        response['lacp_mode'] = self.get_lacp_mode(name)
        response.update(self._parse_minimum_links(config))
        response.update(self._parse_lacp_timeout(config))
        response.update(self._parse_lacp_fallback(config))
        return response

    def _parse_minimum_links(self, config):
        value = 0
        match = re.search(r'port-channel min-links (\d+)', config)
        if match:
            value = int(match.group(1))
        return dict(minimum_links=value)

    def _parse_lacp_fallback(self, config):
        value = DEFAULT_LACP_FALLBACK
        match = re.search(r'lacp fallback (static|individual)', config)
        if match:
            value = match.group(1)
        return dict(lacp_fallback=value)

    def _parse_lacp_timeout(self, config):
        value = DEFAULT_LACP_FALLBACK_TIMEOUT
        match = re.search(r'lacp fallback timeout (\d+)', config)
        if match:
            value = int(match.group(1))
        return dict(lacp_timeout=value)

    def get_lacp_mode(self, name):
        """Returns the LACP mode for the specified Port-Channel interface

        Args:
            name(str): The Port-Channel interface name to return the LACP
                mode for from the configuration

        Returns:
            The configured LACP mode for the interface.  Valid mode values
                are 'on', 'passive', 'active'

        """
        members = self.get_members(name)
        if not members:
            return DEFAULT_LACP_MODE

        for member in self.get_members(name):
            match = re.search(r'channel-group\s\d+\smode\s(?P<value>.+)',
                              self.get_block('^interface %s' % member))
            return match.group('value')

    def get_members(self, name):
        """Returns the member interfaces for the specified Port-Channel

        Args:
            name(str): The Port-channel interface name to return the member
                interfaces for

        Returns:
            A list of physical interface names that belong to the specified
                interface
        """
        grpid = re.search(r'(\d+)', name).group()
        command = 'show port-channel %s all-ports' % grpid
        config = self.node.enable(command, 'text')
        return re.findall(r'\b(?!Peer)Ethernet[\d/]*\b',
                          config[0]['result']['output'])

    def set_members(self, name, members, mode=None):
        """Configures the array of member interfaces for the Port-Channel

        Args:
            name(str): The Port-Channel interface name to configure the member
                interfaces

            members(list): The list of Ethernet interfaces that should be
                member interfaces

            mode(str): The LACP mode to configure the member interfaces to.
                Valid values are 'on, 'passive', 'active'. When there are
                existing channel-group members and their lacp mode differs
                from this attribute, all of those members will be removed and
                then re-added using the specified lacp mode. If this attribute
                is omitted, the existing lacp mode will be used for new
                member additions.

        Returns:
            True if the operation succeeds otherwise False
        """
        commands = list()
        grpid = re.search(r'(\d+)', name).group()
        current_members = self.get_members(name)
        lacp_mode = self.get_lacp_mode(name)
        if mode and mode != lacp_mode:
            lacp_mode = mode
            self.set_lacp_mode(grpid, lacp_mode)

        # remove members from the current port-channel interface
        for member in set(current_members).difference(members):
            commands.append('interface %s' % member)
            commands.append('no channel-group %s' % grpid)

        # add new member interfaces to the port-channel interface
        for member in set(members).difference(current_members):
            commands.append('interface %s' % member)
            commands.append('channel-group %s mode %s' % (grpid, lacp_mode))

        return self.configure(commands) if commands else True

    def set_lacp_mode(self, name, mode):
        """Configures the LACP mode of the member interfaces

        Args:
            name(str): The Port-Channel interface name to configure the
                LACP mode

            mode(str): The LACP mode to configure the member interfaces to.
                Valid values are 'on, 'passive', 'active'

        Returns:
            True if the operation succeeds otherwise False
        """
        if mode not in ['on', 'passive', 'active']:
            return False

        grpid = re.search(r'(\d+)', name).group()

        remove_commands = list()
        add_commands = list()

        for member in self.get_members(name):
            remove_commands.append('interface %s' % member)
            remove_commands.append('no channel-group %s' % grpid)
            add_commands.append('interface %s' % member)
            add_commands.append('channel-group %s mode %s' % (grpid, mode))

        return self.configure(remove_commands + add_commands)

    def set_minimum_links(self, name, value=None, default=False,
                          disable=False):
        """Configures the Port-Channel min-links value

        Args:
            name(str): The Port-Channel interface name

            value(str): The value to configure the min-links

            default (bool): Specifies to default the port channel min-links
                value

            disable (bool): Specifies to disable the port channel min-links
                value

        Returns:
            True if the operation succeeds otherwise False is returned
        """
        commands = ['interface %s' % name]
        commands.append(self.command_builder('port-channel min-links',
                                             value=value, default=default,
                                             disable=disable))
        return self.configure(commands)

    def set_lacp_fallback(self, name, mode=None):
        """Configures the Port-Channel lacp_fallback

        Args:
            name(str): The Port-Channel interface name

            mode(str): The Port-Channel LACP fallback setting
                Valid values are 'disabled', 'static', 'individual':

                * static  - Fallback to static LAG mode
                * individual - Fallback to individual ports
                * disabled - Disable LACP fallback

        Returns:
            True if the operation succeeds otherwise False is returned
        """
        if mode not in ['disabled', 'static', 'individual']:
            return False
        disable = True if mode == 'disabled' else False
        commands = ['interface %s' % name]
        commands.append(self.command_builder('port-channel lacp fallback',
                                             value=mode, disable=disable))
        return self.configure(commands)

    def set_lacp_timeout(self, name, value=None):
        """Configures the Port-Channel LACP fallback timeout
           The fallback timeout configures the period an interface in
           fallback mode remains in LACP mode without receiving a PDU.

        Args:
            name(str): The Port-Channel interface name

            value(int): port-channel lacp fallback timeout in seconds

        Returns:
            True if the operation succeeds otherwise False is returned
        """
        commands = ['interface %s' % name]
        string = 'port-channel lacp fallback timeout'
        commands.append(self.command_builder(string, value=value))
        return self.configure(commands)


class VxlanInterface(BaseInterface):

    DEFAULT_SRC_INTF = ''
    DEFAULT_MCAST_GRP = ''

    def __str__(self):
        return 'VxlanInterface'

    def get(self, name):
        """Returns a Vxlan interface as a set of key/value pairs

        The Vxlan interface resource returns the following:

            * name (str): The name of the interface
            * type (str): Always returns 'vxlan'
            * source_interface (str): The vxlan source-interface value
            * multicast_group (str): The vxlan multicast-group value
            * udp_port (int): The vxlan udp-port value
            * vlans (dict): The vlan to vni mappings
            * flood_list (list): The list of global VTEP flood list
            * multicast_decap (bool): If the multicast decap
                                      feature is configured

        Args:
            name (str): The interface identifier to retrieve from the
                running-configuration

        Returns:
            A Python dictionary object of key/value pairs that represents
                the interface configuration.  If the specified interface
                does not exist, then None is returned
        """
        config = self.get_block('^interface %s' % name)
        if not config:
            return None

        response = super(VxlanInterface, self).get(name)
        response.update(dict(name=name, type='vxlan'))

        response.update(self._parse_source_interface(config))
        response.update(self._parse_multicast_group(config))
        response.update(self._parse_udp_port(config))
        response.update(self._parse_vlans(config))
        response.update(self._parse_flood_list(config))
        response.update(self._parse_multicast_decap(config))

        return response

    def _parse_source_interface(self, config):
        """ Parses the conf block and returns the vxlan source-interface value

        Parses the provided configuration block and returns the value of
        vxlan source-interface.  If the value is not configured, this method
        will return DEFAULT_SRC_INTF instead.

        Args:
            config (str): The Vxlan config block to scan

        Return:
            dict: A dict object intended to be merged into the resource dict
        """
        match = re.search(r'vxlan source-interface ([^\s]+)', config)
        value = match.group(1) if match else self.DEFAULT_SRC_INTF
        return dict(source_interface=value)

    def _parse_multicast_group(self, config):
        match = re.search(r'vxlan multicast-group '
                          r'([\d]{3}\.[\d]+\.[\d]+\.[\d]+)',
                          config)
        value = match.group(1) if match else self.DEFAULT_MCAST_GRP
        return dict(multicast_group=value)

    def _parse_multicast_decap(self, config):
        val1 = 'vxlan multicast-group decap' in config
        val2 = 'no vxlan multicast-group decap' in config
        return dict( multicast_decap=bool(val1 ^ val2) )

    def _parse_udp_port(self, config):
        match = re.search(r'vxlan udp-port (\d+)', config)
        value = int(match.group(1))
        return dict(udp_port=value)

    def _parse_vlans(self, config):
        vlans = frozenset(re.findall(r'vxlan vlan (\d+)', config))
        values = dict()

        for vid in vlans:
            values[vid] = dict()

            regexp = r'vxlan vlan {} vni (\d+)'.format(vid)
            match = re.search(regexp, config)
            values[vid]['vni'] = match.group(1) if match else None

            regexp = r'vxlan vlan {} flood vtep (.*)$'.format(vid)
            matches = re.search(regexp, config, re.M)
            flood_list = matches.group(1).split(' ') if matches else []
            values[vid]['flood_list'] = flood_list

        return dict(vlans=values)

    def _parse_flood_list(self, config):
        match = re.search(r'^ *vxlan flood vtep +([\d. ]+)$', config, re.M)
        values = list()
        if match:
            values = match.group(1).split(' ')
        return dict(flood_list=values)

    def set_source_interface(self, name, value=None, default=False,
                             disable=False):
        """Configures the Vxlan source-interface value

        EosVersion:
            4.13.7M

        Args:
            name(str): The interface identifier to configure, defaults to
                Vxlan1
           value(str): The value to configure the source-interface to
           default(bool): Configures the source-interface value to default
           disable(bool): Negates the source-interface

        Returns:
            True if the operation succeeds otherwise False
        """
        string = 'vxlan source-interface'
        cmds = self.command_builder(string, value=value, default=default,
                                    disable=disable)
        return self.configure_interface(name, cmds)

    def set_multicast_group(self, name, value=None, default=False,
                            disable=False):
        """Configures the Vxlan multicast-group value

        EosVersion:
            4.13.7M

        Args:
            name(str): The interface identifier to configure, defaults to
                Vxlan1
           value(str): The value to configure the multicast-group to
           default(bool): Configures the mulitcast-group value to default
           disable(bool): Negates the multicast-group value

        Returns:
            True if the operation succeeds otherwise False
        """
        string_dpr = 'vxlan multicast-group'
        cmds_dpr = self.command_builder(string_dpr,
            value=value, default=default, disable=disable)
        string_new = 'vxlan multicast-group decap'
        cmds_new = self.command_builder(string_new,
            value=value, default=default, disable=disable)
        return self.configure_interface(name,
            CliVariants(cmds_new, cmds_dpr) )

    def set_multicast_decap(self, name, default=False,
                            disable=False):
        """Configures the Vxlan multicast-group decap feature

        EosVersion:
            4.15.0M

        Args:
            name(str): The interface identifier to configure, defaults to
                Vxlan1
           default(bool): Configures the mulitcast-group decap value to default
           disable(bool): Negates the multicast-group decap value

        Returns:
            True if the operation succeeds otherwise False
        """
        string = 'vxlan multicast-group decap'
        if default or disable:
            cmds = self.command_builder(string, value=None, default=default,
                                        disable=disable)
        else:
            cmds = [string]
        return self.configure_interface(name, cmds)


    def set_udp_port(self, name, value=None, default=False, disable=False):
        """Configures vxlan udp-port value

        EosVersion:
            4.13.7M

        Args:
            name(str): The name of the interface to configure
            value(str): The value to set udp-port to
            default(bool): Configure using the default keyword
            disable(bool): Negate the udp-port value

        Returns:
            True if the operation succeeds otherwise False
        """
        string = 'vxlan udp-port'
        cmds = self.command_builder(string, value=value, default=default,
                                    disable=disable)
        return self.configure_interface(name, cmds)

    def add_vtep(self, name, vtep, vlan=None):
        """Adds a new VTEP endpoint to the global or local flood list

        EosVersion:
            4.13.7M

        Args:
            name (str): The name of the interface to configure
            vtep (str): The IP address of the remote VTEP endpoint to add
            vlan (str): The VLAN ID associated with this VTEP.  If the VLAN
            keyword is used, then the VTEP is configured as a local flood
            endpoing

        Returns:
            True if the command completes successfully
        """
        if not vlan:
            cmd = 'vxlan flood vtep add {}'.format(vtep)
        else:
            cmd = 'vxlan vlan {} flood vtep add {}'.format(vlan, vtep)
        return self.configure_interface(name, cmd)

    def remove_vtep(self, name, vtep, vlan=None):
        """Removes a VTEP endpoint from the global or local flood list

        EosVersion:
            4.13.7M

        Args:
            name (str): The name of the interface to configure
            vtep (str): The IP address of the remote VTEP endpoint to add
            vlan (str): The VLAN ID associated with this VTEP.  If the VLAN
            keyword is used, then the VTEP is configured as a local flood
            endpoing

        Returns:
            True if the command completes successfully
        """
        if not vlan:
            cmd = 'vxlan flood vtep remove {}'.format(vtep)
        else:
            cmd = 'vxlan vlan {} flood vtep remove {}'.format(vlan, vtep)
        return self.configure_interface(name, cmd)

    def update_vlan(self, name, vid, vni):
        """Adds a new vlan to vni mapping for the interface

        EosVersion:
            4.13.7M

        Args:
            vlan (str, int): The vlan id to map to the vni
            vni (str, int): The vni value to use

        Returns:
            True if the command completes successfully

        """
        cmd = 'vxlan vlan add %s vni %s' % (vid, vni)
        return self.configure_interface(name, cmd)

    def remove_vlan(self, name, vid):
        """Removes a vlan to vni mapping for the interface

        EosVersion:
            4.13.7M

        Args:
            vlan (str, int): The vlan id to map to the vni

        Returns:
            True if the command completes successfully

        """
        return self.configure_interface( name,
            CliVariants(f'vxlan vlan remove {vid} vni $',
                f'vxlan vlan remove {vid} vni') )


INTERFACE_CLASS_MAP = {
    'Et': EthernetInterface,
    'Po': PortchannelInterface,
    'Vx': VxlanInterface
}


def instance(api):
    return Interfaces(api)
