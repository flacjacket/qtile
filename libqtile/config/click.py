# Copyright (c) 2016 Sean Vig
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


class Click(object):
    """Defines binding of a mouse click

    It focuses clicked window by default.  If you want to prevent it, pass
    `focus=None` as an argument
    """
    def __init__(self, modifiers, button, *commands, **kwargs):
        self.focus = kwargs.get("focus", "before")
        self.modifiers = modifiers
        self.button = button
        self.commands = commands
        try:
            self.button_code = int(self.button.replace('Button', ''))
            self.modmask = utils.translate_masks(self.modifiers)
        except KeyError as v:
            raise utils.QtileError(v)

    def __repr__(self):
        return "<Click (%s, %s)>" % (self.modifiers, self.button)
