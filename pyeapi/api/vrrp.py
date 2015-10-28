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
"""Module for working with EOS VRRP resources

The Vrrp resource provides configuration management of interface specific
vrrp resources on and EOS node. It provides the following class
implementations:

    * Vrrp - Configure vrrps in EOS

Vrrp Attributes:
    enable (boolean): The shutdown state of the vrrp
    primary_ip (string): The ip address of the vrrp
    secondary_ip (dict): The secondary ip addresses configured for the vrrp
                         This is a dictionary in the format
                            { key: [ list of ip addresses ] }
                         where key is 'add', 'remove', or 'exists'. 'add' is
                         used to add the list of secondary ip addresses
                         to the vrrp. 'remove' will remove the list of
                         secondary ip addresses from the vrrp. 'exists' is
                         a report only key for retrieving the current
                         secondary ip addresses on a vrrp.
    priority (int): The priority rank of the vrrp
    description (string): The description for the vrrp
    ip_version (int): The ip version value for the vrrp
    timers_advertise (int): The timers advertise setting for the vrrp
    mac_address_advertisement_interval (int): The mac-address advertisement-
                                              interval setting for the vrrp
    preempt (boolean): The preempt state of the vrrp
    preempt_delay_minimum (int): The preempt delay minimum setting for the vrrp
    preempt_delay_reload (int): The preempt delay reload setting for the vrrp
    delay_reload (int): The delay reload setting for the vrrp
    authentication (string): The authentication setting for the vrrp
    track (dict): The object tracking settings for the vrrp
    bfd_ip (string): The bfd ip set for the vrrp

Notes:
    The get method will return a dictionary of all the currently configured
    vrrps on a single interface, with the VRID of each vrrp as the keys
    in the dictionary:
        {
            vrrp1: { data },
            vrrp2: { data },
        }

    The getall method will return a dictionary of all the currently configured
    vrrps on the node, with the interface name as the top-level keys, with
    the VRIDs for each vrrp on an interface as a sub-key of that interface:
        {
            interface1: {
                vrrp1: { data },
                vrrp2: { data },
            },
            interface2: {
                vrrp1: { data },
                vrrp2: { data },
            }
        }

    The data for a configured vrrp is a dictionary with the following format:
        {
            enable: <True|False>
            primary_ip: <string>
            priority: <int>
            description: <string|None>
            secondary_ip: {
                exists: [ <ip string1>, <ip string2> ]
                }
            ip_version: <int>
            timers_advertise: <int>
            mac_address_advertisement_interval: <int>
            preempt: <True|False>
            preempt_delay_minimum: <int>
            preempt_delay_reload: <int>
            delay_reload: <int>
            authentication: <string|None>
            track: {
                (<object name>, <shutdown|decrement>): <int|True>,
                (<object name>, <shutdown|decrement>): <int|True>,
                }
            bfd_ip: <string>
        }

    The create and update methods accept a kwargs dictionary which
    defines the properties to be applied to the new or existing vrrp
    configuration. The available keywords and values are as follows:
        enable: True to enable (no shutdown)|False to disable (shutdown)
        primary_ip: <ip_string>|no|default|None
        priority: <int>|no|default|None
        description: <string>|no|default|None
        secondary_ip: <dict> may include the following:
            add: <list of ip address strings>
            remove: <list of ip address strings>
        ip_version: <int>|no|default|None
        timers_advertise: <int>|no|default|None
        mac_address_advertisement_interval: <int>|no|default|None
        preempt: True to enable (preempt)|False to disable (no preempt)
        preempt_delay_minimum: <int>|no|default|None
        preempt_delay_reload: <int>|no|default|None
        delay_reload: <int>|no|default|None
        authentication: <string> NOTE: currently not implemented
        track: <dict> consisting of entries in the following format:
            (<object name string>, <shutdown|decrement>): <amount>
                for shutdown, <amount> may be one of the following:
                    no|None: disable shutdown tracking for the named object
                    default: default shutdown tracking for the named object
                    <any value>: enable shutdown tracking for the named object
                for decrement, <amount> may be one of the following:
                    no|None: disable decremental tracking for the named object
                    default: default decremental tracking for the named object
                    <int>: set the decrement amount for the named object
        bfd_ip: <ip string>|no|default|None

"""

