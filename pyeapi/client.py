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
"""Python Client for eAPI

This module provides the client for eAPI.  It provides the primary functions
for building applications that work with Arista EOS eAPI-enabled nodes.  The
first function is to provide a client for sending and receiving eAPI
request and response objects on a per node basis.  The second function
provides a library for building API enabled data models for configuring
EOS nodes.

This library allows for creating connections to EOS eAPI enabled nodes using
the connect or connect_to function.  Both functions will return an instance
of a Node object that can be used to send and receive eAPI commands.  The
Node object can autoload API modules for a structured object oriented
approach to configuring the EOS node with native Python objects.

Example:

    >>> import pyeapi
    >>> conn = pyeapi.connect(host='10.1.1.1', transport='http')
    >>> conn.execute(['show version'])
    {u'jsonrpc': u'2.0', u'result': [{u'memTotal': 2028008, u'version':
    u'4.14.5F', u'internalVersion': u'4.14.5F-2209869.4145F', u'serialNumber':
    u'', u'systemMacAddress': u'00:0c:29:f5:d2:7d', u'bootupTimestamp':
    1421765066.11, u'memFree': 213212, u'modelName': u'vEOS', u'architecture':
    u'i386', u'internalBuildId': u'f590eed4-1e66-43c6-8943-cee0390fbafe',
    u'hardwareRevision': u''}], u'id': u'4312565648'}

    >>> node = pyeapi.connect_to('veos01')
    >>> node.enable('show version')
    {u'jsonrpc': u'2.0', u'result': [{u'memTotal': 2028008, u'version':
    u'4.14.5F', u'internalVersion': u'4.14.5F-2209869.4145F', u'serialNumber':
    u'', u'systemMacAddress': u'00:0c:29:f5:d2:7d', u'bootupTimestamp':
    1421765066.11, u'memFree': 213212, u'modelName': u'vEOS', u'architecture':
    u'i386', u'internalBuildId': u'f590eed4-1e66-43c6-8943-cee0390fbafe',
    u'hardwareRevision': u''}], u'id': u'4312565648'}

Additionally the node object can automatically load API modules to work
with the resources in the configuration.  The API autoloader supports
automatic loading of modules in pyeapi.api as well as provides the ability
to build custom API modules to be loaded from a different namespace.

Example:

    >>> import pyeapi
    >>> node = pyeapi.connect_to('veos01')
    >>> node.api('vlans').get(1)
    {'state': 'active', 'name': 'default', 'vlan_id': 1, 'trunk_groups': []}

The API autoloader loads API modules by their filename.

The following objects are provide in this module for creating clients to
interface with eAPI.

Node -- Creates an instance of a node object that represents a single EOS
device.  Each EOS device to be managed should have a Node instance

Config -- A subclass of ConfigParser.SafeConfigParser that handles the
configuration file.  The configuration file is an INI style file that
contains the settings for nodes used by the connect_to function.

"""
from uuid import uuid4
import os
import re

try:
    # Try Python 3.x import first
    # Note: SafeConfigParser is deprecated and replaced by ConfigParser
    from configparser import ConfigParser as SafeConfigParser
    from configparser import Error as SafeConfigParserError
except ImportError:
    # Use Python 2.7 import as a fallback
    from ConfigParser import SafeConfigParser
    from ConfigParser import Error as SafeConfigParserError

from pyeapi.utils import load_module, make_iterable, debug

from pyeapi.eapilib import HttpEapiConnection, HttpsEapiConnection
from pyeapi.eapilib import HttpsEapiCertConnection
from pyeapi.eapilib import SocketEapiConnection, HttpLocalEapiConnection
from pyeapi.eapilib import CommandError

CONFIG_SEARCH_PATH = ['~/.eapi.conf', '/mnt/flash/eapi.conf']

TRANSPORTS = {
    'socket': SocketEapiConnection,
    'http_local': HttpLocalEapiConnection,
    'http': HttpEapiConnection,
    'https': HttpsEapiConnection,
    'https_certs': HttpsEapiCertConnection
}

DEFAULT_TRANSPORT = 'https'


