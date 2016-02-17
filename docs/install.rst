.. _install:

############
Installation
############

The installation of pyeapi is straightforward and simple. As mentioned in the
:ref:`intro`, pyeapi can be run on-box or off-box. The instructions below
will provide some tips to help you for either platform.

.. contents::
  :depth: 3

***********************
Pip with Network Access
***********************

If your platform has internet access you can use the Python Package manager
to install pyeapi

.. code-block:: console

  admin:~ admin$ sudo pip install pyeapi

.. Note:: You will likely notice Pip install netaddr, a dependency of pyeapi.


Pip - Upgrade Pyeapi
====================

.. code-block:: console

  admin:~ admin$ sudo pip install --upgrade pyeapi


**************************
Pip without Network Access
**************************

If you want to install pyeapi on a switch with no internet access:

**Step 1:** Download Pypi Package

- `Download <https://pypi.python.org/pypi/pyeapi>`_ the latest version of **pyeapi** on your local machine.
- You will also need a dependency package `netaddr <https://pypi.python.org/pypi/netaddr>`_.

**Step 2:** SCP both files to the Arista switch and install

.. code-block:: console

  admin:~ admin$ scp path/to/pyeapi-<VERSION>.tar.gz ansible@veos01:/mnt/flash/
  admin:~ admin$ scp path/to/netaddr-<VERSION>.tar.gz ansible@veos01:/mnt/flash/

Then SSH into your node and install it. Be sure to replace ``<VERSION>`` with the
actual filename:

.. code-block:: console

  [admin@veos ~]$ sudo pip install /mnt/flash/netaddr-<VERSION>.tar.gz
  [admin@veos ~]$ sudo pip install /mnt/flash/pyeapi-<VERSION>.tar.gz

These packages must be re-installed on reboot. Therefore, add the install
commands to ``/mnt/flash/rc.eos`` to trigger the install on reboot:

.. code-block:: console

  [admin@veos ~]$ vi /mnt/flash/rc.eos

Add the lines (the #! may already exist in your rc.eos)

.. code-block:: console

  #!/bin/bash
  sudo pip install /mnt/flash/netaddr-<VERSION>.tar.gz
  sudo pip install /mnt/flash/pyeapi-<VERSION>.tar.gz


************************************
Development - Run pyeapi from Source
************************************

.. Tip:: We recommend running pyeapi in a virtual environment. For more
         information, `read this. <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_

These instructions will help you install and run pyeapi from source. This
is useful if you plan on contributing or if you'd always like to see the latest
code in the develop branch.

.. Important:: These steps require Pip and Git

**Step 1:** Clone the pyeapi Github repo

.. code-block:: shell

  # Go to a directory where you'd like to keep the source
  admin:~ admin$ cd ~/projects
  admin:~ admin$ git clone https://github.com/arista-eosplus/pyeapi.git
  admin:~ admin$ cd pyeapi

**Step 2:** Check out the desired version or branch

.. code-block:: shell

  # Go to a directory where you'd like to keep the source
  admin:~ admin$ cd ~/projects/pyeapi

  # To see a list of available versions or branches
  admin:~ admin$ git tag
  admin:~ admin$ git branch

  # Checkout the desired version of code
  admin:~ admin$ git checkout v0.3.3

**Step 3:** Install pyeapi using Pip with -e switch

.. code-block:: shell

  # Go to a directory where you'd like to keep the source
  admin:~ admin$ cd ~/projects/pyeapi

  # Install
  admin:~ admin$ sudo pip install -e ~/projects/pyeapi

**Step 4:** Install pyeapi requirements

.. code-block:: shell

  # Go to a directory where you'd like to keep the source
  admin:~ admin$ pip install -r dev-requirements.txt

.. Tip:: If you start using pyeapi and get import errors, make sure your
         PYTHONPATH is set to include the path to pyeapi.


Development - Upgrade Pyeapi
============================

 .. code-block:: shell

   admin:~ admin$ cd ~/projects/pyeapi
   admin:~ admin$ git pull

.. Note:: If you followed the directions above and used ``pip install -e``,
          pip will automatically use the updated code.
