#!/usr/bin/env python3

"""Backend manager for wicd.

Manages and loads the pluggable backends for wicd.

"""

#
#   Copyright (C) 2008-2009 Adam Blackburn
#   Copyright (C) 2008-2009 Dan O'Reilly
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License Version 2 as
#   published by the Free Software Foundation.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import importlib
import os

import wicd.backends as bck


# TODO(gryf): change this, because it's ugly as hell
BACKENDS = {x.split('_')[1][:-3]: x[:-3] for x in
            os.listdir(os.path.dirname(bck.__file__))
            if not x.startswith('__')}


def fail(backend_name, reason):
    """Helper to warn the user about failure in loading backend."""
    print(("Failed to load backend %s: %s" % (backend_name, reason)))
    return True


class BackendManager(object):
    """Manages, validates, and loads wicd backends."""
    def __init__(self):
        """Initialize the backend manager."""
        self.__loaded_backend = None

    def _valid_backend_file(self, be_file):
        """Make sure the backend file is valid."""
        return (os.path.exists(be_file) and
                os.path.basename(be_file).startswith("be-") and
                be_file.endswith(".py"))

    def get_current_backend(self):
        """Returns the name of the loaded backend."""
        if self.__loaded_backend:
            return self.__loaded_backend.NAME
        else:
            return None

    def get_available_backends(self):
        """Returns a list of all valid backends in the backend directory."""
        return list(BACKENDS)

    def get_update_interval(self):
        """Returns how often in seconds the wicd monitor should update."""
        if self.__loaded_backend:
            return self.__loaded_backend.UPDATE_INTERVAL
        else:
            return None

    def get_backend_description(self, backend_name):
        """Loads a backend and returns its description."""
        try:
            return BACKENDS[backend_name].DESCRIPTION
        except KeyError:
            return "No backend data available"

    def _validate_backend(self, backend, backend_name):
        """Ensures that a backend module is valid."""
        failed = False
        if not backend.NAME:
            failed = fail(backend_name, 'Missing NAME attribute.')
        if not backend.UPDATE_INTERVAL:
            failed = fail(backend_name, "Missing UPDATE_INTERVAL attribute.")
        if not backend.NeedsExternalCalls:
            failed = fail(backend_name, "Missing NeedsExternalCalls method.")
        if not backend.WiredInterface:
            failed = fail(backend_name, "Missing WiredInterface class.")
        if not backend.WirelessInterface:
            failed = fail(backend_name, "Missing WirelessInterface class.")
        return failed

    def load_backend(self, backend_name):
        """Load and return a backend module.

        Given a backend name be-foo, attempt to load a python module
        in the backends directory called be-foo.py.  The module must
        include a certain set of classes and variables to be considered
        valid.

        """
        try:
            backend = importlib.import_module('.' + BACKENDS[backend_name],
                                              'wicd.backends')
        except KeyError:
            return None

        failed = self._validate_backend(backend, backend_name)
        if failed:
            return None

        self.__loaded_backend = backend
        print(('successfully loaded backend %s' % backend_name))
        return backend
