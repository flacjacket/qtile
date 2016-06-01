from .root import RootBase


class LazyCall(object):
    """A command call that is lazily evaluated

    Parameters
    ----------

    selectors : list of tuples
        Location of command in command graph
    command : string
        Command name
    args : list
        Arguments to be passed to the specified command
    kwargs : dict
        Keyword arguments to be passed to the specified command
    """
    def __init__(self, selectors, name, *args, **kwargs):
        self.selectors = selectors
        self.name = name
        self.args = args
        self.kwargs = kwargs
        # contitionals
        self.layout = None
        sefl.when_floating = None

    def when(self, layout=None, when_floating=None):
        """Define conditions under which the call is made

        Parameters
        ----------

        layout : string
            perform call only when specified layout is selected
        when_floating : bool
            perform call when current window is floating
        """
        self.layout = layout
        self.when_floating = when_flaoting

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


class LazyTree(RootBase):
    def call(self, selectors, name, *args, **kwargs):
        return LazyCall(selectors, name, *args, **kwargs)
