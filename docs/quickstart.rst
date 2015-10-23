##########
Quickstart
##########

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

The eAPI configuration file provides a way to keep an inventory of your
switches in one central place. You can quickly connect to a switch in your
inventory as shown below. The contents of eapi.conf will change depending upon
where you run pyeapi. Some examples are provided below.


Running pyeapi from a central server
====================================

This method would be used to connect to various Arista nodes from a central
server. The eapi.conf file would then contain all of the switches and would
likely include an HTTP or HTTPS transport method.

Here's an example

The conf file can contain more than one node. Each node section must be
prefaced by ``connection:<name>`` where <name> is the name of the connection.
When no ``host`` key is present, the connection name will be used (ie DNS).

.. code-block:: console

  [connection:veos01]
  username: eapi
  password: password
  transport: http

  [connection:veos02]
  host: 172.16.10.1
  username: eapi
  password: password
  enablepwd: itsasecret
  port: 1234
  transport: https

Running pyeapi locally on a switch
==================================

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


*****************
Connect to a Node
*****************

The Python client for eAPI was designed to be easy to use and implement for
writing tools and applications that interface with the Arista EOS management
plane.

Once EOS is configured properly and the config file created, getting started
with a connection to EOS is simple.  Below demonstrates a basic connection
using pyeapi. For more examples, please see the examples folder.

This first example shows how to instantiate the Node object. The Node object
provides some helpful methods and attributes to work with the switch.

.. code-block:: python

  # start by importing the library
  import pyeapi

  # create a node object by specifying the node to work with
  node = pyeapi.connect_to('veos01')

  # send one or more commands to the node
  node.enable('show hostname')
  [{'command': 'show hostname', 'result': {u'hostname': u'veos01', u'fqdn':
  u'veos01.arista.com'}, 'encoding': 'json'}]

  # use the config method to send configuration commands
  node.config('hostname veos01')
  [{}]

  # multiple commands can be sent by using a list (works for both enable or
  config)
  node.config(['interface Ethernet1', 'description foo'])
  [{}, {}]

  # return the running or startup configuration from the node (output omitted for
  brevity)
  node.running_config

  node.startup_config

The pyeapi library provides both a client for send and receiving commands over
eAPI as well as an API for working directly with EOS resources.   The API is
designed to be easy and straightforward to use yet also extensible.  Below is
an example of working with the ``vlans`` API

.. code-block:: python

  # create a connection to the node
  import pyeapi
  node = pyeapi.connect_to('veos01')

  # get the instance of the API (in this case vlans)
  vlans = node.api('vlans')

  # return all vlans from the node
  vlans.getall()
  {'1': {'state': 'active', 'name': 'default', 'vlan_id': 1, 'trunk_groups': []},
  '10': {'state': 'active', 'name': 'VLAN0010', 'vlan_id': 10, 'trunk_groups':
  []}}

  # return a specific vlan from the node
  vlans.get(1)
  {'state': 'active', 'name': 'default', 'vlan_id': 1, 'trunk_groups': []}

  # add a new vlan to the node
  vlans.create(100)
  True

  # set the new vlan name
  vlans.set_name(100, 'foo')
  True
