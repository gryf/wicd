#!/usr/bin/env python3
#
#   Copyright (C) 2007 - 2009 Adam Blackburn
#   Copyright (C) 2007 - 2009 Dan O'Reilly
#   Copyright (C) 2009        Andrew Psaltis
#   Copyright (C) 2020        Roman Dobosz
#
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
import json
import re
import configparser
import shutil
import subprocess
from distutils import log
from distutils.command import build as _build

import pkg_resources
import setuptools
from setuptools.command import install_scripts as _install_scripts
from setuptools.command import install as _install

import wicd
from wicd import config
from wicd.config import DEFAULTS as RUNTIME_OPTS


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

DISTROS = {'/etc/redhat-release': 'redhat',
           '/etc/SuSE-release': 'suse',
           '/etc/fedora-release': 'redhat',
           '/etc/gentoo-release': 'gentoo',
           '/etc/debian_version': 'debian',
           '/etc/arch-release': 'arch',
           '/etc/slackware-version': 'slackware',
           '/etc/slamd64-version': 'slackware',
           '/etc/bluewhite64-version': 'slackware',
           '/etc/pld-release': 'pld',
           '/usr/bin/crux': 'crux',
           '/etc/lunar.release': 'lunar'}

data = []

# path to the file to put in empty directories
# fixes https://bugs.launchpad.net/wicd/+bug/503028
empty_file = 'other/.empty_on_purpose'

# change to the directory setup.py is contained in
os.chdir(os.path.abspath(os.path.split(__file__)[0]))

BUILD_OPTS = {'bin': '/usr/bin/',
              'dbus': '/etc/dbus-1/system.d/',
              'dbus_service': '/usr/share/dbus-1/system-services/',
              'distro': None,
              'docdir': '/usr/share/doc/wicd/',
              'logrotate': '/etc/logrotate.d/',
              'mandir': '/usr/share/man/',
              'scripts': '/etc/wicd/scripts/',
              'systemd': '/lib/systemd/system/',
              'resume': '/etc/acpi/resume.d/',
              'suspend': '/etc/acpi/suspend.d/',
              'pmutils': '/usr/lib/pm-utils/sleep.d/',
              'no_install_init': False,
              'no_install_man': False,
              'no_install_i18n': False,
              'no_install_i18n_man': False,
              'no_install_acpi': False,
              'no_install_pmutils': False,
              'no_install_docs': False,
              'distro_detect_failed': False,
              'init': '',
              'initfile': '',
              'initfilename': ''}


class build(_build.build):
    sub_commands = _build.build.sub_commands + [('compile_translations', None)]

    def run(self):
        if not os.path.exists('wpath.json'):
            self.run_command('configure')
        _build.build.run(self)


