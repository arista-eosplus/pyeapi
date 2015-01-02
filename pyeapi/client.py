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
from ConfigParser import ConfigParser

from pyeapi.node import Node
from pyeapi.connection import Connection

config = dict()

CONFPATHS = ['~/.eapi.conf', '/mnt/flash/eapi.conf']

def load_config(filename=None):
    if 'EAPI_CONF' in os.environ:
        CONFPATHS.insert(0, os.environ['EAPI_CONF'])

    if filename is not None:
        CONFPATHS.insert(0, filename)

    for filename in CONFPATHS:
        if os.path.exists(os.path.expanduser(filename)):
            conf = ConfigParser()
            conf.read(filename)

            for section in conf.sections():
                name = section.split(':')[1]
                config[section] = dict(host=name)
                config[section].update(dict(conf.items(section)))

            return filename

def config_for(name):
    return config.get('connection:%s' % name)


def connect(host='localhost', username='admin', password='', use_ssl=True,
            enablepwd='', port=None):

    if not isinstance(use_ssl, bool):
        use_ssl = str(use_ssl).upper() in ['TRUE', 'YES', '1']

    kwargs = dict(host=host, use_ssl=use_ssl, port=port, username=username,
                  password=password, enablepwd=enablepwd)

    return Connection(**kwargs)

def connect_to(name):
    kwargs = config_for(name)
    connection = connect(**kwargs)
    return Node(connection)



