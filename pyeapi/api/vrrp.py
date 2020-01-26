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
    - enable (boolean): The shutdown state of the vrrp
    - primary_ip (string): The ip address of the vrrp
    - secondary_ip (dict): The secondary ip addresses configured for the vrrp
        This is a dictionary in the format::

            { key: [ list of ip addresses ] }

        where key is 'add', 'remove', or 'exists'. 'add' is
        used to add the list of secondary ip addresses
        to the vrrp. 'remove' will remove the list of
        secondary ip addresses from the vrrp. 'exists' is
        a report only key for retrieving the current
        secondary ip addresses on a vrrp.

    - priority (int): The priority rank of the vrrp
    - description (string): The description for the vrrp
    - ip_version (int): The ip version value for the vrrp
    - timers_advertise (int): The timers advertise setting for the vrrp
    - mac_addr_adv_interval (int): The mac-address advertisement-interval
        setting for the vrrp

    - preempt (boolean): The preempt state of the vrrp
    - preempt_delay_min (int): The preempt delay minimum setting for the vrrp
    - preempt_delay_reload (int): The preempt delay reload setting for the vrrp
    - delay_reload (int): The delay reload setting for the vrrp
    - track (list): The object tracking settings for the vrrp
    - bfd_ip (string): The bfd ip set for the vrrp

Notes:
    The get method will return a dictionary of all the currently configured
    vrrps on a single interface, with the VRID of each vrrp as the keys
    in the dictionary::

        {
            vrrp1: { data },
            vrrp2: { data },
        }

    The getall method will return a dictionary of all the currently configured
    vrrps on the node, with the interface name as the top-level keys, with
    the VRIDs for each vrrp on an interface as a sub-key of that interface::

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

    The data for a configured vrrp is a dictionary with the following format::

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
            mac_addr_adv_interval: <int>
            preempt: <True|False>
            preempt_delay_min: <int>
            preempt_delay_reload: <int>
            delay_reload: <int>
            track: [
                {
                    name: <string>
                    action: <shutdown|decrement>
                    amount: <int>|default|no|None
                },
                {
                    name: <string>
                    action: <shutdown|decrement>
                    amount: <int>|default|no|None
                },
            ]
            bfd_ip: <string>
        }

    The create and method accepts a kwargs dictionary which
    defines the properties to be applied to the new or existing vrrp
    configuration. The available keywords and values are as follows:

        - enable: True to enable (no shutdown)|False to disable (shutdown)
        - primary_ip: <ip_string>|no|default|None
        - priority: <int>|no|default|None
        - description: <string>|no|default|None
        - secondary_ip: <dict> may include the following
            - add: <list of ip address strings>
            - remove: <list of ip address strings>
        - ip_version: <int>|no|default|None
        - timers_advertise: <int>|no|default|None
        - mac_addr_adv_interval: <int>|no|default|None
        - preempt: True to enable (preempt)|False to disable (no preempt)
        - preempt_delay_min: <int>|no|default|None
        - preempt_delay_reload: <int>|no|default|None
        - delay_reload: <int>|no|default|None
        - track: <list> of dicts in the following format::

            {
                name: <string>
                action: <shutdown|decrement>
                amount: <int>|default|no|None
            }

        - bfd_ip: <ip string>|no|default|None

