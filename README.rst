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

What's done:

1. Installation. It was broken, and was fixed. So now, the usual
   ``python setup.py install`` should just work.
2. TUI in ncurses. Actually, it's using `urwid`_ underneath. It still have some
   issues, like crashing in certain situations, just like wicd-1.7.4.
3. Straight up installation process. Separation for runtime/build only paths
   and options. Use configuration instead of templated ``wpath.py`` module.

What is not:

1. GUI. Graphics interface was built using `pygtk`_, which is Python 2, and
   dead project.
2. Applet for GNOME Shell. There was simple dispatcher for tray icon for the
   GUI client in GNOME Shell, so since GUI client is unsupported in Python 3, I
   have to dro pit aswell.
3. Notifications. `Notification library`_ was used for GTK client, and is
   Python2 only.
4. `python-iwscan`_ and `python-wpactrl`_ are not supported, as they are
   considered as dead projects.


License
=======

License is unchanged, and as the original code it's GPLv2. You can find copy of
the license attached as a ``LICENSE`` file in the root directory of the project.


.. _original: https://launchpad.net/wicd
.. _some activity: https://github.com/PXke/wicd-reloaded
.. _been merged: https://github.com/zeph/wicd
.. _urwid: http://urwid.org/
.. _pygtk: https://web.archive.org/web/20180416083422/http://www.pygtk.org
.. _Notification library: http://www.galago-project.org
.. _python-iwscan: https://web.archive.org/web/20080926094621/http://projects.otaku42.de/browser/python-iwscan
.. _python-wpactrl: https://web.archive.org/web/20100508185722/http://projects.otaku42.de/wiki/PythonWpaCtrl
