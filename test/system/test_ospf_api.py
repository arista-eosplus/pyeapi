#
# Copyright (c) 2016, Arista Networks, Inc.
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
import os
import unittest

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))

from random import randint
from systestlib import DutSystemTest
def clear_ospf_config(dut, id=None):
    if id is None:
        try:
            id = int(dut.get_config(params="section ospf")[0].split()[2])
            dut.config(['no router ospf %d' % id])
        except IndexError:
            '''No OSPF configured'''
            pass

class TestApiOspf(DutSystemTest):
    def test_get(self):
        for dut in self.duts:
            clear_ospf_config(dut)
            dut.config(["router ospf 1", "router-id 1.1.1.1", "network 2.2.2.0/24 area 0", 
                        "redistribute bgp"])
            ospf_response = dut.api('ospf').get()
            config = dict(router_id="1.1.1.1", ospf_process_id=1, 
                          networks=[dict(netmask='24', network="2.2.2.0", area="0.0.0.0")],
                          redistributions=[dict(protocol="bgp")], shutdown=False)
            self.assertEqual(ospf_response, config)
            
    def test_shutdown(self):
        for dut in self.duts:
            clear_ospf_config(dut)
            dut.config(["router ospf 1", "network 1.1.1.1/32 area 0"])
            ospf = dut.api('ospf')
            response = ospf.set_shutdown()
            self.assertTrue(response)
            self.assertIn('shutdown', ospf.get_block("router ospf 1"))

    def test_no_shutown(self):
        for dut in self.duts:
            clear_ospf_config(dut)
            dut.config(["router ospf 10", "network 1.1.1.0/24 area 0", 
                         "shutdown"])
            ospf = dut.api('ospf')
            response = ospf.set_no_shutdown()
            self.assertTrue(response)
            self.assertIn('no shutdown', ospf.get_block("router ospf 10"))

    def test_delete(self):
        for dut in self.duts:
            clear_ospf_config(dut)
            dut.config(["router ospf 10"])
            ospf = dut.api("ospf")
            response = ospf.delete()
            self.assertTrue(response)
            self.assertEqual(None, ospf.get_block("router ospf"))

    def test_create_valid_id(self):
        for dut in self.duts:
            clear_ospf_config(dut)
            id = randint(1,65536)
            ospf = dut.api("ospf")
            response = ospf.create(id)
            self.assertTrue(response)
            self.assertIn("router ospf {}".format(id), dut.get_config())

    def test_create_invalid_id(self):
        for dut in self.duts:
            clear_ospf_config(dut)
            id = randint(70000, 100000)
            with self.assertRaises(ValueError):
                dut.api("ospf").create(id)

    def test_configure_ospf(self):
        for dut in self.duts:
            clear_ospf_config(dut)
            dut.config(["router ospf 1"])
            ospf = dut.api("ospf")
            response = ospf.configure_ospf("router-id 1.1.1.1")
            self.assertTrue(response)
            self.assertIn("router-id 1.1.1.1", ospf.get_block("router ospf 1"))
    def test_set_router_id(self):
        for dut in self.duts:
            clear_ospf_config(dut)
            dut.config(["router ospf 1"])
            ospf = dut.api("ospf")
            response = ospf.set_router_id(randint(1, 65536))
            self.assertFalse(response)
            response = ospf.set_router_id("2.2.2.2")
            self.assertTrue(response)
            self.assertIn("router-id 2.2.2.2", ospf.get_block("router ospf 1"))
            response = ospf.set_router_id(default=True)
            self.assertTrue(response)
            self.assertIn("no router-id", ospf.get_block("router ospf 1"))
            response = ospf.set_router_id(disable=True)
            self.assertTrue(response)
            self.assertIn("no router-id", ospf.get_block("router ospf 1"))
            