class Config(SafeConfigParser):
    """Conifguration instance for managing the eapi.conf file.

    This class provides an instance for handling the configuration file.  It
    should normally need to be instantiated.  A single config object is
    instantiated by the module for working with the config.

    Attributes:
        filename (str): The full path to the loaded filename

    Args:
        filename(str): The full path to the filename to be loaded when the
            object is instantiated.

    """
    def __init__(self, filename=None):
        SafeConfigParser.__init__(self)

        self.filename = filename
        self.tags = dict()

        self.autoload()

    @property
    def connections(self):
        """
        Returns all of the loaded connections names as a list
        """
        conn = lambda x: str(x).replace('connection:', '')
        return [conn(name) for name in self.sections()]

    def autoload(self):
        """ Loads the eapi.conf file

        This method will use the module variable CONFIG_SEARCH_PATH to
        attempt to locate a valid eapi.conf file if a filename is not already
        configured.   This method will load the first eapi.conf file it
        finds and then return.

        The CONFIG_SEARCH_PATH can be overridden using an environment variable
        by setting EAPI_CONF.

        """
        path = list(CONFIG_SEARCH_PATH)
        if 'EAPI_CONF' in os.environ:
            path = os.environ['EAPI_CONF']
        elif self.filename:
            path = self.filename

        path = make_iterable(path)

        for filename in path:
            filename = os.path.expanduser(filename)
            if os.path.exists(filename):
                self.filename = filename
                return self.read(filename)

        self._add_default_connection()

    def read(self, filename):
        """Reads the file specified by filename

        This method will load the eapi.conf file specified by filename into
        the instance object.  It will also add the default connection localhost
        if it was not defined in the eapi.conf file

        Args:
            filename (str): The full path to the file to load
        """

        try:
            SafeConfigParser.read(self, filename)
        except SafeConfigParserError as exc:
            # Ignore file and syslog a message on SafeConfigParser errors
            msg = ("%s: parsing error in eapi conf file: %s" %
                   (type(exc).__name__, filename))
            debug(msg)

        self._add_default_connection()

        for name in self.sections():
            if name.startswith('connection:') and \
               'host' not in dict(self.items(name)):

                self.set(name, 'host', name.split(':')[1])
        self.generate_tags()

    def _add_default_connection(self):
        """Checks the loaded config and adds the localhost profile if needed

        This method wil load the connection:localhost profile into the client
        configuration if it is not already present.
        """
        if not self.get_connection('localhost'):
            self.add_connection('localhost', transport='socket')

    def generate_tags(self):
        """ Generates the tags with collection with hosts
        """
        self.tags = dict()
        for section in self.sections():
            if self.has_option(section, 'tags'):
                tags = self.get(section, 'tags')
                for tag in [str(t).strip() for t in tags.split(',')]:
                    if tag not in self.tags:
                        self.tags[tag] = list()
                    self.tags[tag].append(section.split(':')[1])

    def load(self, filename):
        """Loads the file specified by filename

        This method works in conjunction with the autoload method to load the
        file specified by filename.

        Args:
            filename (str): The full path to the file to be loaded
        """
        self.filename = filename
        self.reload()

    def reload(self):
        """Reloades the configuration

        This method will reload the configuration instance using the last
        known filename.  Note this method will initially clear the
        configuration and reload all entries.

        """
        for section in self.sections():
            self.remove_section(section)
        self.autoload()

    def get_connection(self, name):
        """Returns the properties for a connection name

        This method will return the settings for the configuration specified
        by name.  Note that the name argument should only be the name.

        For instance, give the following eapi.conf file

        .. code-block:: ini

            [connection:veos01]
            transport: http

        The name to use to retrieve the configuration would be veos01

            >>> pyeapi.client.config.get_connection('veos01')

        Args:
            name (str): The name of the connection to return

        Returns:
            A Python dictionary object of key/value pairs that represent
                the node configuration.  If the name provided in the argument
                is not found, then None is returned.
        """
        name = 'connection:{}'.format(name)
        if not self.has_section(name):
            return None
        return dict(self.items(name))

    def add_connection(self, name, **kwargs):
        """Adds a connection to the configuration

        This method will add a connection to the configuration.  The connection
        added is only available for the lifetime of the object and is not
        persisted.

        Note:
            If a call is made to load() or reload(), any connections added
            with this method must be re-added to the config instance

        Args:
            name (str): The name of the connection to add to the config.  The
                name provided will automatically be prepended with the string
                connection:
            **kwargs (dict); The set of properties used to provide the node
                configuration

        """
        name = 'connection:{}'.format(name)
        self.add_section(name)
        for key, value in list(kwargs.items()):
            self.set(name, key, value)
        self.generate_tags()

