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

from collections import namedtuple
from ConfigParser import ConfigParser

from pyeapi.utils import load_module, make_iterable

from pyeapi.eapilib import HttpEapiConnection, HttpsEapiConnection
from pyeapi.eapilib import SocketEapiConnection, HttpLocalEapiConnection
from pyeapi.eapilib import CommandError

config = {'connection:localhost': dict(transport='socket')}

CONF_SEARCH_PATH = ['~/.eapi.conf', '/mnt/flash/eapi.conf']

TRANSPORTS = {
    'socket': SocketEapiConnection,
    'http_local': HttpLocalEapiConnection,
    'http': HttpEapiConnection,
    'https': HttpsEapiConnection
}

DEFAULT_TRANSPORT = 'http'


def load_config(filename=None):
    if 'EAPI_CONF' in os.environ:
        CONF_SEARCH_PATH.insert(0, os.environ['EAPI_CONF'])

    if filename is not None:
        CONF_SEARCH_PATH.insert(0, filename)

    for filename in CONF_SEARCH_PATH:
        if os.path.exists(os.path.expanduser(filename)):
            conf = ConfigParser()
            conf.read(os.path.expanduser(filename))

            for section in conf.sections():
                name = section.split(':')[1]
                config[section] = dict(host=name)
                config[section].update(dict(conf.items(section)))

            return filename

def config_for(name):
    _name = 'connection:{}'.format(name)
    if _name not in config:
        raise KeyError(name)
    return config[_name]

def make_connection(transport, **kwargs):
    if transport not in TRANSPORTS.keys():
        raise TypeError('invalid transport specified')
    klass = TRANSPORTS.get(transport)
    return klass(**kwargs)

def connect(transport=None, host='localhost', username='admin',
            password='', port=None):

    transport = transport or DEFAULT_TRANSPORT
    kwargs = dict(host=host, username=username, password=password, port=port)
    return make_connection(transport, **kwargs)


class Node(object):

    def __init__(self, connection, **kwargs):
        self._connection = connection
        self._exec = None

    @property
    def connection(self):
        return self._connection

    def exec_authentication(self, password):
        """Configures the executive mode authentication password

        EOS supports an additional password authentication mechanism for
        sessions that want to switch to executive (or enable) mode.  This
        method will configure the password, if required, for entering
        executive mode

        Args:
            password (str): The password string in clear text used to
                authenticate to exec mode
        """
        self._exec = password
        self._exec = str(password).strip()

    def config(self, commands):
        """Convenience method that sends commands to config mode
        """
        commands = make_iterable(commands)

        # push the configure command onto the command stack
        commands.insert(0, 'configure')
        response = self.run_commands(commands)

        # pop the configure command output off the stack
        response.pop(0)

        return response

    def enable(self, commands, encoding='json', strict=False):
        """Sends the array of commands to the node in enable mode

        This method will send the commands to the node and evaluate
        the results.  If a command fails due to an encoding error,
        then the command set will be re-issued individual with text
        encoding.

        Args:
            commands (list): The list of commands to send to the node

            encoding (str): The requested encoding of the command output.
                Valid values for encoding are json or text

            strict (bool): If False, this method will attempt to run a
                command with text encoding if json encoding fails

        Returns:
            A dict object that includes the response for each command along
                with the encoding

        Raises:
            TypeError: This method does not support sending configure
                commands and will raise a TypeError if configuration commands
                are found in the list of commands provided

            CommandError: This method will raise a CommandError if any one
                of the commands fails.

        """
        commands = make_iterable(commands)

        if 'configure' in commands:
            raise TypeError('config mode commands not supported')

        results = list()
        if strict:
            responses = self.run_commands(commands, encoding)
            for index, response in enumerate(responses):
                results.append(dict(command=commands[index],
                                    response=response,
                                    encoding=encoding))
        else:
            for command in commands:
                try:
                    resp = self.run_commands(command, encoding)
                    results.append(dict(command=command,
                                        result=resp[0],
                                        encoding=encoding))
                except CommandError as exc:
                    if exc.error_code == 1003:
                        resp = self.run_commands(command, 'text')
                        results.append(dict(command=command,
                                            result=resp[0],
                                            encoding='text'))
                    else:
                        raise
        return results

    def run_commands(self, commands, encoding='json'):
        """Convenience method that sends commands to enable mode
        """
        commands = make_iterable(commands)

        if self._exec:
            commands.insert(0, {'cmd': 'enable', 'input': self._exec})
        else:
            commands.insert(0, 'enable')

        response = self._connection.execute(commands, encoding)

        # pop enable command from the response
        response['result'].pop(0)

        return response['result']

    def api(self, name, namespace='pyeapi.api'):
        """Loads the resource identified by name
        """
        module = load_module('{}.{}'.format(namespace, name))
        if hasattr(module, 'initialize'):
            module.initialize(self)
        if hasattr(module, 'instance'):
            return module.instance(self)
        return module

    def get_config(self, config='running-config', params=None):
        """Convenience method that returns the running-config as a dict
        """
        command = 'show %s' % config
        if params:
            command += ' %s' % params
        result = self.run_commands(command, 'text')
        return str(result[0]['output']).strip()


def connect_to(name):
    kwargs = config_for(name)
    connection = connect(**kwargs)
    node = Node(connection)
    if kwargs.get('enablepwd') is not None:
        node.exec_authentication(kwargs['enablepwd'])
    return node




