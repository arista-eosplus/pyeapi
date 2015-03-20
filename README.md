# Arista eAPI Python Library

[![Build
Status](https://travis-ci.org/arista-eosplus/pyeapi.svg?branch=develop)](https://travis-ci.org/arista-eosplus/pyeapi) [![Coverage
Status](https://coveralls.io/repos/arista-eosplus/pyeapi/badge.svg?branch=develop)](https://coveralls.io/r/arista-eosplus/pyeapi?branch=develop)

The Python library for Arista's eAPI command API implementation provides a
client API work using eAPI and communicating with EOS nodes.  The Python
library can be used to communicate with EOS either locally (on-box) or remotely
(off-box).  It uses a standard INI-style configuration file to specify one or
more nodes and connection properites.

The pyeapi library also provides an API layer for building native Python
objects to interact with the destination nodes.  The API layer is a convienent
implementation for working with the EOS configuration and is extensible for
developing custom implemenations.

This library is freely provided to the open source community for building
robust applications using Arista EOS.  Support is provided as best effort
through Github issues.

## Requirements

* Arista EOS 4.12 or later
* Arista eAPI enabled for at least one transport (see Official EOS Config Guide
  at arista.com for details)
* Python 2.7

# Getting Started
In order to use pyeapi, the EOS command API must be enabled using ``management
api http-commands`` configuration mode.  This library supports eAPI calls over
both HTTP and UNIX Domain Sockets.  Once the command API is enabled on the
destination node, create a configuration file with the node properities. 

**Note:** The default search path for the conf file is ``~/.eapi.conf``
followed by ``/mnt/flash/eapi.conf``.  This can be overridden by setting
``EAPI_CONF=<path file conf file>`` in your environment.

## Example eapi.conf File
Below is an example of an eAPI conf file.  The conf file can contain more than
one node.  Each node section must be prefaced by **connection:\<name\>** where
\<name\> is the name of the connection.

The following configuration options are available for defining node entries:

* **host** - The IP address or FQDN of the remote device.  If the host
  parameter is omitted then the connection name is used
* **username** - The eAPI username to use for authentication (only required for
  http or https connections)
* **password** - The eAPI password to use for authentication (only required for
  http or https connections)
* **enablepwd** - The enable mode password if required by the destination node
* **transport** - Configures the type of transport connection to use.  The
  default value is _https_.  Valid values are:
    * socket (available in EOS 4.14.5 or later)
    * http_local (available in EOS 4.14.5 or later)
    * http
    * https  
* **port** - Configures the port to use for the eAPI connection.  A default
  port is used if this parameter is absent, based on the transport setting
using the following values:
    * transport: http, default port: 80
    * transport: https, deafult port: 443
    * transport: https_local, default port: 8080
    * transport: socket, default port: n/a


_Note:_ See the EOS User Manual found at arista.com for more details on
configuring eAPI values.

All configuration values are optional. 

```
[connection:veos01]
username: eapi
password: password
transport: http

[connection:veos02]
transport: http

[connection:veos03]
transport: socket

[connection:veos04]
host: 172.16.10.1
username: eapi
password: password
enablepwd: itsasecret
port: 1234
transport: https

[connection:localhost]
transport: http_local
```

The above example shows different ways to define EOS node connections.  All
configuration options will attempt to use default values if not explicitly
defined.  If the host parameter is not set for a given entry, then the
connection name will be used as the host address.

### Configuring \[connection:localhost]

The pyeapi library automatically installs a single default configuration entry
for connecting to localhost host using a transport of sockets.  If using the
pyeapi library locally on an EOS node, simply enable the command API to use
sockets and no further configuration is needed for pyeapi to function.  If you
specify an entry in a conf file with the name ``[connection:localhost]``, the
values in the conf file will overwrite the default.

## Using pyeapi
The Python client for eAPI was designed to be easy to use and implement for
writing tools and applications that interface with the Arista EOS management
plane.  

### Creating a connection and sending commands
Once EOS is configured properly and the config file created, getting started
with a connection to EOS is simple.  Below demonstrates a basic connection
using pyeapi.  For more examples, please see the examples folder.

```
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
```

### Using the API

The pyeapi library provides both a client for send and receiving commands over
eAPI as well as an API for working directly with EOS resources.   The API is
designed to be easy and straightforward to use yet also extensible.  Below is
an example of working with the ``vlans`` API

```
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
```

All API implementations developed by Arista EOS+ CS are found in the pyeapi/api
folder.  See the examples folder for additional examples.

# Installation

The source code for pyeapi is provided on Github at
http://github.com/arista-eosplus/pyeapi.  All current development is done in
the develop branch.  Stable released versions are tagged in the master branch
and uploaded to PyPi.

* To install the latest stable version of pyeapi, simply run ``pip install
  pyeapi`` (or ``pip install --upgrade pyeapi``)
* To install the latest development version from Github, simply clone the
  develop branch and run ``python setup.py install``

# Testing
The pyeapi library provides both unit tests and system tests.  The unit tests
can be run without an EOS node.  To run the system tests, you will need to
update the ``dut.conf`` file found in test/fixtures.  

* To run the unit tests, simply run ``make unittest`` from the root of the
  pyeapi source folder
* To run the system tests, simply run ``make systest`` from the root of the
  pyeapi source fodler
* To run all tests, use ``make tests`` from the root of the pyeapi source
  folder


# Contributing

Contributing pull requests are gladly welcomed for this repository.  Please
note that all contributions that modify the library behavior require
corresponding test cases otherwise the pull request will be rejected.  

# License

New BSD, See [LICENSE](LICENSE) file

