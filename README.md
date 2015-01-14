# Arista eAPI Python Library

pyEAPI is a Python library for Arista's eAPI command API implementation which allows for managing Arista EOS node configurations.  The pyEAPI client library provdies a consistent interface to working with EOS resources pragmatically.

## Getting Started

To get started with pyEAPI, you will need an Arista EOS node running EOS 4.12 or later along with eAPI enabled.  pyEAPI can be run both locally in EOS or remotely using HTTP/S.

## Installing

The source code for pyEAPI is provided on Github at http://github.com/arista-eosplus/pyeapi.   Development is done in the develop branch with releases tagged and provide via PyPi.

* To install the latest offical release of pyEAPI, simply run ``pip install pyeapi`` (or ``pip install --upgrade pyeapi``)
* To install the latest development version from Github, clone the develop branch and run ``python setup.py install``

## Enabling EOS Command API

pyEAPI require the command API to be enabled and available for use to communicate with EOS.  Since eAPI is not enabled by default, it must be initially enabled before pyEAPI can be used.


The steps below provide the basic steps to enable eAPI.  For more advanced configurations, please consult the EOS User Guide.

__Step 1.__ Login to the destination node and enter configuration mode

```
switch> enable
switch# configure
switch(config)#
```

__Step 2.__ Enable eAPI

```
switch(config)# management api http-commands
switch(config-mgmt-api-http-cmds)# no shutdown
```
The configuration above enables eAPI with the default settings.  This enables eAPI to listen for connections on HTTPS port 443 by default.

__Step 3.__ Create a local user
The user is used to authenticate commands for use during eAPI calls.  s

```
switch(config)# username eapi secret icanttellyou
```

The username (eapi) and password (icanttellyou) can be anything you like.  In addition, other authentication mechansims could be used such as TACACS+ or RADIUS.

## Configuring pyEAPI

pyEAPI uses a conf file to pass the required parameters for username and password to the API client.  The default conf file location depends on if pyEAPI is running locally on an EOS switch or remotely on a Linux host.

* If running directly in EOS, then the default file location is /mnt/flash/eapi.conf.
* If running on a Linux host, the default file location is ~/.eapi.conf,
  followed by /etc/eapi.conf

The pyEAPI conf file is an INI-style config file that supplies the basic authentication and connection parameters necessary to communicate with eAPI.

### Creating a connection

```
import pyeapi.client
node = pyeapi.client.connect(host='10.10.10.10')
```

### Using a conf file
The library will automatically search for the config file in the following
locations: ~/.eapi.conf, /mnt/flash/eapi.conf.  It will load the first 
config file that it finds.   Alternatively you can pass the full path to the 
config file in the load_config method.

```
import pyeapi.client
pyeapi.client.load_config()
node = pyeapi.client.connect_to('veos01')
```

### Example conf file
Config files support multiple nodes.  Each node should have a connection
section in the config file.  To create a node entry, preceed the name of the 
node with connection: (see examples below).  

```
[connection:eos01]
username: eapi
password: password
transport: http

[connection:localhost]
transport: socket

[connection:eos02]
host: 172.10.10.1
```

The following configuration options are available for entries:

* host - The IP address or FQDN of the remote device.  If the host parameter
    is omitted then the connection name is used
* username - The eAPI username to use for authentication
* password - The eAPI password to use for authentication
* transport - Configures the type of transport connection to use.  Valid
    values are socket, http_local, http, https.  The default value is http
* port - Configures the port to use for the eAPI connection.  A default port
    is used if this parameter is absent, based on the transport setting using
    the following:
        transport: http, default port: 80
        transport: https, deafult port: 443
        transport: https_local, default port: 8080
        trasnport: socket, default port: n/a

## License
BSD-3, See LICENSE file
