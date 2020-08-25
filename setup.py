#!/usr/bin/env python3
#
#   Copyright (C) 2007 - 2009 Adam Blackburn
#   Copyright (C) 2007 - 2009 Dan O'Reilly
#   Copyright (C) 2009        Andrew Psaltis
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
from glob import glob
import os
import re
import shutil
import subprocess

from distutils.core import setup, Command
from distutils.command.build import build as _build
from distutils.command.install import install as _install

import wicd

VERSION_NUM = wicd.__version__
# REVISION_NUM is automatically updated
try:
    REVISION_NUM = subprocess.check_output('git rev-parse --short HEAD'
                                           .split(), text=True)
    if 'fatal' in REVISION_NUM:
        REVISION_NUM = 'unknown'
except IOError:
    REVISION_NUM = 'unknown'
CURSES_REVNO = 'uimod'

data = []

# path to the file to put in empty directories
# fixes https://bugs.launchpad.net/wicd/+bug/503028
empty_file = 'other/.empty_on_purpose'

# change to the directory setup.py is contained in
os.chdir(os.path.abspath(os.path.split(__file__)[0]))


class build(_build):
    sub_commands = _build.sub_commands + [('compile_translations', None)]

    def run(self):
        try:
            import wpath
        except ImportError:
            self.run_command('configure')
            import wpath
            # raise Exception, 'Please run "./setup.py configure" first.'
        _build.run(self)


