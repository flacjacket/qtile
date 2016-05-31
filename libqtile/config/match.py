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

from libqtile import utils


class Match(object):
    """Match for dynamic groups

    It can match by title, class or role.

    ``Match`` supports both regular expression objects (i.e. the result of
    ``re.compile()``) or strings (match as a "include" match). If a window
    matches any of the things in any of the lists, it is considered a match.

    Parameters
    ==========
    title:
        things to match against the title (WM_NAME)
    wm_class:
        things to match against the second string in WM_CLASS atom
    role:
        things to match against the WM_ROLE atom
    wm_type:
        things to match against the WM_TYPE atom
    wm_instance_class:
        things to match against the first string in WM_CLASS atom
    net_wm_pid:
        things to match against the _NET_WM_PID atom (only int allowed in this
        rule)
    """
    def __init__(self, title=None, wm_class=None, role=None, wm_type=None,
                 wm_instance_class=None, net_wm_pid=None):
        if not title:
            title = []
        if not wm_class:
            wm_class = []
        if not role:
            role = []
        if not wm_type:
            wm_type = []
        if not wm_instance_class:
            wm_instance_class = []
        if not net_wm_pid:
            net_wm_pid = []

        try:
            net_wm_pid = list(map(int, net_wm_pid))
        except ValueError:
            error = 'Invalid rule for net_wm_pid: "%s" '\
                    'only ints allowed' % str(net_wm_pid)
            raise utils.QtileError(error)

        self._rules = [('title', t) for t in title]
        self._rules += [('wm_class', w) for w in wm_class]
        self._rules += [('role', r) for r in role]
        self._rules += [('wm_type', r) for r in wm_type]
        self._rules += [('wm_instance_class', w) for w in wm_instance_class]
        self._rules += [('net_wm_pid', w) for w in net_wm_pid]

    def compare(self, client):
        for _type, rule in self._rules:
            if _type == "net_wm_pid":
                def match_func(value):
                    return rule == value
            else:
                match_func = getattr(rule, 'match', None) or \
                    getattr(rule, 'count')

            if _type == 'title':
                value = client.name
            elif _type == 'wm_class':
                value = None
                _value = client.window.get_wm_class()
                if _value and len(_value) > 1:
                    value = _value[1]
            elif _type == 'wm_instance_class':
                value = client.window.get_wm_class()
                if value:
                    value = value[0]
            elif _type == 'wm_type':
                value = client.window.get_wm_type()
            elif _type == 'net_wm_pid':
                value = client.window.get_net_wm_pid()
            else:
                value = client.window.get_wm_window_role()

            if value and match_func(value):
                return True
        return False

    def map(self, callback, clients):
        """Apply callback to each client that matches this Match"""
        for c in clients:
            if self.compare(c):
                callback(c)

    def __repr__(self):
        return '<Match %s>' % self._rules
