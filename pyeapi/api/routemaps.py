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
"""Module for working with EOS routemap resources

The Routemap resource provides configuration management of global route-map
resources on an EOS node. It provides the following class implementations:

    * Routemaps - Configures routemaps in EOS

Notes:
    The set and match attributes produce a list of strings with The
    corresponding configuration. These strings will omit the preceeding
    set or match words, respectively.
"""

import re

from pyeapi.api import EntityCollection


class Routemaps(EntityCollection):
    """The Routemaps class provides management of the routemaps configuration

    The Routemaps class is derived from Entity and provides an API for working
    with the nodes routemaps configuraiton.
    """

    def get(self, name):
        """Provides a method to retrieve all routemap configuration
        related to the name attribute.

        Args:
            name (string): The name of the routemap.

        Returns:
            None if the specified routemap does not exists. If the routermap
            exists a dictionary will be provided as follows::

                {
                    'deny': {
                            30: {
                                    'continue': 200,
                                    'description': None,
                                    'match': ['as 2000',
                                              'source-protocol ospf',
                                              'interface Ethernet2'],
                                    'set': []
                                }
                            },
                    'permit': {
                            10: {
                                    'continue': 100,
                                    'description': None,
                                    'match': ['interface Ethernet1'],
                                    'set': ['tag 50']},
                            20: {
                                    'continue': 200,
                                    'description': None,
                                    'match': ['as 2000',
                                              'source-protocol ospf',
                                              'interface Ethernet2'],
                                    'set': []
                                }
                            }
                }
        """
        if not self.get_block(r'route-map\s%s\s\w+\s\d+' % name):
            return None

        return self._parse_entries(name)

    def getall(self):
        resources = dict()
        routemaps_re = re.compile(r'^route-map\s(\w+)\s\w+\s\d+$', re.M)
        for name in routemaps_re.findall(self.config):
            routemap = self.get(name)
            if routemap:
                resources[name] = routemap
        return resources

    def _parse_entries(self, name):

        routemap_re = re.compile(r'^route-map\s%s\s(\w+)\s(\d+)$'
                                 % name, re.M)
        entries = list()
        for entry in routemap_re.findall(self.config):
            resource = dict()
            action, seqno = entry
            routemap = self.get_block(r'route-map\s%s\s%s\s%s'
                                      % (name, action, seqno))

            resource = dict(name=name, action=action, seqno=seqno, attr=dict())
            resource['attr'].update(self._parse_match_statements(routemap))
            resource['attr'].update(self._parse_set_statements(routemap))
            resource['attr'].update(self._parse_continue_statement(routemap))
            resource['attr'].update(self._parse_description(routemap))
            entries.append(resource)

        return self._merge_entries(entries)

    def _merge_entries(self, entries):
        response = dict()
        for e in entries:
            action = e['action']
            seqno = int(e['seqno'])
            if not response.get(action):
                response[action] = dict()
            response[action][seqno] = e['attr']

        return response

    def _parse_match_statements(self, config):
        match_re = re.compile(r'^\s+match\s(.+)$', re.M)
        return dict(match=match_re.findall(config))

    def _parse_set_statements(self, config):
        set_re = re.compile(r'^\s+set\s(.+)$', re.M)
        return dict(set=set_re.findall(config))

    def _parse_continue_statement(self, config):
        continue_re = re.compile(r'^\s+continue\s(\d+)$', re.M)
        match = continue_re.search(config)
        value = int(match.group(1)) if match else None
        return {'continue': value}

    def _parse_description(self, config):
        desc_re = re.compile(r'^\s+description\s(.+)$', re.M)
        match = desc_re.search(config)
        value = match.group(1) if match else None
        return dict(description=value)

    def create(self, name, action, seqno):
        """Creates a new routemap on the node

        Note:
            This method will attempt to create the routemap regardless
            if the routemap exists or not.  If the routemap already exists
            then this method will still return True.

        Args:
            name (string): The full name of the routemap.
            action (string): The action to take for this routemap clause.
            seqno (integer): The sequence number for the routemap clause.

        Returns:
            True if the routemap could be created otherwise False (see Note)

        """
        return self.configure('route-map %s %s %s' % (name, action, seqno))

    def delete(self, name, action, seqno):
        """Deletes the routemap from the node

        Note:
            This method will attempt to delete the routemap from the nodes
            operational config.  If the routemap does not exist then this
            method will not perform any changes but still return True

        Args:
            name (string): The full name of the routemap.
            action (string): The action to take for this routemap clause.
            seqno (integer): The sequence number for the routemap clause.

        Returns:
            True if the routemap could be deleted otherwise False (see Node)

        """
        return self.configure('no route-map %s %s %s' % (name, action, seqno))

    def default(self, name, action, seqno):
        """Defaults the routemap on the node

        Note:
            This method will attempt to default the routemap from the nodes
            operational config. Since routemaps do not exist by default,
            the default action is essentially a negation and the result will
            be the removal of the routemap clause.
            If the routemap does not exist then this
            method will not perform any changes but still return True

        Args:
            name (string): The full name of the routemap.
            action (string): The action to take for this routemap clause.
            seqno (integer): The sequence number for the routemap clause.

        Returns:
            True if the routemap could be deleted otherwise False (see Node)

        """
        return self.configure('default route-map %s %s %s'
                              % (name, action, seqno))

    def set_match_statements(self, name, action, seqno, statements):
        """Configures the match statements within the routemap clause.
        The final configuration of match statements will reflect the list
        of statements passed into the statements attribute. This implies
        match statements found in the routemap that are not specified in the
        statements attribute will be removed.

        Args:
            name (string): The full name of the routemap.
            action (string): The action to take for this routemap clause.
            seqno (integer): The sequence number for the routemap clause.
            statements (list): A list of the match-related statements. Note
                               that the statements should omit the leading
                               match.

        Returns:
            True if the operation succeeds otherwise False
        """
        try:
            current_statements = self.get(name)[action][seqno]['match']
        except:
            current_statements = []

        commands = list()

        # remove set statements from current routemap
        for entry in set(current_statements).difference(statements):
            commands.append('route-map %s %s %s' % (name, action, seqno))
            commands.append('no match %s' % entry)

        # add new set statements to the routemap
        for entry in set(statements).difference(current_statements):
            commands.append('route-map %s %s %s' % (name, action, seqno))
            commands.append('match %s' % entry)

        return self.configure(commands) if commands else True

    def set_set_statements(self, name, action, seqno, statements):
        """Configures the set statements within the routemap clause.
        The final configuration of set statements will reflect the list
        of statements passed into the statements attribute. This implies
        set statements found in the routemap that are not specified in the
        statements attribute will be removed.

        Args:
            name (string): The full name of the routemap.
            action (string): The action to take for this routemap clause.
            seqno (integer): The sequence number for the routemap clause.
            statements (list): A list of the set-related statements. Note that
                               the statements should omit the leading set.

        Returns:
            True if the operation succeeds otherwise False
        """
        try:
            current_statements = self.get(name)[action][seqno]['set']
        except:
            current_statements = []

        commands = list()

        # remove set statements from current routemap
        for entry in set(current_statements).difference(statements):
            commands.append('route-map %s %s %s' % (name, action, seqno))
            commands.append('no set %s' % entry)

        # add new set statements to the routemap
        for entry in set(statements).difference(current_statements):
            commands.append('route-map %s %s %s' % (name, action, seqno))
            commands.append('set %s' % entry)

        return self.configure(commands) if commands else True

    def set_continue(self, name, action, seqno, value=None, default=False,
                     disable=False):
        """Configures the routemap continue value

        Args:
            name (string): The full name of the routemap.
            action (string): The action to take for this routemap clause.
            seqno (integer): The sequence number for the routemap clause.
            value (integer): The value to configure for the routemap continue
            default (bool): Specifies to default the routemap continue value
            disable (bool): Specifies to negate the routemap continue value

        Returns:
            True if the operation succeeds otherwise False is returned
        """
        commands = ['route-map %s %s %s' % (name, action, seqno)]
        if default:
            commands.append('default continue')
        elif disable:
            commands.append('no continue')
        else:
            if not str(value).isdigit() or value < 1:
                raise ValueError('seqno must be a positive integer unless '
                                 'default or disable is specified')
            commands.append('continue %s' % value)

        return self.configure(commands)

    def set_description(self, name, action, seqno, value=None, default=False,
                        disable=False):
        """Configures the routemap description

        Args:
            name (string): The full name of the routemap.
            action (string): The action to take for this routemap clause.
            seqno (integer): The sequence number for the routemap clause.
            value (string): The value to configure for the routemap description
            default (bool): Specifies to default the routemap description value
            disable (bool): Specifies to negate the routemap description

        Returns:
            True if the operation succeeds otherwise False is returned
        """
        commands = ['route-map %s %s %s' % (name, action, seqno)]
        if value is not None:
            # Before assigning a new description, clear any existing desc
            commands.append(self.command_builder('description', disable=True))
        commands.append(self.command_builder('description', value=value,
                                             default=default, disable=disable))
        return self.configure(commands)


def instance(node):
    """Returns an instance of Routemaps

    Args:
        node (Node): The node argument passes an instance of Node to the
            resource

    Returns:
        object: An instance of Routemaps
    """
    return Routemaps(node)
