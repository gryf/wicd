====
WICD
====

Wired and Wireless Network Connection Manager.

This is expansion of the `original`_ WICD, which is semi dead project - even
though there was `some activity`_ regarding moving it to the Python3, its even
`been merged`_ to the original sources, yet it's still borken.

My motivation is to make it usable again, and my effort concentrate on the
curses part of the project.

What's works:

1. Installation. It was broken, but the fix was trivial. So now, the usual
   ``python setup.py install`` should just work.
2. TUI in ncurses. Actually, it's using `urwid`_ underneath. No

What is not:

1. GUI in GTK. WICD used to use `pygtk`_, which (unfortunately) is Python 2
   only project. I would be tempted to reimplement it with gobject, but I have
   0 motivation for doing so, because GTK2 is not supported through it.



.. _original: https://launchpad.net/wicd
.. _some activity:
.. _been merged:
.. _urwid:
