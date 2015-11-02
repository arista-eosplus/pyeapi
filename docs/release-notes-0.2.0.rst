######
v0.2.0
######

2015-03-19

- adds udp_port, vlans and flood_list attributes to vxlan interfaces
- renames spanningtree api module to stp for consistency
- depreciated spanningtree api module in favor of stp
- interfaces module now properly responds to hasattr calls
- fixes an issue with collecting the vxlan global flood list from the config
- fixes an issue with properly parsing portchannel configurations
- adds portfast_type attribute to stp interfaces resource
