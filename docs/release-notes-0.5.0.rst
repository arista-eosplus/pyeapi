######
v0.5.0
######

2016-02-16

New APIs
^^^^^^^^

* NTP module (`72 <https://github.com/arista-eosplus/pyeapi/pull/72>`_) [`grybak-arista <https://github.com/grybak-arista>`_]
    Add NTP functionality.

Enhancements
^^^^^^^^^^^^

* Add banner support to System API (`75 <https://github.com/arista-eosplus/pyeapi/pull/75>`_) [`dathelen <https://github.com/dathelen>`_]
    Add API support for EOS banners and motd.
* Issue #18 performance fixes (`74 <https://github.com/arista-eosplus/pyeapi/pull/74>`_) [`cheynearista <https://github.com/cheynearista>`_]
    Rework underlying HTTP transport to improve receive performance.
* Redmine issue 648 (`73 <https://github.com/arista-eosplus/pyeapi/pull/73>`_) [`grybak-arista <https://github.com/grybak-arista>`_]
    Fix some instances where an empty string as negation would not properly negate the option/command.
* setup.py print statement for python 3 (`71 <https://github.com/arista-eosplus/pyeapi/pull/71>`_) [`mzbenami <https://github.com/mzbenami>`_]
    Reformat print statement to work properly with Python3+
* Implement add ACL with seq nos (`70 <https://github.com/arista-eosplus/pyeapi/pull/70>`_) [`dathelen <https://github.com/dathelen>`_]
    Add a sequence number when adding a new ACL entry.
* Fix for redmine issues 234 and 268 (`68 <https://github.com/arista-eosplus/pyeapi/pull/68>`_) [`grybak-arista <https://github.com/grybak-arista>`_]
    Reworked some system tests for robustness
    get_block accepts a config string as well as the default 'running_config'
* fix #7 and fix #37 (`67 <https://github.com/arista-eosplus/pyeapi/pull/67>`_) [`grybak-arista <https://github.com/grybak-arista>`_]
    Certain command errors will return more detailed information.
    The connect() method can optionally return a node object.
* Add disable key to existing modules for negation of properties (`65 <https://github.com/arista-eosplus/pyeapi/pull/65>`_) [`grybak-arista <https://github.com/grybak-arista>`_]
    Modules now take disable=<True/False> to negate the command, rather than overloading value.
* Compatibility fix for current mock versions (`64 <https://github.com/arista-eosplus/pyeapi/pull/64>`_) [`wtucker <https://github.com/wtucker>`_]
* Add key error checking to set_tracks (`63 <https://github.com/arista-eosplus/pyeapi/pull/63>`_) [`grybak-arista <https://github.com/grybak-arista>`_]
    .. comment

Fixed
^^^^^

* Failure when eapi.conf is not formatted correctly (`38 <https://github.com/arista-eosplus/pyeapi/issues/38>`_)
    Adds more robust error handling when parsing eapi.conf files. Also, if an error is found it will syslog the error and continue parsing any other eapi.conf files.

Known Caveats
^^^^^^^^^^^^^