class configure(setuptools.Command):
    description = "configure the paths that Wicd will be installed to"

    user_options = [
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
        for key, val in BUILD_OPTS.items():
            setattr(self, key, val)
        for key, val in RUNTIME_OPTS.items():
            setattr(self, key, val)

        self.detected_distro = 'FAIL'
        for fname, distro in DISTROS.items():
            if os.path.exists(fname):
                self.detected_distro = distro
                break

        if self.detected_distro == 'FAIL':
            log.warn('WARNING: Unable to detect the distribution in use.\nIf '
                     'you have specified --distro or --init and --initfile, '
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

    def distro_check(self):
        log.info("Distro is: %s", self.distro)

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
        if (self.distro_detect_failed and not self.no_install_init and
                'FAIL' in [self.init, self.initfile]):
            log.error('ERROR: Failed to detect distro. Configure cannot '
                      'continue.\nPlease specify --init and --initfile to '
                      'continue with configuration.')  # raise?

    def run(self):
        values = list()
        for argument in self.user_options:
            if argument[0].endswith('='):
                cur_arg = argument[0][:-1]
                cur_arg_value = getattr(self, cur_arg.replace('-', '_'))
                log.info("%s is %s", cur_arg, cur_arg_value)
                values.append((cur_arg, getattr(self, cur_arg.replace('-',
                                                                      '_'))))
            else:
                cur_arg = argument[0]
                cur_arg_value = getattr(self, cur_arg.replace('-', '_'))
                log.info("Found switch %s %s", argument, cur_arg_value)
                values.append((cur_arg, bool(cur_arg_value)))

        log.info('Replacing values in template files...')
        for item in os.listdir('in'):
            if item.endswith('.in'):
                original_name = os.path.join('in', item)
                item_in = open(original_name, 'r')
                final_name = item[:-3].replace('=', '/')
                parent_dir = os.path.dirname(final_name)
                if parent_dir and not os.path.exists(parent_dir):
                    log.info('(mkdir %s)', parent_dir)
                    os.makedirs(parent_dir)
                log.info('Replacing values in %s to %s', item, final_name)
                item_out = open(final_name, 'w')
                for line in item_in.readlines():
                    for item, value in values:
                        line = line.replace('%' + str(item.upper())
                                            .replace('-', '_') + '%',
                                            str(value))

                    # other things to replace that aren't arguments
                    line = line.replace('%VERSION%', VERSION_NUM)
                    line = line.replace('%REVNO%', REVISION_NUM)
                    line = line.replace('%CURSES_REVNO%', CURSES_REVNO)

                    item_out.write(line)

                item_out.close()
                item_in.close()
                shutil.copymode(original_name, final_name)

        # create wpath.json and changed options for wicd.conf
        opts = {}
        for key in BUILD_OPTS:
            opts[key] = getattr(self, key)

        conf = {}
        for key, val in RUNTIME_OPTS.items():
            opts[key] = getattr(self, key)
            if opts[key] != val:
                conf[key] = opts[key]

        with open('wpath.json', 'w') as fobj:
            json.dump(opts, fobj)

        # write changed paths used in runtime as the config file.
        if conf:
            parser = configparser.ConfigParser()
            parser.add_section('wicd')
            for key, val in conf.items():
                parser.set('wicd', key, str(val))

            with open('data/etc/wicd.conf', 'w') as fobj:
                parser.write(fobj)
        else:
            try:
                os.unlink('data/etc/wicd.conf')
            except FileNotFoundError:
                pass


class install_scripts(_install_scripts.install_scripts):
    def write_script(self, script_name, contents, mode="t", *ignored):
        """Write an executable file to the scripts directory"""
        from setuptools.command.easy_install import chmod, current_umask

        log.info("Installing %s script to %s", script_name, self.install_dir)
        install_dir = self.install_dir
        if script_name == 'wicd':
            install_dir = os.path.join(
                self.install_dir[:self.install_dir.rfind('bin')], 'sbin')
        target = os.path.join(install_dir, script_name)
        self.outfiles.append(target)

        mask = current_umask()
        if not self.dry_run:
            pkg_resources.ensure_directory(target)
            f = open(target, "w" + mode)
            f.write(contents)
            f.close()
            chmod(target, 0o777 - mask)


class clear_generated(setuptools.Command):
    description = 'clears out files generated by configure'

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        log.info('Removing completed template files...')
        for item in os.listdir('in'):
            if item.endswith('.in'):
                final_name = item[:-3].replace('=', '/')
                if os.path.exists(final_name):
                    os.remove(final_name)
                    log.info('Removing completed %s (%s)', final_name, item)
                else:
                    log.info('%s Does not exist.', final_name)
        log.info('Removing compiled translation files...')
        if os.path.exists('translations'):
            shutil.rmtree('translations/')
        os.makedirs('translations/')


class install(_install.install):
    def run(self):
        try:
            with open('wpath.json') as fobj:
                wpath = config.Config(json.load(fobj))
        except FileNotFoundError:
            self.run_command('build')
            with open('wpath.json') as fobj:
                wpath = config.Config(json.load(fobj))

        data.extend([(wpath.log, [empty_file]),
                     (wpath.networks, [empty_file]),
                     (wpath.scripts, [empty_file]),
                     (wpath.predisconnectscripts, [empty_file]),
                     (wpath.postdisconnectscripts, [empty_file]),
                     (wpath.preconnectscripts, [empty_file]),
                     (wpath.postconnectscripts, [empty_file])])

        if not wpath.no_install_docs:
            data.append((wpath.docdir, ['AUTHORS', 'CHANGES', 'INSTALL',
                                        'LICENSE', 'README.cli',
                                        'README.curses', 'README.old',
                                        'README.rst']))
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
            data.append((wpath.mandir + 'man8/', ['man/wicd-curses.8']))
            data.append((wpath.mandir + 'man8/', ['man/wicd-cli.8']))

            if not wpath['no_install_i18n_man']:
                # Dutch translations of the man
                data.append((wpath.mandir + 'nl/man8/', ['man/nl/wicd.8']))
                data.append((wpath.mandir + 'nl/man5/',
                             ['man/nl/wicd-manager-settings.conf.5']))
                data.append((wpath.mandir + 'nl/man5/',
                             ['man/nl/wicd-wired-settings.conf.5']))
                data.append((wpath.mandir + 'nl/man5/',
                             ['man/nl/wicd-wireless-settings.conf.5']))
                data.append((wpath.mandir + 'nl/man8/',
                             ['man/nl/wicd-curses.8']))

        # TODO(gryf): sort out paths for pmutils/acpi
        if not wpath.no_install_acpi:
            data.append((wpath.resume, ['other/80-wicd-connect.sh']))
            data.append((wpath.suspend, ['other/50-wicd-suspend.sh']))
        if not wpath.no_install_pmutils:
            data.append((wpath.pmutils, ['other/55wicd']))

        log.info('Using pid path %s', os.path.basename(wpath.pidfile))

        if not wpath.no_install_i18n:
            for language in sorted(glob('translations/*')):
                language = language.replace('translations/', '')
                log.info('Language support for %s', language)
                data.append((os.path.join(wpath.translations, language,
                                          '/LC_MESSAGES/'),
                             [os.path.join('translations/', language,
                                           'LC_MESSAGES', 'wicd.mo')]))

        for dir_ in (os.listdir('data')):
            path = os.path.join('data', dir_)
            for fname in os.listdir(path):
                data.append((wpath[dir_], [os.path.join(path, fname)]))

        _install.install.run(self)


class test(setuptools.Command):
    description = "run Wicd's unit tests"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        log.info("importing tests")
        import tests
        log.info('running tests')
        tests.run_tests()


class update_message_catalog(setuptools.Command):
    description = "update wicd.pot with new strings"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('pybabel extract . -o po/wicd.pot --sort-output')
        os.system('xgettext -L glade data/wicd.ui -j -o po/wicd.pot')


class update_translations(setuptools.Command):
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


class compile_translations(setuptools.Command):
    description = 'compile po-files to binary mo'
    threshold = 0.8

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            with open('wpath.json') as fobj:
                wpath = config.Config(json.load(fobj))
        except FileNotFoundError:
            self.run_command('build')
            with open('wpath.json') as fobj:
                wpath = config.Config(json.load(fobj))

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
                        log.info("%s %s", len(output), returncode)
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
                                log.info('Disabled %s (%s%% < %s%%).',
                                         lang, completeness*100,
                                         self.threshold*100)
                                continue
                except (OSError, ValueError):
                    log.error('ARGH. Yeah, seriosuly.')

                if compile_po:
                    os.makedirs('translations/' + lang + '/LC_MESSAGES/')
                    os.system('pybabel compile -D wicd -i %s -l %s -d '
                              'translations/' % (pofile, lang))

            os.environ['LANG'] = oldlang


class uninstall(setuptools.Command):
    description = "remove Wicd using uninstall.sh and install.log"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system("./uninstall.sh")


setuptools.setup(cmdclass={'build': build,
                           'configure': configure,
                           'install': install,
                           'install_scripts': install_scripts,
                           'test': test,
                           'clear_generated': clear_generated,
                           'update_message_catalog': update_message_catalog,
                           'update_translations': update_translations,
                           'compile_translations': compile_translations},
                 version=VERSION_NUM,
                 description="",
                 long_description=__doc__,
                 url="https://launchpad.net/wicd",
                 license="http://www.gnu.org/licenses/old-licenses/gpl-2.0"
                 ".html",
                 data_files=data)
