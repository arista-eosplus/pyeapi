#
# Copyright (c) 2014, Arista Networks, Inc.

class Ipinterface(object):

    def __init__(self, api):
        self.api = api

    def getall(self):
        """ Returns all of the IP interfaces found in the running-config

        Example:
            {
                'Ethernet1': {
                    'address': <string>,
                    'mtu': <int>
                }
            }

        Returns:
            dict: a dict object of IP interface attributes
        """
        result = self.api.enable('show ip interfaces')
        response = dict()
        for key, value in result[0]['interfaces'].items():
            address = '%s/%s' % \
                (value['interfaceAddress']['primaryIp']['address'],
                 value['interfaceAddress']['primaryIp']['maskLen'])
            response[key] = dict(address=address, mtu=value['mtu'])
        return response

    def create(self, name):
        """ Creates a new IP interface instance
        """
        return self.api.config(['interface %s' % name, 'no switchport']) == [{}, {}]

    def delete(self, name):
        """ Deletes an IP interface instance from the running configuration
        """
        commands = ['interface %s' % name, 'no ip address', 'switchport']
        return self.api.config(commands)  == [{}, {}, {}]

    def set_address(self, name, value=None, default=False):
        """ Configures the interface IP address
        """
        commands = ['interface %s' % name]
        if default:
            commands.append('default ip address')
        elif value is not None:
            commands.append('ip address %s' % value)
        else:
            commands.append('no ip address')
        return self.api.config(commands) == [{}, {}]

    def set_mtu(self, name, value=None, default=False):
        """ Configures the interface IP MTU
        """
        commands = ['interface %s' % name]
        if default:
            commands.append('default mtu')
        elif value is not None:
            commands.append('mtu %s' % value)
        else:
            commands.append('no mtu')
        return self.api.config(commands) == [{}, {}]

def instance(api):
    return Ipinterface(api)
