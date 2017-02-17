Configuring Sub-interfaces Using Python Client for eAPI
======================================================

Sub-interfaces can be configured on Ethernet and Port-Channel interfaces. To do this in
eAPI simply call create or delete with your sub-interface name.

import pyeapi
node = pyeapi.connect_to('veos01')
node.api('interfaces').create('Ethernet1.1')

At this point the below should be in your running configuration.

!
interface Ethernet1
!
interface Ethernet1.1
!

Sub-interfaces require that the primary interface be in routed mode.

node.api('ipinterfaces').create('Ethernet1')

!
interface Ethernet1
   no switchport
!
interface Ethernet1.1
!

Sub-interfaces also require a vlan to be applied to them.

node.api('interfaces').set_encapsulation('Ethernet1.1', 4)

!
interface Ethernet1
   no switchport
!
interface Ethernet1.1
   encapsulation dot1q vlan 4
!

Using delete in the same format as create will remove the sub-interface.

For more detailed information about configuring sub-interfaces in EOS, reference the user
manual for the version of EOS running on your switch.
