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

from libqtile import utils

from .click import Click
from .drag import Drag
from .key import Key


class EzConfig(object):
    """
    Helper class for defining key and button bindings in an emacs-like format.
    Inspired by Xmonad's XMonad.Util.EZConfig.
    """

    modifier_keys = {
        'M': 'mod4',
        'A': 'mod1',
        'S': 'shift',
        'C': 'control',
    }

    def parse(self, spec):
        """
        Splits an emacs keydef into modifiers and keys. For example:
          "M-S-a"     -> ['mod4', 'shift'], 'a'
          "A-<minus>" -> ['mod1'], 'minus'
          "C-<Tab>"   -> ['control'], 'Tab'
        """
        mods = []
        keys = []

        for key in spec.split('-'):
            if not key:
                break
            if key in self.modifier_keys:
                if keys:
                    msg = 'Modifiers must always come before key/btn: %s'
                    raise utils.QtileError(msg % spec)
                mods.append(self.modifier_keys[key])
                continue
            if len(key) == 1:
                keys.append(key)
                continue
            if len(key) > 3 and key[0] == '<' and key[-1] == '>':
                keys.append(key[1:-1])
                continue

        if not keys:
            msg = 'Invalid key/btn specifier: %s'
            raise utils.QtileError(msg % spec)

        if len(keys) > 1:
            msg = 'Key chains are not supported: %s' % spec
            raise utils.QtileError(msg)

        return mods, keys[0]


class EzKey(EzConfig, Key):
    def __init__(self, keydef, *commands):
        modkeys, key = self.parse(keydef)
        super(EzKey, self).__init__(modkeys, key, *commands)


class EzClick(EzConfig, Click):
    def __init__(self, btndef, *commands, **kwargs):
        modkeys, button = self.parse(btndef)
        button = 'Button%s' % button
        super(EzClick, self).__init__(modkeys, button, *commands, **kwargs)


class EzDrag(EzConfig, Drag):
    def __init__(self, btndef, *commands, **kwargs):
        modkeys, button = self.parse(btndef)
        button = 'Button%s' % button
        super(EzDrag, self).__init__(modkeys, button, *commands, **kwargs)
