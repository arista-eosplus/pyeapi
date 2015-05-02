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
import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))

from testlib import get_fixture, random_string, function
from testlib import EapiConfigUnitTest

import pyeapi.api.system

class TestApiSystem(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestApiSystem, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.system.instance(None)
        self.config = open(get_fixture('running_config.text')).read()

    def test_get(self):
        keys = ['hostname']
        result = self.instance.get()
        self.assertEqual(keys, result.keys())

    def test_set_hostname(self):
        for state in ['config', 'negate', 'default']:
            value = random_string()
            if state == 'config':
                cmds = 'hostname %s' % value
                func = function('set_hostname', value)
            elif state == 'negate':
                cmds = 'no hostname'
                func = function('set_hostname')
            elif state == 'default':
                cmds = 'default hostname'
                func = function('set_hostname', value=value, default=True)
            self.eapi_positive_config_test(func, cmds)

if __name__ == '__main__':
    unittest.main()


