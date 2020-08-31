import configparser
import os


DEFAULTS = {'bin': '/usr/bin',
            'daemon': '/usr/share/wicd/daemon',
            'encryption': '/etc/wicd/encryption-templates',
            'etc': '/etc/wicd',
            'log': '/var/log/wicd',
            'loggroup': '',
            'logperms': '0600',
            'networks': '/var/lib/wicd/configurations',
            'pidfile': '/var/run/wicd.pid',
            'postconnectscripts': '/etc/wicd/scripts/postconnect',
            'postdisconnectscripts': '/etc/wicd/scripts/postdisconnect',
            'preconnectscripts': '/etc/wicd/scripts/preconnect',
            'predisconnectscripts': '/etc/wicd/scripts/predisconnect',
            'python': 'python',
            'revision': '',
            'translations': '/usr/share/locale',
            'varlib': '/var/lib/wicd',
            'wicdgroup': 'users'}
SECTION = 'wicd'
CFG_FILE = 'wicd.conf'


class Config(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parser = configparser.ConfigParser()
        self._build_defaults()

    def _build_defaults(self):
        for name, path in DEFAULTS.items():
            self.parser.set(self.parser.default_section, name, path)

    def load(self):
        """
        Try to load config from hardcoded location. At least, on proper
        installation, we need to have an entry point to look at. Most of the
        time distro package maintainers rely on defaults, since they are sane
        and mostly tested. Let's keep it up.
        """
        self.parser.read(os.path.join(self.etc, CFG_FILE))
        if SECTION in self.parser.sections():
            for opt in self.parser.options(SECTION):
                self[opt] = self.parser.get(SECTION, opt)

    def __getattr__(self, k):
        try:
            return object.__getattribute__(self, k)
        except AttributeError:
            try:
                return self[k]
            except KeyError:
                raise AttributeError(k)

    def __setattr__(self, k, v):
        try:
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                self[k] = v
            except Exception:
                raise AttributeError(k)
        else:
            object.__setattr__(self, k, v)

    def __delattr__(self, k):
        try:
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                del self[k]
            except KeyError:
                raise AttributeError(k)
        else:
            object.__delattr__(self, k)


CFG = Config(DEFAULTS)