# TODO: This is a global variable (in the module) - to review the impact on
# having a shared state for the config file.


config = Config()


def load_config(filename):
    """Function method that loads a conf file

    This function will load the file specified by filename into the config
    instance.   Its a convenience function that calls load on the config
    instance

    Args:
        filename (str): The full path to the filename to load
    """
    return config.load(filename)


def config_for(name):
    """ Function to get settings for named config

    This function will return the settings for a specific connection as
    specified by name.  Its a convenience function that calls get_connection
    on the global config instance

    Args:
        name (str): The name of the connection to return.  The connection
            name is specified as the string right of the : in the INI file

    Returns:
        A Python dictionary object of key/value pairs that represent the
            nodes configuration settings from the config instance
    """
    return config.get_connection(name)


def hosts_for_tag(tag):
    """ Returns the hosts assocated with the specified tag

    This function will return the hosts assoicated with the tag specified
    in the argument.  It will return an array of connecition names.

    Args:
        tag (str): The name of the tag to retrieve the list of hosts for

    Returns:
        list: A Python list object that includes the list of hosts assoicated
            with the specified tag.

        None: If the specified tag does not exist, then None is returned.
    """
    return config.tags.get(tag)


def make_connection(transport, **kwargs):
    """ Creates a connection instance based on the transport

    This function creates the EapiConnection object based on the desired
    transport.  It looks up the transport class in the TRANSPORTS global
    dictionary.

    Args:
        transport (string): The transport to use to create the instance.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        An instance of a connection object based on the transport

    Raises:
        TypeError: A TypeError is raised if the transport keyword is not
            found in the list (keys) of available transports.
    """
    if transport not in TRANSPORTS:
        raise TypeError('invalid transport specified')
    klass = TRANSPORTS[transport]
    return klass(**kwargs)


def connect(transport=None, host='localhost', username='admin',
            password='', port=None, key_file=None, cert_file=None,
            ca_file=None, timeout=60, return_node=False, context=None,
            **kwargs):
    """ Creates a connection using the supplied settings

    This function will create a connection to an Arista EOS node using
    the arguments.  All arguments are optional with default values.

    Args:
        transport (str): Specifies the type of connection transport to use.
            Valid values for the connection are socket, http_local, http, and
            https.  The default value is specified in DEFAULT_TRANSPORT
        host (str): The IP addres or DNS host name of the connection device.
            The default value is 'localhost'
        username (str): The username to pass to the device to authenticate
            the eAPI connection.   The default value is 'admin'
        password (str): The password to pass to the device to authenticate
            the eAPI connection.  The default value is ''
        port (int): The TCP port of the endpoint for the eAPI connection.  If
            this keyword is not specified, the default value is automatically
            determined by the transport type. (http=80, https=443)
        key_file (str): Path to private key file for ssl validation
        cert_file (str): Path to PEM formatted cert file for ssl validation
        ca_file (str): Path to CA PEM formatted cert file for ssl validation
        timeout (int): timeout
        context (ssl.SSLContext): ssl object's context. The default is None
        return_node (bool): Returns a Node object if True, otherwise
            returns an EapiConnection object.


    Returns:
        An instance of an EapiConnection object for the specified transport.

    Note:
        Python 3.10 increases security strength of the TLS stack by among other
        things using a stronger (than 3.9) default cipher suite. Thus programs
        relying on the https transport and using the default cypher suite that
        used to work in prior python versions may fail with the error:
        ``[SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failure``.
        The solution to that issue is to configure the https web server to use
        a stronger cipher suite.

        If the solution is not attainable, then a work-around might be
        considered (weighing all due implications) - one could pass an ssl
        context where cipher can be specified::

          import pyeapi
          import ssl
          ...
          ctx = ssl.create_default_context()
          ctx.set_ciphers('DEFAULT')          # set a preferred cipher
          ctx.check_hostname = False          # for the sake of example
          ctx.verify_mode = ssl.CERT_NONE     # do it w/o certificate
          ...
          cc = pyeapi.client.connect( host=host_name, context=ctx )
    """
    transport = transport or DEFAULT_TRANSPORT
    connection = make_connection(transport, host=host, username=username,
                                 password=password, key_file=key_file,
                                 cert_file=cert_file, ca_file=ca_file,
                                 port=port, timeout=timeout, context=context)
    if return_node:
        return Node(connection, transport=transport, host=host,
                    username=username, password=password, key_file=key_file,
                    cert_file=cert_file, ca_file=ca_file, port=port, **kwargs)
    return connection


