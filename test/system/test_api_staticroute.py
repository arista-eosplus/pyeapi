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
import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))

from random import choice
from testlib import random_int, random_string
from systestlib import DutSystemTest

NEXT_HOPS = ['Ethernet1', 'Ethernet2', 'Null0', 'IP']
DISTANCES = TAGS = ROUTE_NAMES = [None, True]


def _ip_addr():
    ip1 = random_int(0, 223)
    ip2 = random_int(0, 255)
    ip3 = random_int(0, 255)
    return "%s.%s.%s.0/24" % (ip1, ip2, ip3)


def _next_hop():
    next_hop = choice(NEXT_HOPS)
    if next_hop == 'Null0':
        return (next_hop, None)
    ip1 = random_int(0, 223)
    ip2 = random_int(0, 255)
    ip3 = random_int(0, 255)
    ip4 = random_int(0, 255)
    ip_addr = "%s.%s.%s.%s" % (ip1, ip2, ip3, ip4)
    if next_hop == 'IP':
        return (ip_addr, None)
    return (next_hop, ip_addr)


def _distance():
    return random_int(1, 255)


def _tag():
    return random_int(0, 255)


def _route_name():
    return random_string(minchar=4, maxchar=10)


class TestApiStaticroute(DutSystemTest):

    def test_create(self):
        # Validate the create function returns without an error
        # when creating routes with varying parameters included.

        for dut in self.duts:
            dut.config(['no ip routing delete-static-routes',
                        'ip routing'])

            for t_distance in DISTANCES:
                for t_tag in TAGS:
                    for t_route_name in ROUTE_NAMES:
                        ip_dest = _ip_addr()
                        (next_hop, next_hop_ip) = _next_hop()
                        distance = t_distance
                        if distance is True:
                            distance = _distance()
                        tag = t_tag
                        if tag is True:
                            tag = _tag()
                        route_name = t_route_name
                        if route_name is True:
                            route_name = _route_name()

                        result = dut.api('staticroute').create(
                            ip_dest, next_hop, next_hop_ip=next_hop_ip,
                            distance=distance, tag=tag, route_name=route_name)

                        self.assertTrue(result)

    def test_get(self):
        # Validate the get function returns the exact value that
        # is passed in when the route exists on the switch.

        for dut in self.duts:
            dut.config(['no ip routing delete-static-routes',
                        'ip routing'])

            ip_dest = '1.2.3.0/24'
            next_hop = 'Ethernet1'
            next_hop_ip = '1.1.1.1'
            distance = 1
            tag = 1
            route_name = 'test1'

            cmd = "ip route %s %s %s %s tag %s name %s" % \
                (ip_dest, next_hop, next_hop_ip, distance, tag, route_name)
            dut.config([cmd])

            route = {
                next_hop: {
                    next_hop_ip: {
                        distance: {
                            'tag': tag,
                            'route_name': route_name
                        }
                    }
                }
            }

            result = dut.api('staticroute').get(ip_dest)

            # Make sure the funtion returns a true result (match found)
            self.assertTrue(result)
            # Then make sure the returned string is what was expected
            # self.assertEqual(result.group(0), cmd)
            self.assertEqual(result, route)

    def test_getall(self):
        # Validate the get_all function returns a list of entries
        # containing the matched parameters, and that parameters
        # are matched in full (i.e. name 'test1' does not match
        # name 'test10').

        for dut in self.duts:
            dut.config(['no ip routing delete-static-routes',
                        'ip routing'])

            # Declare a set of 3 routes with same ip dest and next hop.
            # Set different distance, tag and name for each route,
            # including values 1 and 10 in each, so the test will verify
            # that matching 1 does not also match 10.
            route1 = \
                'ip route 1.2.3.0/24 Ethernet1 1.1.1.1 10 tag 1 name test1'
            route2 = \
                'ip route 1.2.3.0/24 Ethernet1 1.1.1.1 1 tag 1 name test10'
            route3 = \
                'ip route 1.2.3.0/24 Ethernet1 1.1.1.1 2 tag 10 name test1'

            dut.config([route1, route2, route3])

            routes = {
                '1.2.3.0/24': {
                    'Ethernet1': {
                        '1.1.1.1': {
                            10: {
                                'tag': 1,
                                'route_name': 'test1'
                            },
                            1: {
                                'tag': 1,
                                'route_name': 'test10'
                            },
                            2: {
                                'tag': 10,
                                'route_name': 'test1'
                            }
                        }
                    }
                }
            }

            # Get the list of ip routes from the switch
            result = dut.api('staticroute').getall()

            # Assert that the result dict is equivalent to the routes dict
            self.assertEqual(result, routes)

    def test_delete(self):
        # Validate the delete function returns without an error
        # when deleting routes with varying parameters included.
        # Note: the routes do not have to exist for the
        # delete command to succeed, but only that the command
        # does not error.

        for dut in self.duts:
            dut.config(['no ip routing delete-static-routes',
                        'ip routing'])

            for t_distance in DISTANCES:
                for t_tag in TAGS:
                    for t_route_name in ROUTE_NAMES:
                        ip_dest = _ip_addr()
                        (next_hop, next_hop_ip) = _next_hop()
                        distance = t_distance
                        if distance is True:
                            distance = _distance()
                        tag = t_tag
                        if tag is True:
                            tag = _tag()
                        route_name = t_route_name
                        if route_name is True:
                            route_name = _route_name()

                        result = dut.api('staticroute').delete(
                            ip_dest, next_hop, next_hop_ip=next_hop_ip,
                            distance=distance, tag=tag, route_name=route_name)

                        self.assertTrue(result)

    def test_default(self):
        # Validate the default function returns without an error
        # when deleting routes with varying parameters included.
        # Note: currently EOS functionality of 'default ip route ...'
        # is equivalent to 'no ip route ...', which is the delete
        # function.

        for dut in self.duts:
            dut.config(['no ip routing delete-static-routes',
                        'ip routing'])

            for t_distance in DISTANCES:
                for t_tag in TAGS:
                    for t_route_name in ROUTE_NAMES:
                        ip_dest = _ip_addr()
                        (next_hop, next_hop_ip) = _next_hop()
                        distance = t_distance
                        if distance is True:
                            distance = _distance()
                        tag = t_tag
                        if tag is True:
                            tag = _tag()
                        route_name = t_route_name
                        if route_name is True:
                            route_name = _route_name()

                        result = dut.api('staticroute').default(
                            ip_dest, next_hop, next_hop_ip=next_hop_ip,
                            distance=distance, tag=tag, route_name=route_name)

                        self.assertTrue(result)

    def test_set_tag(self):
        # Validate the set_tag function returns without an error
        # when modifying the tag on an existing route

        for dut in self.duts:
            dut.config(['no ip routing delete-static-routes',
                        'ip routing',
                        'ip route 1.2.3.0/24 Ethernet1 1.1.1.1 10 tag 99'])

            result = dut.api('staticroute').set_tag(
                '1.2.3.0/24', 'Ethernet1', next_hop_ip='1.1.1.1',
                distance=10, tag=3)
            self.assertTrue(result)

    def test_set_route_name(self):
        # Validate the set_route_name function returns without an error
        # when modifying the tag on an existing route

        for dut in self.duts:
            dut.config(['no ip routing delete-static-routes',
                        'ip routing',
                        'ip route 1.2.3.0/24 Ethernet1 1.1.1.1 1 name test99'])

            result = dut.api('staticroute').set_route_name(
                '1.2.3.0/24', 'Ethernet1', next_hop_ip='1.1.1.1',
                distance=1, route_name='test3')
            self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
