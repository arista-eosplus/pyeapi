import sys
import unittest

from mock import patch, Mock
import pyeapi.utils

if sys.version_info < (3, 3):
    from collections import Iterable
else:
    from collections.abc import Iterable

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
        self.assertIsInstance(result, Iterable)
        self.assertEqual(len(result), 1)

    def test_make_iterable_from_unicode(self):
        result = pyeapi.utils.make_iterable(u'test')
        self.assertIsInstance(result, Iterable)
        self.assertEqual(len(result), 1)

    def test_make_iterable_from_iterable(self):
        result = pyeapi.utils.make_iterable(['test'])
        self.assertIsInstance(result, Iterable)
        self.assertEqual(len(result), 1)


    def test_make_iterable_raises_type_error(self):
        with self.assertRaises(TypeError):
            pyeapi.utils.make_iterable(object())

    def test_import_module(self):
        result = pyeapi.utils.import_module('pyeapi.api.vlans')
        self.assertIsNotNone(result)

    def test_import_module_raises_import_error(self):
        with self.assertRaises(ImportError):
            pyeapi.utils.import_module('fake.module.test')

    def test_expand_singles(self):
        vlans = '1,2,3'
        result = pyeapi.utils.expand_range(vlans)
        result = ','.join(result)
        self.assertTrue(vlans == result)

    def test_expand_range(self):
        vlans = '1-15'
        expected = [str(x) for x in range(1, 16)]
        result = pyeapi.utils.expand_range(vlans)
        self.assertEqual(result, expected)

    def test_expand_mixed(self):
        vlans = '1,3,5-7,9'
        result = pyeapi.utils.expand_range(vlans)
        self.assertEqual(result, ['1', '3', '5', '6', '7', '9'])

    def test_collapse_singles(self):
        vlans = '1,3,5,7'
        result = pyeapi.utils.collapse_range(vlans)
        self.assertEqual(result, ['1', '3', '5', '7'])

    def test_collapse_range(self):
        vlans = '1,2,3,4,5'
        result = pyeapi.utils.collapse_range(vlans)
        self.assertEqual(result, ['1-5'])

    def test_collapse_mixed(self):
        vlans = '1,3,5,6,7,9'
        result = pyeapi.utils.collapse_range(vlans)
        self.assertEqual(result, ['1', '3', '5-7', '9'])

    @patch('pyeapi.utils._LOGGER')
    def test_debug(self, mock_logger):
        pyeapi.utils.islocalconnection = Mock(return_value=True)
        pyeapi.utils.debug('test')
        mock_logger.debug.assert_called_with('test_utils.test_debug: test')