class configure(Command):
    description = "configure the paths that Wicd will be installed to"

    user_options = [
        # The first bunch is DIRECTORIES - they need to end with a slash ("/"),
        # which will automatically be tacked on in the finalize_options method
        ('lib=', None, 'set the lib directory'),
        ('share=', None, 'set the share directory'),
        ('etc=', None, 'set the etc directory'),
        ('scripts=', None, 'set the global scripts directory'),
        ('encryption=', None, 'set the encryption template directory'),
        ('bin=', None, 'set the bin directory'),
        ('sbin=', None, 'set the sbin directory'),
        ('networks=', None, 'set the encryption configuration directory'),
        ('log=', None, 'set the log directory'),
        ('resume=', None, 'set the directory the resume from suspend script '
         'is stored in'),
        ('suspend=', None, 'set the directory the  suspend script is stored '
         'in'),
        ('pmutils=', None, 'set the directory the  pm-utils hooks are stored '
         'in'),
        ('dbus=', None, 'set the directory the dbus config file is stored in'),
        ('dbus-service=', None, 'set the directory where the dbus services '
         'config files are stored in'),
        ('systemd=', None, 'set the directory where the systemd system '
         'services config files are stored in'),
        ('logrotate=', None, 'set the directory where the logrotate '
         'configuration files are stored in'),
        ('translations=', None, 'set the directory translations are stored '
         'in'),
        ('varlib=', None, 'set the path for wicd\'s variable state data'),
        ('init=', None, 'set the directory for the init file'),
        ('docdir=', None, 'set the directory for the documentation'),
        ('mandir=', None, 'set the directory for the man pages'),
        ('python=', None, 'set the path to the Python executable'),
        ('pidfile=', None, 'set the pid file'),
        ('initfile=', None, 'set the init file to use'),
        ('initfilename=', None, "set the name of the init file (don't use)"),
        ('wicdgroup=', None, "set the name of the group used for wicd"),
        ('distro=', None, 'set the distribution for which wicd will be '
         'installed'),
        ('loggroup=', None, 'the group the log file belongs to'),
        ('logperms=', None, 'the log file permissions'),
        ('no-install-init', None, "do not install the init file"),
        ('no-install-man', None, 'do not install the man files'),
        ('no-install-i18n', None, 'do not install translation files'),
        ('no-install-i18n-man', None, 'do not install the translated man '
         'files'),
        ('no-install-acpi', None, 'do not install the suspend.d and resume.d '
         'acpi scripts'),
        ('no-install-pmutils', None, 'do not install the pm-utils hooks'),
        ('no-install-docs', None, 'do not install the auxiliary '
         'documentation')]

    def initialize_options(self):
        self.lib = '/usr/lib/wicd/'
        self.share = '/usr/share/wicd/'
        self.etc = '/etc/wicd/'
        self.scripts = self.etc + "scripts/"
        self.encryption = self.etc + 'encryption/templates/'
        self.bin = '/usr/bin/'
        self.sbin = '/usr/sbin/'
        self.varlib = '/var/lib/wicd/'
        self.networks = self.varlib + 'configurations/'
        self.log = '/var/log/wicd/'
        self.resume = '/etc/acpi/resume.d/'
        self.suspend = '/etc/acpi/suspend.d/'
        self.pmutils = '/usr/lib/pm-utils/sleep.d/'
        self.dbus = '/etc/dbus-1/system.d/'
        self.dbus_service = '/usr/share/dbus-1/system-services/'
        self.systemd = '/lib/systemd/system/'
        self.logrotate = '/etc/logrotate.d/'
        self.translations = '/usr/share/locale/'
        self.docdir = '/usr/share/doc/wicd/'
        self.mandir = '/usr/share/man/'
        self.distro = 'auto'

        self.no_install_init = False
        self.no_install_man = False
        self.no_install_i18n = False
        self.no_install_i18n_man = False
        self.no_install_acpi = False
        self.no_install_pmutils = False
        self.no_install_docs = False

        # Determine the default init file location on several different distros
        self.distro_detect_failed = False

        self.initfile = 'init/default/wicd'
        # ddistro is the detected distro
        if os.path.exists('/etc/redhat-release'):
            self.ddistro = 'redhat'
        elif os.path.exists('/etc/SuSE-release'):
            self.ddistro = 'suse'
        elif os.path.exists('/etc/fedora-release'):
            self.ddistro = 'redhat'
        elif os.path.exists('/etc/gentoo-release'):
            self.ddistro = 'gentoo'
        elif os.path.exists('/etc/debian_version'):
            self.ddistro = 'debian'
        elif os.path.exists('/etc/arch-release'):
            self.ddistro = 'arch'
        elif (os.path.exists('/etc/slackware-version') or
              os.path.exists('/etc/slamd64-version') or
              os.path.exists('/etc/bluewhite64-version')):
            self.ddistro = 'slackware'
        elif os.path.exists('/etc/pld-release'):
            self.ddistro = 'pld'
        elif os.path.exists('/usr/bin/crux'):
            self.ddistro = 'crux'
        elif os.path.exists('/etc/lunar.release'):
            self.distro = 'lunar'
        else:
            self.ddistro = 'FAIL'
            # self.no_install_init = True
            # self.distro_detect_failed = True
            print('WARNING: Unable to detect the distribution in use.\n'
                  'If you have specified --distro or --init and --initfile, '
                  'configure will continue.\nPlease report this warning, '
                  'along with the name of your distribution, to the wicd '
                  'developers.')

        # Try to get the pm-utils sleep hooks directory from pkg-config.
        # Don't run these in a shell because it's not needed and because shell
        # swallows the OSError we would get if pkg-config do not exist
        # If we don't get anything from *-config, or it didn't run properly,
        # or the path is not a proper absolute path, raise an error
        try:
            pmtemp = subprocess.Popen(["pkg-config",
                                       "--variable=pm_sleephooks",
                                       "pm-utils"], stdout=subprocess.PIPE)
            returncode = pmtemp.wait()  # let it finish, and get the exit code
            # read stdout
            pmutils_candidate = str(pmtemp.stdout.readline().strip())
            if len(pmutils_candidate) == 0 or returncode != 0 or \
               not os.path.isabs(pmutils_candidate):
                raise ValueError
            else:
                self.pmutils = pmutils_candidate
        except (OSError, ValueError, FileNotFoundError):
            pass  # use our default

        self.python = '/usr/bin/python3'
        self.pidfile = '/var/run/wicd/wicd.pid'
        self.initfilename = os.path.basename(self.initfile)
        self.wicdgroup = 'users'
        self.loggroup = ''
        self.logperms = '0600'

    def distro_check(self):
        print("Distro is: " + self.distro)

        if self.distro is None and self.detected_distro != 'FAIL':
            self.distro = self.detected_distro

        if self.distro in ['sles', 'suse']:
            self.init = '/etc/init.d/'
            self.initfile = 'data/init/suse/wicd'
        elif self.distro in ['redhat', 'centos', 'fedora']:
            self.init = '/etc/rc.d/init.d/'
            self.initfile = 'data/init/redhat/wicd'
            self.pidfile = '/var/run/wicd.pid'
        elif self.distro in ['slackware', 'slamd64', 'bluewhite64']:
            self.init = '/etc/rc.d/'
            self.initfile = 'data/init/slackware/rc.wicd'
            self.docdir = '/usr/doc/wicd-%s' % VERSION_NUM
            self.mandir = '/usr/man/'
            self.no_install_acpi = True
            self.wicdgroup = "netdev"
        elif self.distro in ['debian']:
            self.wicdgroup = "netdev"
            self.loggroup = "adm"
            self.logperms = "0640"
            self.init = '/etc/init.d/'
            self.initfile = 'data/init/debian/wicd'
        elif self.distro in ['arch']:
            self.init = '/etc/rc.d/'
            self.initfile = 'data/init/arch/wicd'
        elif self.distro in ['gentoo']:
            self.init = '/etc/init.d/'
            self.initfile = 'data/init/gentoo/wicd'
        elif self.distro in ['pld']:
            self.init = '/etc/rc.d/init.d/'
            self.initfile = 'data/init/pld/wicd'
        elif self.distro in ['crux']:
            self.init = '/etc/rc.d/'
        elif self.distro in ['lunar']:
            self.init = '/etc/init.d/'
            self.initfile = 'data/init/lunar/wicd'
        else:
            log.warn("WARNING: Distro detection failed!")
            self.no_install_init = True
            self.distro_detect_failed = True

    def finalize_options(self):
        self.distro_check()
        if self.distro_detect_failed and not self.no_install_init and \
           'FAIL' in [self.init, self.initfile]:
            print('ERROR: Failed to detect distro. Configure cannot '
                  'continue.\nPlease specify --init and --initfile to '
                  'continue with configuration.')

        # loop through the argument definitions in user_options
        for argument in self.user_options:
            # argument name is the first item in the user_options list
            # sans the = sign at the end
            argument_name = argument[0][:-1]
            # select the first one, which is the name of the option
            value = getattr(self, argument_name.replace('-', '_'))
            # if the option is not python (which is not a directory)
            if not argument[0][:-1] == "python":
                # see if it ends with a /
                if not str(value).endswith("/"):
                    # if it doesn't, slap one on
                    setattr(self, argument_name, str(value) + "/")
            else:
                # as stated above, the python entry defines the beginning
                # of the files section
                return

    def run(self):
        values = list()
        for argument in self.user_options:
            if argument[0].endswith('='):
                cur_arg = argument[0][:-1]
                cur_arg_value = getattr(self, cur_arg.replace('-', '_'))
                print("%s is %s" % (cur_arg, cur_arg_value))
                values.append((cur_arg, getattr(self, cur_arg.replace('-',
                                                                      '_'))))
            else:
                cur_arg = argument[0]
                cur_arg_value = getattr(self, cur_arg.replace('-', '_'))
                print("Found switch %s %s" % (argument, cur_arg_value))
                values.append((cur_arg, bool(cur_arg_value)))

        print('Replacing values in template files...')
        for item in os.listdir('in'):
            if item.endswith('.in'):
                print('Replacing values in', item, end=' ')
                original_name = os.path.join('in', item)
                item_in = open(original_name, 'r')
                final_name = item[:-3].replace('=', '/')
                parent_dir = os.path.dirname(final_name)
                if parent_dir and not os.path.exists(parent_dir):
                    print('(mkdir %s)' % parent_dir, end=' ')
                    os.makedirs(parent_dir)
                print(final_name)
                item_out = open(final_name, 'w')
                for line in item_in.readlines():
                    for item, value in values:
                        line = line.replace('%' + str(item.upper())
                                            .replace('-', '_') + '%',
                                            str(value))

                    # other things to replace that aren't arguments
                    line = line.replace('%VERSION%', str(VERSION_NUM))
                    line = line.replace('%REVNO%', str(REVISION_NUM))
                    line = line.replace('%CURSES_REVNO%', str(CURSES_REVNO))

                    item_out.write(line)

                item_out.close()
                item_in.close()
                shutil.copymode(original_name, final_name)


