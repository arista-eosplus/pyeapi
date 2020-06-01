Using Config Sessions via Python Client for eAPI
=======================================================

Config Sessions can be used via Pyeapi. Config sessions allow a block of config
to be added as one operation instead of as individual lines. Configurations applied
in this manner allow the user to abort all the config being applied if an error occurs.

Using Config Sessions:

.. code-block:: python

  import pyeapi
  node = pyeapi.connect_to('veos01')
  vlans = node.api('vlans')

  node.configure_session()

  node.diff()  # Sends "configure session 9c27d0e8-afef-4afd-95ae-3e3200bb7a3e" and "show session-config diff"

  """
  =>
  --- system:/running-config
  +++ session:/9c27d0e8-afef-4afd-95ae-3e3200bb7a3e-session-config
  @@ -32,7 +32,7 @@
   !
   clock timezone Asia/Tokyo
   !
  -vlan 1000,3001-3006
  +vlan 100,1000,3001-3006
   !
   interface Port-Channel1
      switchport trunk allowed vlan 3001-3003
  """

  node.abort()  # Sends "configure session 9c27d0e8-afef-4afd-95ae-3e3200bb7a3e" and "abort"
  # or
  node.commit() # Sends "configure session 9c27d0e8-afef-4afd-95ae-3e3200bb7a3e" and "commit"

Config Session with invalid config line:

.. code-block:: python

  node = pyeapi.connect_to('veos01')
  interfaces = node.api('interfaces')
  node.configure_session()

  if not (interfaces.configure(['interface Eth6', 'no switchport', 'ip address 172.16.0.1/30']) and \
      interfaces.configure(['interface Eth7', 'no switchport', 'ip address 172.16.0.1/30'])):
      node.abort()  # This aborts everything!!

For more detailed information about using Configure Sessions in EOS, reference the user
manual for the version of EOS running on your switch.
