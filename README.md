# Arista eAPI Python Library

[![Build Status](https://travis-ci.org/arista-eosplus/pyeapi.svg?branch=develop)](https://travis-ci.org/arista-eosplus/pyeapi) [![Coverage Status](https://coveralls.io/repos/github/arista-eosplus/pyeapi/badge.svg?branch=develop)](https://coveralls.io/github/arista-eosplus/pyeapi?branch=develop) [![Documentation Status](https://readthedocs.org/projects/pyeapi/badge/?version=latest)](http://readthedocs.org/docs/pyeapi/en/latest/?badge=latest)

The Python library for Arista's eAPI command API implementation provides a
client API work using eAPI and communicating with EOS nodes.  The Python
library can be used to communicate with EOS either locally (on-box) or remotely
(off-box).  It uses a standard INI-style configuration file to specify one or
more nodes and connection properties.

The pyeapi library also provides an API layer for building native Python
objects to interact with the destination nodes. The API layer is a convenient
implementation for working with the EOS configuration and is extensible for
developing custom implementations.

This library is freely provided to the open source community for building
robust applications using Arista EOS.  Support is provided as best effort
through Github issues.

## Documentation

* [Quickstart] [quickstart]
* [Installation] [install]
* [Modules] [modules]
* [Release Notes] [rns]
* [Contribute] [contribute]

### Building Local Documentation

If you cannot access readthedocs.org you have the option of building the
documentation locally.

1. ``pip install -r dev-requirements.txt``
2. ``cd docs``
3. ``make html``
4. ``open _build/html/index.html``

# License

Copyright (c) 2015, Arista Networks EOS+
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the Arista nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


[pyeapi]: https://github.com/arista-eosplus/pyeapi
[quickstart]: http://pyeapi.readthedocs.org/en/master/quickstart.html
[install]: http://pyeapi.readthedocs.org/en/master/install.html
[contribute]: http://pyeapi.readthedocs.org/en/master/contribute.html
[modules]: http://pyeapi.readthedocs.org/en/master/modules.html
[support]: http://pyeapi.readthedocs.org/en/master/support.html
[rns]: http://pyeapi.readthedocs.org/en/master/release-notes.html
