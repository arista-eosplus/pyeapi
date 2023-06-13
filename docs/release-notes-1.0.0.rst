Release 1.0.0
-------------

2023-06-06

- This is a Python3 (3.7 onwards) release only (Python2 is no longer supported)
- Arista EOS 4.22 or later required (for on-box use cases only)

New Modules
^^^^^^^^^^^

Enhancements
^^^^^^^^^^^^

Fixed
^^^^^

* Let ``config`` method to raise ``ConnectionError`` exception (`198 <https://github.com/arista-eosplus/pyeapi/issues/198>`_)
    The fix ensures that the behavior is consistent with other methods.
* Fixed parsing of VLAN groupings by ``vlans.getall()`` (`200 <https://github.com/arista-eosplus/pyeapi/pull/200>`_)
    The fix allows handling a case when multiple VLANs in the configs may be grouped under a common (group) name.
* Enhanced ``vlans.get()`` to return an actual list of VLANs (`202 <https://github.com/arista-eosplus/pyeapi/pull/202>`_)
    The method used to return the argument itself (e.g., an RE: ``200-.*``), now the actual list of matched VLANs is returned
* Fixed a corner crash in ``portsVlans.getall()``  (`213 <https://github.com/arista-eosplus/pyeapi/issues/213>`_)
    The crash may occur when the switchport is configured with a VLAN profile 
* Improved ``switchports.getall()`` behavior (`216 <https://github.com/arista-eosplus/pyeapi/pull/216>`_)
    The method will not consider subinterfaces anymore
* Improved JSON parsing speed (`166 <https://github.com/arista-eosplus/pyeapi/pull/166>`_)
    User may improve the speed by using ``ujson`` or ``rapidjson`` modules. The standard ``json`` is used as a fallback.
* Allow user to specify an SSL context (`234 <https://github.com/arista-eosplus/pyeapi/issues/234>`_)
    Provided the argument option ``context`` to specify an SSL context in ``connection()`` method.
* Fixed user password vulnerability in tracebacks (`238 <https://github.com/arista-eosplus/pyeapi/pull/238>`_)
    A user password is exposed in a traceback, which could occur due to invalid credentials.
* Added support for login password exclusively for ssh-key authentication (`227 <https://github.com/arista-eosplus/pyeapi/pull/227>`_)
    Catching up with EOS CLI which already supports such login password.
* Fixed user password vulnerability in debugs (`242 <https://github.com/arista-eosplus/pyeapi/pull/242>`_)
    A user password was exposed in user enabled debugs. With this commit the user password is masked out now.
* Added option not to include config defaults (`221 <https://github.com/arista-eosplus/pyeapi/pull/221>`_)
    Reading running-config or startup-config with default values is not always a desirable behavior. This commit adds an option to control such behavior.
* Fixed a corner crash in ``ipinterfaces`` module (`210 <https://github.com/arista-eosplus/pyeapi/issues/210>`_)
    Fixed a crash when MTU value is not present in the interface configuration (this is rather a corner case condition).
* Fixed a bug where vxlan floodlist might return a bogus data (`193 <https://github.com/arista-eosplus/pyeapi/issues/193>`_)
    Fixed the issue with ``interfaces`` module, where ``get()`` method returned vxlan data structure with ``flood_list`` parsed incorrectly.  
* Improved performance of config parsing (`220 <https://github.com/arista-eosplus/pyeapi/pull/220>`_)
    Drastically improved perfromance of config parsing by cacheing section splitting results. This fix also tightens the prior relaxed section match behavior by allowing matching only section line (as vs entire section's content)     
* Enhanced PR (`220 <https://github.com/arista-eosplus/pyeapi/pull/220>`_) allowing to match sub-sections (`245 <https://github.com/arista-eosplus/pyeapi/pull/245>`_)
    After PR #220, matching subsections was impossible (only entire section could have been matched). This enhancement brings back such functionality.     
* Added support for a session based authentication (`203 <https://github.com/arista-eosplus/pyeapi/pull/203>`_)
    Added a couple new transport options (``http_session`` and ``https_session``) to ``connect()`` method to support a session based authentication.     
* Added support infrastructure to handle deprecated EOS CLI (`247 <https://github.com/arista-eosplus/pyeapi/pull/247>`_)
    The added ``CliVariants`` class helps managing transitions from deprecated EOS CLI (by allowing specifying both, new and deprecated CLI variants).
* Added support for parsing secondary ip addresses (`251 <https://github.com/arista-eosplus/pyeapi/pull/251>`_)
    The added fix extends the return result for ``get()`` method of ``ipinterfaces`` module with the parsed secondary ip addresses (if present).
* A minor fix to include internal exception handling (`252 <https://github.com/arista-eosplus/pyeapi/pull/252>`_)
    With this fix the ``pyeapi.eapilib.CommandError`` exception will elaborate on the causes of internal errors.
* Enhance parsing of BGP router section with ``asdot`` notation (`256 <https://github.com/arista-eosplus/pyeapi/pull/256>`_)
    Allow matching and parsing ``router bgp`` sections if spelled with ``asdot`` notation.
* removed and updated deprecations (`204 <https://github.com/arista-eosplus/pyeapi/pull/204>`_, `212 <https://github.com/arista-eosplus/pyeapi/pull/212>`_, `235 <https://github.com/arista-eosplus/pyeapi/pull/235>`_, `260 <https://github.com/arista-eosplus/pyeapi/pull/260>`_, `262 <https://github.com/arista-eosplus/pyeapi/pull/262>`_, `263 <https://github.com/arista-eosplus/pyeapi/pull/263>`_)
* documentation fixes and updates (`209 <https://github.com/arista-eosplus/pyeapi/pull/209>`_, `225 <https://github.com/arista-eosplus/pyeapi/pull/225>`_, `239 <https://github.com/arista-eosplus/pyeapi/pull/239>`_, `257 <https://github.com/arista-eosplus/pyeapi/pull/257>`_, `259 <https://github.com/arista-eosplus/pyeapi/pull/259>`_)

Known Caveats
^^^^^^^^^^^^^


