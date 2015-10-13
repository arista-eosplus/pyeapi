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
# XXX fix the documentation below
"""Module for working with EOS static routes
XXX
The staticroute resource provides configuration management of static
route resources on an EOS node. It provides the following class
implementations:

    * StaticRoute - Configure static routes in EOS

StaticRoute Attributes:
    ip_dest (string): The ip address of the destination in the
        form of A.B.C.D/E
    next_hop (string): The next hop interface or ip address
    next_hop_ip (string): The next hop address on destination interface
    distance (int): Administrative distance for this route
    tag (int): Route tag
    route_name (string): Route name

Notes:
    The 'default' prefix function of the 'ip route' command,
    'default ip route ...', currently equivalent to the 'no ip route ...'
    command.
"""

import re

from pyeapi.api import EntityCollection

# Create the regular expression for matching ip route strings
ROUTES_RE = re.compile(r'''(?<=^ip\sroute\s)
                           (?P<ip_dest>[^\s]+)\s
                           (?P<next_hop>[^\s$]+)
                           [\s|$]{0,1}(?P<next_hop_ip>\d+\.\d+\.\d+\.\d+)?
                           [\s|$](?P<distance>\d+)
                           [\s|$]{1}(?:tag\s(?P<tag>\d+))?
                           [\s|$]{1}(?:name\s(?P<name>.+))?
                        ''', re.X)


