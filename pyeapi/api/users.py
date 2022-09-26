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
"""API Module for working with EOS local user resources

The Users resource provides configuration of local user resources for
an EOS node.

Parameters:

    username (string): The username parameter maps to the local username
        defined in the running-config.
    nopassword (boolean): Configures the username to use no password at login.
        This parameter is mutually exclusive with secret
    privilege (integer): Configures the user privilege level in EOS
    role (string): Configures the users role in EOS
    secret (string): Configures the users secret (password) to use at login.
        This parameter is mutually exclusive with secret and is used in
        conjunction with format.
    format (string): Configures the format of the secret value.  Accepted
        values for format are "cleartext", "md5", "nologin" and "sha512"

"""

import re

from pyeapi.api import EntityCollection

DEFAULT_ENCRYPTION = 'cleartext'
ENCRYPTION_MAP = {'cleartext': 0, 'md5': 5, 'sha512': 'sha512', 'nologin': '*'}


def isprivilege(value):
    """Checks value for valid privilege level

    Args:
        value (str, int): Checks if value is a valid user privilege

    Returns:
        True if the value is valid, otherwise False
    """
    try:
        value = int(value)
        return 0 <= value < 16
    except ValueError:
        return False


class Users(EntityCollection):
    """The Users class provides a configuration resource for local users.
    The regex used here parses the running configuration to find username
    entries. There is extra logic in the regular expression to store
    the username as 'user' and then creates a backreference to find a
    following configuration line that might contain the users sshkey.
    """

    def get(self, name):
        """Returns the local user configuration as a resource dict

        Args:
            name (str): The username to return from the nodes global running-
                config.

        Returns:
            dict: A resource dict object

            If the `name` does not exist, then None is returned
        """
        return self.getall().get(name)

    def getall(self):
        """Returns all local users configuration as a resource dict

        Returns:
            dict: A dict of usernames with a nested resource dict object
        """
        if self.version_number >= '4.23':
            self.users_re = re.compile(r'username (?P<user>[^\s]+) '
                                       r'privilege (\d+)'
                                       r'(?: role ([^\s]+))?'
                                       r'(?: (nopassword))?'
                                       r'(?: secret (0|5|7|sha512) (.+))?'
                                       r'.*$\n(?:username (?P=user) '
                                       r'ssh.key (.+)$)?', re.M)
        else:
            self.users_re = re.compile(r'username (?P<user>[^\s]+) '
                                       r'privilege (\d+)'
                                       r'(?: role ([^\s]+))?'
                                       r'(?: (nopassword))?'
                                       r'(?: secret (0|5|7|sha512) (.+))?'
                                       r'.*$\n(?:username (?P=user) '
                                       r'sshkey (.+)$)?', re.M)

        users = self.users_re.findall(self.config, re.M)
        resources = dict()
        for user in users:
            resources.update(self._parse_username(user))
        return resources

    def _parse_username(self, config):
        """Scans the config block and returns the username as a dict

        Args:
            config (str): The config block to parse

        Returns:
            dict: A resource dict that is intended to be merged into the
                user resource
        """
        (username, priv, role, nopass, fmt, secret, sshkey) = config
        resource = dict()
        resource['privilege'] = priv
        resource['role'] = role
        resource['nopassword'] = nopass == 'nopassword'
        resource['format'] = fmt
        resource['secret'] = secret
        if self.version_number >= '4.23':
            resource['ssh-key'] = sshkey
        else:
            resource['sshkey'] = sshkey
        return {username: resource}

    def create(self, name, nopassword=None, secret=None, encryption=None):
        """Creates a new user on the local system.

        Creating users requires either a secret (password) or the nopassword
        keyword to be specified.

        Args:
            name (str): The name of the user to craete

            nopassword (bool): Configures the user to be able to authenticate
                without a password challenage

            secret (str): The secret (password) to assign to this user

            encryption (str): Specifies how the secret is encoded.  Valid
                values are "cleartext", "md5", "nologin", "sha512".
                The default is "cleartext"

        Returns:
            True if the operation was successful otherwise False

        Raises:
            TypeError: if the required arguments are not satisfied
        """
        if secret is not None or encryption == 'nologin':
            return self.create_with_secret(name, secret, encryption)
        elif nopassword is True:
            return self.create_with_nopassword(name)
        else:
            raise TypeError('either "nopassword" or "secret" must be '
                            'specified to create a user')

    def create_with_secret(self, name, secret, encryption):
        """Creates a new user on the local node

        Args:
            name (str): The name of the user to craete

            secret (str): The secret (password) to assign to this user

            encryption (str): Specifies how the secret is encoded.  Valid
                values are "cleartext", "md5", "nologin" and "sha512".
                The default is "cleartext"

        Returns:
            True if the operation was successful otherwise False
        """
        try:
            encryption = encryption or DEFAULT_ENCRYPTION
            enc = ENCRYPTION_MAP[encryption]
        except KeyError:
            raise TypeError('encryption must be one of "cleartext", "md5"'
                            ' "nologin" or "sha512"')

        cmd = 'username %s secret %s %s' % (name, enc, secret)
        if encryption == 'nologin':
            cmd = 'username %s secret %s' % (name, enc)
        return self.configure(cmd)

    def create_with_nopassword(self, name):
        """Creates a new user on the local node

        Args:
            name (str): The name of the user to create

        Returns:
            True if the operation was successful otherwise False
        """
        return self.configure('username %s nopassword' % name)

    def delete(self, name):
        """Deletes the local username from the config

        Args:
            name (str): The name of the user to delete

        Returns:
            True if the operation was successful otherwise False
        """
        if name == 'admin':
            raise TypeError('the admin user cannot be deleted.')

        return self.configure('no username %s' % name)

    def default(self, name):
        """Configures the local username using the default keyword

        Args:
            name (str): The name of the user to configure

        Returns:
            True if the operation was successful otherwise False
        """
        return self.configure('default username %s' % name)

    def set_privilege(self, name, value=None):
        """Configures the user privilege value in EOS

        Args:
            name (str): The name of the user to craete

            value (int): The privilege value to assign to the user.  Valid
                values are in the range of 0 to 15

        Returns:
            True if the operation was successful otherwise False

        Raises:
            TypeError: if the value is not in the valid range
        """
        cmd = 'username %s' % name
        if value is not None:
            if not isprivilege(value):
                raise TypeError('priviledge value must be between 0 and 15')
            cmd += ' privilege %s' % value
        else:
            cmd += ' privilege 1'
        return self.configure(cmd)

    def set_role(self, name, value=None, default=False, disable=False):
        """Configures the user role vale in EOS

        Args:
            name (str): The name of the user to create

            value (str): The value to configure for the user role

            default (bool): Configure the user role using the EOS CLI
                default command

            disable (bool): Negate the user role using the EOS CLI no command

        Returns:
            True if the operation was successful otherwise False
        """
        cmd = self.command_builder('username %s role' % name, value=value,
                                   default=default, disable=disable)
        return self.configure(cmd)

    def set_sshkey(self, name, value=None, default=False, disable=False):
        """Configures the user sshkey

        Args:
            name (str): The name of the user to add the sshkey to

            value (str): The value to configure for the sshkey.

            default (bool): Configure the sshkey using the EOS CLI
                default command

            disable (bool): Negate the sshkey using the EOS CLI no command

        Returns:
            True if the operation was successful otherwise False
        """
        if self.version_number >= '4.23':
            cmd = self.command_builder('username %s ssh-key' % name,
                                       value=value,
                                       default=default, disable=disable)
        else:
            cmd = self.command_builder('username %s sshkey' % name,
                                       value=value,
                                       default=default, disable=disable)
        return self.configure(cmd)


def instance(node):
    """Returns an instance of Users

    This method will create and return an instance of the Users object passing
    the value of API to the object.  The instance method is required for the
    resource to be autoloaded by the Node object

    Args:
        node (Node): The node argument passes an instance of Node to the
            resource
    """
    return Users(node)
