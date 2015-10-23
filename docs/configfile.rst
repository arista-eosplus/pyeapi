#########################
Pyeapi Configuration File
#########################

In order to use pyeapi, the EOS command API must be enabled using configuration
mode.  This library supports eAPI calls over both HTTP/S and UNIX Domain
Sockets. Once the command API is enabled on the destination node, create a
configuration file with the node properties.

**************
Install Pyeapi
**************

Follow the instructions on the :ref:`install` guide to prepare your node for
pyeapi.

************************
Create an eapi.conf file
************************

This method would be used to run a pyeapi script on-box. In this mode, eAPI
can be configured to require or not require authentication. A quick summary:

=========== ========================
Type        Authentication Required
=========== ========================
https       Yes
http        Yes
http_local  No
socket      No
=========== ========================

The default transport for pyeapi is ``socket`` and the default host is
``localhost``. Therefore, if running a pyeapi script on-box and have
Unix Sockets enabled, you do not need an eapi.conf, nor do you need to pass
any credentials (quite handy!).

If instead, ``https``, ``http`` or ``http_local`` is configured on your
node, then you will need an eapi.conf file in ``/mnt/flash/eapi.conf``. It
would contain something like:

.. code-block:: console

  [connection:localhost]
  transport: http_local

.. code-block:: console

  [connection:localhost]
  transport: https
  username: admin
  password: admin

.. code-block:: console

  [connection:localhost]
  transport: http
  username: admin
  password: admin

.. Note:: The default search path for the conf file is ``~/.eapi.conf``
          followed by ``/mnt/flash/eapi.conf``.  This can be overridden by setting
          ``EAPI_CONF=<path file conf file>`` in your environment.

The following configuration options are available for defining node entries:

:host: The IP address or FQDN of the remote device.  If the host
  parameter is omitted then the connection name is used

:username: The eAPI username to use for authentication (only required for
  http or https connections)

:password: The eAPI password to use for authentication (only required for
  http or https connections)

:enablepwd: The enable mode password if required by the destination node

:transport: Configures the type of transport connection to use. Valid
  values are:
    - socket (default, available in EOS 4.14.5 or later)
    - http_local (available in EOS 4.14.5 or later)
    - http
    - https

:port: Configures the port to use for the eAPI connection.  A default
  port is used if this parameter is absent, based on the transport setting
  using the following values:
    - transport: http, default port: 80
    - transport: https, deafult port: 443
    - transport: http_local, default port: 8080
    - transport: socket, default port: n/a
