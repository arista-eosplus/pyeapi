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
import json
import urllib2

from pyeapi.utils import load_module, parseconfig, debug

class CommandError(Exception):
    """ Base exception raised for command errors
    """
    pass

class Connection(object):
    """ Creates a connection for sending and receiving data using Arista
        eAPI.  In order for the API to be able to send and receive data
        the command API must be enabled in the switches running configuration.
        To enable command API execute the following configuration commands
        on the destination device:

            eos# config
            eos(config)# management api http-commands
            eos(config-mgmt-api-http-cmds)# no shutdown

        The above configuration will enable eAPI listening on the default
        HTTPS port 443.   For additional configuration options please
        consult the Arista EOS Command API Guide downloadable from
        http://www.arista.com.
    """

    def __init__(self, host, username, password, **kwargs):

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
        self._uri = None

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
        if self._http is not None:
            for handler in self._http.handlers:
                handler.retried = 0
            return self._http.open(*args, **kwargs)
        self._http = self._get_auth_opener()
        return self._http.open(*args, **kwargs)

    def _get_auth_opener(self):
        """create a URL opener with an authentication handler"""
        passmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passmgr.add_password(None, self.uri, self.username, self.password)
        handler = urllib2.HTTPBasicAuthHandler(passmgr)
        opener = urllib2.build_opener(handler)
        return opener

    def _request(self, commands, encoding=None, reqid=None):
        """generate the request data"""

        reqid = id(self) if reqid is None else reqid

        params = {"version": 1, "cmds": commands, "format": encoding}

        return json.dumps({"jsonrpc": "2.0", "method": "runCmds",
                           "params": params, "id": str(reqid)})

    def _send(self, data):
        """send the request data to the host and return the response"""

        header = {'Content-Type': 'application/json'}

        debug('EAPI REQ: %s' % data)
        request = urllib2.Request(self.uri, data, header)
        response = self.http(request)
        decoded = json.loads(response.read())
        debug('EAPI RESP: %s' % decoded)

        if "error" in decoded:
            _message = decoded["error"]["message"]
            _code = decoded["error"]["code"]
            raise CommandError("Error [{}]: {}".format(_code, _message))

        return decoded

    def execute(self, commands, encoding='json', **kwargs):
        """Executes the commands and returns the response
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
            self.error = exc
            raise


