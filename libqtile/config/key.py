# Copyright (c) 2012-2015 Tycho Andersen
# Copyright (c) 2013 xarvh
# Copyright (c) 2013 horsik
# Copyright (c) 2013-2014 roger
# Copyright (c) 2013 Tao Sauvage
# Copyright (c) 2014 ramnes
# Copyright (c) 2014 Sean Vig
# Copyright (c) 2014 Adi Sieker
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from . import command
from . import hook
from . import utils

from six import MAXSIZE
import warnings


class Key(object):
    """Defines a keybinding.

    Parameters
    ==========
    modifiers:
        A list of modifier specifications. Modifier specifications are one of:
        "shift", "lock", "control", "mod1", "mod2", "mod3", "mod4", "mod5".
    key:
        A key specification, e.g. "a", "Tab", "Return", "space".
    commands:
        A list of lazy command objects generated with the command.lazy helper.
        If multiple Call objects are specified, they are run in sequence.
    kwds:
        A dictionary containing "desc", allowing a description to be added
    """
    def __init__(self, modifiers, key, *commands, **kwds):
        self.modifiers = modifiers
        self.key = key
        self.commands = commands
        self.desc = kwds.get("desc", "")
        try:
            self.modmask = utils.translate_masks(self.modifiers)
        except KeyError as v:
            raise utils.QtileError(v)

    def __repr__(self):
        return "<Key (%s, %s)>" % (self.modifiers, self.key)
