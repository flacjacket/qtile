# Copyright (c) 2008, Aldo Cortesi. All rights reserved.
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

import abc
import inspect
import traceback
import os
import six
import sys

from . import ipc
from .utils import get_cache_dir
from .log_utils import logger


class CommandError(Exception):
    pass


class CommandException(Exception):
    pass


class _SelectError(Exception):
    def __init__(self, name, sel):
        Exception.__init__(self)
        self.name = name
        self.sel = sel


SUCCESS = 0
ERROR = 1
EXCEPTION = 2

SOCKBASE = "qtilesocket.%s"


def formatSelector(lst):
    """
        Takes a list of (name, sel) tuples, and returns a formatted
        selector expression.
    """
    expr = []
    for name, sel in iter(lst):
        if expr:
            expr.append(".")
        expr.append(name)
        if sel is not None:
            expr.append("[%s]" % repr(sel))
    return "".join(expr)


class _Server(ipc.Server):
    def __init__(self, fname, qtile, conf, eventloop):
        if os.path.exists(fname):
            os.unlink(fname)
        ipc.Server.__init__(self, fname, self.call, eventloop)
        self.qtile = qtile
        self.widgets = {}
        for i in conf.screens:
            for j in i.gaps:
                if hasattr(j, "widgets"):
                    for w in j.widgets:
                        if w.name:
                            self.widgets[w.name] = w

    def call(self, data):
        selectors, name, args, kwargs = data
        try:
            obj = self.qtile.select(selectors)
        except _SelectError as v:
            e = formatSelector([(v.name, v.sel)])
            s = formatSelector(selectors)
            return (ERROR, "No object %s in path '%s'" % (e, s))
        cmd = obj.command(name)
        if not cmd:
            return (ERROR, "No such command.")
        logger.info("Command: %s(%s, %s)", name, args, kwargs)
        try:
            return (SUCCESS, cmd(*args, **kwargs))
        except CommandError as v:
            return (ERROR, v.args[0])
        except Exception as v:
            return (EXCEPTION, traceback.format_exc())


class _Command(object):
    def __init__(self, call, selectors, name):
        """
            :command A string command name specification
            :*args Arguments to be passed to the specified command
            :*kwargs Arguments to be passed to the specified command
        """
        self.selectors = selectors
        self.name = name
        self.call = call

    def __call__(self, *args, **kwargs):
        return self.call(self.selectors, self.name, *args, **kwargs)


class _CommandTree(six.with_metaclass(abc.ABCMeta)):
    """A hierarchical collection of objects that contain commands

    CommandTree objects act as containers, allowing them to be nested. The
    commands themselves appear on the object as callable attributes.
    """
    def __init__(self, selectors, myselector, parent):
        self.selectors = selectors
        self.myselector = myselector
        self.parent = parent

    @property
    def path(self):
        s = self.selectors[:]
        if self.name:
            s += [(self.name, self.myselector)]
        return formatSelector(s)

    @property
    @abc.abstractmethod
    def name(self):
        pass

    @property
    @abc.abstractmethod
    def _contains(self):
        pass

    def call(self, selectors, name, *args, **kwargs):
        if self.parent:
            return self.parent.call(selectors, name, *args, **kwargs)
        else:
            raise NotImplementedError()

    def __getitem__(self, select):
        if self.myselector:
            raise KeyError("No such key: %s" % select)
        return self.__class__(self.selectors, select, self)

    def __getattr__(self, name):
        nextSelector = self.selectors[:]
        if self.name:
            nextSelector.append((self.name, self.myselector))
        if name in self._contains:
            return _TreeMap[name](nextSelector, None, self)
        else:
            return _Command(self.call, nextSelector, name)


class _TLayout(_CommandTree):
    name = "layout"
    _contains = ["group", "window", "screen"]


class _TWidget(_CommandTree):
    name = "widget"
    _contains = ["bar", "screen", "group"]


class _TBar(_CommandTree):
    name = "bar"
    _contains = ["screen"]


class _TWindow(_CommandTree):
    name = "window"
    _contains = ["group", "screen", "layout"]


class _TScreen(_CommandTree):
    name = "screen"
    _contains = ["layout", "window", "bar"]


class _TGroup(_CommandTree):
    name = "group"
    _contains = ["layout", "window", "screen"]


_TreeMap = {
    "layout": _TLayout,
    "widget": _TWidget,
    "bar": _TBar,
    "window": _TWindow,
    "screen": _TScreen,
    "group": _TGroup,
}


class _CommandRoot(six.with_metaclass(abc.ABCMeta, _CommandTree)):
    """Root object of the command tree

    This class constructs the entire hierarchy of callable commands from a conf
    object
    """
    name = None
    _contains = ["layout", "widget", "screen", "bar", "window", "group"]

    def __init__(self):
        _CommandTree.__init__(self, [], None, None)

    def __getitem__(self, select):
        raise KeyError("No such key: %s" % select)

    @abc.abstractmethod
    def call(self, selectors, name, *args, **kwargs):
        """This method is called for issued commands.

        Parameters
        ==========
        selectors :
            A list of (name, selector) tuples.
        name :
            Command name.
        """
        pass


def find_sockfile(display=None):
    """
        Finds the appropriate socket file.
    """
    display = display or os.environ.get('DISPLAY') or ':0.0'
    if '.' not in display:
        display += '.0'
    cache_directory = get_cache_dir()
    return os.path.join(cache_directory, SOCKBASE % display)


class Client(_CommandRoot):
    """Exposes a command tree used to communicate with a running instance of Qtile"""
    def __init__(self, fname=None, is_json=False):
        if not fname:
            fname = find_sockfile()
        self.client = ipc.Client(fname, is_json)
        _CommandRoot.__init__(self)

    def call(self, selectors, name, *args, **kwargs):
        state, val = self.client.call((selectors, name, args, kwargs))
        if state == SUCCESS:
            return val
        elif state == ERROR:
            raise CommandError(val)
        else:
            raise CommandException(val)


class CommandRoot(_CommandRoot):
    def __init__(self, qtile):
        self.qtile = qtile
        super(CommandRoot, self).__init__()

    def call(self, selectors, name, *args, **kwargs):
        state, val = self.qtile.server.call((selectors, name, args, kwargs))
        if state == SUCCESS:
            return val
        elif state == ERROR:
            raise CommandError(val)
        else:
            raise CommandException(val)


class _Call(object):
    """
    Parameters
    ==========
    command :
        A string command name specification
    args :
        Arguments to be passed to the specified command
    kwargs :
        Arguments to be passed to the specified command
    """
    def __init__(self, selectors, name, *args, **kwargs):
        self.selectors = selectors
        self.name = name
        self.args = args
        self.kwargs = kwargs
        # Conditionals
        self.layout = None

    def when(self, layout=None, when_floating=True):
        self.layout = layout
        self.when_floating = when_floating
        return self

    def check(self, q):
        if self.layout:
            if self.layout == 'floating':
                if q.currentWindow.floating:
                    return True
                return False
            if q.currentLayout.name != self.layout:
                return False
            if q.currentWindow and q.currentWindow.floating \
                    and not self.when_floating:
                return False
        return True


class _LazyTree(_CommandRoot):
    def call(self, selectors, name, *args, **kwargs):
        return _Call(selectors, name, *args, **kwargs)

lazy = _LazyTree()
