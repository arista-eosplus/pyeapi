import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))

from testlib import get_fixture, function
from testlib import EapiConfigUnitTest

import pyeapi.api.ospf


class TestApiOspf(EapiConfigUnitTest):

    def __init__(self, *args, **kwargs):
        super(TestApiOspf, self).__init__(*args, **kwargs)
        self.instance = pyeapi.api.ospf.instance(None)
        self.config = open(get_fixture('running_config.ospf')).read()

    def test_get(self):
        result = self.instance.get()
        keys = ['networks', 'ospf_process_id', 'redistributions', 'router_id', 'shutdown']
        self.assertEqual(sorted(keys), sorted(result.keys()))

    def test_create(self):
        for ospf_id in ['65000', 65000]:
            func = function('create', ospf_id)
            cmds = 'router ospf {}'.format(ospf_id)
            self.eapi_positive_config_test(func, cmds)

    def test_create_invalid_id(self):
        for ospf_id in ['66000', 66000]:
            with self.assertRaises(ValueError):
                self.instance.create(ospf_id)

    def test_delete(self):
        func = function('delete')
        cmds = 'no router ospf 65000'
        self.eapi_positive_config_test(func, cmds)

    def test_add_network(self):
        func = function('add_network', '172.16.10.0', '24', '0')
        cmds = ['router ospf 65000', 'network 172.16.10.0/24 area 0']
        self.eapi_positive_config_test(func, cmds)

        func = function('add_network', '', '24', '0')
        self.eapi_exception_config_test(func, ValueError)

        func = function('add_network', '172.16.10.0', '', '0')
        self.eapi_exception_config_test(func, ValueError)

    def test_remove_network(self):
        func = function('remove_network', '172.16.10.0', '24', '0')
        cmds = ['router ospf 65000', 'no network 172.16.10.0/24 area 0']
        self.eapi_positive_config_test(func, cmds)

        func = function('remove_network', '', '24', '0')
        self.eapi_exception_config_test(func, ValueError)

        func = function('remove_network', '172.16.10.0', '', '0')
        self.eapi_exception_config_test(func, ValueError)

    def test_set_router_id(self):
        for state in ['config', 'negate', 'default']:
            rid = '1.1.1.1'
            if state == 'config':
                cmds = ['router ospf 65000', 'router-id 1.1.1.1']
                func = function('set_router_id', rid)
            elif state == 'negate':
                cmds = ['router ospf 65000', 'no router-id']
                func = function('set_router_id')
            elif state == 'default':
                cmds = ['router ospf 65000', 'default router-id']
                func = function('set_router_id', rid, True)
            self.eapi_positive_config_test(func, cmds)

        cmds = ['router ospf 65000', 'no router-id']
        func = function('set_router_id')
        self.eapi_positive_config_test(func, cmds)

    def test_set_shutdown(self):
        for state in ['config', 'negate', 'default']:
            if state == 'config':
                cmds = ['router ospf 65000', 'shutdown']
                func = function('set_shutdown')
            elif state == 'negate':
                cmds = ['router ospf 65000', 'no shutdown']
                func = function('set_no_shutdown')
            self.eapi_positive_config_test(func, cmds)


if __name__ == '__main__':
    unittest.main()

