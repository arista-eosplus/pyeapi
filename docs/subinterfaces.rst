Configuring Subinterfaces Using Python Client for eAPI
=======================================================

Subinterfaces can be configured on Ethernet and Port-Channel interfaces. To do this in
pyeapi simply call create or delete with your subinterface name.

Subinterfaces require that the primary interface be in routed mode.

.. code-block:: python

  import pyeapi
  node = pyeapi.connect_to('veos01')
  node.api('ipinterfaces').create('Ethernet1')

At this point the below should be in your running configuration.

.. code-block:: shell

  !
  interface Ethernet1
     no switchport
  !

Next step is to create the subinterface

.. code-block:: python

  node.api('interfaces').create('Ethernet1.1')

.. code-block:: shell

  !
  interface Ethernet1
     no switchport
  !
  interface Ethernet1.1
  !

Subinterfaces also require a vlan to be applied to them.

.. code-block:: python

  node.api('interfaces').set_encapsulation('Ethernet1.1', 4)

.. code-block:: shell

  !
  interface Ethernet1
     no switchport
  !
  interface Ethernet1.1
     encapsulation dot1q vlan 4
  !

Using delete in the same format as create will remove the subinterface.

For more detailed information about configuring subinterfaces in EOS, reference the user
manual for the version of EOS running on your switch.
