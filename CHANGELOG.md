Python Client for eAPI
======================

## v0.2.2, 04/15/2015

- fixes an issue with eAPI error messages that do not return a data key

## v0.2.1, 03/28/2015

- restores default certificate validation behavior for py2.7.9

## v0.2.0, 3/19/2015

- adds udp_port, vlans and flood_list attributes to vxlan interfaces
- renames spanningtree api module to stp for consistency
- depreciated spanningtree api module in favor of stp
- interfaces module now properly responds to hasattr calls
- fixes an issue with collecting the vxlan global flood list from the config
- fixes an issue with properly parsing portchannel configurations
- adds portfast_type attribute to stp interfaces resource

## v0.1.1, 2/17/2015

- adds introspection properties to CommandError for more details (#4)
- changed the default transport from HTTP to HTTPS to align with EOS
- updates the message returned if the connection profile name is not found
- fixes connection name not copied to host parameter if host not configured
- fixes an issue where an ipinterface wasnt properly recognized
- fixes an issue where a switchport interface was propertly recognized

## v0.1.0, 1/23/2015

- initial public release of pyeapi
- initial support for vlans
- initial support for interfaces
- initial support for spanningtree
- initial support for switchports
- initial support for ipinterfaces
