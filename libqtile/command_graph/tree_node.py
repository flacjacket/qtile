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

import abc
import six


class TreeNode(six.with_metaclass(abc.ABCMeta)):
    """A hierarchical collection of objects that define commands

    CollectionNode objects act as containers, allowing them to be nested. The
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

    def node(self, node_name, parent=None):
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


class LayoutTree(TreeNode):
    name = "layout"
    _contains = ["group", "window", "screen"]


class _TWidget(TreeNode):
    name = "widget"
    _contains = ["bar", "screen", "group"]


class _TBar(TreeNode):
    name = "bar"
    _contains = ["screen"]


class _TWindow(TreeNode):
    name = "window"
    _contains = ["group", "screen", "layout"]


class _TScreen(TreeNode):
    name = "screen"
    _contains = ["layout", "window", "bar"]


_TreeMap = {
    "layouts": _TLayout,
    "widgets": _TWidget,
    "bars": _TBar,
    "windows": _TWindow,
    "screens": _TScreen,
    "groups": _TGroup,
}
