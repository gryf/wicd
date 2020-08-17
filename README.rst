====
WICD
====

This is expansion of the `original`_ WICD, which is semi dead project - even
though there was `some activity`_ regarding moving it to the Python3, some of
them even has `been merged`_ to the original sources, yet it's still unreleased
and what worse - broken.


What is WICD?
=============

Wired and Wireless Network Connection Manager.

A complete network connection manager Wicd supports wired and wireless
networks, and capable of creating and tracking profiles for both. It has a
template-based wireless encryption system, which allows the user to easily add
encryption methods used. It ships with some common encryption types, such as
WPA and WEP. Wicd will automatically connect at startup to any preferred
network within range.


Why are you doing this?
=======================

My motivation is to make it usable again, and my effort concentrate on the
daemon itself and curses TUI, as the most attractive parts of the project to me.

What's works:

1. Installation. It was broken, but the fix was trivial. So now, the usual
   ``python setup.py install`` should just work.
2. TUI in ncurses. Actually, it's using `urwid`_ underneath. It still have some
   issue, like crashing in some situations, just like wicd-1.7.4, but I have a
   plan to take a close look at it.

What is not:

1. GUI/client in GTK. WICD used to use `pygtk`_, which (unfortunately) is
   Python 2 only project. I would be tempted to reimplement it with gobject,
   but I have 0 motivation for doing so, because GTK2 is not supported through
   it.
2. Applet for GNOME Shell. There was simple dispatcher for try icon used in
   GNOME Shell, yet, it just use GUI.
3. Notification - it was used for GTK client.


License
=======

License is unchanged, and as the original code it's GPLv2. You can find copy of
the license attached as a ``LICENSE`` file in the root directory of the project.


.. _original: https://launchpad.net/wicd
.. _some activity: https://github.com/PXke/wicd-reloaded
.. _been merged: https://github.com/zeph/wicd
.. _urwid: http://urwid.org/
.. _pygtk: https://web.archive.org/web/20180416083422/http://www.pygtk.org
