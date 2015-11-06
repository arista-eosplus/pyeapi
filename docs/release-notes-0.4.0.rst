######
v0.4.0
######

2015-11-05

New APIs
^^^^^^^^

* Add VRRP (`57 <https://github.com/arista-eosplus/pyeapi/pull/57>`_) [`grybak <https://github.com/grybak>`_]
    Add support for VRRP configuration.
* Add Staticroute (`45 <https://github.com/arista-eosplus/pyeapi/pull/45>`_) [`grybak <https://github.com/grybak>`_]
    The staticroute API enables you to set static IPv4 routes on your EOS device.
* Add VARP (`43 <https://github.com/arista-eosplus/pyeapi/pull/43>`_) [`phil-arista <https://github.com/phil-arista>`_]
    The Varp API includes the subclass VarpInterfaces. These two combine to provide methods to set virtual IP addresses on interfaces as well as set the global virtual-router mac-address.
* Add Routemap (`40 <https://github.com/arista-eosplus/pyeapi/pull/40>`_) [`phil-arista <https://github.com/phil-arista>`_]
    .. comment

Enhancements
^^^^^^^^^^^^

* Making configure RADIUS compatible (`53 <https://github.com/arista-eosplus/pyeapi/pull/53>`_) [`GaryCarneiro <https://github.com/GaryCarneiro>`_]
    Modifies the syntax of the ``config`` method to use ``configure terminal`` instead of just ``configure``.
* Close #46 (`47 <https://github.com/arista-eosplus/pyeapi/pull/47>`_) [`phil-arista <https://github.com/phil-arista>`_]
    This enhancement allows you to set the LACP Mode while executing the set_members method.  The call would look like ``node.api('interfaces').set_members(1, [Ethernet1,Ethernet2], mode='active')``
* Added support to specify timeout (`41 <https://github.com/arista-eosplus/pyeapi/pull/41>`_) [`dbarrosop <https://github.com/dbarrosop>`_]
    This enhancement provides a way to specify a connection timeout.  The default is set to 60 seconds.
* Add BGP maximum-paths support (`36 <https://github.com/arista-eosplus/pyeapi/pull/36>`_) [`phil-arista <https://github.com/phil-arista>`_]
    This enhancement adds more attributes to ``eos_bgp_config``.  This provides the ability to configure ``maximum-paths N ecmp M`` in your ``router bgp R`` configuration.
* Add sshkey support to users API (`34 <https://github.com/arista-eosplus/pyeapi/pull/34>`_) [`phil-arista <https://github.com/phil-arista>`_]
    This enhancement augments the ``users`` API to now support SSH Keys.

Fixed
^^^^^

* client.py 'def enable' returned dictionary key inconsistency (`35 <https://github.com/arista-eosplus/pyeapi/issues/35>`_)
    The key that's supposed to be returned is ``result`` but instead the method formerly returned the key ``response``.  For now, both ``response`` and ``result`` will be returned with the same data, but ``response`` will be removed in a future release.
* [API Users] Can't run set_role with no value (`33 <https://github.com/arista-eosplus/pyeapi/issues/33>`_)
    The node.api('users').set_role('test') method didn't remove the role or default the role as you would expect. This bug fix resolves that.
* [API Users] Can't run set_privilege with no value (`32 <https://github.com/arista-eosplus/pyeapi/issues/32>`_)
    The set_privilege('user') method did not properly negate the privilege level when no argument was passed into the method.
* [ API interfaces ] get_members regex wrongly includes PeerEthernet when lag is up (`28 <https://github.com/arista-eosplus/pyeapi/issues/28>`_)
    The get_members() method wrongly included a duplicate member when the ``show port-channel N all-ports`` showed the PeerEthernetX. The regular expression has been updated to ignore these entries.
* [API] users - can't create password with non-alpha/int characters (`23 <https://github.com/arista-eosplus/pyeapi/issues/23>`_)
    The characters ``(){}[]`` cannot be part of a username. Documentation has been updated to reflect this.
* Users with sha512 passwords don't get processed correctly using api('users').getall() (`22 <https://github.com/arista-eosplus/pyeapi/issues/22>`_)
    Fixed regex to extract the encrypted passwords accurately.

Known Caveats
^^^^^^^^^^^^^

* failure when eapi.conf is not formatted correctly (`38 <https://github.com/arista-eosplus/pyeapi/issues/38>`_)
    .. comment
