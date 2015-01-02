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
import re
from collections import namedtuple

SECTION_START_RE = re.compile(r'^[a-z!]')

ConfigLine = namedtuple('ConfigLine', "linenum text")

class Config(object):

    def __init__(self, text):
        self._text = text
        self._objs = self.parse()

    @property
    def text(self):
        return self._text

    def _find(self, regex):
        regex = re.compile(regex)
        return [obj[0] for obj in self._objs if regex.search(obj[0].text)]

    def _get_children(self, parent):
        return [obj[0] for obj in self._objs if obj[1] == parent]

    def _get_parent(self, linespec):
        regex = re.compile(r'^%s' % linespec)
        return [obj[0] for obj in self._objs if regex.match(obj[0].text)]

    def get_block(self, linespec):
        block = list()
        for parent in self._get_parent(linespec):
            block.append(parent.text)
            block.extend([child.text for child in self._get_children(parent)])
            block.append('!')
        return '\n'.join(block)

    def find(self, regex):
        match = re.search(regex, self.text, re.M)
        if match:
            return match.group()

    def findall(self, regex):
        return [obj.text for obj in self._find(regex)]

    def parse(self, block_delimiter=3):
        parsed = list()
        parents = dict()

        for linenum, token in enumerate(self.text.strip().split('\n')):
            offset = len(re.match(r'\s*', token).group())
            config = ConfigLine(linenum, token)

            if offset == 0:
                parent = None
                parents[0] = config

            else:
                offset_parent = parents.get(offset)
                if offset_parent != config:
                    parents[offset] = config
                offset -= block_delimiter
                parent = parents[offset]

            parsed.append((config, parent))

        return parsed

