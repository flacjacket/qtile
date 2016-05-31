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

from libqtile.log_utils import logger


class TreeNode(object):
    def __init__(self, children):
        self.children = children

    def ls(self):
        return list(self.children.keys())


class CommandNode(six.with_metaclass(abc.ABCMeta)):
    """Base class for objects that expose commands

    Each command should be a method named `cmd_X`, where `X` is the command
    name.

    Every node object can contain references to other adjacent objects in the
    graph.  This may be to other trees (when this object contains a set of
    another type of object, e.g. a group links to a set of windows) or to
    specific nodes (typically a node that has this node in a tree, e.g. a
    window links to its containing group).
    """

    parent_name = None
    children_names = []
    node_names = []

    def __init__(self, parent=None, **children):
        self.parent = parent

        # check that all children are defined
        assert set(children.keys()) == set(self.children_names)
        self.children = children
        for name, value in self.children:
            setattr(self, name, value)

        # check that all child nodes are also child trees
        node_trees = [node + "s" for node in self.child_node_names
        assert set(node_trees) <= set(self.children_names)
        for node in self.node_names:
            setattr(self, node, None)

    @property
    @abs.abstractmethod
    def name(self):
        """Name of the node"""
        pass

    @property
    @abs.abstractmethod
    def id(self):
        """Unique identifier for this node"""
        pass

    def ls(self):
        return ["{}/".format(child) for name in self.children_names] + [parent_name] + self.

    def select(self, *selectors):
        """Return a selected object from the graph

        Recursively finds an object specified by a list of `(name, selector)`
        tuples by traversing through the graph.

        Raises
        ------

        SelectError if the object does not exist.
        """
        # base recursion case
        if not selectors:
            return self

        # get the next name/selector tuple
        name, selector = selectors.pop(0)

        # if we try to access an element down the tree
        if name in self.children:
            tree = self.children[name]
            # if we specify the selector for the tree
            if selector:
                node = tree[selector]
                return node.select(selectors)
            # if we don't specify the selector of the tree, this must be the end of the search
            elif selectors:
                raise SelectError(name, selector, "Must specify item of {}".format(name))
            return tree
        elif name in self.nodes:
            # cannot perform a selection on an object
            if selector:
                raise SelectError(name, selector, "Cannot perform selection on {} object".format(selector))
            return self.nodes[name]
        # otherwise try to search up the tree
        elif self.parent:
            if name == self.parent_name:
                # cannot perform a selection on an object
                if selector:
                    raise SelectError(name, selector, "Cannot perform selection on {} object".format(selector))
                node = self.node(name)
                return node.select(selectors)
            # otherwise, if we specify a node, try to traverse up the tree to find the node
            try:
                return self.parent.select((name, selector), selectors)
            except SelectError:
                pass
        raise SelectError(name, selector, "Unable to find selection")

    def command(self, name):
        """Return the command corresponding to the given name"""
        return getattr(self, "cmd_" + name, None)

    @property
    def commands(self):
        """Return a list of the names of all commands

        Commands are all methods starting with `cmd_`
        """
        cmds = [i[4:] for i in dir(self) if i.startswith("cmd_")]
        return cmds

    def cmd_commands(self):
        """Returns a list of possible commands for this object

        Used by __qsh__ for command completion and online help
        """
        return self.commands

    def cmd_items(self, name):
        """Returns a list of contained items for the specified name

        Used by __qsh__ to allow navigation of the object graph.
        """
        return self.items(name)

    def docSig(self, name):
        # inspect.signature introduced in Python 3.3
        if sys.version_info < (3, 3):
            args, varargs, varkw, defaults = inspect.getargspec(self.command(name))
            if args and args[0] == "self":
                args = args[1:]
            return name + inspect.formatargspec(args, varargs, varkw, defaults)

        sig = inspect.signature(self.command(name))
        args = list(sig.parameters)
        if args and args[0] == "self":
            args = args[1:]
            sig = sig.replace(parameters=args)
        return name + str(sig)

    def docText(self, name):
        return inspect.getdoc(self.command(name)) or ""

    def doc(self, name):
        spec = self.docSig(name)
        htext = self.docText(name)
        return spec + '\n' + htext

    def cmd_doc(self, name):
        """Deprecated: use help()"""
        return self.cmd_help(name)

    def cmd_help(self, name):
        """Returns the documentation for a specified command name

        Used by __qsh__ to provide online help.
        """
        if name in self.commands:
            return self.doc(name)
        else:
            raise CommandError("No such command: %s" % name)

    def cmd_eval(self, code):
        """Evaluates code in the same context as this function

        Return value is tuple `(success, result)`, success being a boolean and
        result being a string representing the return value of eval, or None if
        exec was used instead.
        """
        try:
            try:
                return (True, str(eval(code)))
            except SyntaxError:
                exec(code)
                return (True, None)
        except:
            error = traceback.format_exc().strip().split("\n")[-1]
            return (False, error)

    def cmd_function(self, function, *args, **kwargs):
        """Call a function with current object as argument"""
        try:
            function(self, *args, **kwargs)
        except Exception:
            error = traceback.format_exc()
            logger.error('Exception calling "%s":\n%s' % (function, error))
