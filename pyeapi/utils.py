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
import sys
import importlib
import inspect
import logging
import logging.handlers
if sys.version_info < (3, 3):
    from collections import Iterable
else:
    from collections.abc import Iterable


from itertools import tee

try:
    # Try Python 3.x import first
    from itertools import zip_longest
except ImportError:
    # Use Python 2.7 import as a fallback
    from itertools import izip_longest as zip_longest

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

# Create a handler to log messages to syslog
if sys.platform == "darwin":
    _syslog_handler = logging.handlers.SysLogHandler(address='/var/run/syslog')
else:
    _syslog_handler = logging.handlers.SysLogHandler()
_LOGGER.addHandler(_syslog_handler)

# Create a handler to log messages to stderr
_stderr_formatter = logging.Formatter('\n\n**** LOG NOTE ****\n%(message)s\n')
_stderr_handler = logging.StreamHandler()
_stderr_handler.setFormatter(_stderr_formatter)
_LOGGER.addHandler(_stderr_handler)


def import_module(name):
    """ Imports a module into the current runtime environment

    This function emulates the Python import system that allows for
    importing full path modules.  It will break down the module and
    import each part (or skip if it is already loaded in cache).

    Args:
        name (str): The name of the module to import.  This should be
            the full path of the module

    Returns:
        The module that was imported

    """
    if name in sys.modules:
        # Be sure not to reload a previously loaded module
        mod = sys.modules[name]
    else:
        mod = importlib.import_module(name)
    return mod


def load_module(name):
    """ Attempts to load a module into the current environment

    This function will load a module specified by name.  The module
    name is first checked to see if it is already loaded and will return
    the module if it is.   If the module hasn't been previously loaded
    it will attempt to import it

    Args:
        name (str): Specifies the full name of the module.  For instance
            pyeapi.api.vlans

    Returns:
        The module that has been imported or retrieved from the sys modules

    """
    try:
        mod = None
        mod = sys.modules[name]
    except KeyError:
        mod = import_module(name)
    finally:
        if not mod:
            raise ImportError('unable to import module %s' % name)
        return mod


class ProxyCall(object):

    def __init__(self, proxy, method):
        self.proxy = proxy
        self.method = method

    def __call__(self, *args, **kwargs):
        return self.proxy(self.method, *args, **kwargs)


def islocalconnection():
    """ Checks if running locally on EOS device or remotely

    This function will return a boolean indicating if the current
    execution environment is running locally on an EOS device (True) or
    running remotely and communicating over HTTP/S (False)

    Returns:
        A boolean value that indicates whether or not the current
            thread is local or remote
    """
    return os.path.exists('/etc/Eos-release')


def debug(text):
    """Log a message to syslog and stderr

    Args:
        text (str): The string object to print

    """
    frame = inspect.currentframe().f_back
    module = frame.f_globals['__name__']
    func = frame.f_code.co_name
    msg = "%s.%s: %s" % (module, func, text)
    _LOGGER.debug(msg)


def make_iterable(value):
    """Converts the supplied value to a list object

    This function will inspect the supplied value and return an
    iterable in the form of a list.

    Args:
        value (object): An valid Python object

    Returns:
        An iterable object of type list
    """
    if sys.version_info <= (3, 0):
        # Convert unicode values to strings for Python 2
        if isinstance(value, unicode):
            value = str(value)
    if isinstance(value, str) or isinstance(value, dict):
        value = [value]

    if not isinstance(value, Iterable):
        raise TypeError('value must be an iterable object')

    return value


def lookahead(it):
    it1, it2 = tee(iter(it))
    next(it2)
    return zip_longest(it1, it2)


def expand_range(arg, value_delimiter=',', range_delimiter='-'):
    """
    Expands a delimited string of ranged integers into a list of strings

    :param arg: The string range to expand
    :param value_delimiter: The delimiter that separates values
    :param range_delimiter: The delimiter that signifies a range of values

    :return: An array of expanded string values
    :rtype: list
    """
    values = list()
    expanded = arg.split(value_delimiter)
    for item in expanded:
        if range_delimiter in item:
            start, end = item.split(range_delimiter)
            _expand = range(int(start), int(end) + 1)
            values.extend([str(x) for x in _expand])
        else:
            values.extend([item])
    return [str(x) for x in values]


def collapse_range(arg, value_delimiter=',', range_delimiter='-'):
    """
    Collapses a list of values into a range set

    :param arg: The list of values to collapse
    :param value_delimiter: The delimiter that separates values
    :param range_delimiter: The delimiter that separates a value range

    :return: An array of collapsed string values
    :rtype: list
    """
    values = list()
    expanded = arg.split(value_delimiter)
    range_start = None

    for v1, v2 in lookahead(expanded):
        if v2:
            v1 = int(v1)
            v2 = int(v2)
            if (v1 + 1) == v2:
                if not range_start:
                    range_start = v1
            elif range_start:
                item = '{}{}{}'.format(range_start, range_delimiter, v1)
                values.extend([item])
                range_start = None
            else:
                values.extend([v1])
        elif range_start:
            item = '{}{}{}'.format(range_start, range_delimiter, v1)
            values.extend([item])
            range_start = None
        else:
            values.extend([v1])
    return [str(x) for x in values]
