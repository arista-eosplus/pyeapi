#
# Copyright (c) 2014, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   Neither the name of Arista Networks nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""Module for working with EOS access control list resources

This module provides an implementation for configuring and managing access
access control lists on Arista EOS nodes.  Access control lists can be
specified as either 'standard' or 'extended' ACLs.  This module provides the
following class implementations:

    * Acls -- The top-level class used to manage both standard and extended
        access control lists in EOS
    * StandardAcls -- Class that manages the set of standard ACLs
    * ExtendedAcls -- Class that manages the set of extended ACLs

"""
import re

import netaddr

from pyeapi.api import EntityCollection
from pyeapi.utils import ProxyCall

VALID_ACLS = frozenset(['standard', 'extended'])


def mask_to_prefixlen(mask):
    """Converts a subnet mask from dotted decimal to bit length

    Args:
        mask (str): The dotted decimal subnet mask to convert

    Returns:
        str: The subnet mask as a valid prefix length
    """
    mask = mask or '255.255.255.255'
    return netaddr.IPAddress(mask).netmask_bits()


def prefixlen_to_mask(prefixlen):
    """Converts a prefix length to a dotted decimal subnet mask

    Args:
        prefixlen (str): The prefix length value to convert

    Returns:
        str: The subt mask as a dotted decimal string
    """
    prefixlen = prefixlen or '32'
    addr = '0.0.0.0/%s' % prefixlen
    return str(netaddr.IPNetwork(addr).netmask)


class Acls(EntityCollection):

    def __init__(self, node, *args, **kwargs):
        super(Acls, self).__init__(node, *args, **kwargs)
        self._instances = dict()

    def get(self, name):
        return self.get_instance(name)[name]

    def getall(self):
        """Returns all ACLs in a dict object.

        Returns:
            A Python dictionary object containing all ACL
            configuration indexed by ACL name::

                {
                    "<ACL1 name>": {...},
                    "<ACL2 name>": {...}
                }

        """
        acl_re = re.compile(r'^ip access-list (?:(standard) )?(.+)$', re.M)
        response = {'standard': {}, 'extended': {}}
        for acl_type, name in acl_re.findall(self.config):
            acl = self.get(name)
            if acl_type and acl_type == 'standard':
                response['standard'][name] = acl
            else:
                response['extended'][name] = acl
        return response

    def __getattr__(self, name):
        return ProxyCall(self.marshall, name)

    def marshall(self, name, *args, **kwargs):
        acl_name = args[0]
        acl_instance = self.get_instance(acl_name)
        if not hasattr(acl_instance, name):
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (acl_instance, name))
        method = getattr(acl_instance, name)
        return method(*args, **kwargs)

    def get_instance(self, name):
        if name in self._instances:
            return self._instances[name]
        acl_re = re.compile(r'^ip access-list (?:(standard) )?(%s)$' % name,
                            re.M)
        match = acl_re.search(self.config)
        if match:
            acl_type = match.group(1) or 'extended'
            return self.create_instance(match.group(2), acl_type)
        return {name: None}

    def create_instance(self, name, acl_type):
        if acl_type not in VALID_ACLS:
            acl_type = 'standard'
        acl_instance = ACL_CLASS_MAP.get(acl_type)
        self._instances[name] = acl_instance(self.node)
        return self._instances[name]

    def create(self, name, type='standard'):
        # Create ACL instance for ACL type Standard or Extended then call
        # create method for specific ACL class.
        acl_instance = self.create_instance(name, type)
        return acl_instance.create(name)


class StandardAcls(EntityCollection):

    entry_re = re.compile(r'(\d+)'
                          r'(?: ([p|d]\w+))'
                          r'(?: (any))?'
                          r'(?: (host))?'
                          r'(?: ([0-9]+(?:\.[0-9]+){3}))?'
                          r'(?:/([0-9]{1,2}))?'
                          r'(?: ([0-9]+(?:\.[0-9]+){3}))?'
                          r'(?: (log))?')

    def get(self, name):
        config = self.get_block('ip access-list standard %s' % name)
        if not config:
            return None
        resource = dict(name=name, type='standard')
        resource.update(self._parse_entries(config))
        return resource

    def _parse_entries(self, config):
        entries = dict()
        for item in re.finditer(r'\d+ [p|d].*$', config, re.M):
            match = self.entry_re.match(item.group(0))
            (seq, act, anyip, host, ip, mlen, mask, log) = match.groups()
            entry = dict()
            entry['action'] = act
            entry['srcaddr'] = ip or '0.0.0.0'
            entry['srclen'] = mlen or mask_to_prefixlen(mask)
            entry['log'] = log is not None
            entries[seq] = entry
        return dict(entries=entries)

    def create(self, name):
        return self.configure('ip access-list standard %s' % name)

    def delete(self, name):
        return self.configure('no ip access-list standard %s' % name)

    def default(self, name):
        return self.configure('default ip access-list standard %s' % name)

    def update_entry(self, name, seqno, action, addr, prefixlen, log=False):
        cmds = ['ip access-list standard %s' % name]
        cmds.append('no %s' % seqno)
        entry = '%s %s %s/%s' % (seqno, action, addr, prefixlen)
        if log:
            entry += ' log'
        cmds.append(entry)
        cmds.append('exit')
        return self.configure(cmds)

    def add_entry(self, name, action, addr, prefixlen, log=False, seqno=None):
        cmds = ['ip access-list standard %s' % name]
        entry = '%s %s/%s' % (action, addr, prefixlen)
        if seqno is not None:
            entry = '%s %s' % (seqno, entry)
        if log:
            entry += ' log'
        cmds.append(entry)
        cmds.append('exit')
        return self.configure(cmds)

    def remove_entry(self, name, seqno):
        cmds = ['ip access-list standard %s' % name, 'no %s' % seqno, 'exit']
        return self.configure(cmds)


class ExtendedAcls(EntityCollection):

    entry_re = re.compile(r'(\d+)'
                          r'(?: ([p|d]\w+))'
                          r'(?: (\w+|\d+))'
                          r'(?: ([a|h]\w+))?'
                          r'(?: ([0-9]+(?:\.[0-9]+){3}))?'
                          r'(?:/([0-9]{1,2}))?'
                          r'(?: ((?:eq|gt|lt|neq|range) [\w-]+))?'
                          r'(?: ([a|h]\w+))?'
                          r'(?: ([0-9]+(?:\.[0-9]+){3}))?'
                          r'(?:/([0-9]{1,2}))?'
                          r'(?: ([0-9]+(?:\.[0-9]+){3}))?'
                          r'(?: ((?:eq|gt|lt|neq|range) [\w-]+))?'
                          r'(?: (.+))?')

    def get(self, name):
        config = self.get_block('ip access-list %s' % name)
        if not config:
            return None
        resource = dict(name=name, type='extended')
        resource.update(self._parse_entries(config))
        return resource

    def _parse_entries(self, config):
        entries = dict()
        for item in re.finditer(r'\d+ [p|d].*$', config, re.M):
            match = self.entry_re.match(item.group(0))
            if match:
                entry = dict()
                entry['action'] = match.group(2)
                entry['protocol'] = match.group(3)
                entry['srcaddr'] = match.group(5) or 'any'
                entry['srclen'] = match.group(6)
                entry['srcport'] = match.group(7)
                entry['dstaddr'] = match.group(9) or 'any'
                entry['dstlen'] = match.group(10)
                entry['dstport'] = match.group(12)
                entry['other'] = match.group(13)
                entries[match.group(1)] = entry
        return dict(entries=entries)

    def create(self, name):
        return self.configure('ip access-list %s' % name)

    def delete(self, name):
        return self.configure('no ip access-list %s' % name)

    def default(self, name):
        return self.configure('default ip access-list %s' % name)

    def update_entry(self, name, seqno, action, protocol, srcaddr,
                     srcprefixlen, dstaddr, dstprefixlen, log=False):
        cmds = ['ip access-list %s' % name]
        cmds.append('no %s' % seqno)
        entry = '%s %s %s %s/%s %s/%s' % (seqno, action, protocol, srcaddr,
                                          srcprefixlen, dstaddr, dstprefixlen)
        if log:
            entry += ' log'
        cmds.append(entry)
        cmds.append('exit')
        return self.configure(cmds)

    def add_entry(self, name, action, protocol, srcaddr, srcprefixlen,
                  dstaddr, dstprefixlen, log=False, seqno=None):
        cmds = ['ip access-list %s' % name]
        entry = '%s %s %s/%s %s/%s' % (action, protocol, srcaddr,
                                       srcprefixlen, dstaddr, dstprefixlen)
        if seqno is not None:
            entry = '%s %s' % (seqno, entry)
        if log:
            entry += ' log'
        cmds.append(entry)
        cmds.append('exit')
        return self.configure(cmds)

    def remove_entry(self, name, seqno):
        cmds = ['ip access-list %s' % name, 'no %s' % seqno, 'exit']
        return self.configure(cmds)


ACL_CLASS_MAP = {'standard': StandardAcls, 'extended': ExtendedAcls}


def instance(node):
    return Acls(node)
