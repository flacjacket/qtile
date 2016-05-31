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

from .command_node import CommandNode


class Screen(CommandNode):
    """A physical screen, and its associated paraphernalia.

    Define a screen with a given set of Bars and Gaps.  Note that bar.Bar
    objects can only be placed at the top or the bottom of the screen (bar.Gap
    objects can be placed anywhere).  Also, ``x``, ``y``, ``width``, and
    ``height`` aren't specified usually unless you are using 'fake screens'.

    Parameters
    ----------

    top: List of Gap/Bar objects, or None.
    bottom: List of Gap/Bar objects, or None.
    left: List of Gap/Bar objects, or None.
    right: List of Gap/Bar objects, or None.
    x : int or None
    y : int or None
    width : int or None
    height : int or None
    """

    children_names = ["bars", "groups"]

    def __init__(self, top=None, bottom=None, left=None, right=None,
                 x=None, y=None, width=None, height=None):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

        # x position of upper left corner can be > 0
        # if one screen is "right" of the other
        self.x = x
        self.y = y
        self.width = width
        self.height = height
