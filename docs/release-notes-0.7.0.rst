######
v0.7.0
######

2016-09-08

New Modules
^^^^^^^^^^^

* Add OSPF API (`95 <https://github.com/arista-eosplus/pyeapi/pull/95>`_) [`brigoldberg <https://github.com/brigoldberg>`_]
    Big thanks for the community support!

Enhancements
^^^^^^^^^^^^

* Enhance Node enable() method (`100 <https://github.com/arista-eosplus/pyeapi/pull/100>`_) [`dathelen <https://github.com/dathelen>`_]
    This enhancement adds a send_enable flag to the enable and run_commands Node methods.  By default the enable command will be sent, however you can now run commands without prepending the enable.
* Finish OSPF API (`99 <https://github.com/arista-eosplus/pyeapi/pull/99>`_) [`dathelen <https://github.com/dathelen>`_]
    Create system tests and add unit tests to increase code coverage.
* Add Cross-Platform Support for pyeapi (`94 <https://github.com/arista-eosplus/pyeapi/pull/94>`_) [`grybak-arista <https://github.com/grybak-arista>`_]
    Use logging instead of syslog for better cross-platform compatibility.  This enhancement provides support for Windows users.

Fixed
^^^^^

* Allow dot and hyphen in mlag domain-id (`91 <https://github.com/arista-eosplus/pyeapi/issues/91>`_)
    Include handling any character in domain-id string, including dot, hyphen, and space.
