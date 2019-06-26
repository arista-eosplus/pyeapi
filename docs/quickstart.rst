##########
Quickstart
##########

In order to use pyeapi, the EOS command API must be enabled using configuration
mode.  This library supports eAPI calls over both HTTP/S and UNIX Domain
Sockets. Once the command API is enabled on the destination node, create a
configuration file with the node properties. There are some nuances about the
configuration file that are important to understand; take a minute and read
about the :ref:`configfile`.

**********************
Enable EOS Command API
**********************

Refer to your official Arista EOS Configuration Guide to learn how to enable
EOS Command API. Depending upon your software version, the options available
include:

  - HTTP
  - HTTPS
  - HTTPS Certificates
  - HTTP Local
  - Unix Socket

**************
Install Pyeapi
**************

Follow the instructions on the :ref:`install` guide to prepare your node for
pyeapi.

************************
Create an eapi.conf file
************************

Follow the instructions on the :ref:`configfile` guide to create a pyeapi
configuration file. You can skip this step if you are running the pyeapi
script on-box and Unix Sockets are enabled for EOS Command API.

*****************
Connect to a Node
*****************

The Python client for eAPI was designed to be easy to use and implement for
writing tools and applications that interface with the Arista EOS management
plane.

Once EOS is configured properly and the config file created, getting started
with a connection to EOS is simple.  Below demonstrates a basic connection
using pyeapi. For more examples, please see the
`examples <https://github.com/arista-eosplus/pyeapi/tree/develop/examples>`_
folder on Github.

This first example shows how to instantiate the Node object. The Node object
provides some helpful methods and attributes to work with the switch.

.. code-block:: python

  # start by importing the library
  import pyeapi

  # create a node object by specifying the node to work with
  node = pyeapi.connect_to('veos01')

  # send one or more commands to the node
  node.enable('show hostname')
  [{'command': 'show hostname',
    'encoding': 'json',
    'result': {u'hostname': u'veos01',
               u'fqdn': u'veos01.arista.com'}}]

  # Request a specific revision of a command that has been updated
  node.enable({'cmd': 'show cvx', 'revision': 2})
  [{'command': {'cmd': 'show cvx', 'revision': 2},
    'encoding': 'json',
    'result': {u'clusterMode': False,
               u'controllerUUID': u'',
               u'enabled': False,
               u'heartbeatInterval': 20.0,
               u'heartbeatTimeout': 60.0}}]

  # use the config method to send configuration commands
  node.config('hostname veos01')
  [{}]

  # multiple commands can be sent by using a list
  # (works for both enable or config)
  node.config(['interface Ethernet1', 'description foo'])
  [{}, {}]

  # return the running or startup configuration from the
  # node (output omitted for brevity)
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
