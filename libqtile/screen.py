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


class Screen(command.CommandObject):
    """A physical screen, and its associated paraphernalia.

    Define a screen with a given set of Bars of a specific geometry.  Note that
    bar.Bar objects can only be placed at the top or the bottom of the screen
    (bar.Gap objects can be placed anywhere).  Also, ``x``, ``y``, ``width``,
    and ``height`` aren't specified usually unless you are using 'fake
    screens'.

    Parameters
    ==========
    top: List of Gap/Bar objects, or None.
    bottom: List of Gap/Bar objects, or None.
    left: List of Gap/Bar objects, or None.
    right: List of Gap/Bar objects, or None.
    x : int or None
    y : int or None
    width : int or None
    height : int or None
    """
    def __init__(self, top=None, bottom=None, left=None, right=None,
                 x=None, y=None, width=None, height=None):
        self.group = None
        self.previous_group = None

        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
        self.qtile = None
        self.index = None
        # x position of upper left corner can be > 0
        # if one screen is "right" of the other
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def _configure(self, qtile, index, x, y, width, height, group):
        self.qtile = qtile
        self.index = index
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.setGroup(group)
        for i in self.gaps:
            i._configure(qtile, self)

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

    def get_rect(self):
        return ScreenRect(self.dx, self.dy, self.dwidth, self.dheight)

    def setGroup(self, new_group, save_prev=True):
        """Put group on this screen"""
        if new_group.screen == self:
            return

        if save_prev:
            self.previous_group = self.group

        if new_group is None:
            return

        if new_group.screen:
            # g1 <-> s1 (self)
            # g2 (new_group) <-> s2 to
            # g1 <-> s2
            # g2 <-> s1
            g1 = self.group
            s1 = self
            g2 = new_group
            s2 = new_group.screen

            s2.group = g1
            g1._setScreen(s2)
            s1.group = g2
            g2._setScreen(s1)
        else:
            old_group = self.group
            self.group = new_group

            # display clients of the new group and then hide from old group
            # to remove the screen flickering
            new_group._setScreen(self)

            if old_group is not None:
                old_group._setScreen(None)

        hook.fire("setgroup")
        hook.fire("focus_change")
        hook.fire(
            "layout_change",
            self.group.layouts[self.group.currentLayout],
            self.group
        )

    def _items(self, name):
        if name == "layout":
            return (True, list(range(len(self.group.layouts))))
        elif name == "window":
            return (True, [i.window.wid for i in self.group.windows])
        elif name == "bar":
            return (False, [x.position for x in self.gaps])

    def _select(self, name, sel):
        if name == "layout":
            if sel is None:
                return self.group.layout
            else:
                return utils.lget(self.group.layouts, sel)
        elif name == "window":
            if sel is None:
                return self.group.currentWindow
            else:
                for i in self.group.windows:
                    if i.window.wid == sel:
                        return i
        elif name == "bar":
            return getattr(self, sel)

    def resize(self, x=None, y=None, w=None, h=None):
        x = x or self.x
        y = y or self.y
        w = w or self.width
        h = h or self.height
        self._configure(self.qtile, self.index, x, y, w, h, self.group)
        for bar in [self.top, self.bottom, self.left, self.right]:
            if bar:
                bar.draw()
        self.qtile.call_soon(self.group.layoutAll())

    def cmd_info(self):
        """
            Returns a dictionary of info for this screen.
        """
        return dict(
            index=self.index,
            width=self.width,
            height=self.height,
            x=self.x,
            y=self.y
        )

    def cmd_resize(self, x=None, y=None, w=None, h=None):
        """Resize the screen"""
        self.resize(x, y, w, h)

    def cmd_next_group(self, skip_empty=False, skip_managed=False):
        """Switch to the next group"""
        n = self.group.nextGroup(skip_empty, skip_managed)
        self.setGroup(n)
        return n.name

    def cmd_prev_group(self, skip_empty=False, skip_managed=False):
        """Switch to the previous group"""
        n = self.group.prevGroup(skip_empty, skip_managed)
        self.setGroup(n)
        return n.name

    def cmd_toggle_group(self, group_name=None):
        """Switch to the selected group or to the previously active one"""
        group = self.qtile.groupMap.get(group_name)
        if group in (self.group, None):
            group = self.previous_group
        self.setGroup(group)

    def cmd_togglegroup(self, groupName=None):
        """Switch to the selected group or to the previously active one

        Deprecated: use toggle_group()"""
        warnings.warn("togglegroup is deprecated, use toggle_group", DeprecationWarning)
        self.cmd_toggle_group(groupName)
