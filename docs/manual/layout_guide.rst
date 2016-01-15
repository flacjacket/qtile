============
Layout Guide
============

This guide lays out what is expected of layouts, what methods and commands they
need to define and what each method should do, in order to make it easy for
users to change between multiple layouts.

Required Methods
================

The following are the required abstract methods that *must* be overridden by
any base modules:

.. automethod:: libqtile.layout.base.Layout.add

.. automethod:: libqtile.layout.base.Layout.remove

.. automethod:: libqtile.layout.base.Layout.configure

.. automethod:: libqtile.layout.base.Layout.focus_first

.. automethod:: libqtile.layout.base.Layout.focus_last

.. automethod:: libqtile.layout.base.Layout.focus_next

.. automethod:: libqtile.layout.base.Layout.focus_previous

.. automethod:: libqtile.layout.base.Layout.cmd_next

.. automethod:: libqtile.layout.base.Layout.cmd_previous

remove(self, client)
--------------------



Testing
=======

It is greatly encouraged to have a set of tests for every layout.  You can see
examples of various tests in ``./test/layouts``.