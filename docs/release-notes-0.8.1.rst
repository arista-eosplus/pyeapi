######
v0.8.1
######

2017-07-20

New Modules
^^^^^^^^^^^

Enhancements
^^^^^^^^^^^^

Fixed
^^^^^

* hard coded /command-api was probably a safe default (`141 <https://github.com/arista-eosplus/pyeapi/issues/141>`_)
    This issue/PR (`142 <https://github.com/arista-eosplus/pyeapi/pull/142>`_) reverts a change that introduced a bug breaking pyeapi's unix-socket connection. Regardless of using TCP/IP or unix-socket for communicating with the EAPI process the data being sent to the process is formatted in HTTP requests. The HTTP requests should always POST to the /command-api endpoint. The change being reverted by this prevents the unix-socket path from ever erroneously being used as the HTTP endpoint.
* Execute does not work well with long running commands (`138 <https://github.com/arista-eosplus/pyeapi/issues/138>`_)
    Added socket specific error messages in PR (`144 <https://github.com/arista-eosplus/pyeapi/pull/144>`_) to help distinguish errors caused by command timeouts.
* eAPI does not handle commands sent as unicode strings (`137 <https://github.com/arista-eosplus/pyeapi/issues/137>`_)
    Bug fixed in PR (`139 <https://github.com/arista-eosplus/pyeapi/pull/139>`_) unicode commands converted to strings when detected.