"""

import re

from pyeapi.api import EntityCollection

PROPERTIES = ['primary_ip', 'priority', 'description', 'secondary_ip',
              'ip_version', 'enable', 'timers_advertise',
              'mac_addr_adv_interval', 'preempt',
              'preempt_delay_min', 'preempt_delay_reload',
              'delay_reload', 'track', 'bfd_ip']


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
            subd.update(self._parse_delay_reload(config, vrid))
            subd.update(self._parse_description(config, vrid))
            subd.update(self._parse_enable(config, vrid))
            subd.update(self._parse_ip_version(config, vrid))
            subd.update(self._parse_mac_addr_adv_interval(config, vrid))
            subd.update(self._parse_preempt(config, vrid))
            subd.update(self._parse_preempt_delay_min(config, vrid))
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

    def _parse_enable(self, config, vrid):
        if self.version_number >= '4.21.3':
            match = re.search(r'^\s+vrrp %s disabled$' % vrid, config, re.M)
        else:
            match = re.search(r'^\s+vrrp %s shutdown$' % vrid, config, re.M)
        if match:
            return dict(enable=False)
        return dict(enable=True)

    def _parse_primary_ip(self, config, vrid):
        if self.version_number >= '4.21.3':
            match = re.search(r'^\s+vrrp %s ipv4 (\d+\.\d+\.\d+\.\d+)$' %
                              vrid, config, re.M)
        else:
            match = re.search(r'^\s+vrrp %s ip (\d+\.\d+\.\d+\.\d+)$' %
                              vrid, config, re.M)
        value = match.group(1) if match else None
        return dict(primary_ip=value)

    def _parse_priority(self, config, vrid):
        if self.version_number >= '4.21.3':
            match = re.search(r'^\s+vrrp %s priority-level (\d+)$' %
                              vrid, config, re.M)
        else:
            match = re.search(r'^\s+vrrp %s priority (\d+)$' %
                              vrid, config, re.M)
        value = int(match.group(1)) if match else None
        return dict(priority=value)

    def _parse_timers_advertise(self, config, vrid):
        if self.version_number >= '4.21.3':
            match = re.search(r'^\s+vrrp %s advertisement interval (\d+)$' %
                              vrid, config, re.M)
        else:
            match = re.search(r'^\s+vrrp %s timers advertise (\d+)$' %
                              vrid, config, re.M)
        value = int(match.group(1)) if match else None
        return dict(timers_advertise=value)

    def _parse_preempt(self, config, vrid):
        match = re.search(r'^\s+vrrp %s preempt$' % vrid, config, re.M)
        if match:
            return dict(preempt=True)
        return dict(preempt=False)

    def _parse_secondary_ip(self, config, vrid):
        if self.version_number >= '4.21.3':
            matches = re.findall(r'^\s+vrrp %s ipv4 (\d+\.\d+\.\d+\.\d+) '
                                 r'secondary$' % vrid, config, re.M)
        else:
            matches = re.findall(r'^\s+vrrp %s ip (\d+\.\d+\.\d+\.\d+) '
                                 r'secondary$' % vrid, config, re.M)
        value = matches if matches else []
        return dict(secondary_ip=value)

    def _parse_description(self, config, vrid):
        if self.version_number >= '4.21.3':
            match = re.search(r'^\s+vrrp %s session description(.*)$' %
                              vrid, config, re.M)
        else:
            match = re.search(r'^\s+vrrp %s description(.*)$' %
                              vrid, config, re.M)
        if match:
            return dict(description=match.group(1).lstrip())
        return dict(description='')

    def _parse_mac_addr_adv_interval(self, config, vrid):
        match = re.search(r'^\s+vrrp %s mac-address advertisement-interval '
                          r'(\d+)$' % vrid, config, re.M)
        value = int(match.group(1)) if match else None
        return dict(mac_addr_adv_interval=value)

    def _parse_preempt_delay_min(self, config, vrid):
        match = re.search(r'^\s+vrrp %s preempt delay minimum (\d+)$' %
                          vrid, config, re.M)
        value = int(match.group(1)) if match else None
        return dict(preempt_delay_min=value)

    def _parse_preempt_delay_reload(self, config, vrid):
        match = re.search(r'^\s+vrrp %s preempt delay reload (\d+)$' %
                          vrid, config, re.M)
        value = int(match.group(1)) if match else None
        return dict(preempt_delay_reload=value)

    def _parse_bfd_ip(self, config, vrid):
        match = re.search(r'^\s+vrrp %s bfd ip'
                          r'(?: (\d+\.\d+\.\d+\.\d+)|)$' %
                          vrid, config, re.M)
        if match:
            return dict(bfd_ip=match.group(1))
        return dict(bfd_ip='')

    def _parse_ip_version(self, config, vrid):
        if self.version_number >= '4.21.3':
            match = re.search(r'^\s+vrrp %s ipv4 version (\d+)$' %
                              vrid, config, re.M)
        else:
            match = re.search(r'^\s+vrrp %s ip version (\d+)$' %
                              vrid, config, re.M)
        value = int(match.group(1)) if match else None
        return dict(ip_version=value)

    def _parse_delay_reload(self, config, vrid):
        if self.version_number >= '4.21.3':
            match = re.search(r'^\s+vrrp %s timers delay reload (\d+)$' %
                              vrid, config, re.M)
        else:
            match = re.search(r'^\s+vrrp %s delay reload (\d+)$' %
                              vrid, config, re.M)
        value = int(match.group(1)) if match else None
        return dict(delay_reload=value)

    def _parse_track(self, config, vrid):
        if self.version_number >= '4.21.3':
            matches = re.findall(r'^\s+vrrp %s tracked-object (\S+) '
                                 r'(decrement|shutdown)(?:( \d+$|$))' %
                                 vrid, config, re.M)
        else:
            matches = re.findall(r'^\s+vrrp %s track (\S+) '
                                 r'(decrement|shutdown)(?:( \d+$|$))' %
                                 vrid, config, re.M)
        value = []
        for match in matches:
            tr_obj = match[0]
            action = match[1]
            amount = None if match[2] == '' else int(match[2])
            entry = {
                'name': tr_obj,
                'action': action,
            }
            if amount:
                entry.update({'amount': amount})
            value.append(entry)

        # Return the list, sorted for easier comparison
        track_list = sorted(value, key=lambda k: (k['name'], k['action']))
        return dict(track=track_list)

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

    def set_enable(self, name, vrid, value=False, run=True):
        """Set the enable property of the vrrp

        Args:
            name (string): The interface to configure.
            vrid (integer): The vrid number for the vrrp to be managed.
            value (boolean): True to enable the vrrp, False to disable.
            run (boolean): True to execute the command, False to
                return a string with the formatted command.

        Returns:
            If run is True, returns True if the command executed successfully,
            error if failure

            If run is False, returns the formatted command string which can
            be passed to the node

        """

        if value is False:
            if self.version_number >= '4.21.3':
                cmd = "vrrp %d disabled" % vrid
            else:
                cmd = "vrrp %d shutdown" % vrid
        elif value is True:
            if self.version_number >= '4.21.3':
                cmd = "no vrrp %d disabled" % vrid
            else:
                cmd = "no vrrp %d shutdown" % vrid
        else:
            raise ValueError("vrrp property 'enable' must be "
                             "True or False")

        # Run the command if requested
        if run:
            result = self.configure_interface(name, cmd)
            # And verify the command succeeded
            if result is False:
                return self.error
            return result

        # Otherwise return the formatted command
        return cmd

    def set_primary_ip(self, name, vrid, value=None, disable=False,
                       default=False, run=True):
        """Set the primary_ip property of the vrrp

        Args:
            name (string): The interface to configure.
            vrid (integer): The vrid number for the vrrp to be managed.
            value (string): IP address to be set.
            disable (boolean): Unset primary ip if True.
            default (boolean): Set primary ip to default if True.
            run (boolean): Set to True to execute the command, False to
                return a string with the formatted command.

        Returns:
            If run is True, returns True if the command executed successfully,
            error if failure.

            If run is False, returns the formatted command string which can
            be passed to the node

        """

        if default is True:
            vrrps = self.get(name)
            primary_ip = vrrps[vrid]['primary_ip']
            if self.version_number >= '4.21.3':
                cmd = "default vrrp %d ipv4 %s" % (vrid, primary_ip)
            else:
                cmd = "default vrrp %d ip %s" % (vrid, primary_ip)
        elif disable is True or value is None:
            vrrps = self.get(name)
            primary_ip = vrrps[vrid]['primary_ip']
            if self.version_number >= '4.21.3':
                cmd = "no vrrp %d ipv4 %s" % (vrid, primary_ip)
            else:
                cmd = "no vrrp %d ip %s" % (vrid, primary_ip)
        elif re.match(r'^\d+\.\d+\.\d+\.\d+$', str(value)):
            if self.version_number >= '4.21.3':
                cmd = "vrrp %d ipv4 %s" % (vrid, value)
            else:
                cmd = "vrrp %d ip %s" % (vrid, value)
        else:
            raise ValueError("vrrp property 'primary_ip' must be "
                             "a properly formatted IP address")

        # Run the command if requested
        if run:
            result = self.configure_interface(name, cmd)
            # And verify the command succeeded
            if result is False:
                return self.error
            return result

        # Otherwise return the formatted command
        return cmd

    def set_priority(self, name, vrid, value=None, disable=False,
                     default=False, run=True):
        """Set the primary_ip property of the vrrp

        Args:
            name (string): The interface to configure.
            vrid (integer): The vrid number for the vrrp to be managed.
            value (integer): Priority to assign to the vrrp.
            disable (boolean): Unset priority if True.
            default (boolean): Set priority to default if True.
            run (boolean): Set to True to execute the command, False to
                return a string with the formatted command.

        Returns:
            If run is True, returns True if the command executed successfully,
            error if failure.

            If run is False, returns the formatted command string which can
            be passed to the node

        """

        if not default and not disable:
            if not str(value).isdigit() or value < 1 or value > 254:
                raise ValueError("vrrp property 'priority' must be "
                                 "an integer in the range 1-254")
        if self.version_number >= '4.21.3':
            cmd = self.command_builder('vrrp %d priority-level' %
                                       vrid, value=value,
                                       default=default, disable=disable)
        else:
            cmd = self.command_builder('vrrp %d priority' %
                                       vrid, value=value,
                                       default=default, disable=disable)

        # Run the command if requested
        if run:
            result = self.configure_interface(name, cmd)
            # And verify the command succeeded
            if result is False:
                return self.error
            return result

        # Otherwise return the formatted command
        return cmd

    def set_description(self, name, vrid, value=None, disable=False,
                        default=False, run=True):
        """Set the description property of the vrrp

        Args:
            name (string): The interface to configure.
            vrid (integer): The vrid number for the vrrp to be managed.
            value (string): Description to assign to the vrrp.
            disable (boolean): Unset description if True.
            default (boolean): Set description to default if True.
            run (boolean): Set to True to execute the command, False to
                return a string with the formatted command.

        Returns:
            If run is True, returns True if the command executed successfully,
            error if failure.

            If run is False, returns the formatted command string which can
            be passed to the node

        """
        if self.version_number >= '4.21.3':
            cmd = self.command_builder('vrrp %d session description' %
                                       vrid, value=value,
                                       default=default, disable=disable)
        else:
            cmd = self.command_builder('vrrp %d description' %
                                       vrid, value=value,
                                       default=default, disable=disable)

        # Run the command if requested
        if run:
            result = self.configure_interface(name, cmd)
            # And verify the command succeeded
            if result is False:
                return self.error
            return result

        # Otherwise return the formatted command
        return cmd

    def set_ip_version(self, name, vrid, value=None, disable=False,
                       default=False, run=True):
        """Set the ip_version property of the vrrp

        Args:
            name (string): The interface to configure.
            vrid (integer): The vrid number for the vrrp to be managed.
            value (integer): IP version to assign to the vrrp.
            disable (boolean): Unset ip_version if True.
            default (boolean): Set ip_version to default if True.
            run (boolean): Set to True to execute the command, False to
                return a string with the formatted command.

        Returns:
            If run is True, returns True if the command executed successfully,
            error if failure.

            If run is False, returns the formatted command string which can
            be passed to the node

        """

        if not default and not disable:
            if value not in (2, 3):
                raise ValueError("vrrp property 'ip_version' must be 2 or 3")
        if self.version_number >= '4.21.3':
            cmd = self.command_builder('vrrp %d ipv4 version' %
                                       vrid, value=value,
                                       default=default, disable=disable)
        else:
            cmd = self.command_builder('vrrp %d ip version' %
                                       vrid, value=value,
                                       default=default, disable=disable)

        # Run the command if requested
        if run:
            result = self.configure_interface(name, cmd)
            # And verify the command succeeded
            if result is False:
                return self.error
            return result

        # Otherwise return the formatted command
        return cmd

    def set_secondary_ips(self, name, vrid, secondary_ips, run=True):
        """Configure the secondary_ip property of the vrrp

        Notes:
            set_secondary_ips takes a list of secondary ip addresses
            which are to be set on the virtal router. An empty list will
            remove any existing secondary ip addresses from the vrrp.
            A list containing addresses will configure the virtual router
            with only the addresses specified in the list - any existing
            addresses not included in the list will be removed.

        Args:
            name (string): The interface to configure.
            vrid (integer): The vrid number for the vrrp to be managed.
            secondary_ips (list): A list of secondary ip addresses to
                be assigned to the virtual router.
            run (boolean): Set to True to execute the command, False to
                return a string with the formatted command.

        Returns:
            If run is True, returns True if the command executed successfully,
            error if failure.

            If run is False, returns the formatted command string which can
            be passed to the node

        """

        cmds = []

        # Get the current set of tracks defined for the vrrp
        curr_sec_ips = []
        vrrps = self.get(name)
        if vrrps and vrid in vrrps:
            curr_sec_ips = vrrps[vrid]['secondary_ip']

        # Validate the list of ip addresses
        for sec_ip in secondary_ips:
            if type(sec_ip) is not str or \
                    not re.match(r'^\d+\.\d+\.\d+\.\d+$', sec_ip):
                raise ValueError("vrrp property 'secondary_ip' must be a list "
                                 "of properly formatted ip address strings")

        intersection = list(set(curr_sec_ips) & set(secondary_ips))

        # Delete the intersection from both lists to determine which
        # addresses need to be added or removed from the vrrp
        remove = list(set(curr_sec_ips) - set(intersection))
        add = list(set(secondary_ips) - set(intersection))

        # Build the commands to add and remove the secondary ip addresses
        for sec_ip in remove:
            if self.version_number >= '4.21.3':
                cmds.append("no vrrp %d ipv4 %s secondary" % (vrid, sec_ip))
            else:
                cmds.append("no vrrp %d ip %s secondary" % (vrid, sec_ip))

        for sec_ip in add:
            if self.version_number >= '4.21.3':
                cmds.append("vrrp %d ipv4 %s secondary" % (vrid, sec_ip))
            else:
                cmds.append("vrrp %d ip %s secondary" % (vrid, sec_ip))

        cmds = sorted(cmds)

        # Run the command if requested
        if run:
            result = self.configure_interface(name, cmds)
            # And verify the command succeeded
            if result is False:
                return self.error
            return result

        # Otherwise return the formatted command
        return cmds

    def set_timers_advertise(self, name, vrid, value=None, disable=False,
                             default=False, run=True):
        """Set the ip_version property of the vrrp

        Args:
            name (string): The interface to configure.
            vrid (integer): The vrid number for the vrrp to be managed.
            value (integer): Timers advertise value to assign to the vrrp.
            disable (boolean): Unset timers advertise if True.
            default (boolean): Set timers advertise to default if True.
            run (boolean): Set to True to execute the command, False to
                return a string with the formatted command.

        Returns:
            If run is True, returns True if the command executed successfully,
            error if failure.

            If run is False, returns the formatted command string which can
            be passed to the node

        """

        if not default and not disable:
            if not int(value) or int(value) < 1 or int(value) > 255:
                raise ValueError("vrrp property 'timers_advertise' must be"
                                 "in the range 1-255")
        if self.version_number >= '4.21.3':
            cmd = self.command_builder('vrrp %d advertisement interval' %
                                       vrid,
                                       value=value, default=default,
                                       disable=disable)
        else:
            cmd = self.command_builder('vrrp %d timers advertise' %
                                       vrid,
                                       value=value, default=default,
                                       disable=disable)

        # Run the command if requested
        if run:
            result = self.configure_interface(name, cmd)
            # And verify the command succeeded
            if result is False:
                return self.error
            return result

        # Otherwise return the formatted command
        return cmd

    def set_mac_addr_adv_interval(self, name, vrid, value=None, disable=False,
                                  default=False, run=True):
        """Set the mac_addr_adv_interval property of the vrrp

        Args:
            name (string): The interface to configure.
            vrid (integer): The vrid number for the vrrp to be managed.
            value (integer): mac-address advertisement-interval value to
                assign to the vrrp.
            disable (boolean): Unset mac-address advertisement-interval
                if True.
            default (boolean): Set mac-address advertisement-interval to
                default if True.
            run (boolean): Set to True to execute the command, False to
                return a string with the formatted command.

        Returns:
            If run is True, returns True if the command executed successfully,
            error if failure.

            If run is False, returns the formatted command string which can
            be passed to the node

        """

        if not default and not disable:
            if not int(value) or int(value) < 1 or int(value) > 3600:
                raise ValueError("vrrp property 'mac_addr_adv_interval' must "
                                 "be in the range 1-3600")

        cmd = self.command_builder('vrrp %d mac-address advertisement-interval'
                                   % vrid, value=value, default=default,
                                   disable=disable)

        # Run the command if requested
        if run:
            result = self.configure_interface(name, cmd)
            # And verify the command succeeded
            if result is False:
                return self.error
            return result

        # Otherwise return the formatted command
        return cmd

    def set_preempt(self, name, vrid, value=None, disable=False,
                    default=False, run=True):
        """Set the preempt property of the vrrp

        Args:
            name (string): The interface to configure.
            vrid (integer): The vrid number for the vrrp to be managed.
            value (boolean): True to enable preempt, False to disable
                preempt on the vrrp.
            disable (boolean): Unset preempt if True.
            default (boolean): Set preempt to default if True.
            run (boolean): Set to True to execute the command, False to
                return a string with the formatted command.

        Returns:
            If run is True, returns True if the command executed successfully,
            error if failure.

            If run is False, returns the formatted command string which can
            be passed to the node

        """

        if not default and not disable:
            if value is not True and value is not False:
                raise ValueError("vrrp property 'preempt' must be True "
                                 "or False")

        cmd = self.command_builder('vrrp %d preempt' % vrid, value=value,
                                   default=default, disable=disable)

        # Run the command if requested
        if run:
            result = self.configure_interface(name, cmd)
            # And verify the command succeeded
            if result is False:
                return self.error
            return result

        # Otherwise return the formatted command
        return cmd

    def set_preempt_delay_min(self, name, vrid, value=None, disable=False,
                              default=False, run=True):
        """Set the preempt_delay_min property of the vrrp

        Args:
            name (string): The interface to configure.
            vrid (integer): The vrid number for the vrrp to be managed.
            value (integer): Preempt delay minimum value to set on the vrrp.
            disable (boolean): Unset preempt delay minimum if True.
            default (boolean): Set preempt delay minimum to default if True.
            run (boolean): Set to True to execute the command, False to
                return a string with the formatted command.

        Returns:
            If run is True, returns True if the command executed successfully,
            error if failure.

            If run is False, returns the formatted command string which can
            be passed to the node

        """

        if not default and not disable:
            if not int(value) or int(value) < 1 or int(value) > 3600:
                raise ValueError("vrrp property 'preempt_delay_min' must be"
                                 "in the range 0-3600 %r" % value)

        cmd = self.command_builder('vrrp %d preempt delay minimum'
                                   % vrid, value=value, default=default,
                                   disable=disable)

        # Run the command if requested
        if run:
            result = self.configure_interface(name, cmd)
            # And verify the command succeeded
            if result is False:
                return self.error
            return result

        # Otherwise return the formatted command
        return cmd

    def set_preempt_delay_reload(self, name, vrid, value=None, disable=False,
                                 default=False, run=True):
        """Set the preempt_delay_min property of the vrrp

        Args:
            name (string): The interface to configure.
            vrid (integer): The vrid number for the vrrp to be managed.
            value (integer): Preempt delay reload value to set on the vrrp.
            disable (boolean): Unset preempt delay reload if True.
            default (boolean): Set preempt delay reload to default if True.
            run (boolean): Set to True to execute the command, False to
                return a string with the formatted command.

        Returns:
            If run is True, returns True if the command executed successfully,
            error if failure.

            If run is False, returns the formatted command string which can
            be passed to the node

        """

        if not default and not disable:
            if not int(value) or int(value) < 1 or int(value) > 3600:
                raise ValueError("vrrp property 'preempt_delay_reload' must be"
                                 "in the range 0-3600 %r" % value)

        cmd = self.command_builder('vrrp %d preempt delay reload'
                                   % vrid, value=value, default=default,
                                   disable=disable)

        # Run the command if requested
        if run:
            result = self.configure_interface(name, cmd)
            # And verify the command succeeded
            if result is False:
                return self.error
            return result

        # Otherwise return the formatted command
        return cmd

    def set_delay_reload(self, name, vrid, value=None, disable=False,
                         default=False, run=True):
        """Set the preempt_delay_min property of the vrrp

        Args:
            name (string): The interface to configure.
            vrid (integer): The vrid number for the vrrp to be managed.
            value (integer): Preempt delay reload value to set on the vrrp.
            disable (boolean): Unset preempt delay reload if True.
            default (boolean): Set preempt delay reload to default if True.
            run (boolean): Set to True to execute the command, False to
                return a string with the formatted command.

        Returns:
            If run is True, returns True if the command executed successfully,
            error if failure.

            If run is False, returns the formatted command string which can
            be passed to the node

        """

        if not default and not disable:
            if not int(value) or int(value) < 1 or int(value) > 3600:
                raise ValueError("vrrp property 'delay_reload' must be"
                                 "in the range 0-3600 %r" % value)
        if self.version_number >= '4.21.3':
            cmd = self.command_builder('vrrp %d timers delay reload' %
                                       vrid, value=value,
                                       default=default, disable=disable)
        else:
            cmd = self.command_builder('vrrp %d delay reload' %
                                       vrid, value=value,
                                       default=default, disable=disable)

        # Run the command if requested
        if run:
            result = self.configure_interface(name, cmd)
            # And verify the command succeeded
            if result is False:
                return self.error
            return result

        # Otherwise return the formatted command
        return cmd

    def set_tracks(self, name, vrid, tracks, run=True):
        """Configure the track property of the vrrp

        Notes:
            set_tracks takes a list of tracked objects which are
            to be set on the virtual router. An empty list will remove
            any existing tracked objects from the vrrp. A list containing
            track entries configures the virtual router to track only the
            objects specified in the list - any existing tracked objects
            on the vrrp not included in the list will be removed.

        Args:
            name (string): The interface to configure.
            vrid (integer): The vrid number for the vrrp to be managed.
            tracks (list): A list of track definition dictionaries. Each
                dictionary is a definition of a tracked object in one
                of the two formats::

                    {'name': tracked_object_name,
                     'action': 'shutdown'}
                    {'name': tracked_object_name,
                     'action': 'decrement',
                     'amount': amount_of_decrement}

            run (boolean): Set to True to execute the command, False to
                return a string with the formatted command.

        Returns:
            If run is True, returns True if the command executed successfully,
            error if failure.

            If run is False, returns the formatted command string which can
            be passed to the node

        """

        cmds = []

        # Get the current set of tracks defined for the vrrp
        curr_tracks = []
        vrrps = self.get(name)
        if vrrps and vrid in vrrps:
            curr_tracks = vrrps[vrid]['track']

        # Determine which tracked objects are in both lists using
        # sets of temporary strings built from the track specifications
        unset = '_none_'
        tracks_set = []
        for track in tracks:
            keys = track.keys()

            # Validate no extraneous keys in track definition
            err_keys = set(keys).difference(('name', 'action', 'amount'))
            if err_keys:
                err_keys = ', '.join(err_keys)
                raise ValueError("Error found in vrrp property 'track': "
                                 "unknown key(s) '%s' found. Valid keys are "
                                 "name, action, and amount" % err_keys)

            # Validate required keys in track definition
            if not set(keys).issuperset(('name', 'action')):
                raise ValueError("Error found in vrrp property 'track': "
                                 "track definition must contain 'name' and "
                                 "'action' keys")

            tr_obj = track['name']
            action = track['action']
            amount = track['amount'] if 'amount' in track else unset

            # Validate values in track definition
            error = False
            if action not in ('shutdown', 'decrement'):
                error = True
            if action == 'shutdown' and amount != unset:
                error = True
            if amount != unset and not str(amount).isdigit():
                error = True
            if error:
                raise ValueError("Error found in vrrp property 'track'. "
                                 "See documentation for format specification.")

            tid = "%s   %s   %s" % (tr_obj, action, amount)
            tracks_set.append(tid)

        curr_set = []
        for track in curr_tracks:
            tr_obj = track['name']
            action = track['action']
            amount = track['amount'] if 'amount' in track else unset

            # Validate track definition
            error = False
            if action not in ('shutdown', 'decrement'):
                error = True
            if action == 'shutdown' and amount != unset:
                error = True
            if amount != unset and not str(amount).isdigit():
                error = True
            if error:
                raise ValueError("Error found in vrrp property 'track'. "
                                 "See documentation for format specification.")

            tid = "%s   %s   %s" % (tr_obj, action, amount)
            curr_set.append(tid)

        intersection = list(set(tracks_set) & set(curr_set))

        # Delete the intersection from both lists to determine which
        # track definitions need to be added or removed from the vrrp
        remove = list(set(curr_set) - set(intersection))
        add = list(set(tracks_set) - set(intersection))

        # Build the commands to add and remove the tracked objects
        for track in remove:
            match = re.match(r'(\S+)\s+(\S+)\s+(\S+)', track)
            if match:
                (tr_obj, action, amount) = \
                    (match.group(1), match.group(2), match.group(3))

                if amount == unset:
                    amount = ''
                if self.version_number >= '4.21.3':
                    t_cmd = ("no vrrp %d tracked-object %s %s %s"
                             % (vrid, tr_obj, action, amount))
                else:
                    t_cmd = ("no vrrp %d track %s %s %s"
                             % (vrid, tr_obj, action, amount))
                cmds.append(t_cmd.rstrip())

        for track in add:
            match = re.match(r'(\S+)\s+(\S+)\s+(\S+)', track)
            if match:
                (tr_obj, action, amount) = \
                    (match.group(1), match.group(2), match.group(3))

                if amount == unset:
                    amount = ''
                if self.version_number >= '4.21.3':
                    t_cmd = ("vrrp %d tracked-object %s %s %s"
                             % (vrid, tr_obj, action, amount))
                else:
                    t_cmd = ("vrrp %d track %s %s %s"
                             % (vrid, tr_obj, action, amount))
                cmds.append(t_cmd.rstrip())

        cmds = sorted(cmds)

        # Run the command if requested
        if run:
            result = self.configure_interface(name, cmds)
            # And verify the command succeeded
            if result is False:
                return self.error
            return result

        # Otherwise return the formatted command
        return cmds

    def set_bfd_ip(self, name, vrid, value=None, disable=False,
                   default=False, run=True):
        """Set the bfd_ip property of the vrrp

        Args:
            name (string): The interface to configure.
            vrid (integer): The vrid number for the vrrp to be managed.
            value (string): The bfd ip address to be set.
            disable (boolean): Unset bfd ip if True.
            default (boolean): Set bfd ip to default if True.
            run (boolean): Set to True to execute the command, False to
                return a string with the formatted command.

        Returns:
            If run is True, returns True if the command executed successfully,
            error if failure.

            If run is False, returns the formatted command string which can
            be passed to the node

        """
        if not default and not disable:
            if not re.match(r'^\d+\.\d+\.\d+\.\d+$', str(value)):
                raise ValueError("vrrp property 'bfd_ip' must be "
                                 "a properly formatted IP address")
        cmd = self.command_builder('vrrp %d bfd ip' % vrid, value=value,
                                   default=default, disable=disable)

        # Run the command if requested
        if run:
            result = self.configure_interface(name, cmd)
            # And verify the command succeeded
            if result is False:
                return self.error
            return result

        # Otherwise return the formatted command
        return cmd

    def _vrrp_set(self, name, vrid, **kwargs):
        # Configure the commands to create or update a vrrp
        # configuration, and send the commands to the node.

        vrconf = kwargs

        # step through the individual vrrp properties and
        # set those that need to be changed
        commands = []

        enable = vrconf.get('enable', '__NONE__')
        if enable != '__NONE__':
            cmd = self.set_enable(name, vrid, value=enable, run=False)
            commands.append(cmd)

        primary_ip = vrconf.get('primary_ip', '__NONE__')
        if primary_ip != '__NONE__':
            if primary_ip in ('no', None):
                cmd = self.set_primary_ip(name, vrid, value=None,
                                          disable=True, run=False)
            elif primary_ip == 'default':
                cmd = self.set_primary_ip(name, vrid, value=None,
                                          default=True, run=False)
            else:
                cmd = self.set_primary_ip(name, vrid, value=primary_ip,
                                          run=False)
            commands.append(cmd)

        priority = vrconf.get('priority', '__NONE__')
        if priority != '__NONE__':
            if priority in ('no', None):
                cmd = self.set_priority(name, vrid, value=priority,
                                        disable=True, run=False)
            elif priority == 'default':
                cmd = self.set_priority(name, vrid, value=priority,
                                        default=True, run=False)
            else:
                cmd = self.set_priority(name, vrid, value=priority, run=False)
            commands.append(cmd)

        description = vrconf.get('description', '__NONE__')
        if description != '__NONE__':
            if description in ('no', None):
                cmd = self.set_description(name, vrid, value=description,
                                           disable=True, run=False)
            elif description == 'default':
                cmd = self.set_description(name, vrid, value=description,
                                           default=True, run=False)
            else:
                cmd = self.set_description(name, vrid, value=description,
                                           run=False)
            commands.append(cmd)

        ip_version = vrconf.get('ip_version', '__NONE__')
        if ip_version != '__NONE__':
            if ip_version in ('no', None):
                cmd = self.set_ip_version(name, vrid, value=ip_version,
                                          disable=True, run=False)
            elif ip_version == 'default':
                cmd = self.set_ip_version(name, vrid, value=ip_version,
                                          default=True, run=False)
            else:
                cmd = self.set_ip_version(name, vrid, value=ip_version,
                                          run=False)
            commands.append(cmd)

        secondary_ip = vrconf.get('secondary_ip', '__NONE__')
        if secondary_ip != '__NONE__':
            cmds = self.set_secondary_ips(name, vrid, secondary_ip, run=False)
            for cmd in cmds:
                commands.append(cmd)

        timers_advertise = vrconf.get('timers_advertise', '__NONE__')
        if timers_advertise != '__NONE__':
            if timers_advertise in ('no', None):
                cmd = self.set_timers_advertise(name, vrid,
                                                value=timers_advertise,
                                                disable=True, run=False)
            elif timers_advertise == 'default':
                cmd = self.set_timers_advertise(name, vrid,
                                                value=timers_advertise,
                                                default=True, run=False)
            else:
                cmd = self.set_timers_advertise(name, vrid,
                                                value=timers_advertise,
                                                run=False)
            commands.append(cmd)

        mac_addr_adv_interval = \
            vrconf.get('mac_addr_adv_interval', '__NONE__')
        if mac_addr_adv_interval != '__NONE__':
            if mac_addr_adv_interval in ('no', None):
                cmd = \
                    self.set_mac_addr_adv_interval(name, vrid,
                                                   value=mac_addr_adv_interval,
                                                   disable=True, run=False)
            elif mac_addr_adv_interval == 'default':
                cmd = \
                    self.set_mac_addr_adv_interval(name, vrid,
                                                   value=mac_addr_adv_interval,
                                                   default=True, run=False)
            else:
                cmd = \
                    self.set_mac_addr_adv_interval(name, vrid,
                                                   value=mac_addr_adv_interval,
                                                   run=False)
            commands.append(cmd)

        preempt = vrconf.get('preempt', '__NONE__')
        if preempt != '__NONE__':
            if preempt in ('no', False):
                cmd = self.set_preempt(name, vrid, value=preempt,
                                       disable=True, run=False)
            elif preempt == 'default':
                cmd = self.set_preempt(name, vrid, value=preempt,
                                       default=True, run=False)
            else:
                cmd = self.set_preempt(name, vrid, value=preempt, run=False)
            commands.append(cmd)

        preempt_delay_min = vrconf.get('preempt_delay_min', '__NONE__')
        if preempt_delay_min != '__NONE__':
            if preempt_delay_min in ('no', None):
                cmd = self.set_preempt_delay_min(name, vrid,
                                                 value=preempt_delay_min,
                                                 disable=True, run=False)
            elif preempt_delay_min == 'default':
                cmd = self.set_preempt_delay_min(name, vrid,
                                                 value=preempt_delay_min,
                                                 default=True, run=False)
            else:
                cmd = self.set_preempt_delay_min(name, vrid,
                                                 value=preempt_delay_min,
                                                 run=False)
            commands.append(cmd)

        preempt_delay_reload = vrconf.get('preempt_delay_reload', '__NONE__')
        if preempt_delay_reload != '__NONE__':
            if preempt_delay_reload in ('no', None):
                cmd = self.set_preempt_delay_reload(name, vrid,
                                                    value=preempt_delay_reload,
                                                    disable=True, run=False)
            elif preempt_delay_reload == 'default':
                cmd = self.set_preempt_delay_reload(name, vrid,
                                                    value=preempt_delay_reload,
                                                    default=True, run=False)
            else:
                cmd = self.set_preempt_delay_reload(name, vrid,
                                                    value=preempt_delay_reload,
                                                    run=False)
            commands.append(cmd)

        delay_reload = vrconf.get('delay_reload', '__NONE__')
        if delay_reload != '__NONE__':
            if delay_reload in ('no', None):
                cmd = self.set_delay_reload(name, vrid, value=delay_reload,
                                            disable=True, run=False)
            elif delay_reload == 'default':
                cmd = self.set_delay_reload(name, vrid, value=delay_reload,
                                            default=True, run=False)
            else:
                cmd = self.set_delay_reload(name, vrid, value=delay_reload,
                                            run=False)
            commands.append(cmd)

        track = vrconf.get('track', '__NONE__')
        if track != '__NONE__':
            cmds = self.set_tracks(name, vrid, track, run=False)
            for cmd in cmds:
                commands.append(cmd)

        bfd_ip = vrconf.get('bfd_ip', '__NONE__')
        if bfd_ip != '__NONE__':
            if bfd_ip in ('no', None):
                cmd = self.set_bfd_ip(name, vrid, value=bfd_ip,
                                      disable=True, run=False)
            elif bfd_ip == 'default':
                cmd = self.set_bfd_ip(name, vrid, value=bfd_ip,
                                      default=True, run=False)
            else:
                cmd = self.set_bfd_ip(name, vrid, value=bfd_ip, run=False)
            commands.append(cmd)

        # Send the commands to the requested interface
        result = self.configure_interface(name, commands)
        # And verify the commands succeeded
        if result is False:
            return self.error
        return result

    def vrconf_format(self, vrconfig):
        """Formats a vrrp configuration dictionary to match the
        information as presented from the get and getall methods.
        vrrp configuration dictionaries passed to the create
        method may contain data for setting properties which results
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
        # secondary_ip: list should be exactly what is required,
        # just sort it for easier comparison
        if 'secondary_ip' in fixed:
            fixed['secondary_ip'] = sorted(fixed['secondary_ip'])
        # ip_version: default, no, None results in value of 2
        if fixed['ip_version'] in ('no', 'default', None):
            fixed['ip_version'] = 2
        # timers_advertise: default, no, None results in value of 1
        if fixed['timers_advertise'] in ('no', 'default', None):
            fixed['timers_advertise'] = 1
        # mac_address_advertisement_interaval:
        #    default, no, None results in value of 30
        if fixed['mac_addr_adv_interval'] in \
                ('no', 'default', None):
            fixed['mac_addr_adv_interval'] = 30
        # preempt: default, no results in value of False
        if fixed['preempt'] in ('no', 'default'):
            fixed['preempt'] = False
        # preempt_delay_min: default, no, None results in value of 0
        if fixed['preempt_delay_min'] in ('no', 'default', None):
            fixed['preempt_delay_min'] = 0
        # preempt_delay_reload: default, no, None results in value of 0
        if fixed['preempt_delay_reload'] in ('no', 'default', None):
            fixed['preempt_delay_reload'] = 0
        # delay_reload: default, no, None results in value of 0
        if fixed['delay_reload'] in ('no', 'default', None):
            fixed['delay_reload'] = 0
        # track: list should be exactly what is required,
        # just sort it for easier comparison
        if 'track' in fixed:
            fixed['track'] = \
                sorted(fixed['track'], key=lambda k: (k['name'], k['action']))
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