class StaticRoute(EntityCollection):
    """The StaticRoute class provides a configuration instance
    for working with static routes

    """

    def __str__(self):
        return 'StaticRoute'

    def get(self, ip_dest, next_hop, next_hop_ip=None,
            distance=None, tag=None, route_name=None):
        """Check the running config for a route that matches the input
            values exactly.

        This may be used as a route_exists function.

        Args:
            ip_dest (string): The ip address of the destination in the
                form of A.B.C.D/E
            next_hop (string): The next hop interface or ip address
            next_hop_ip (string): The next hop address on destination
                interface
            distance (int): Administrative distance for this route
            tag (int): Route tag
            route_name (string): Route name

        Returns the matched ip route string if the route entry exists,
        otherwise returns False.
        """

        # If distance is None, then distance on the switch is 1 by default
        if distance is None:
            distance = 1

        # If tag is None, then tag on the switch is 0 by default
        if tag is None:
            tag = 0

        # Create the match string based on the parameters received
        match_str = self._build_commands(ip_dest, next_hop,
                                         next_hop_ip=next_hop_ip,
                                         distance=distance,
                                         tag=tag,
                                         route_name=route_name)
        ip_route_re = re.compile(r'^%s$' % match_str, re.M)

        # Search the configuration for the match string
        config = ip_route_re.search(self.config)

        # Return the matched string from the config if found, otherwise
        # will return None
        return config.group(0)

    def get_all(self, ip_dest, next_hop, next_hop_ip=None,
                distance=None, tag=None, route_name=None):
        # XXX documentation
        """Return a list of all static route strings that contain
        exact matches for each of the specified parameters. If a
        parameter is not specified, then static routes with or without
        that parameter can be matched

        Args:
            ip_dest (string): The ip address of the destination in the
                form of A.B.C.D/E
            next_hop (string): The next hop interface or ip address
            next_hop_ip (string): The next hop address on destination
                interface
            distance (int): Administrative distance for this route
            tag (int): Route tag
            route_name (string): Route name

        Returns a list of the routes on the list that match all the
        specified parameters exactly, or None if no matches are found.
        """

        # Initialize the return array
        match_list = []

        # Initialize the match string with the required parameters
        # and the 'ip route' label
        match_str = "ip route %s %s" % (ip_dest, next_hop)

        # Each segment should match a specific value if passed in as
        # a parameter, or if not specified, it should match any value
        # in that place or an empty string where that toke should be.
        # The name and tag negation prevents matching tag and name
        # to an earlier regex which would prevent the exact match
        # later in the string.

        # If next_hop_ip is specified, look for an exact match,
        # otherwise allow any or no next_hop_ip to match
        if next_hop_ip is not None:
            match_str += " %s" % next_hop_ip
        else:
            match_str += "( (?!name)(?!tag)[^\s]*)?"

        # If distance is specified, look for an exact match,
        # otherwise allow any or no distance to match
        if distance is not None:
            match_str += " %s" % distance
        else:
            match_str += "( (?!name)(?!tag)[^\s]*)?"

        # If tag is specified, look for an exact match,
        # otherwise allow any or no tag to match
        if tag is not None:
            match_str += " tag %s" % tag
        else:
            match_str += "( (?!name)[^\s]*)?( (?!name)[^\s]*)?"

        # If route_name is specified, look for an exact match,
        # otherwise allow any or no route_name to match
        if route_name is not None:
            match_str += " name %s" % route_name
        else:
            match_str += "( [^\s]*)?( [^\s]*)?"

        # Enclose the entire string in parenthesis to capture
        # the whole string as well as any groups from above
        match_str = "^(%s)$" % match_str

        ip_route_re = re.compile(r'%s' % match_str, re.M)

        # Add the matching full strings to the match_list, using
        # the first entry when the result has other groups that
        # match (when one or more parameters is unspecified), or
        # using the single string when only the entire string matches.
        for route in ip_route_re.findall(self.config):
            if type(route).__name__ == 'str':
                match_list.append(route)
            else:
                match_list.append(route[0])

        return match_list

    def create(self, ip_dest, next_hop, next_hop_ip=None,
               distance=None, tag=None, route_name=None):
        """Create a static route

        Args:
            ip_dest (string): The ip address of the destination in the
                form of A.B.C.D/E
            next_hop (string): The next hop interface or ip address
            next_hop_ip (string): The next hop address on destination
                interface
            distance (int): Administrative distance for this route
            tag (int): Route tag
            route_name (string): Route name

        Returns:
            True if the operation succeeds, otherwise False.
        """

        # Call _set_route with the delete flag set to True
        return self._set_route(ip_dest, next_hop, next_hop_ip=next_hop_ip,
                               distance=distance, tag=tag,
                               route_name=route_name)

    def delete(self, ip_dest, next_hop, next_hop_ip=None,
               distance=None, tag=None, route_name=None):
        """Delete a static route

        Args:
            ip_dest (string): The ip address of the destination in the
                form of A.B.C.D/E
            next_hop (string): The next hop interface or ip address
            next_hop_ip (string): The next hop address on destination
                interface
            distance (int): Administrative distance for this route
            tag (int): Route tag
            route_name (string): Route name

        Returns:
            True if the operation succeeds, otherwise False.
        """

        # Call _set_route with the delete flag set to True
        return self._set_route(ip_dest, next_hop, next_hop_ip=next_hop_ip,
                               distance=distance, tag=tag,
                               route_name=route_name, delete=True)

    def default(self, ip_dest, next_hop, next_hop_ip=None,
                distance=None, tag=None, route_name=None):
        """Set a static route to default (i.e. delete the matching route)

        Args:
            ip_dest (string): The ip address of the destination in the
                form of A.B.C.D/E
            next_hop (string): The next hop interface or ip address
            next_hop_ip (string): The next hop address on destination
                interface
            distance (int): Administrative distance for this route
            tag (int): Route tag
            route_name (string): Route name

        Returns:
            True if the operation succeeds, otherwise False.
        """

        # Call _set_route with the delete flag set to True
        return self._set_route(ip_dest, next_hop, next_hop_ip=next_hop_ip,
                               distance=distance, tag=tag,
                               route_name=route_name, default=True)

    def _build_commands(self, ip_dest, next_hop, next_hop_ip=None,
                        distance=None, tag=None, route_name=None):
        """Build the EOS command string for ip route interactions.

        Args:
            ip_dest (string): The ip address of the destination in the
                form of A.B.C.D/E
            next_hop (string): The next hop interface or ip address
            next_hop_ip (string): The next hop address on destination
                interface
            distance (int): Administrative distance for this route
            tag (int): Route tag
            route_name (string): Route name

        Returns the ip route command string to be sent to the switch for
        the given set of parameters.
        """

        commands = "ip route %s %s" % (ip_dest, next_hop)

        if next_hop_ip is not None:
            commands += " %s" % next_hop_ip
        if distance is not None:
            commands += " %s" % distance
        if tag is not None:
            commands += " tag %s" % tag
        if route_name is not None:
            commands += " name %s" % route_name

        return commands

    def _set_route(self, ip_dest, next_hop, next_hop_ip=None,
                   distance=None, tag=None, route_name=None,
                   delete=False, default=False):
        """Configure a static route

        Args:
            ip_dest (string): The ip address of the destination in the
                form of A.B.C.D/E
            next_hop (string): The next hop interface or ip address
            next_hop_ip (string): The next hop address on destination
                interface
            distance (int): Administrative distance for this route
            tag (int): Route tag
            route_name (string): Route name
            delete (boolean): If true, deletes the specified route
                instead of creating or setting values for the route

        Returns:
            True if the operation succeeds, otherwise False.
        """

        # Build the route string based on the parameters given
        commands = self._build_commands(ip_dest, next_hop,
                                        next_hop_ip=next_hop_ip,
                                        distance=distance,
                                        tag=tag,
                                        route_name=route_name)

        # Prefix with 'no' if delete is set
        if delete:
            commands = "no " + commands
        # Or with 'default' if default is setting
        else:
            if default:
                commands = "default " + commands

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
    return StaticRoute(node)
