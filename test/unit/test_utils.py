import unittest
import collections

from mock import patch, Mock

import pyeapi.utils

class TestUtils(unittest.TestCase):

    @patch('pyeapi.utils.import_module')
    def test_load_module(self, mock_import_module):
        loaded_module = Mock(object='loaded_module')
        mock_import_module.return_value = loaded_module
        result = pyeapi.utils.load_module('test')
        self.assertEqual(result, loaded_module)

    @patch('pyeapi.utils.import_module')
    def test_load_module_raises_import_error(self, mock_import_module):
        mock_import_module.return_value = None
        with self.assertRaises(ImportError):
            pyeapi.utils.load_module('test')

    def test_make_iterable_from_string(self):
        result = pyeapi.utils.make_iterable('test')
        self.assertIsInstance(result, collections.Iterable)

    def test_make_iterable_from_iterable(self):
        result = pyeapi.utils.make_iterable(['test'])
        self.assertIsInstance(result, collections.Iterable)

    def test_make_iterable_raises_type_error(self):
        with self.assertRaises(TypeError):
            pyeapi.utils.make_iterable(object())

    def test_import_module(self):
        result = pyeapi.utils.import_module('pyeapi.api.vlans')
        self.assertIsNotNone(result)

    def test_import_module_raises_import_error(self):
        with self.assertRaises(ImportError):
            pyeapi.utils.import_module('fake.module.test')

    @patch('pyeapi.utils.syslog')
    def test_debug(self, mock_syslog):
        pyeapi.utils.islocalconnection = Mock(return_value=True)
        pyeapi.utils.debug('test')
        mock_syslog.syslog.assert_called_with(mock_syslog.LOG_NOTICE, 'test')
