Python client for eAPI
======================

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
