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
"""Module for working with EOS static routes

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

# Define the regex to match ip route lines (by lines in regex):
#   'ip route' header
#   ip_dest
#   next_hop
#   next_hop_ip
#   distance
#   tag
#   name
ROUTES_RE = re.compile(r'(?<=^ip route)'
                       r' (\d+\.\d+\.\d+\.\d+\/\d+)'
                       r' (\d+\.\d+\.\d+\.\d+|\S+)'
                       r'(?: (\d+\.\d+\.\d+\.\d+))?'
                       r' (\d+)'
                       r'(?: tag (\d+))?'
                       r'(?: name (\S+))?', re.M)


class StaticRoute(EntityCollection):
    """The StaticRoute class provides a configuration instance
    for working with static routes

    """

    def __str__(self):
        return 'StaticRoute'

    def get(self, name):
        """Retrieves the ip route information for the destination
        ip address specified.

        Args:
            name (string): The ip address of the destination in the
                form of A.B.C.D/E

        Returns:
            dict: An dict object of static route entries in the form::

                { ip_dest:
                    { next_hop:
                        { next_hop_ip:
                            { distance:
                                { 'tag': tag,
                                  'route_name': route_name
                                }
                            }
                        }
                    }
                }

            If the ip address specified does not have any associated
            static routes, then None is returned.

        Notes:
            The keys ip_dest, next_hop, next_hop_ip, and distance in
            the returned dictionary are the values of those components
            of the ip route specification. If a route does not contain
            a next_hop_ip, then that key value will be set as 'None'.
        """

        # Return the route configurations for the specified ip address,
        # or None if its not found
        return self.getall().get(name)

    def getall(self):
        """Return all ip routes configured on the switch as a resource dict

        Returns:
            dict: An dict object of static route entries in the form::

                { ip_dest:
                    { next_hop:
                        { next_hop_ip:
                            { distance:
                                { 'tag': tag,
                                  'route_name': route_name
                                }
                            }
                        }
                    }
                }

            If the ip address specified does not have any associated
            static routes, then None is returned.

        Notes:
            The keys ip_dest, next_hop, next_hop_ip, and distance in
            the returned dictionary are the values of those components
            of the ip route specification. If a route does not contain
            a next_hop_ip, then that key value will be set as 'None'.
        """

        # Find all the ip routes in the config
        matches = ROUTES_RE.findall(self.config)

        # Parse the routes and add them to the routes dict
        routes = dict()
        for match in matches:

            # Get the four identifying components
            ip_dest = match[0]
            next_hop = match[1]
            next_hop_ip = None if match[2] == '' else match[2]
            distance = int(match[3])

            # Create the data dict with the remaining components
            data = {}
            data['tag'] = None if match[4] == '' else int(match[4])
            data['route_name'] = None if match[5] == '' else match[5]

            # Build the complete dict entry from the four components
            # and the data.
            # temp_dict = parent_dict[key] = parent_dict.get(key, {})
            # This creates the keyed dict in the parent_dict if it doesn't
            # exist, or reuses the existing keyed dict.
            # The temp_dict is used to make things more readable.
            ip_dict = routes[ip_dest] = routes.get(ip_dest, {})
            nh_dict = ip_dict[next_hop] = ip_dict.get(next_hop, {})
            nhip_dict = nh_dict[next_hop_ip] = nh_dict.get(next_hop_ip, {})
            nhip_dict[distance] = data

        return routes

    def create(self, ip_dest, next_hop, **kwargs):
        """Create a static route

        Args:
            ip_dest (string): The ip address of the destination in the
                form of A.B.C.D/E
            next_hop (string): The next hop interface or ip address
            **kwargs['next_hop_ip'] (string): The next hop address on
                destination interface
            **kwargs['distance'] (string): Administrative distance for this
                route
            **kwargs['tag'] (string): Route tag
            **kwargs['route_name'] (string): Route name

        Returns:
            True if the operation succeeds, otherwise False.
        """

        # Call _set_route with delete and default set to False
        return self._set_route(ip_dest, next_hop, **kwargs)

    def delete(self, ip_dest, next_hop, **kwargs):
        """Delete a static route

        Args:
            ip_dest (string): The ip address of the destination in the
                form of A.B.C.D/E
            next_hop (string): The next hop interface or ip address
            **kwargs['next_hop_ip'] (string): The next hop address on
                destination interface
            **kwargs['distance'] (string): Administrative distance for this
                route
            **kwargs['tag'] (string): Route tag
            **kwargs['route_name'] (string): Route name

        Returns:
            True if the operation succeeds, otherwise False.
        """

        # Call _set_route with the delete flag set to True
        kwargs.update({'delete': True})
        return self._set_route(ip_dest, next_hop, **kwargs)

    def default(self, ip_dest, next_hop, **kwargs):
        """Set a static route to default (i.e. delete the matching route)

        Args:
            ip_dest (string): The ip address of the destination in the
                form of A.B.C.D/E
            next_hop (string): The next hop interface or ip address
            **kwargs['next_hop_ip'] (string): The next hop address on
                destination interface
            **kwargs['distance'] (string): Administrative distance for this
                route
            **kwargs['tag'] (string): Route tag
            **kwargs['route_name'] (string): Route name

        Returns:
            True if the operation succeeds, otherwise False.
        """

        # Call _set_route with the default flag set to True
        kwargs.update({'default': True})
        return self._set_route(ip_dest, next_hop, **kwargs)

    def set_tag(self, ip_dest, next_hop, **kwargs):
        """Set the tag value for the specified route

        Args:
            ip_dest (string): The ip address of the destination in the
                form of A.B.C.D/E
            next_hop (string): The next hop interface or ip address
            **kwargs['next_hop_ip'] (string): The next hop address on
                destination interface
            **kwargs['distance'] (string): Administrative distance for this
                route
            **kwargs['tag'] (string): Route tag
            **kwargs['route_name'] (string): Route name

        Returns:
            True if the operation succeeds, otherwise False.

        Notes:
            Any existing route_name value must be included in call to
                set_tag, otherwise the tag will be reset
                by the call to EOS.
        """

        # Call _set_route with the new tag information
        return self._set_route(ip_dest, next_hop, **kwargs)

    def set_route_name(self, ip_dest, next_hop, **kwargs):
        """Set the route_name value for the specified route

        Args:
            ip_dest (string): The ip address of the destination in the
                form of A.B.C.D/E
            next_hop (string): The next hop interface or ip address
            **kwargs['next_hop_ip'] (string): The next hop address on
                destination interface
            **kwargs['distance'] (string): Administrative distance for this
                route
            **kwargs['tag'] (string): Route tag
            **kwargs['route_name'] (string): Route name

        Returns:
            True if the operation succeeds, otherwise False.

        Notes:
            Any existing tag value must be included in call to
                set_route_name, otherwise the tag will be reset
                by the call to EOS.
        """

        # Call _set_route with the new route_name information
        return self._set_route(ip_dest, next_hop, **kwargs)

    def _build_commands(self, ip_dest, next_hop, **kwargs):
        """Build the EOS command string for ip route interactions.

        Args:
            ip_dest (string): The ip address of the destination in the
                form of A.B.C.D/E
            next_hop (string): The next hop interface or ip address
            **kwargs['next_hop_ip'] (string): The next hop address on
                destination interface
            **kwargs['distance'] (string): Administrative distance for this
                route
            **kwargs['tag'] (string): Route tag
            **kwargs['route_name'] (string): Route name

        Returns the ip route command string to be sent to the switch for
        the given set of parameters.
        """

        commands = "ip route %s %s" % (ip_dest, next_hop)

        next_hop_ip = kwargs.get('next_hop_ip', None)
        distance = kwargs.get('distance', None)
        tag = kwargs.get('tag', None)
        route_name = kwargs.get('route_name', None)

        if next_hop_ip is not None:
            commands += " %s" % next_hop_ip
        if distance is not None:
            commands += " %s" % distance
        if tag is not None:
            commands += " tag %s" % tag
        if route_name is not None:
            commands += " name %s" % route_name

        return commands

    def _set_route(self, ip_dest, next_hop, **kwargs):
        """Configure a static route

        Args:
            ip_dest (string): The ip address of the destination in the
                form of A.B.C.D/E
            next_hop (string): The next hop interface or ip address
            **kwargs['next_hop_ip'] (string): The next hop address on
                destination interface
            **kwargs['distance'] (string): Administrative distance for this
                route
            **kwargs['tag'] (string): Route tag
            **kwargs['route_name'] (string): Route name
            **kwargs['delete'] (boolean): If true, deletes the specified route
                instead of creating or setting values for the route
            **kwargs['default'] (boolean): If true, defaults the specified
                route instead of creating or setting values for the route

        Returns:
            True if the operation succeeds, otherwise False.
        """

        commands = self._build_commands(ip_dest, next_hop, **kwargs)

        delete = kwargs.get('delete', False)
        default = kwargs.get('default', False)

        # Prefix with 'no' if delete is set
        if delete:
            commands = "no " + commands
        # Or with 'default' if default is setting
        else:
            if default:
                commands = "default " + commands

        return self.configure(commands)


def instance(node):
    """Returns an instance of StaticRoute

    This method will create and return an instance of the StaticRoute
    object passing the value of API to the object. The instance method
    is required for the resource to be autoloaded by the Node object

    Args:
        node (Node): The node argument passes an instance of Node to the
            resource
    """
    return StaticRoute(node)
