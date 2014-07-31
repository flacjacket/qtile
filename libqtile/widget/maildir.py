# -*- coding: utf-8 -*-
# vim: set sw=4 et tw=80:
from __future__ import print_function, division

from . import base
from ..compat import string_type

import os.path
import mailbox


class Maildir(base.ThreadedPollText):
    """
    A simple widget showing the number of new mails in maildir mailboxes.
    """

    # TODO: make this use our settings framework
    def __init__(self, maildirPath, subFolders, separator=" ", **config):
        """
        Constructor.

        @param maildirPath: the path to the Maildir (e.g. "~/Mail").
        @param subFolders: the subfolders to scan (e.g. [{"path": "INBOX", "label": "Home mail"}, {"path": "spam", "label": "Home junk"}]).
        @param separator: the string to put between the subfolder strings.
        @param timeout: the refresh timeout in seconds.
        """
        base.ThreadedPollText.__init__(self, **config)
        self._maildirPath = os.path.expanduser(maildirPath)
        self._separator = separator
        self._subFolders = []

        # if it looks like a list of strings then we just convert them
        # and use the name as the label
        if isinstance(subFolders[0], string_type):
            self._subFolders = [
                {"path": folder, "label": folder}
                for folder in subFolders
            ]
        else:
            self._subFolders = subFolders

    def poll(self):
        """
        Scans the mailbox for new messages.

        @return: A string representing the current mailbox state.
        """
        state = {}

        def to_maildir_fmt(paths):
            for path in iter(paths):
                yield path.rsplit(":")[0]

        for subFolder in self._subFolders:
            path = os.path.join(self._maildirPath, subFolder["path"])
            maildir = mailbox.Maildir(path)
            state[subFolder["label"]] = 0

            for file in to_maildir_fmt(os.listdir(os.path.join(path, "new"))):
                if file in maildir:
                    state[subFolder["label"]] += 1

        return self.format_text(state)

    def format_text(self, state):
        """
        Converts the state of the subfolders to a string.

        @param state: a dictionary as returned by mailbox_state.
        @return: a string representation of the given state.
        """
        return self._separator.join(
            "{}: {}".format(*item) for item in state.items()
        )
