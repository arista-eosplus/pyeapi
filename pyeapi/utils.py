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
import imp
import syslog
import collections

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
    parts = name.split('.')
    path = None
    module_name = ''

    for index, part in enumerate(parts):
        module_name = part if index == 0 else '%s.%s' % (module_name, part)
        path = [path] if path is not None else path

        try:
            fhandle, path, descr = imp.find_module(part, path)
            if module_name in sys.modules:
                # since imp.load_module works like reload, need to be sure not
                # to reload a previously loaded module
                mod = sys.modules[module_name]
            else:
                mod = imp.load_module(module_name, fhandle, path, descr)
        finally:
            # lets be sure to clean up after ourselves
            if fhandle:
                fhandle.close()

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
    """Prints test to syslog when on a local connection

    Args:
        text (str): The string object to print to syslog

    """
    if islocalconnection():
        syslog.openlog('pyeapi')
        syslog.syslog(syslog.LOG_NOTICE, str(text))

def make_iterable(value):
    """Converts the supplied value to a list object

    This function will inspect the supplied value and return an
    iterable in the form of a list.

    Args:
        value (object): An valid Python object

    Returns:
        An iterable object of type list
    """
    if isinstance(value, basestring):
        value = [value]

    if not isinstance(value, collections.Iterable):
        raise TypeError('value must be an iterable object')

    return value

