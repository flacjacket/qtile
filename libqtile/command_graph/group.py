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

from six import MAXSIZE

from libqtile import utils
from .command_node import CommandNode


class Group(CommandNode):
    """Represents a "dynamic" group

    These groups can spawn apps, only allow certain Matched windows to be on
    them, hide when they're not in use, etc.

    Parameters
    ----------

    name : string
        the name of this group
    matches : default ``None``
        list of ``Match`` objects whose  windows will be assigned to this group
    exclusive : boolean
        when other apps are started in this group, should we allow them here or
        not?
    spawn : string or list of strings
        this will be ``exec()`` d when the group is created, you can pass
        either a program name or a list of programs to ``exec()``
    layout : string
        the default layout for this group (e.g. 'max' or 'stack')
    layouts : list
        the group layouts list overriding global layouts
    persist : boolean
        should this group stay alive with no member windows?
    init : boolean
        is this group alive when qtile starts?
    position : int
        group position
    """
    parent_name = "screen"
    children_names = "layouts", "windows"]

    def __init__(self, name, layout=None, layouts=None, layout_opts=None,
                 matches=None, exclusive=False, spawn=None, persist=True, init=True,
                 screen_affinity=None, position=MAXSIZE):
        CommandNode.__init__(self, parent=None, windows=[], layouts=layouts)

        self.name = name
        self.layout = layout
        self.layout_opts = layout_opts
        self.matches = matches
        self.exclusive = exclusize
        self.spawn = spawn
        self.persist = persist
        self.init = init
        self.screen_affinity = screen_affinity
        self.position = position

    def __repr__(self):
        attrs = utils.describe_attributes(self, [
            "layout", "layout_opts", "matches", "exclusive", "spawn",
            "persist", "init", "screen_affinity", "position"
        ]
        return "{cls}({name}, {kwargs})".format(self.__class__.__name__, self.name, attrs)