class Node(object):
    """Represents a single device for sending and receiving eAPI messages

    The Node object provides an instance for communicating with Arista EOS
    devices.  The Node object provides easy to use methods for sending both
    enable and config commands to the device using a specific transport.  This
    object forms the base for communicating with devices.

    Attributes:
        connection (EapiConnection): The connection property represents the
            underlying transport used by the Node object to communicate
            with the device using eAPI.
        running_config (str): The running-config from the device.  This
            property is lazily loaded and refreshed over the life cycle of
            the instance.
        startup_config (str): The startup-config from the device.  This
            property is lazily loaded and refreshed over the life cycle of
            the instance.
        autorefresh (bool): If True, the running-config and startup-config are
            refreshed on config events.  If False, then the config properties
            must be manually refreshed.
        settings (dict): Provides access to the settings used to create the
            Node instance.

    Args:
        connection (EapiConnection): An instance of EapiConnection used as the
            transport for sending and receiving eAPI requests and responses.
        **kwargs: An arbitrary list of keyword arguments
    """
    def __init__(self, connection, **kwargs):
        self._connection = connection
        self._running_config = None
        self._startup_config = None
        self._version = None
        self._version_number = None
        self._model = None
        self._session_name = None

        self._enablepwd = kwargs.get('enablepwd')
        self.autorefresh = kwargs.get('autorefresh', True)
        self.settings = kwargs

    def __str__(self):
        return 'Node(connection=%s)' % str(self._connection)

    def __repr__(self):
        return 'Node(connection=%s)' % repr(self._connection)

    @property
    def connection(self):
        return self._connection

    @property
    def running_config(self):
        if self._running_config is not None:
            return self._running_config
        self._running_config = self.get_config(params='all',
                                               as_string=True)
        return self._running_config

    @property
    def startup_config(self):
        if self._startup_config is not None:
            return self._startup_config
        self._startup_config = self.get_config('startup-config',
                                               as_string=True)
        return self._startup_config

    @property
    def version(self):
        if self._version:
            return self._version
        self._get_version_properties()
        return self._version

    @property
    def version_number(self):
        if self._version_number:
            return self._version_number
        self._get_version_properties()
        return self._version_number

    @property
    def model(self):
        if self._model:
            return self._model
        self._get_version_properties()
        return self._model

    def _get_version_properties(self):
        """Parses version and model information out of 'show version' output
        and uses the output to populate class properties.
        """
        # Parse out version info
        output = self.enable('show version')
        self._version = str(output[0]['result']['version'])
        match = re.match(r'[\d.\d]+', str(output[0]['result']['version']))
        if match:
            self._version_number = str(match.group(0))
        else:
            self._version_number = str(output[0]['result']['version'])
        # Parse out model number
        match = re.search(r'\d\d\d\d', str(output[0]['result']['modelName']))
        if match:
            self._model = str(match.group(0))
        else:
            self._model = str(output[0]['result']['modelName'])

    def enable_authentication(self, password):
        """Configures the enable mode authentication password

        EOS supports an additional password authentication mechanism for
        sessions that want to switch to executive (or enable) mode.  This
        method will configure the password, if required, for entering
        executive mode

        Args:
            password (str): The password string in clear text used to
                authenticate to exec mode
        """
        self._enablepwd = str(password).strip()

    def config(self, commands, **kwargs):
        """Configures the node with the specified commands

        This method is used to send configuration commands to the node.  It
        will take either a string or a list and prepend the necessary commands
        to put the session into config mode.

        Args:
            commands (str, list): The commands to send to the node in config
                mode.  If the commands argument is a string it will be cast to
                a list.
                The list of commands will also be prepended with the
                necessary commands to put the session in config mode.
            **kwargs: Additional keyword arguments for expanded eAPI
                functionality. Only supported eAPI params are used in building
                the request

        Returns:
            The config method will return a list of dictionaries with the
                output from each command.  The function will strip the
                response from any commands it prepends.
        """
        if self._session_name:  # If in a config session
            return self._configure_session(commands, **kwargs)

        return self._configure_terminal(commands, **kwargs)

    def _configure_terminal(self, commands, **kwargs):
        """Configures the node with the specified commands with leading
        "configure terminal"
        """
        commands = make_iterable(commands)
        commands = list(commands)

        # push the configure command onto the command stack
        commands.insert(0, 'configure terminal')
        response = self.run_commands(commands, **kwargs)

        if self.autorefresh:
            self.refresh()

        # pop the configure command output off the stack
        response.pop(0)

        return response

    def _configure_session(self, commands, **kwargs):
        """Configures the node with the specified commands with leading
        "configure session <session name>"
        """
        if not self._session_name:
            raise CommandError('Not currently in a session')

        commands = make_iterable(commands)
        commands = list(commands)

        # push the configure command onto the command stack
        commands.insert(0, 'configure session %s' % self._session_name)
        response = self.run_commands(commands, **kwargs)

        # pop the configure command output off the stack
        response.pop(0)

        return response

    def section(self, regex, config='running_config'):
        """Returns a section of the config

        Args:
            regex (str): A valid regular expression used to select sections
                of configuration to return
            config (str): The configuration to return.  Valid values for config
                are "running_config" or "startup_config".  The default value
                is "running_config"

        Returns:
            The configuration section as a string object.
        """
        if config in ['running_config', 'startup_config']:
            config = getattr(self, config)
        match = re.search(regex, config, re.M)
        if not match:
            raise TypeError('config section not found')
        block_start, line_end = match.regs[0]

        match = re.search(r'^[^\s]', config[line_end:], re.M)
        if not match:
            raise TypeError('could not find end block')
        _, block_end = match.regs[0]

        block_end = line_end + block_end
        return config[block_start:block_end]

    def enable(self, commands, encoding='json', strict=False,
               send_enable=True, **kwargs):
        """Sends the array of commands to the node in enable mode

        This method will send the commands to the node and evaluate
        the results.  If a command fails due to an encoding error,
        then the command set will be re-issued individual with text
        encoding.

        Args:
            commands (list): The list of commands to send to the node

            encoding (str): The requested encoding of the command output.
                Valid values for encoding are JSON or text

            strict (bool): If False, this method will attempt to run a
                command with text encoding if JSON encoding fails
            send_enable (bool): If True the enable command will be
                               prepended to the command list automatically.
            **kwargs: Additional keyword arguments for expanded eAPI
                functionality. Only supported eAPI params are used in building
                the request

        Returns:
            A dict object that includes the response for each command along
                with the encoding

        Raises:
            TypeError:
                This method does not support sending configure
                commands and will raise a TypeError if configuration commands
                are found in the list of commands provided

                This method will also raise a TypeError if the specified
                encoding is not one of 'json' or 'text'

            CommandError: This method will raise a CommandError if any one
                of the commands fails.
        """
        commands = make_iterable(commands)

        if 'configure' in commands:
            raise TypeError('config mode commands not supported')

        results = list()
        # IMPORTANT: There are two keys (response, result) that both
        # return the same value. 'response' was originally placed
        # there in error and both are now present to avoid breaking
        # existing scripts. 'response' will be removed in a future release.
        if strict:
            responses = self.run_commands(commands, encoding, send_enable,
                                          **kwargs)
            for index, response in enumerate(responses):
                results.append(dict(command=commands[index],
                                    result=response,
                                    response=response,
                                    encoding=encoding))
        else:
            for command in commands:
                try:
                    resp = self.run_commands(command, encoding, send_enable,
                                             **kwargs)
                    results.append(dict(command=command,
                                        result=resp[0],
                                        encoding=encoding))
                except CommandError as exc:
                    if exc.error_code == 1003:
                        resp = self.run_commands(command, 'text', send_enable,
                                                 **kwargs)
                        results.append(dict(command=command,
                                            result=resp[0],
                                            encoding='text'))
                    else:
                        raise
        return results

    def run_commands(self, commands, encoding='json', send_enable=True,
                     **kwargs):
        """Sends the commands over the transport to the device

        This method sends the commands to the device using the nodes
        transport.  This is a lower layer function that shouldn't normally
        need to be used, preferring instead to use config() or enable().

        Args:
            commands (list): The ordered list of commands to send to the
                device using the transport
            encoding (str): The encoding method to use for the request and
                excpected response.
            send_enable (bool): If True the enable command will be
                               prepended to the command list automatically.
            **kwargs: Additional keyword arguments for expanded eAPI
                functionality. Only supported eAPI params are used in building
                the request

        Returns:
            This method will return the raw response from the connection
                which is a Python dictionary object.
        """
        commands = make_iterable(commands)

        # Some commands are multiline commands. These are banner commands and
        # SSL commands. So with this two lines we
        # can support those by passing commands by doing:
        # banner login MULTILINE: This is my banner.\nAnd I even support
        # multiple lines.
        # Why this? To be able to read a configuration from a file, split it
        # into lines and pass it as it is
        # to pyeapi without caring about multiline commands.
        commands = [{'cmd': c.split('MULTILINE:')[0],
                     'input': '%s\n' % (c.split('MULTILINE:')[1].strip())}
                    if 'MULTILINE:' in c else c for c in commands]

        if send_enable:
            if self._enablepwd:
                commands.insert(0, {'cmd': 'enable', 'input': self._enablepwd})
            else:
                commands.insert(0, 'enable')

        response = self._connection.execute(commands, encoding, **kwargs)

        # pop enable command from the response only if we sent enable
        if send_enable:
            response['result'].pop(0)

        return response['result']

    def api(self, name, namespace='pyeapi.api'):
        """Loads the specified api module

        This method is the API autoload mechanism that will load the API
        module specified by the name argument.  The API module will be loaded
        and look first for an initialize() function and secondly for an
        instance() function.  In both cases, the node object is passed to
        the module.

        Args:
            name (str): The name of the module to load.  The name should be
                the name of the python file to import
            namespace (str): The namespace to use to load the module.  The
                default value is 'pyeapi.api'

        Returns:
            The API module loaded with the node instance.
        """
        module = load_module('{}.{}'.format(namespace, name))
        if hasattr(module, 'initialize'):
            module.initialize(self)
        if hasattr(module, 'instance'):
            return module.instance(self)
        return module

    def get_config(self, config='running-config', params=None,
                   as_string=False):
        """ Retreives the config from the node

        This method will retrieve the config from the node as either a string
        or a list object.  The config to retrieve can be specified as either
        the startup-config or the running-config.

        Args:
            config (str): Specifies to return either the nodes startup-config
                or running-config.  The default value is the running-config
            params (str): A string of keywords to append to the command for
                retrieving the config.
            as_string (boo): Flag that determines the response.  If True, then
                the configuration is returned as a raw string.  If False, then
                the configuration is returned as a list.  The default value is
                False

        Returns:
            This method will return either a string or a list depending on the
            states of the as_string keyword argument.

        Raises:
            TypeError: If the specified config is not one of either
                'running-config' or 'startup-config'
        """
        if config not in ['startup-config', 'running-config']:
            raise TypeError('invalid config name specified')

        command = 'show %s' % config
        if params:
            command += ' %s' % params

        result = self.run_commands(command, 'text')
        if as_string:
            return str(result[0]['output']).strip()

        return str(result[0]['output']).split('\n')

    def refresh(self):
        """Refreshes the instance config properties

        This method will refresh the public running_config and startup_config
        properites.  Since the properties are lazily loaded, this method will
        clear the current internal instance variables.  One the next call the
        instance variables will be repopulated with the current config

        """
        self._running_config = None
        self._startup_config = None

    def configure_session(self):
        """Enter a config session
        """
        self._session_name = self._session_name or uuid4()

    def diff(self):
        """Returns session-config diffs in text encoding

        Note: "show session-config diffs" doesn't support json encoding
        """
        response = self._configure_session(
            ['show session-config diffs'], encoding='text' )

        return response[0]['output']

    def commit(self):
        """Commits the current config session
        """
        return self._configure_and_exit_session(['commit'])

    def abort(self):
        """Aborts the current config session
        """
        return self._configure_session(['abort'])

    def _configure_and_exit_session(self, commands, **kwargs):
        response = self._configure_session(commands, **kwargs)

        if self.autorefresh:
            self.refresh()

        # Exit the current config session
        self._session_name = None

        return response


def connect_to(name):
    """Creates a node instance based on an entry from the config

    This function will retrieve the settings for the specified connection
    from the config and return a Node instance.  The configuration must
    be loaded prior to calling this function.

    Args:
        name (str): The name of the connection to load from the config.  The
            name argument should be the connection name (everything right of
            the colon from the INI file)

    Returns:
        This function will return an instance of Node with the settings
            from the config instance.

    Raises:
        AttributeError: raised if the specified configuration name is not
            found in the loaded configuration

    """
    kwargs = config_for(name)

    if not kwargs:
        raise AttributeError('connection profile not found in config')

    node = connect(return_node=True, **kwargs)
    return node
