import configparser

import munch

import wicd


DEFAULTS = {# paths
            'autostart': '/etc/xdg/autostart/',
            'bin': '/usr/bin/',
            'cli': '/usr/share/wicd/cli/',
            'curses': '/usr/share/wicd/curses/',
            'daemon': '/usr/share/wicd/daemon/',  # ✔
            'dbus': '/etc/dbus-1/system.d/',
            'dbus_service': '/usr/share/dbus-1/system-services/',
            'desktop': '/usr/share/applications/',
            'docdir': '/usr/share/doc/wicd/',
            'encryption': '/etc/wicd/encryption/templates/',  # ✔
            'etc': '/etc/wicd/',  # ✔
            'gnome_shell_extensions': '/usr/share/gnome-shell/extensions/',
            'gtk': '/usr/share/wicd/gtk/',
            'icons': '/usr/share/icons/hicolor/',
            'images': '/usr/share/wicd/icons/',
            'init': '/etc/init.d/',
            'kdedir': '/usr/share/autostart/',
            'lib': '/usr/lib/wicd/',
            'log': '/var/log/wicd/',
            'logrotate': '/etc/logrotate.d/',
            'mandir': '/usr/share/man/',
            'networks': '/var/lib/wicd/configurations/',  # ✔
            'pidfile': '/var/run/wicd/wicd.pid',  # ✔
            'pixmaps': '/usr/share/pixmaps/',
            'pmutils': '/usr/lib/pm-utils/sleep.d/',
            'postconnectscripts': '/etc/wicd/scripts/postconnect',  # ✔
            'postdisconnectscripts': '/etc/wicd/scripts/postdisconnect',  # ✔
            'preconnectscripts': '/etc/wicd/scripts/preconnect',  # ✔
            'predisconnectscripts': '/etc/wicd/scripts/predisconnect',  # ✔
            'resume': '/etc/acpi/resume.d/',
            'sbin': '/usr/sbin/',  # ✔
            'scripts': '/etc/wicd/scripts/',
            'share': '/usr/share/wicd/',
            'suspend': '/etc/acpi/suspend.d/',
            'systemd': '/lib/systemd/system/',
            'translations': '/usr/share/locale/',  # ✔
            'varlib': '/var/lib/wicd/',  # ✔
            # vars
            'log_group': '',  # ✔
            'log_perms': '0600',  # ✔
            'revision': '',  # ✔
            'wicd_group': 'users',  # ✔
            'python': '/usr/bin/python3',  # ✔ TODO

           }


