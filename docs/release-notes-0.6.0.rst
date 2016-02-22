######
v0.6.0
######

2016-02-22

New Modules
^^^^^^^^^^^
* None

Enhancements
^^^^^^^^^^^^

* Added support for multiline commands without having to pass them as a dictionary (`78 <https://github.com/arista-eosplus/pyeapi/pull/78>`_) [`dbarrosop <https://github.com/dbarrosop>`_]
    (See example below)

.. code-block:: python

  >>> import pyeapi
  >>> connection = pyeapi.client.connect(
  ...     transport='https',
  ...     host='192.168.56.201',
  ...     username='vagrant',
  ...     password='vagrant',
  ...     port=443,
  ...     timeout=60
  ... )
  >>> device = pyeapi.client.Node(connection)
  >>> device.run_commands('show hostname')
  [{u'hostname': u'localhost', u'fqdn': u'localhost'}]
  >>> device.run_commands('show banner login')
  [{u'loginBanner': u''}]
  >>> my_commands = [
  ...     'configure session whatever',
  ...     'hostname new-hostname',
  ...     'banner login MULTILINE:This is a new banner\nwith different lines!!!',
  ...     'end'
  ... ]
  >>>
  >>> device.run_commands(my_commands)
  [{}, {}, {}, {}]
  >>> print device.run_commands(['show session-config named whatever diffs'], encoding='text')[0]['output']
  --- system:/running-config
  +++ session:/whatever-session-config
  @@ -3,6 +3,8 @@
  ! boot system flash:/vEOS-lab.swi
  !
  transceiver qsfp default-mode 4x10G
  +!
  +hostname new-hostname
  !
  spanning-tree mode mstp
  !
  @@ -22,6 +24,11 @@
  !
  no ip routing
  !
  +banner login
  +This is a new banner
  +with different lines!!!
  +EOF
  +!
  management api http-commands
    no shutdown
  !
  >>> device.run_commands(['configure session whatever', 'commit'])
  [{}, {}]
  >>> device.run_commands('show hostname')
  [{u'hostname': u'new-hostname', u'fqdn': u'new-hostname'}]
  >>> device.run_commands('show banner login')
  [{u'loginBanner': u'This is a new banner\nwith different lines!!!\n'}]
  >>>
