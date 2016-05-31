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


class Rule(object):
    """How to act on a Match

    A Rule contains a Match object, and a specification about what to do when
    that object is matched.

    Parameters
    ==========
    match :
        ``Match`` object associated with this ``Rule``
    float :
        auto float this window?
    intrusive :
        override the group's exclusive setting?
    break_on_match :
        Should we stop applying rules if this rule is matched?
    """
    def __init__(self, match, group=None, float=False, intrusive=False,
                 break_on_match=True):
        self.match = match
        self.group = group
        self.float = float
        self.intrusive = intrusive
        self.break_on_match = break_on_match

    def matches(self, w):
        return self.match.compare(w)

    def __repr__(self):
        actions = utils.describe_attributes(self, ['group', 'float',
            'intrusive', 'break_on_match'])
        return '<Rule match=%r actions=(%s)>' % (self.match, actions)
