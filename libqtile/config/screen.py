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

from . import command
from . import hook
from . import utils

from six import MAXSIZE
import warnings


class ScreenRect(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __repr__(self):
        return '<%s %d,%d %d,%d>' % (
            self.__class__.__name__,
            self.x, self.y,
            self.width, self.height
        )

    def hsplit(self, columnwidth):
        assert columnwidth > 0
        assert columnwidth < self.width
        return (
            self.__class__(self.x, self.y, columnwidth, self.height),
            self.__class__(
                self.x + columnwidth, self.y,
                self.width - columnwidth, self.height
            )
        )

    def vsplit(self, rowheight):
        assert rowheight > 0
        assert rowheight < self.height
        return (
            self.__class__(self.x, self.y, self.width, rowheight),
            self.__class__(
                self.x, self.y + rowheight,
                self.width, self.height - rowheight
            )
        )


class Screen(object):
    """A physical screen, and its associated paraphernalia.

    Define a screen with a given set of Bars of a specific geometry.  Note that
    bar.Bar objects can only be placed at the top or the bottom of the screen
    (bar.Gap objects can be placed anywhere).  Also, ``x``, ``y``, ``width``,
    and ``height`` aren't specified usually unless you are using 'fake
    screens'.

    Parameters
    ==========
    top: Gap, Bar object, or None.
    bottom: Gap, Bar, or None.
    left: Gap, Bar, or None.
    right: Gap, Bar, or None.
    x : int or None
    y : int or None
    width : int or None
    height : int or None
    """
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

    @property
    def gaps(self):
        return (i for i in [self.top, self.bottom, self.left, self.right] if i)

    @property
    def dx(self):
        return self.x + self.left.size if self.left else self.x

    @property
    def dy(self):
        return self.y + self.top.size if self.top else self.y

    @property
    def dwidth(self):
        val = self.width
        if self.left:
            val -= self.left.size
        if self.right:
            val -= self.right.size
        return val

    @property
    def dheight(self):
        val = self.height
        if self.top:
            val -= self.top.size
        if self.bottom:
            val -= self.bottom.size
        return val

    def resize(self, x=None, y=None, w=None, h=None):
        x = x or self.x
        y = y or self.y
        w = w or self.width
        h = h or self.height
        for bar in [self.top, self.bottom, self.left, self.right]:
            if bar:
                bar.draw()
        self.qtile.call_soon(self.group.layoutAll())