import re

from pyeapi.api import EntityCollection

ENABLED = {'no': False, '': True}
SHUTDOWN = {'no': True, '': False}
PROPERTIES = ['primary_ip', 'priority', 'description', 'secondary_ip',
              'ip_version', 'enable', 'timers_advertise',
              'mac_address_advertisement_interval', 'preempt',
              'preempt_delay_minimum', 'preempt_delay_reload',
              'delay_reload', 'authentication', 'track', 'bfd_ip']


class Vrrp(EntityCollection):
    """The Vrrp class provides management of the VRRP configuration

    The Vrrp class is derived from EntityCollection and provides an API for
    working with the node's vrrp configurations.
    """

    def get(self, name):
        """Get the vrrp configurations for a single node interface

        Args:
            name (string): The name of the interface for which vrrp
                configurations will be retrieved.

        Returns:
            A dictionary containing the vrrp configurations on the interface.
            Returns None if no vrrp configurations are defined or
            if the interface is not configured.
        """

        # Validate the interface and vrid are specified
        interface = name
        if not interface:
            raise ValueError("Vrrp.get(): interface must contain a value.")

        # Get the config for the interface. Return None if the
        # interface is not defined
        config = self.get_block('interface %s' % interface)
        if config is None:
            return config

        # Find all occurrences of vrids in this interface and make
        # a set of the unique vrid numbers
        match = set(re.findall(r'^\s+(?:no |)vrrp (\d+)', config, re.M))
        if not match:
            return None

        # Initialize the result dict
        result = dict()

        for vrid in match:
            subd = dict()

            # Parse the vrrp configuration for the vrid(s) in the list
            subd.update(self._parse_authentication(config, vrid))
            subd.update(self._parse_delay_reload(config, vrid))
            subd.update(self._parse_description(config, vrid))
            subd.update(self._parse_enable(config, vrid))
            subd.update(self._parse_ip_version(config, vrid))
            subd.update(self._parse_mac_addr_adv_interval(config, vrid))
            subd.update(self._parse_preempt(config, vrid))
            subd.update(self._parse_preempt_delay_minimum(config, vrid))
            subd.update(self._parse_preempt_delay_reload(config, vrid))
            subd.update(self._parse_primary_ip(config, vrid))
            subd.update(self._parse_priority(config, vrid))
            subd.update(self._parse_secondary_ip(config, vrid))
            subd.update(self._parse_timers_advertise(config, vrid))
            subd.update(self._parse_track(config, vrid))
            subd.update(self._parse_bfd_ip(config, vrid))

            result.update({int(vrid): subd})

        # If result dict is empty, return None, otherwise return result
        return result if result else None

    def getall(self):
        """Get the vrrp configurations for all interfaces on a node

        Returns:
            A dictionary containing the vrrp configurations on the node,
            keyed by interface.
        """

        vrrps = dict()

        # Find the available interfaces
        interfaces = re.findall(r'^interface\s(\S+)', self.config, re.M)

        # Get the vrrps defined for each interface
        for interface in interfaces:
            vrrp = self.get(interface)
            # Only add those interfaces that have vrrps defined
            if vrrp:
                vrrps.update({interface: vrrp})

        return vrrps

    def _parse_primary_ip(self, config, vrid):
        match = re.search(r'^\s+vrrp %s ip (\d+\.\d+\.\d+\.\d+)$' %
                          vrid, config, re.M)
        value = match.group(1) if match else None
        return dict(primary_ip=value)

    def _parse_priority(self, config, vrid):
        match = re.search(r'^\s+vrrp %s priority (\d+)$' % vrid, config, re.M)
        value = int(match.group(1)) if match else None
        return dict(priority=value)

    def _parse_timers_advertise(self, config, vrid):
        match = re.search(r'^\s+vrrp %s timers advertise (\d+)$' %
                          vrid, config, re.M)
        value = int(match.group(1)) if match else None
        return dict(timers_advertise=value)

    def _parse_preempt(self, config, vrid):
        match = re.search(r'^\s+(no|) vrrp %s preempt$' % vrid, config, re.M)
        value = match.group(1) if match else None
        value = ENABLED.get(value, 'Error')
        return dict(preempt=value)

    def _parse_enable(self, config, vrid):
        match = re.search(r'^\s+(no|) vrrp %s shutdown$' % vrid, config, re.M)
        value = match.group(1) if match else None
        value = SHUTDOWN.get(value, 'Error')
        return dict(enable=value)

    def _parse_secondary_ip(self, config, vrid):
        matches = re.findall(r'^\s+vrrp %s ip (\d+\.\d+\.\d+\.\d+) '
                             r'secondary$' % vrid, config, re.M)
        value = matches if matches else None
        return dict(secondary_ip={'exists': value})

    def _parse_description(self, config, vrid):
        match = re.search(r'^\s+(no|) vrrp %s description(.*)$' %
                          vrid, config, re.M)
        enabled = match.group(1) if match else None
        enabled = ENABLED.get(enabled, 'Error')
        value = match.group(2).lstrip() if enabled is True else ''
        value = match.group(2).lstrip()
        return dict(description=value)

    def _parse_mac_addr_adv_interval(self, config, vrid):
        match = re.search(r'^\s+vrrp %s mac-address advertisement-interval '
                          r'(\d+)$' % vrid, config, re.M)
        value = int(match.group(1)) if match else None
        return dict(mac_address_advertisement_interval=value)

    def _parse_preempt_delay_minimum(self, config, vrid):
        match = re.search(r'^\s+vrrp %s preempt delay minimum (\d+)$' %
                          vrid, config, re.M)
        value = int(match.group(1)) if match else None
        return dict(preempt_delay_minimum=value)

    def _parse_preempt_delay_reload(self, config, vrid):
        match = re.search(r'^\s+vrrp %s preempt delay reload (\d+)$' %
                          vrid, config, re.M)
        value = int(match.group(1)) if match else None
        return dict(preempt_delay_reload=value)

    def _parse_authentication(self, config, vrid):
        match = re.search(r'^\s+(no|) vrrp %s authentication'
                          r'($| ietf-md5 key-string 7 .*$| text .*$)' %
                          vrid, config, re.M)
        enabled = match.group(1) if match else None
        enabled = ENABLED.get(enabled)
        value = match.group(2).lstrip() if enabled is True else ''
        return dict(authentication=value)

    def _parse_bfd_ip(self, config, vrid):
        match = re.search(r'^\s+(no|) vrrp %s bfd ip'
                          r'(?: (\d+\.\d+\.\d+\.\d+)|)$' %
                          vrid, config, re.M)
        enabled = match.group(1) if match else None
        enabled = ENABLED.get(enabled, 'Error')
        value = match.group(2) if enabled is True else ''
        return dict(bfd_ip=value)

    def _parse_ip_version(self, config, vrid):
        match = re.search(r'^\s+vrrp %s ip version (\d+)$' %
                          vrid, config, re.M)
        value = int(match.group(1)) if match else None
        return dict(ip_version=value)

    def _parse_delay_reload(self, config, vrid):
        match = re.search(r'^\s+vrrp %s delay reload (\d+)$' %
                          vrid, config, re.M)
        value = int(match.group(1)) if match else None
        return dict(delay_reload=value)

    def _parse_track(self, config, vrid):
        matches = re.findall(r'^\s+vrrp %s track (\S+) '
                             r'(decrement|shutdown)(?:( \d+$|$))' %
                             vrid, config, re.M)
        value = dict()
        for match in matches:
            object = match[0]
            action = match[1]
            amount = None if match[2] == '' else int(match[2])
            key = (object, action)
            value.update({key: amount})
        return dict(track=value)

    def create(self, interface, vrid, **kwargs):
        """Creates a vrrp instance from an interface

        Note:
            This method will attempt to create a vrrp in the node's
            operational config. If the vrrp already exists on the
            interface, then this method will set the properties of
            the existing vrrp to those that have been passed in, if
            possible.

        Args:
            interface (string): The interface to configure.
            vrid (integer): The vrid number for the vrrp to be created.
            kwargs (dict): A dictionary specifying the properties to
                be applied to the new vrrp instance. See library
                documentation for available keys and values.

        Returns:
            True if the vrrp could be created otherwise False (see Node)

        """

        if 'enable' not in kwargs:
            kwargs['enable'] = False

        return self._vrrp_set(interface, vrid, **kwargs)

    def delete(self, interface, vrid):
        """Deletes a vrrp instance from an interface

        Note:
            This method will attempt to delete the vrrp from the node's
            operational config. If the vrrp does not exist on the
            interface then this method will not perform any changes
            but still return True

        Args:
            interface (string): The interface to configure.
            vrid (integer): The vrid number for the vrrp to be deleted.

        Returns:
            True if the vrrp could be deleted otherwise False (see Node)

        """

        vrrp_str = "no vrrp %d" % vrid
        return self.configure_interface(interface, vrrp_str)

    def default(self, interface, vrid):
        """Defaults a vrrp instance from an interface

        Note:
            This method will attempt to default the vrrp on the node's
            operational config. Default results in the deletion of the
            specified vrrp . If the vrrp does not exist on the
            interface then this method will not perform any changes
            but still return True

        Args:
            interface (string): The interface to configure.
            vrid (integer): The vrid number for the vrrp to be defaulted.

        Returns:
            True if the vrrp could be defaulted otherwise False (see Node)

        """

        vrrp_str = "default vrrp %d" % vrid
        return self.configure_interface(interface, vrrp_str)

    def update(self, interface, vrid, **kwargs):
        """Update a vrrp instance from an interface

        Note:
            This method will attempt to set parameters for the vrrp on
            the node's operational config. Parameters specified in the
            kwargs argument will be matched against the current
            parameters for the vrrp, and only those parameters that
            have changed from the current configuration will be updated.

        Args:
            interface (string): The interface to configure.
            vrid (integer): The vrid number for the vrrp to be updated.
            kwargs (dict): A dictionary specifying the properties to
                be applied to the vrrp instance. See library documentation
                for available keys and values.

        Returns:
            True if the vrrp could be updated otherwise False (see Node)

        """

        update = dict(kwargs)

        # Get the current configuration for the vrrp from the switch.
        # Raise an error if the vrrp does not exist on the interface.
        try:
            current = self.get(interface)[vrid]
        except:
            raise ValueError("Attempt to configure a non-existent vrrp")

        # Keep only those properties in the update dictionary that
        # are different than the current vrrp configuration.
        for prop in PROPERTIES:
            if prop in update:
                if update[prop] == current[prop]:
                    del update[prop]

        # Configure the vrrp
        return self._vrrp_set(interface, vrid, **update)

    def _vrrp_set(self, interface, vrid, **kwargs):
        # Configure the commands to create or update a vrrp
        # configuration, and send the commands to the node.

        vrconf = kwargs

        # step through the individual vrrp properties and
        # set those that need to be changed
        commands = []

        primary_ip = vrconf.get('primary_ip', '__NONE__')
        if primary_ip != '__NONE__':
            if primary_ip in ('no', None):
                vrrps = self.get(interface)
                primary_ip = vrrps[vrid]['primary_ip']
                commands.append("no vrrp %d ip %s" % (vrid, primary_ip))
            elif primary_ip is 'default':
                vrrps = self.get(interface)
                primary_ip = vrrps[vrid]['primary_ip']
                commands.append("default vrrp %d ip %s" % (vrid, primary_ip))
            else:
                commands.append("vrrp %d ip %s" % (vrid, primary_ip))

        priority = vrconf.get('priority', '__NONE__')
        if priority != '__NONE__':
            if priority in ('no', None):
                commands.append("no vrrp %d priority" % vrid)
            elif priority == 'default':
                commands.append("default vrrp %d priority" % vrid)
            else:
                commands.append("vrrp %d priority %d" % (vrid, priority))

        description = vrconf.get('description', '__NONE__')
        if description != '__NONE__':
            if description in ('no', None):
                commands.append("no vrrp %d description" % vrid)
            elif description == 'default':
                commands.append("default vrrp %d description" % vrid)
            else:
                commands.append("vrrp %d description %s" % (vrid, description))

        secondary_ip = vrconf.get('secondary_ip', '__NONE__')
        if secondary_ip != '__NONE__':
            secondary_add = secondary_ip.get('add', '__NONE__')
            secondary_remove = secondary_ip.get('remove', '__NONE__')
            if secondary_add != '__NONE__':
                for s_ip in secondary_add:
                    commands.append("vrrp %d ip %s secondary" % (vrid, s_ip))
            if secondary_remove != '__NONE__':
                for s_ip in secondary_remove:
                    commands.append("no vrrp %d ip %s secondary"
                                    % (vrid, s_ip))

        ip_version = vrconf.get('ip_version', '__NONE__')
        if ip_version != '__NONE__':
            if ip_version in ('no', None):
                commands.append("no vrrp %d ip version" % vrid)
            elif ip_version == 'default':
                commands.append("default vrrp %d ip version" % vrid)
            elif ip_version in (2, 3):
                commands.append("vrrp %d ip version %d" % (vrid, ip_version))
            else:
                raise ValueError("vrrp property 'ip_version' must be "
                                 "2, 3, 'no', 'default', or None")

        enable = vrconf.get('enable', '__NONE__')
        if enable != '__NONE__':
            if enable in ('no', True):
                commands.append("no vrrp %d shutdown" % vrid)
            elif enable is False:
                commands.append("vrrp %d shutdown" % vrid)
            elif enable == 'default':
                commands.append("default vrrp %d shutdown" % vrid)
            else:
                raise ValueError("vrrp property 'enable' must "
                                 "be True, False, 'no', or 'default'")

        timers_advertise = vrconf.get('timers_advertise', '__NONE__')
        if timers_advertise != '__NONE__':
            if timers_advertise in ('no', None):
                commands.append("no vrrp %d timers advertise" % vrid)
            elif timers_advertise == 'default':
                commands.append("default vrrp %d timers advertise" % vrid)
            elif 1 <= timers_advertise <= 255:
                commands.append("vrrp %d timers advertise %d"
                                % (vrid, timers_advertise))
            else:
                raise ValueError("vrrp property 'timers_advertise' must "
                                 "be in the range 1-255, 'no', 'default', "
                                 "or None")

        mac_add_adv_int = \
            vrconf.get('mac_address_advertisement_interval', '__NONE__')
        if mac_add_adv_int != '__NONE__':
            if mac_add_adv_int in ('no', None):
                commands.append("no vrrp %d mac-address "
                                "advertisement-interval" % vrid)
            elif mac_add_adv_int == 'default':
                commands.append("default vrrp %d mac-address "
                                "advertisement-interval" % vrid)
            elif 1 <= mac_add_adv_int <= 3600:
                commands.append("vrrp %d mac-address advertisement-interval %d"
                                % (vrid, mac_add_adv_int))
            else:
                raise ValueError("vrrp property 'mac_address_advertisement_"
                                 "interval must be in the range 1-3600, 'no', "
                                 "'default', or None")

        preempt = vrconf.get('preempt', '__NONE__')
        if preempt != '__NONE__':
            if preempt in ('no', False):
                commands.append("no vrrp %d preempt" % vrid)
            elif preempt == 'default':
                commands.append("default vrrp %d preempt" % vrid)
            elif preempt is True:
                commands.append("vrrp %d preempt" % vrid)
            else:
                raise ValueError("vrrp property 'preempt' must "
                                 "be True, False, 'no', or 'default'")

        preempt_delay_minimum = vrconf.get('preempt_delay_minimum',
                                           '__NONE__')
        if preempt_delay_minimum != '__NONE__':
            if preempt_delay_minimum in ('no', None):
                commands.append("no vrrp %d preempt delay minimum" % vrid)
            elif preempt_delay_minimum == 'default':
                commands.append("default vrrp %d preempt delay minimum" % vrid)
            elif 0 <= preempt_delay_minimum <= 3600:
                commands.append("vrrp %d preempt delay minimum %d" %
                                (vrid, preempt_delay_minimum))
            else:
                raise ValueError("vrrp property 'preempt_delay_minimum' "
                                 "must an integer in the range 0-3600, None "
                                 "'no', or 'default'")

        preempt_delay_reload = vrconf.get('preempt_delay_reload', '__NONE__')
        if preempt_delay_reload != '__NONE__':
            if preempt_delay_reload in ('no', None):
                commands.append("no vrrp %d preempt delay reload" % vrid)
            elif preempt_delay_reload == 'default':
                commands.append("default vrrp %d preempt delay reload" % vrid)
            elif 0 <= preempt_delay_reload <= 3600:
                commands.append("vrrp %d preempt delay reload %d" %
                                (vrid, preempt_delay_reload))
            else:
                raise ValueError("vrrp property 'preempt_delay_reload' "
                                 "must be an integer in the range 0-3600, "
                                 "None, 'no', or 'default'")

        delay_reload = vrconf.get('delay_reload', '__NONE__')
        if delay_reload != '__NONE__':
            if delay_reload in ('no', None):
                commands.append("no vrrp %d delay reload" % vrid)
            elif delay_reload == 'default':
                commands.append("default vrrp %d delay reload" % vrid)
            elif 0 <= delay_reload <= 3600:
                commands.append("vrrp %d delay reload %d" %
                                (vrid, delay_reload))
            else:
                raise ValueError("vrrp property 'delay_reload' "
                                 "must be an integer in the range 0-3600, "
                                 "None, 'no', or 'default'")

        authentication = vrconf.get('authentication', '__NONE__')
        if authentication != '__NONE__':
            pass
            # XXX not yet implemented
            # needs some handling, because input string does not
            # necessarily match the status string.

        track = vrconf.get('track', '__NONE__')
        if track != '__NONE__':
            for (key, amount) in track.iteritems():
                (tracked, action) = key
                if amount in ('no', None):
                    commands.append("no vrrp %d track %s %s"
                                    % (vrid, tracked, action))
                elif amount is 'default':
                    commands.append("default vrrp %d track %s %s"
                                    % (vrid, tracked, action))
                elif action == 'shutdown':
                    # if action is shutdown, and amount is not 'no', None,
                    # or 'default, track shutdown for this object
                    commands.append("vrrp %d track %s %s"
                                    % (vrid, tracked, action))
                elif amount is int(amount) and action == 'decrement':
                    # if the amount is an integer and the action is
                    # decrement, use decremental tracking for this object
                    commands.append("vrrp %d track %s %s %d"
                                    % (vrid, tracked, action, amount))
                else:
                    # The action/amount combination did not match above,
                    # there is something wrong.
                    raise ValueError("vrrp property 'track' contains "
                                     "improperly formatted data (%s, %s): "
                                     "%s. See library documentation for "
                                     "formatting example."
                                     % (tracked, action, amount))

        bfd_ip = vrconf.get('bfd_ip', '__NONE__')
        if bfd_ip != '__NONE__':
            if bfd_ip in ('no', None):
                commands.append("no vrrp %d bfd ip" % vrid)
            elif bfd_ip == 'default':
                commands.append("default vrrp %d bfd ip" % vrid)
            else:
                commands.append("vrrp %d bfd ip %s" % (vrid, bfd_ip))

        # Send the commands to the requested interface
        result = self.configure_interface(interface, commands)
        # And verify the commands succeeded
        if result is False:
            return self.error
        return result

    def vrconf_format(self, vrconfig):
        """Formats a vrrp configuration dictionary to match the
        information as presented from the get and getall methods.
        vrrp configuration dictionaries passed to the create and update
        methods may contain data for setting properties which results
        in a default value on the node. In these instances, the data
        for setting or changing the property is replaced with the
        value that would be returned from the get and getall methods.

        Intended for validating updated vrrp configurations.
        """

        fixed = dict(vrconfig)

        # primary_ip: default, no, None results in address of 0.0.0.0
        if fixed['primary_ip'] in ('no', 'default', None):
            fixed['primary_ip'] = '0.0.0.0'
        # priority: default, no, None results in priority of 100
        if fixed['priority'] in ('no', 'default', None):
            fixed['priority'] = 100
        # description: default, no, None results in None
        if fixed['description'] in ('no', 'default', None):
            fixed['description'] = None
        # secondary_ip: add key becomes exists key
        if 'secondary_ip' in fixed:
            if 'add' in dict(fixed['secondary_ip']):
                fixed['secondary_ip']['exists'] = fixed['secondary_ip']['add']
                del fixed['secondary_ip']['add']
            if 'remove' in fixed['secondary_ip']:
                del fixed['secondary_ip']['remove']
        # # secondary_ip: default, no, None results in None
        # if fixed['secondary_ip'] in ('no', 'default', None):
        #     fixed['secondary_ip'] = None
        # ip_version: default, no, None results in value of 2
        if fixed['ip_version'] in ('no', 'default', None):
            fixed['ip_version'] = 2
        # timers_advertise: default, no, None results in value of 1
        if fixed['timers_advertise'] in ('no', 'default', None):
            fixed['timers_advertise'] = 1
        # mac_address_advertisement_interaval:
        #    default, no, None results in value of 30
        if fixed['mac_address_advertisement_interval'] in \
                ('no', 'default', None):
            fixed['mac_address_advertisement_interval'] = 30
        # preempt: default, no results in value of False
        if fixed['preempt'] in ('no', 'default'):
            fixed['preempt'] = False
        # preempt_delay_minimum: default, no, None results in value of 0
        if fixed['preempt_delay_minimum'] in ('no', 'default', None):
            fixed['preempt_delay_minimum'] = 0
        # preempt_delay_reload: default, no, None results in value of 0
        if fixed['preempt_delay_reload'] in ('no', 'default', None):
            fixed['preempt_delay_reload'] = 0
        # delay_reload: default, no, None results in value of 0
        if fixed['delay_reload'] in ('no', 'default', None):
            fixed['delay_reload'] = 0
        # authenticetion -> XXX needs implemented
        # track: default, no, None removes the entry
        if 'track' in fixed:
            # Work with a temporary copy to keep things straight
            tracks = {}
            for (key, amount) in fixed['track'].iteritems():
                (tracked, action) = key
                if amount in ('no', 'default', None):
                    # This tracked object should have been deleted
                    # from the config. Do not keep it in the dictionary.
                    pass
                elif action == 'shutdown':
                    # This is a valid tracked shutdown. Set it's value to None.
                    tracks[key] = None
                else:
                    # This is a valid decerment. Copy it exactly.
                    tracks[key] = amount
            # Copy back the temporary dict into the original
            fixed['track'] = dict(tracks)
        # bfd_ip: default, no, None results in ''
        if fixed['bfd_ip'] in ('no', 'default', None):
            fixed['bfd_ip'] = ''

        return fixed


def instance(node):
    """Returns an instance of Vrrp

    Args:
        node (Node): The node argument passes an instance of Node to the
            resource

    Returns:
        object: An instance of Vrrp
    """
    return Vrrp(node)
