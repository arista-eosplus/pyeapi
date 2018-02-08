Release 0.8.2
-------------

2018-02-09

New Modules
^^^^^^^^^^^


Enhancements
^^^^^^^^^^^^

* Support eapi command revision syntax (`158 <https://github.com/arista-eosplus/pyeapi/pull/158>`_) [`jerearista <https://github.com/jerearista>`_]
    Support requests for specific revisions of EOS command output

  .. code-block:: python

    >>> node.enable({'cmd': 'show cvx', 'revision': 2})
    [{'command': {'cmd': 'show cvx', 'revision': 2},
      'encoding': 'json',
      'result': {u'clusterMode': False,
                 u'controllerUUID': u'',
                 u'enabled': False,
                 u'heartbeatInterval': 20.0,
                 u'heartbeatTimeout': 60.0}}]

* Add clearer error message for bad user credentials. (`152 <https://github.com/arista-eosplus/pyeapi/pull/152>`_) [`mharista <https://github.com/mharista>`_]
    .. comment
* Reformat EapiConnection send methods exception handling. (`148 <https://github.com/arista-eosplus/pyeapi/pull/148>`_) [`mharista <https://github.com/mharista>`_]
    .. comment

Fixed
^^^^^

* Fix route map getall function to find route maps with a hyphen in the name. (`154 <https://github.com/arista-eosplus/pyeapi/pull/154>`_) [`mharista <https://github.com/mharista>`_]
    .. comment

Known Caveats
^^^^^^^^^^^^^


