.. _configfile:

#########################
Pyeapi Configuration File
#########################

The pyeapi configuration file is a convenient place to store node connection
information. By keeping connection information central, your pyeapi scripts
can effortlessly reference nodes without any manual import of credentials
or location information. Therefore, the pyeapi configuration file becomes
a reflection of your switch inventory and the way in which the EOS Command
API is enabled on the node. The following explains how to craft your
pyeapi configuration file to address specific implementation styles.

.. contents::
  :depth: 2

********************
eapi.conf Parameters
********************

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
      - https_certs

:port: Configures the port to use for the eAPI connection.  A default
    port is used if this parameter is absent, based on the transport setting
    using the following values:

      - transport: http, default port: 80
      - transport: https, default port: 443
      - transport: https_certs, default port: 443
      - transport: http_local, default port: 8080
      - transport: socket, default port: n/a

*********************************
When is an eapi.conf file needed?
*********************************

It's important to understand the nuances of the pyeapi configuration file so
you can simplify your implementation. Here's a quick summary of when the
eapi.conf file is needed:

=========== ================== =============== ========================
Transport   eapi.conf Required Script run from Authentication Required
=========== ================== =============== ========================
http        Yes                On/Off-switch   Yes
https       Yes                On/Off-switch   Yes
https_certs Yes                On/Off-switch   Yes (Auth done via certs, not un/pw)
http_local  Yes                On-switch only  No
socket      No                 On-switch only  No
=========== ================== =============== ========================


********************************
Where should the file be placed?
********************************

============ =================================================
Search Order Search Location
============ =================================================
1            Environment Variable EAPI_CONF=/path/to/eapi.conf
2            $HOME/.eapi.conf
3            /mnt/flash/eapi.conf
============ =================================================

.. Note:: There is a slight difference in #2 ``.eapi.conf`` versus
          #3 ``eapi.conf``

************************************
eapi.conf for On-box Implementations
************************************

This method would be used to run a pyeapi script on-box. In this mode, eAPI
can be configured to require or not require authentication depending upon
how you enabled EOS Command API.

Notice from the table above, that if EOS Command API Unix Sockets are enabled,
or HTTP Local, you get the benefit of not needing to pass in credentials
since the connection can only be made from localhost and it assumes the user
has already authenticated to get on the switch.

Using Unix Sockets
==================

This is the preferred method. The default transport for pyeapi is ``socket``
and the default host is ``localhost``. Therefore, if running a pyeapi script
on-box and have Unix Sockets enabled, you do not need an eapi.conf, nor do you
need to pass any credentials (quite handy!).

.. Note:: Unix Sockets are supported on EOS 4.14.5+

Using HTTP Local
================

As the table above indicates, a pyeapi configuration file is required in
``/mnt/flash/eapi.conf``. It would contain something like:

.. code-block:: console

  [connection:localhost]
  transport: http_local

Pay attention: once ``eapi.conf`` exists, the respective protocol method must be
configured on the box. E.g., for the above ``eapi.conf`` sample, the following
configuration must also exist:

.. code-block:: console

  switch(config)#management http-server
  switch(config-mgmt-http-server)#protocol http localhost


Using HTTP or HTTPS
===================

As the table above indicates, a pyeapi configuration file is required in
``/mnt/flash/eapi.conf``. It would contain something like:

.. code-block:: console

  [connection:localhost]
  transport: http[s]
  username: admin
  password: admin

*************************************
eapi.conf for Off-box Implementations
*************************************

This method would be used to run a pyeapi script from another server. In this
mode, eAPI will require authentication. The only real option is whether you
connect over HTTP or HTTPS.

.. Note:: The ``socket`` and ``http_local`` transport options are not
          applicable.

Notice from the table above, that if EOS Command API Unix Sockets are enabled,
or HTTP Local, you get the benefit of not needing to pass in credentials
since the connection can only be made from localhost and it assumes the user
has already authenticated to get on the switch.

Using HTTP or HTTPS
===================

As the table above indicates, a pyeapi configuration file is required in
``$HOME/.eapi.conf``. It would contain something like:

.. code-block:: console

  [connection:veos01]
  transport: http
  username: paul
  password: nottelling

  [connection:veos03]
  transport: https
  username: bob
  password: mysecret

  [connection:veos04]
  host: 192.168.2.10
  transport: https
  username: admin
  password: admin

.. Note:: avoid using ``localhost`` name in the connection description (i.e.: ``[connection:localhost]``). 
          The name ``localhost`` is reserved solely for ``on-box`` connection method and it won't work when
          connecting ``off-box``


Using HTTPS with Certificates
=============================

The https_certs transport options allows users to do authentication for pyeapi
with certificates instead of username/password. This requires functional
certificate chains are setup, copied to the proper location and trusted by
EOS beforehand. The ca_file parameter is optional. If provided the switches
certificate will also be validated against the provided CA cert. If no CA cert
is provided then no server side validation will be done.

.. code-block:: console

  [connection:veos01]
  transport: https_certs
  cert_file: /path/to/certificate/file
  key_file: /path/to/private/key/file
  ca_file: /path/to/CA/certificate/file

  [connection:veos02]
  transport: https_certs
  cert_file: /path/to/certificate/file
  key_file: /path/to/private/key/file

*******************
The DEFAULT Section
*******************

The [DEFAULT] section can be used to gather globally applicable settings.
Say that all of your nodes use the same transport or username, you can do
something like:

.. code-block:: console

  [connection:veos01]

  [connection:veos03]
  transport: https
  username: bob
  password: mysecret

  [connection:veos04]
  host: 192.168.2.10

  [DEFAULT]
  transport: https
  username: admin
  password: admin