class clear_generated(Command):
    description = 'clears out files generated by configure'

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print('Removing completed template files...')
        for item in os.listdir('in'):
            if item.endswith('.in'):
                print('Removing completed', item, end=' ')
                final_name = item[:-3].replace('=', '/')
                print(final_name, '...', end=' ')
                if os.path.exists(final_name):
                    os.remove(final_name)
                    print('Removed.')
                else:
                    print('Does not exist.')
        print('Removing compiled translation files...')
        if os.path.exists('translations'):
            shutil.rmtree('translations/')
        os.makedirs('translations/')


class install(_install):
    def run(self):
        try:
            import wpath
        except ImportError:
            self.run_command('build')
            import wpath

        print("Using init file", wpath.init, wpath.initfile)
        data.extend([
            (wpath.dbus, ['other/wicd.conf']),
            (wpath.dbus_service, ['other/org.wicd.daemon.service']),
            (wpath.systemd, ['other/wicd.service']),
            (wpath.logrotate, ['other/wicd.logrotate']),
            (wpath.log, [empty_file]),
            (wpath.etc, ['other/dhclient.conf.template.default']),
            (wpath.encryption, [('encryption/templates/' + b) for b in
                                os.listdir('encryption/templates')
                                if not b.startswith('.')]),
            (wpath.networks, [empty_file]),
            (wpath.sbin,  ['scripts/wicd']),
            (wpath.daemon, ['wicd/monitor.py', 'wicd/wicd-daemon.py',
                            'wicd/suspend.py', 'wicd/autoconnect.py']),
            (wpath.backends, ['wicd/backends/be-external.py',
                              'wicd/backends/be-ioctl.py']),
            (wpath.scripts, [empty_file]),
            (wpath.predisconnectscripts, [empty_file]),
            (wpath.postdisconnectscripts, [empty_file]),
            (wpath.preconnectscripts, [empty_file]),
            (wpath.postconnectscripts, [empty_file])
        ])

        if not wpath.no_install_ncurses:
            data.append((wpath.curses, ['curses/curses_misc.py']))
            data.append((wpath.curses, ['curses/prefs_curses.py']))
            data.append((wpath.curses, ['curses/wicd-curses.py']))
            data.append((wpath.curses, ['curses/netentry_curses.py']))
            data.append((wpath.curses, ['curses/configscript_curses.py']))
            data.append((wpath.bin, ['scripts/wicd-curses']))
            if not wpath.no_install_man:
                data.append((wpath.mandir + 'man8/', ['man/wicd-curses.8']))
            if not wpath.no_install_man and not wpath.no_install_i18n_man:
                data.append((wpath.mandir + 'nl/man8/',
                             ['man/nl/wicd-curses.8']))
            if not wpath.no_install_docs:
                data.append((wpath.docdir, ['curses/README.curses']))
        if not wpath.no_install_cli:
            data.append((wpath.cli, ['cli/wicd-cli.py']))
            data.append((wpath.bin, ['scripts/wicd-cli']))
            if not wpath.no_install_man:
                data.append((wpath.mandir + 'man8/', ['man/wicd-cli.8']))
            if not wpath.no_install_docs:
                data.append((wpath.docdir, ['cli/README.cli']))
        piddir = os.path.dirname(wpath.pidfile)
        if not piddir.endswith('/'):
            piddir += '/'
        if not wpath.no_install_docs:
            data.append((wpath.docdir, ['INSTALL', 'LICENSE', 'AUTHORS',
                                        'README', 'CHANGES', ]))
            data.append((wpath.varlib, ['other/WHEREAREMYFILES']))
        if not wpath.no_install_init:
            data.append((wpath.init, [wpath.initfile]))
        if not wpath.no_install_man:
            data.append((wpath.mandir + 'man8/', ['man/wicd.8']))
            data.append((wpath.mandir + 'man5/',
                         ['man/wicd-manager-settings.conf.5']))
            data.append((wpath.mandir + 'man5/',
                         ['man/wicd-wired-settings.conf.5']))
            data.append((wpath.mandir + 'man5/',
                         ['man/wicd-wireless-settings.conf.5']))
            data.append((wpath.mandir + 'man1/', ['man/wicd-client.1']))
        if not wpath.no_install_man and not wpath.no_install_i18n_man:
            # Dutch translations of the man
            data.append((wpath.mandir + 'nl/man8/', ['man/nl/wicd.8']))
            data.append((wpath.mandir + 'nl/man5/',
                         ['man/nl/wicd-manager-settings.conf.5']))
            data.append((wpath.mandir + 'nl/man5/',
                         ['man/nl/wicd-wired-settings.conf.5']))
            data.append((wpath.mandir + 'nl/man5/',
                         ['man/nl/wicd-wireless-settings.conf.5']))
            data.append((wpath.mandir + 'nl/man1/',
                         ['man/nl/wicd-client.1']))
        if not wpath.no_install_acpi:
            data.append((wpath.resume, ['other/80-wicd-connect.sh']))
            data.append((wpath.suspend, ['other/50-wicd-suspend.sh']))
        if not wpath.no_install_pmutils:
            data.append((wpath.pmutils, ['other/55wicd']))
        print('Using pid path', os.path.basename(wpath.pidfile))
        if not wpath.no_install_i18n:
            print('Language support for', end=' ')
            for language in sorted(glob('translations/*')):
                language = language.replace('translations/', '')
                print(language, end=' ')
                data.append((wpath.translations + language + '/LC_MESSAGES/',
                             ['translations/' + language +
                              '/LC_MESSAGES/wicd.mo']))
        print()

        _install.run(self)


