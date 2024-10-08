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
import unittest
import random

from testlib import get_fixture
from pyeapi.utils import CliVariants

import pyeapi.client

class DutSystemTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(DutSystemTest, self).__init__(*args, **kwargs)
        self.longMessage = True

    def setUp(self):
        pyeapi.client.load_config(filename=get_fixture('dut.conf'))
        config = pyeapi.client.config

        self.duts = list()
        for name in config.sections():
            if not name.startswith('connection:'):
                continue
            if 'localhost' in name:
                continue
            name = name.split(':')[1]
            self.duts.append( pyeapi.client.connect_to(name) )
            # revert to a legacy behavior for interface availability
            if self.duts[ -1 ]:
                self.duts[ -1 ].config( CliVariants(
                    'service interface inactive expose', 'enable') )

    def sort_dict_by_keys(self, d):
        keys = sorted(d.keys())
        return dict([(k, d[k]) for k in keys])


def random_interface(dut, exclude=None):
    # interfaces read in 'show run all' and those actually present may differ,
    # thus interface list must be picked from the actually present
    if not getattr( random_interface, 'present', False ):
        random_interface.present = dut.run_commands(
            'show interfaces', send_enable=False )[ 0 ][ 'interfaces' ].keys()
    exclude = [] if exclude is None else exclude
    interfaces = dut.api('interfaces')
    names = [ name for name in list(interfaces.keys()) if name.startswith('Et') ]
    names = [ name for name in names if name in random_interface.present ]

    exclude_interfaces = dut.settings.get('exclude_interfaces', [])
    if exclude_interfaces:
        exclude_interfaces = exclude_interfaces.split(',')
    exclude_interfaces.extend(exclude)

    if sorted(exclude_interfaces) == sorted(names):
        raise TypeError('unable to allocate interface from dut')

    choices = set(names).difference(exclude)
    return random.choice(list(choices))



