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
import functools
import inspect
import traceback
from typing import Any, Callable, List, Optional, Tuple, TypeVar

from libqtile.log_utils import logger
from libqtile.command_graph import CommandGraphCall, CommandGraphRoot, _CommandGraphNode, _Command


lazy = CommandGraphRoot()


class CommandError(Exception):
    pass


class CommandException(Exception):
    pass


class _SelectError(Exception):
    def __init__(self, name, sel):
        super().__init__()
        self.name = name
        self.sel = sel


SUCCESS = 0
ERROR = 1
EXCEPTION = 2


def format_selectors(lst):
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


_T = TypeVar('_T')


def wrap_ipc_data(func: Callable[[CommandGraphCall], _T]) -> Callable[[Any], _T]:
    @functools.wraps(func)
    def wrapper(data):
        selectors, name, args, kwargs = data
        return func(CommandGraphCall(selectors, name, *args, **kwargs))

    return wrapper


class Client:
    def __init__(self, client, command_graph_node: _CommandGraphNode = None) -> None:
        self._client = client
        if command_graph_node is None:
            command_graph_node = CommandGraphRoot()
        self.command_graph_node = command_graph_node

    @property
    def parent(self):
        return self.command_graph_node.parent

    @property
    def path(self) -> str:
        return "path"

    def __getattr__(self, selection: str) -> "Client":
        self.command_graph_node = getattr(self.command_graph_node, selection)
        print("command:", self.command_graph_node, selection)
        return self

    def __getitem__(self, name: str) -> "Client":
        self.command_graph_node = self.command_graph_node[name]
        print("command:", self.command_graph_node, name)
        return self

    def __call__(self, *args, **kwargs) -> str:
        if not isinstance(self.command_graph_node, _Command):
            raise CommandError("Current selection is not a command")
        call = self.command_graph_node(*args, **kwargs)
        state, val = self._client.call((call.selectors, call.name, call.args, call.kwargs))
        if state == SUCCESS:
            return val
        elif state == ERROR:
            raise CommandError(val)
        else:
            raise CommandException(val)


class CommandObject(metaclass=abc.ABCMeta):
    """Base class for objects that expose commands

    Each command should be a method named `cmd_X`, where X is the command name.
    A CommandObject should also implement `._items()` and `._select()` methods
    (c.f. docstring for `.items()` and `.select()`).
    """

    def select(self, selectors: List[Tuple[str, Optional[str]]]) -> "CommandObject":
        """Return a selected object

        Recursively finds an object specified by a list of `(name, selector)`
        items.

        Raises _SelectError if the object does not exist.
        """
        if not selectors:
            return self

        name, selector = selectors[0]
        next_selector = selectors[1:]

        root, items = self.items(name)

        # cases that cause selection errors:
        # if no selector given, but no root object
        # if selector is given, but no items in container
        # if selector is given, but not in the list of contained items
        if (selector is None and root is False) or \
                (selector is not None and items is None) or \
                (selector is not None and selector not in items):
            raise _SelectError(name, selector)

        obj = self._select(name, selector)
        if obj is None:
            raise _SelectError(name, selector)
        return obj.select(next_selector)

    def items(self, name: str) -> Tuple[bool, List[str]]:
        """Build a list of contained items for the given item class

        Returns a tuple `(root, items)` for the specified item class, where:

            root: True if this class accepts a "naked" specification without an
            item seletion (e.g. "layout" defaults to current layout), and False
            if it does not (e.g. no default "widget").

            items: a list of contained items
        """
        ret = self._items(name)
        if ret is None:
            # Not finding information for a particular item class is OK here;
            # we don't expect layouts to have a window, etc.
            return False, []
        return ret

    @abc.abstractmethod
    def _select(self, name: str, sel: Optional[str]) -> "CommandObject":
        """Select the given item of the given item class

        This method is called with the following guarantees:
            - `name` is a valid selector class for this item
            - `sel` is a valid selector for this item
            - the `(name, sel)` tuple is not an "impossible" combination (e.g. a
              selector is specified when `name` is not a containment object).

        Return None if no such object exists
        """
        pass

    @abc.abstractmethod
    def _items(self, name) -> Tuple[bool, List[str]]:
        """Generate the items for a given

        Same return as `.items()`. Return `None` if name is not a valid item
        class.
        """
        pass

    def command(self, name: str) -> Callable:
        return getattr(self, "cmd_" + name, None)

    @property
    def commands(self):
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

    def get_command_signature(self, name):
        signature = inspect.signature(self.command(name))
        args = list(signature.parameters)
        if args and args[0] == "self":
            args = args[1:]
            signature = signature.replace(parameters=args)
        return name + str(signature)

    def get_command_docstring(self, name):
        return inspect.getdoc(self.command(name)) or ""

    def get_command_documentation(self, name):
        spec = self.get_command_signature(name)
        htext = self.get_command_docstring(name)
        return spec + '\n' + htext

    def cmd_doc(self, name):
        """Returns the documentation for a specified command name

        Used by __qsh__ to provide online help.
        """
        if name in self.commands:
            return self.get_command_documentation(name)
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
                return True, str(eval(code))
            except SyntaxError:
                exec(code)
                return True, None
        except Exception:
            error = traceback.format_exc().strip().split("\n")[-1]
            return False, error

    def cmd_function(self, function, *args, **kwargs):
        """Call a function with current object as argument"""
        try:
            function(self, *args, **kwargs)
        except Exception:
            error = traceback.format_exc()
            logger.error('Exception calling "%s":\n%s' % (function, error))

    def dispatch_call(self, call: CommandGraphCall) -> Tuple[int, str]:
        """Forward a call from the command graph into the command object

        Parameters
        ----------
        data:
            The data that is sent in, a tuple of the object graph selectors,
            the name of the command to run, the args to the command, and the
            kwargs to the command.

        Returns
        -------
        Tuple[int, str]
            The return code from the command call and the string that is
            returned from the command call.
        """
        logger.debug("Command: %s(%s, %s)", call.name, call.args, call.kwargs)

        try:
            selected_object = self.select(call.selectors)
        except _SelectError as v:
            e = format_selectors([(v.name, v.sel)])
            s = format_selectors(call.selectors)
            return ERROR, "No object {} in path '{}'".format(e, s)

        command = selected_object.command(call.name)
        if command is None:
            return ERROR, "No such command: {}".format(call.name)

        try:
            print(command)
            print(call.args)
            print(call.kwargs)
            output = command(*call.args, **call.kwargs)
        except CommandError as v:
            return ERROR, v.args[0]
        except Exception:
            return EXCEPTION, traceback.format_exc()

        return SUCCESS, output