class test(Command):
    description = "run Wicd's unit tests"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print("importing tests")
        import tests
        print('running tests')
        tests.run_tests()


class update_message_catalog(Command):
    description = "update wicd.pot with new strings"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('pybabel extract . -o po/wicd.pot --sort-output')
        os.system('xgettext -L glade data/wicd.ui -j -o po/wicd.pot')


class update_translations(Command):
    description = "update po-files with new strings from wicd.pot"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for pofile in glob('po/*.po'):
            lang = pofile.replace('po/', '').replace('.po', '')
            os.system('pybabel update -N -o %s -i po/wicd.pot -D wicd -l %s' %
                      (pofile, lang))


class compile_translations(Command):
    description = 'compile po-files to binary mo'
    threshold = 0.8

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            import wpath
        except ImportError:
            # if there's no wpath.py, then run configure+build
            self.run_command('build')
            import wpath

        if not wpath.no_install_i18n:
            if os.path.exists('translations'):
                shutil.rmtree('translations/')
            os.makedirs('translations')

            oldlang = os.environ['LANG']
            os.environ['LANG'] = 'C'

            for pofile in sorted(glob('po/*.po')):
                lang = pofile.replace('po/', '').replace('.po', '')
                compile_po = False
                try:
                    msgfmt = subprocess.Popen(['msgfmt', '--statistics',
                                               pofile, '-o', '/dev/null'],
                                              stderr=subprocess.PIPE)
                    # let it finish, and get the exit code
                    returncode = msgfmt.wait()
                    output = msgfmt.stderr.readline().strip().decode('utf-8')
                    if len(output) == 0 or returncode != 0:
                        print(len(output), returncode)
                        raise ValueError
                    else:
                        m = re.match(r'(\d+) translated messages(?:, (\d+) '
                                     r'fuzzy translation)?(?:, (\d+) '
                                     r'untranslated messages)?.', output)
                        if m:
                            done, fuzzy, missing = m.groups()
                            fuzzy = int(fuzzy) if fuzzy else 0
                            missing = int(missing) if missing else 0

                            completeness = float(done)/(int(done) + missing +
                                                        fuzzy)
                            if completeness >= self.threshold:
                                compile_po = True
                            else:
                                print('Disabled %s (%s%% < %s%%).' %
                                      (lang, completeness*100,
                                       self.threshold*100))
                                continue
                except (OSError, ValueError):
                    print('ARGH')

                if compile_po:
                    os.makedirs('translations/' + lang + '/LC_MESSAGES/')
                    os.system('pybabel compile -D wicd -i %s -l %s -d '
                              'translations/' % (pofile, lang))

            os.environ['LANG'] = oldlang


