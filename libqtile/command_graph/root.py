from .nodes import CommandNode


class RootBase(CommandNode):
    """Root object of the command tree

    This class constructs the entire hierarchy of callable commands from a conf
    object
    """
    children_names = ["screens", "groups", "layouts", "bars", "widgets", "windows"]
    node_names = ["screen", "group", "layout", "window"]


class CommandRoot(RootBase):
    pass
