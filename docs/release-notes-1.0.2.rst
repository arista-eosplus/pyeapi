Release 1.0.2
-------------

2023-06-30

New Modules
^^^^^^^^^^^

Enhancements
^^^^^^^^^^^^

Fixed
^^^^^

* Fixed a regression introduced by PR#220 (`220 <https://github.com/arista-eosplus/pyeapi/pull/220>`_)
    Performance enchancement achieved with cacheing in PR#220 has a side effect: if configuration was read before the config 
    modifications made, then the modifications won't be reflected in the consecutive configuration reads (due to the cached read) 
* Fixed all failing system tests, plus made some improvements in unit tests.   

Known Caveats
^^^^^^^^^^^^^


