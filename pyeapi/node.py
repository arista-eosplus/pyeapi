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
import collections

from pyeapi.utils import load_module


class Node(object):

    def __init__(self, connection):
        self._connection = connection

    @property
    def connection(self):
        return self._connection

    def __str__(self):
        return 'Node(uri=%s)' % self.connection.uri

    def __repr__(self):
        return 'Node(%s)' % repr(self.connection)

    def config(self, commands):
        """Convenience method that sends commands to config mode
        """
        if isinstance(commands, basestring):
            commands = [commands]

        if not isinstance(commands, collections.Iterable):
            raise TypeError('commands must be an iterable object')

        # push the configure command onto the command stack
        commands.insert(0, 'configure')
        response = self.enable(commands)

        # pop the configure command output off the stack
        response.pop(0)

        return response

    def enable(self, commands, serialization='json'):
        """Convenience method that sends commands to enable mode
        """
        if isinstance(commands, basestring):
            commands = [commands]

        if not isinstance(commands, collections.Iterable):
            raise TypeError('commands must be an iterable object')

        response = self._connection.execute(commands, serialization)
        return response['result']

    def api(self, name, namespace='pyeapi.api'):
        """Loads the resource identified by name
        """
        module = load_module('{}.{}'.format(namespace, name))
        return module.instance(self)

    def get_config(self, config='running-config', params=None):
        """Convenience method that returns the running-config as a dict
        """
        command = 'show %s' % config
        if params:
            command += ' %s' % params
        result = self.enable(command, 'text')
        return str(result[0]['output']).strip()