class Config(munch.Munch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parser = configparser.ConfigParser()
        self._build_defaults()

    def _build_defaults(self):
        for name, path in DEFAULTS.items():
            self.parser.set(self.parser.default_section, name, path)

    version = '%VERSION%'
    revision = '%REVNO%'
    curses_revision = '%CURSES_REVNO%'

# # FILES
#
# # python begins the file section
#     python = '%PYTHON%'
#     pidfile = '%PIDFILE%'
# # stores something like other/wicd
# # really only used in the install
#     initfile = '%INITFILE%'
# # stores only the file name, i.e. wicd
#     initfilename = '%INITFILENAME%'
#     wicd_group = '%WICDGROUP%'
#     log_group = '%LOGGROUP%'
#     log_perms = '%LOGPERMS%'
#
#     # BOOLEANS
#     no_install_pmutils = %NO_INSTALL_PMUTILS%
#     no_install_init = %NO_INSTALL_INIT%
#     no_install_man = %NO_INSTALL_MAN%
#     no_install_i18n = %NO_INSTALL_I18N%
#     no_install_i18n_man = %NO_INSTALL_I18N_MAN%
#     no_install_kde = %NO_INSTALL_KDE%
#     no_install_acpi = %NO_INSTALL_ACPI%
#     no_install_docs = %NO_INSTALL_DOCS%
#     no_install_gtk = %NO_INSTALL_GTK%
#     no_install_ncurses = %NO_INSTALL_NCURSES%
#     no_install_cli = %NO_INSTALL_CLI%
#     no_install_gnome_shell_extensions = %NO_INSTALL_GNOME_SHELL_EXTENSIONS%
#     no_use_notifications = %NO_USE_NOTIFICATIONS%
#
#         self.distro = 'auto'
#
#         self.no_install_init = False
#         self.no_install_man = False
#         self.no_install_i18n = False
#         self.no_install_i18n_man = False
#         self.no_install_kde = False
#         self.no_install_acpi = False
#         self.no_install_pmutils = False
#         self.no_install_docs = False
#         self.no_install_gtk = False
#         self.no_install_ncurses = False
#         self.no_install_cli = False
#         self.no_install_gnome_shell_extensions = False
#         self.no_use_notifications = False
#
#         # Determine the default init file location on several different distros
#         self.distro_detect_failed = False
#
#         self.initfile = 'init/default/wicd'
#         # ddistro is the detected distro
#         if os.path.exists('/etc/redhat-release'):
#             self.ddistro = 'redhat'
#         elif os.path.exists('/etc/SuSE-release'):
#             self.ddistro = 'suse'
#         elif os.path.exists('/etc/fedora-release'):
#             self.ddistro = 'redhat'
#         elif os.path.exists('/etc/gentoo-release'):
#             self.ddistro = 'gentoo'
#         elif os.path.exists('/etc/debian_version'):
#             self.ddistro = 'debian'
#         elif os.path.exists('/etc/arch-release'):
#             self.ddistro = 'arch'
#         elif (os.path.exists('/etc/slackware-version') or
#               os.path.exists('/etc/slamd64-version') or
#               os.path.exists('/etc/bluewhite64-version')):
#             self.ddistro = 'slackware'
#         elif os.path.exists('/etc/pld-release'):
#             self.ddistro = 'pld'
#         elif os.path.exists('/usr/bin/crux'):
#             self.ddistro = 'crux'
#         elif os.path.exists('/etc/lunar.release'):
#             self.distro = 'lunar'
#         else:
#             self.ddistro = 'FAIL'
#             # self.no_install_init = True
#             # self.distro_detect_failed = True
#             print('WARNING: Unable to detect the distribution in use.\n'
#                   'If you have specified --distro or --init and --initfile, '
#                   'configure will continue.\nPlease report this warning, '
#                   'along with the name of your distribution, to the wicd '
#                   'developers.')
#
#         # Try to get the pm-utils sleep hooks directory from pkg-config and
#         # the kde prefix from kde-config
#         # Don't run these in a shell because it's not needed and because shell
#         # swallows the OSError we would get if {pkg,kde}-config do not exist
#         # If we don't get anything from *-config, or it didn't run properly,
#         # or the path is not a proper absolute path, raise an error
#         try:
#             pmtemp = subprocess.Popen(["pkg-config",
#                                        "--variable=pm_sleephooks",
#                                        "pm-utils"], stdout=subprocess.PIPE)
#             returncode = pmtemp.wait()  # let it finish, and get the exit code
#             # read stdout
#             pmutils_candidate = str(pmtemp.stdout.readline().strip())
#             if len(pmutils_candidate) == 0 or returncode != 0 or \
#                not os.path.isabs(pmutils_candidate):
#                 raise ValueError
#             else:
#                 self.pmutils = pmutils_candidate
#         except (OSError, ValueError, FileNotFoundError):
#             pass  # use our default
#
#         try:
#             kdetemp = subprocess.Popen(["kde-config", "--prefix"],
#                                        stdout=subprocess.PIPE)
#             # let it finish, and get the exit code
#             returncode = kdetemp.wait()
#             # read stdout
#             kdedir_candidate = str(kdetemp.stdout.readline().strip())
#             if (len(kdedir_candidate) == 0 or
#                     returncode != 0 or
#                     not os.path.isabs(kdedir_candidate)):
#                 raise ValueError
#             else:
#                 self.kdedir = kdedir_candidate + '/share/autostart'
#         except (OSError, ValueError, FileNotFoundError):
#             # If kde-config isn't present, we'll check for kde-4.x
#             try:
#                 kde4temp = subprocess.Popen(["kde4-config", "--prefix"],
#                                             stdout=subprocess.PIPE)
#                 # let it finish, and get the exit code
#                 returncode = kde4temp.wait()
#                 # read stdout
#                 kde4dir_candidate = str(kde4temp.stdout.readline().strip())
#                 if len(kde4dir_candidate) == 0 or returncode != 0 or \
#                    not os.path.isabs(kde4dir_candidate):
#                     raise ValueError
#                 else:
#                     self.kdedir = kde4dir_candidate + '/share/autostart'
#             except (OSError, ValueError, FileNotFoundError):
#                 # If neither kde-config nor kde4-config are not present or
#                 # return an error, then we can assume that kde isn't installed
#                 # on the user's system
#                 self.no_install_kde = True
#                 # If the assumption above turns out to be wrong, do this:
#                 # pass # use our default
#
#         self.python = '/usr/bin/python3'
#         self.pidfile = '/var/run/wicd/wicd.pid'
#         self.initfilename = os.path.basename(self.initfile)
#         self.wicdgroup = 'users'
#         self.loggroup = ''
#         self.logperms = '0600'
#
#     def distro_check(self):
#         print("Distro is: " + self.distro)
#         if self.distro in ['sles', 'suse']:
#             self.init = '/etc/init.d/'
#             self.initfile = 'init/suse/wicd'
#         elif self.distro in ['redhat', 'centos', 'fedora']:
#             self.init = '/etc/rc.d/init.d/'
#             self.initfile = 'init/redhat/wicd'
#             self.pidfile = '/var/run/wicd.pid'
#         elif self.distro in ['slackware', 'slamd64', 'bluewhite64']:
#             self.init = '/etc/rc.d/'
#             self.initfile = 'init/slackware/rc.wicd'
#             self.docdir = '/usr/doc/wicd-%s' % VERSION_NUM
#             self.mandir = '/usr/man/'
#             self.no_install_acpi = True
#             self.wicdgroup = "netdev"
#         elif self.distro in ['debian']:
#             self.wicdgroup = "netdev"
#             self.loggroup = "adm"
#             self.logperms = "0640"
#             self.init = '/etc/init.d/'
#             self.initfile = 'init/debian/wicd'
#         elif self.distro in ['arch']:
#             self.init = '/etc/rc.d/'
#             self.initfile = 'init/arch/wicd'
#         elif self.distro in ['gentoo']:
#             self.init = '/etc/init.d/'
#             self.initfile = 'init/gentoo/wicd'
#         elif self.distro in ['pld']:
#             self.init = '/etc/rc.d/init.d/'
#             self.initfile = 'init/pld/wicd'
#         elif self.distro in ['crux']:
#             self.init = '/etc/rc.d/'
#         elif self.distro in ['lunar']:
#             self.init = '/etc/init.d/'
#             self.initfile = 'init/lunar/wicd'
#         else:
#             if self.distro == 'auto':
#                 print("NOTICE: Automatic distro detection found: %s, retrying "
#                       "with that..." % self.ddistro)
#                 self.distro = self.ddistro
#                 self.distro_check()
#             else:
#                 print("WARNING: Distro detection failed!")
#                 self.no_install_init = True
#                 self.distro_detect_failed = True

CFG = Config(DEFAULTS)
