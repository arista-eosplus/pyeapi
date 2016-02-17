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
import os
import unittest

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))

from testlib import random_int, random_string
from systestlib import DutSystemTest


class TestApiVlans(DutSystemTest):

    def test_get(self):
        for dut in self.duts:
            dut.config(['no vlan 1', 'vlan 1'])
            response = dut.api('vlans').get('1')
            values = dict(vlan_id='1', name='default', state='active',
                          trunk_groups=[])
            self.assertEqual(values, response)

    def test_getall(self):
        for dut in self.duts:
            dut.config(['no vlan 1-4094', 'vlan 1', 'vlan 10'])
            response = dut.api('vlans').getall()
            self.assertIsInstance(response, dict, 'dut=%s' % dut)
            for vid in ['1', '10']:
                self.assertIn(vid, response, 'dut=%s' % dut)

    def test_create_and_return_true(self):
        for dut in self.duts:
            dut.config('no vlan 2-4094')
            vid = str(random_int(2, 4094))
            result = dut.api('vlans').create(vid)
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show vlan')
            self.assertIn(vid, config[0]['vlans'], 'dut=%s' % dut)

    def test_create_and_return_false(self):
        for dut in self.duts:
            result = dut.api('vlans').create('5000')
            self.assertFalse(result, 'dut=%s' % dut)

    def test_delete_and_return_true(self):
        for dut in self.duts:
            vid = str(random_int(2, 4094))
            dut.config('vlan %s' % vid)
            result = dut.api('vlans').delete(vid)
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show vlan')
            self.assertNotIn(vid, config[0]['vlans'])

    def test_delete_and_return_false(self):
        for dut in self.duts:
            result = dut.api('vlans').delete('5000')
            self.assertFalse(result, 'dut=%s' % dut)

    def test_default(self):
        for dut in self.duts:
            vid = str(random_int(2, 4095))
            name = random_string(maxchar=20)
            dut.config(['no vlan %s' % vid, 'vlan %s' % vid,
                        'vlan %s' % vid, 'name %s' % name])
            result = dut.api('vlans').default(vid)
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show vlan')
            self.assertNotIn(vid, config[0]['vlans'], 'dut=%s' % dut)

    def test_set_name(self):
        for dut in self.duts:
            name = random_string(maxchar=20)
            vid = str(random_int(2, 4095))
            dut.config(['no vlan %s' % vid, 'vlan %s' % vid])
            result = dut.api('vlans').set_name(vid, name)
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show vlan')
            self.assertEqual(name, config[0]['vlans'][vid]['name'],
                             'dut=%s' % dut)

    def test_set_state_active(self):
        for dut in self.duts:
            vid = str(random_int(2, 4095))
            dut.config(['no vlan %s' % vid, 'vlan %s' % vid, 'state suspend'])
            result = dut.api('vlans').set_state(vid, 'active')
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show vlan')
            self.assertEqual('active', config[0]['vlans'][vid]['status'],
                             'dut=%s' % dut)

    def test_set_state_suspend(self):
        for dut in self.duts:
            vid = str(random_int(2, 4095))
            dut.config(['no vlan %s' % vid, 'vlan %s' % vid, 'state active'])
            result = dut.api('vlans').set_state(vid, 'suspend')
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show vlan')
            self.assertEqual('suspended', config[0]['vlans'][vid]['status'],
                             'dut=%s' % dut)

    def test_set_trunk_groups_default(self):
        for dut in self.duts:
            vid = str(random_int(2, 4094))
            tg = random_string()
            dut.config(['no vlan %s' % vid, 'vlan %s' % vid,
                        'trunk group %s' % tg])
            result = dut.api('vlans').set_trunk_groups(vid, default=True)
            self.assertTrue(result, 'dut=%s' % dut)
            cmd = 'show running-config section vlan %s' % vid
            config = dut.run_commands(cmd, 'text')
            self.assertNotIn('trunk group', config[0]['output'])

    def test_set_trunk_groups(self):
        for dut in self.duts:
            vid = str(random_int(2, 4094))
            tg1 = random_string(maxchar=10)
            tg2 = random_string(maxchar=10)
            tg3 = random_string(maxchar=10)
            dut.config(['no vlan %s' % vid, 'vlan %s' % vid,
                        'trunk group %s' % tg1, 'trunk group %s' % tg2])
            result = dut.api('vlans').set_trunk_groups(vid, [tg1, tg3])
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show vlan %s trunk group' % vid)
            config = sorted(config[0]['trunkGroups'][vid]['names'])
            self.assertEqual(sorted([tg1, tg3]), config)

    def test_set_trunk_groups_disable(self):
        for dut in self.duts:
            vid = str(random_int(2, 4094))
            tg1 = random_string(maxchar=10)
            tg2 = random_string(maxchar=10)
            tg3 = random_string(maxchar=10)
            dut.config(['no vlan %s' % vid, 'vlan %s' % vid,
                        'trunk group %s' % tg1, 'trunk group %s' % tg2,
                        'trunk group %s' % tg3])
            result = dut.api('vlans').set_trunk_groups(vid, disable=True)
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show vlan %s trunk group' % vid)
            config = sorted(config[0]['trunkGroups'][vid]['names'])
            self.assertEqual([], config)

    def test_add_trunk_group(self):
        for dut in self.duts:
            tg = random_string(maxchar=32)
            vid = str(random_int(2, 4095))
            dut.config(['no vlan %s' % vid, 'vlan %s' % vid, 'no trunk group'])
            result = dut.api('vlans').add_trunk_group(vid, tg)
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show vlan trunk group')
            self.assertIn(tg, config[0]['trunkGroups'][vid]['names'],
                          'dut=%s' % dut)

    def test_remove_trunk_group(self):
        for dut in self.duts:
            tg = random_string(maxchar=32)
            vid = str(random_int(2, 4095))
            dut.config(['no vlan %s' % vid, 'vlan %s' % vid, 'no trunk group',
                        'trunk group %s' % tg])
            result = dut.api('vlans').remove_trunk_group(vid, tg)
            self.assertTrue(result, 'dut=%s' % dut)
            config = dut.run_commands('show vlan trunk group')
            self.assertNotIn(tg, config[0]['trunkGroups'][vid]['names'],
                             'dut=%s' % dut)


if __name__ == '__main__':
    unittest.main()