class uninstall(Command):
    description = "remove Wicd using uninstall.sh and install.log"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system("./uninstall.sh")


py_modules = ['wicd.networking', 'wicd.misc', 'wicd.wnettools', 'wicd.wpath',
              'wicd.dbusmanager', 'wicd.logfile', 'wicd.backend',
              'wicd.configmanager', 'wicd.translations']

setup(cmdclass={'build': build,
                'configure': configure,
                'install': install,
                'uninstall': uninstall,
                'test': test,
                'clear_generated': clear_generated,
                'update_message_catalog': update_message_catalog,
                'update_translations': update_translations,
                'compile_translations': compile_translations},
      name="wicd",
      version=VERSION_NUM,
      description="A wireless and wired network manager",
      long_description="A complete network connection manager Wicd supports "
      "wired and wireless networks, and capable of creating and tracking "
      "profiles for both. It has a template-based wireless encryption system, "
      "which allows the user to easily add encryption methods used. It ships "
      "with some common encryption types, such as WPA and WEP. Wicd will "
      "automatically connect at startup to any preferred network within "
      "range.",
      author="Tom Van Braeckel, Adam Blackburn, Dan O'Reilly, Andrew Psaltis, "
      "David Paleino",
      author_email="tomvanbraeckel@gmail.com, compwiz18@gmail.com, "
      "oreilldf@gmail.com, ampsaltis@gmail.com, d.paleino@gmail.com",
      url="https://launchpad.net/wicd",
      license="http://www.gnu.org/licenses/old-licenses/gpl-2.0.html",
      py_modules=py_modules,
      data_files=data)
