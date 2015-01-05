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
"""Provides wrapper for eAPI calls

This module provides a connection to eAPI by wrapping eAPI calls in an
instance of Connection.  The connection module provides an easy implementation
for sending and receiving calls over eAPI using a HTTP/S transport.
"""

import json
import urllib2

from pyeapi.utils import debug

class CommandError(Exception):
    """Base exception raised for command errors

    The CommandError instance provides a custom exception that can be used
    if the eAPI command(s) fail.  It provides some additional information
    that can be used to understand what caused the exception.

    Args:
        error_code (int): The error code returned from the eAPI call.
        error_text (string): The error text message that coincides with the
            error_code
        commands (array): The list of commands that were sent to the node
            that generated the error
        message (string): The exception error message which is a concatentation
            of the error_code and error_text
    """
    def __init__(self, code, message, commands=None):
        self.error_code = code
        self.error_text = message
        self.commands = commands
        self.message = 'Error [{}]: {}'.format(code, message)
        super(CommandError, self).__init__(message)


class Connection(object):
    """Creates a connection to an EOS node using eAPI

    The Connection object wraps around JSON-RPC calls to an EOS node for
    sending and receive data using eAPI.  In order for the connection
    object to be successful, the command API (eAPI) must be enabled on the
    destination node using the following configuration commands:

        eos# config
        eos(config)# management api http-commands
        eos(config-mgmt-api-http-cmds)# no shutdown

        The above configuration will enable eAPI listening on the default
        HTTPS port 443.   For additional configuration options please
        consult the Arista EOS Command API Guide downloadable from
        http://www.arista.com.

    Args:
        host (string): The hostname to set host to, defaults to 'localhost'
        username (string): The username to set username to, defaults to a
            value of 'admin'
        password (string): The password to set the connection instance to,
            defaults to the value of ''
        uri (string): The full URI of the connection object, defaults to
            ''.  This parameter will override all others when creating a
            new instance of Connection
        **kwargs: Arbitrary set of keyword arguments

    Attributes:
        host (string): The IP address or hostname of the node
        username (string): The username used to authenticate to eAPI
        password (string): The password used to authenticate to eAPI
        enablepwd (string): The enable password to use, if required
        protocol (string): The protocol as either 'http' or 'https'.  This
            attribute is automatically set and should generally not need to
            be overridden
        port (int): The port of the eAPI endpoint.  If the port is not
            specified, then it is automatically determined based on the
            protocol setting (443 for https, 80 for http)

    """

    def __init__(self, host='localhost', username='admin', password='',
                 uri=None, **kwargs):

        self.host = host
        self.username = username
        self.password = password
        self.enablepwd = kwargs.get('enablepwd') or ''
        self.protocol = 'https' if kwargs.get('use_ssl') else 'http'
        self.port = kwargs.get('port') or \
            (443 if self.protocol == 'https' else 80)

        self._http = None
        self.error = None
        self.debug = kwargs.get('debug') or False

        # runtime properties
        self._uri = uri

    def __str__(self):
        return 'Connection(uri=%s)' % self.uri

    def __repr__(self):
        return 'Connection(uri=%s)' % self.uri

    @property
    def uri(self):
        if self._uri is not None:
            return self._uri
        self._uri = "{}://{}:{}/command-api".format(self.protocol, self.host,
                                                    self.port)
        return self._uri

    def http(self, *args, **kwargs):
        """Opens a HTTP request

        This method will take the current URI and open an HTTP request to
        the destination endpoint.   The HTTP connection is returned to the
        caller for sending requests

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            An open HTTP connection for sending requests
        """
        if self._http is not None:
            for handler in self._http.handlers:
                handler.retried = 0
            return self._http.open(*args, **kwargs)
        self._http = self._get_auth_opener()
        return self._http.open(*args, **kwargs)

    def _get_auth_opener(self):
        """Creates a URL opener using basic authentication

        The HTTP opener adds a basic authentication header to the HTTP
        call which is required by eAPI.  The authentication header passes
        the username and password values of the instance

        Returns:
            An URL opener object
        """
        passmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passmgr.add_password(None, self.uri, self.username, self.password)
        handler = urllib2.HTTPBasicAuthHandler(passmgr)
        opener = urllib2.build_opener(handler)
        return opener

    def _request(self, commands, encoding=None, reqid=None):
        """Generates an eAPI request object

        This method will take a list of EOS commands and generate a valid
        eAPI request object form them.  The eAPI request object is then
        JSON encoding and returned to the caller.

        eAPI Request Object
            {
                "jsonrpc": "2.0",
                "method": "runCmds",
                "params": {
                    "version": 1,
                    "cmds": [
                        <commands>
                    ],
                    "format": [json, text],
                }
                "id": <reqid>
            }

        Args:
            commands (list): A list of commands to include in the eAPI
                request object
            encoding (string): The encoding method passed as the `format`
                parameter in the eAPI request
            reqid (string): A custom value to assign to the request ID
                field.  This value is automatically generated if not passed

        Returns:
            A JSON encoding request struture that can be send over eAPI

        """

        reqid = id(self) if reqid is None else reqid

        params = {"version": 1, "cmds": commands, "format": encoding}

        return json.dumps({"jsonrpc": "2.0", "method": "runCmds",
                           "params": params, "id": str(reqid)})

    def _send(self, data):
        """Sends the eAPI request to the destination node

        This method is responsible for sending an eAPI request to the
        destination node and returning a response based on the eAPI response
        object.  eAPI responds to request messages with either a success
        message or failure message.

        eAPI Response - success
            {
                "jsonrpc": "2.0",
                "result": [
                    {},
                    {}
                    {
                        "warnings": [
                            <message>
                        ]
                    },
                ],
                "id": <reqid>
            }

        eAPI Response - failure
            {
                "jsonrpc": "2.0",
                "error": {
                    "code": <int>,
                    "message": <string>
                    "data": [
                        {},
                        {},
                        {
                            "errors": [
                                <message>
                            ]
                        }
                    ]
                }
                "id": <reqid>
            }

        Args:
            data (string): The data to be included in the body of the eAPI
                request object

        Returns:
            A decoded response.  The response object is deserialized from
                JSON and returned as a standard Python dictionary object

        Raises:
            CommandError if an eAPI failure response object is returned from
                the node.   The CommandError exception includes the error
                code and error message from the eAPI response.
        """
        header = {'Content-Type': 'application/json'}

        debug('EAPI REQ: %s' % data)
        request = urllib2.Request(self.uri, data, header)
        response = self.http(request)
        decoded = json.loads(response.read())
        debug('EAPI RESP: %s' % decoded)

        if 'error' in decoded:
            _message = decoded['error']['message']
            _code = decoded['error']['code']
            raise CommandError(_code, _message)

        return decoded

    def execute(self, commands, encoding='json', **kwargs):
        """Executes the list of commands on the destination node

        This method takes a list of commands and sends them to the
        destination node, returning the results.  The execute method handles
        putting the destination node in enable mode and will pass the
        enable password, if required.

        Args:
            commands (list): A list of commands to execute on the remote node
            encoding (string): The encoding to send along with the request
                message to the destination node.  Valid values include 'json'
                or 'text'.  This argument will influence the response object
                encoding
            **kwargs: Arbitrary keyword arguments

        Returns:
            A decoded response message as a native Python dictionary object
            that has been deserialized from JSON.

        Raises:
            CommandError:  A CommandError is raised that includes the error
                code, error message along wit the list of commands that were
                sent to the node.  The exception instance is also stored in
                the error property and is availble until the next request is
                sent
        """
        if encoding not in ['json', 'text']:
            raise TypeError('encoding must be one of [json, text]')

        try:
            self.error = None

            # push enable into the command stack
            commands.insert(0, {'cmd': 'enable', 'input': self.enablepwd})

            request = self._request(commands, encoding=encoding, **kwargs)
            response = self._send(request)

            # pop enable command from the response
            response['result'].pop(0)
            return response

        except CommandError as exc:
            exc.commands = commands
            self.error = exc
            raise


