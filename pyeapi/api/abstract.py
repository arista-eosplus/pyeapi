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
"""Provides an abstract implementation for building API modules

This module provides a set of classes that are used to build API modules
that work with Node objects.  Using this module will allow the API
modules to be automatically loaded using the Node.api method.

The classes in this module should not be instantiated directly but rather
provide parent class for API implementations.  All API modules will
ultimately derive from BaseEntity which provides some common functions to
make building API modules easier.
"""

from collections.abc import Callable, Mapping
from pyeapi.eapilib import CommandError
from pyeapi.utils import make_iterable


class BaseEntity(object):
    """Base class for all resources to derive from

    This BaseEntity class should not be directly instatiated.  It is
    designed to be implemented by all resource classes to provide common
    methods.

    Attributes:
        node (Node): The node instance this resource will perform operations
            against for configuration
        config (Config): Returns an instance of Config with the nodes
            current running configuration
        error (CommandError): Holds the latest CommandError exception
            instance if raised

    Args:
        node (Node): An instance of Node
    """
    def __init__(self, node):
        self.node = node

    @property
    def version_number(self):
        return self.node.version_number

    @property
    def config(self):
        return self.node.running_config

    @property
    def error(self):
        return self.node.connection.error

    def get_block(self, parent, config='running_config'):
        """ Scans the config and returns a block of code

        Args:
            parent (str): The parent string to search the config for and
                return the block
            config (str): A text config string to be searched. Default
                is to search the running-config of the Node.

        Returns:
            A string object that represents the block from the config.  If
            the parent string is not found, then this method will
            return None.

        """
        try:
            parent = r'^%s$' % parent
            return self.node.section(parent, config=config)
        except TypeError:
            return None

    def configure(self, commands):
        """Sends the commands list to the node in config mode

        This method performs configuration the node using the array of
        commands specified.   This method wraps the configuration commands
        in a try/except block and stores any exceptions in the error
        property.

        Note:
            If the return from this method is False, use the error property
            to investigate the exception

        Args:
            commands (list): A list of commands to be sent to the node in
                config mode

        Returns:
            True if the commands are executed without exception otherwise
                False is returned
        """
        try:
            self.node.config(commands)
            return True
        except (CommandError):
            return False

    def command_builder(self, string, value=None, default=None, disable=None):
        """Builds a command with keywords

        Notes:
            Negating a command string by overriding 'value' with None or an
                assigned value that evalutates to false has been deprecated.
                Please use 'disable' to negate a command.

            Parameters are evaluated in the order 'default', 'disable', 'value'

        Args:
            string (str): The command string
            value (str): The configuration setting to subsititue into the
                command string. If value is a boolean and True, just the
                command string is used
            default (bool): Specifies the command should use the default
                keyword argument. Default preempts disable and value.
            disable (bool): Specifies the command should use the no
                keyword argument. Disable preempts value.

        Returns:
            A command string that can be used to configure the node
        """
        if default:
            return 'default %s' % string
        elif disable:
            return 'no %s' % string
        elif value is True:
            return string
        elif value:
            return '%s %s' % (string, value)
        else:
            return 'no %s' % string
            # -- above line to be deprecated and replaced with the error below
            # raise ValueError("abstract.command_builder: No value "
            #                  "received '%s'" % value)

    def configure_interface(self, name, commands):
        """Configures the specified interface with the commands

        Args:
            name (str): The interface name to configure
            commands: The commands to configure in the interface

        Returns:
            True if the commands completed successfully
        """
        commands = make_iterable(commands)
        commands.insert(0, 'interface %s' % name)
        return self.configure(commands)


class Entity(BaseEntity, Callable):
    """Abstract class for building Entity resources

    The Entity class provides an abstract implementation that allows for
    building an API configuration resource.  The Entity class should not
    be directly instantiated.  It is used in instances where a single config
    entity is appropriate in the configuration.

    Examples of Entity candidates include global spanning tree
    """
    def __call__(self):
        return self.get()

    def get(self):
        raise NotImplementedError


class EntityCollection(BaseEntity, Mapping):
    """Abstract class for building EntityCollection resources

    The EntityCollection class provides an abstract implementat that allows
    for building API configuration resources with multiple resources.  The
    EntityCollection class should not be directly instantiated.

    Examples of an EntityCollection candidate include VLANs and interfaces
    """

    def __call__(self):
        return self.getall()

    def __getitem__(self, value):
        return self.get(value)

    def __len__(self):
        return len(self.getall())

    def __iter__(self):
        return iter(self.getall())

    def getall(self):
        raise NotImplementedError

    def get(self, name, default=None):
        raise NotImplementedError
