######
v0.8.0
######

2017-03-14

New Modules
^^^^^^^^^^^

* Base API for VRF support. (`133 <https://github.com/arista-eosplus/pyeapi/pull/133>`_) [`mharista <https://github.com/mharista>`_]
    Added new API module for creating VRFs. In addition to creating, configuring and removing VRFs the updates allow for applying a VRF to an interface and creating a VRF specific OSPF instance.

Enhancements
^^^^^^^^^^^^

* Add base extended ACL support. (`135 <https://github.com/arista-eosplus/pyeapi/pull/135>`_) [`mharista <https://github.com/mharista>`_]
    Updated ACL api to include extended ACLs in addition to standard. To create an extended ACL provide the type as extended when creating the ACL (default is standard). Currently extended ACL statements can be added with action, protocol, and source/destination address. The API will determine the type of ACL by name after it has been created for future updates.
* Add support for creating and deleting ethernet subinterfaces (`132 <https://github.com/arista-eosplus/pyeapi/pull/132>`_) [`mharista <https://github.com/mharista>`_]
    Allow for creation and deletion of ethernet subinterfaces as part of the EthernetInterface class. Subinterfaces are also supported on PortChannel interfaces. An example using the API to create an ethernet subinterface is provided in the docs.
* Add node attributes from show version command (`131 <https://github.com/arista-eosplus/pyeapi/pull/131>`_) [`mharista <https://github.com/mharista>`_]
    Added information from show version as attributes to a node. Version, version number and model are added. Version number is simply the numeric portion of the version. For example 4.17.1 if the version is 4.17.1M. All three parameters are populated from the output of show version when any one of the parameters is accessed the first time.
* Add support for eAPI expandAliases parameter (`127 <https://github.com/arista-eosplus/pyeapi/pull/127>`_) [`mharista <https://github.com/mharista>`_]
    Allowed users to provide the expandAliases parameter to eAPI calls. This allows users to use aliased commands via the API. For example if an alias is configured as 'sv' for 'show version' then an API call with sv and the expandAliases parameter will return the output of show version.
* Add support for autoComplete parameter. Issue 119 (`123 <https://github.com/arista-eosplus/pyeapi/pull/123>`_) [`mharista <https://github.com/mharista>`_]
    Allows users to use short hand commands in eAPI calls. With this parameter included a user can send 'sh ver' via eAPI to get the output of show version.
* expose portchannel attributes :lacp fallback, lacp fallback timeout (`118 <https://github.com/arista-eosplus/pyeapi/pull/118>`_) [`lruslan <https://github.com/lruslan>`_]
    Helps for configuring LACP fallback in EOS.

Fixed
^^^^^

* API path is hardcoded in EapiConnection.send() (`129 <https://github.com/arista-eosplus/pyeapi/issues/129>`_)
    Updated the previously hardcoded path to /command-api in the EAPI connection to use the transport objects path.
* Cannot run 'no ip virtual-router mac-address' in eos 4.17.x (`122 <https://github.com/arista-eosplus/pyeapi/issues/122>`_)
    Fixed command format for negating an ip virtual-router mac-address. Default and disable forms of the command changed and require the mac-address value in EOS 4.17. Update fixes this for newer versions and is backwards compatible.
* Non-standard HTTP/s port would cause connection to fail (`120 <https://github.com/arista-eosplus/pyeapi/issues/120>`_)
    Bug fixed in PR (`121 <https://github.com/arista-eosplus/pyeapi/pull/121>`_) where a port passed in via eapi.conf as a unicode value caused the http connection to fail.
