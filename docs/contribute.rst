
##########
Contribute
##########

The Arista EOS+ team is happy to accept community contributions to the Pyeapi
project. Please note that all contributions that modify the library behavior
require corresponding test cases otherwise the pull request will be rejected.


*******
Testing
*******

The pyeapi library provides both unit tests and system tests.  The unit tests
can be run without an EOS node.  To run the system tests, you will need to
update the ``dut.conf`` file found in test/fixtures.


Unit Test
=========

To run the unit tests, simply run ``make unittest`` from the root of the
pyeapi source folder

System Test
===========

To run the system tests, simply run ``make systest`` from the root of the
pyeapi source folder.

.. Tip:: To run all tests, use ``make tests`` from the root of the pyeapi source
  folder

********
Coverage
********

Contributions should maintain 100% code coverage. You can check this locally
before submitting your Pull Request.

1. Run ``make unittest``
2. Run ``make coverage_report`` to confirm code coverage.
