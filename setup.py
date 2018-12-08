import distutils.core
import distutils.errors
import json
import os
import os.path
import platform
import re
import shutil
import sys
import tarfile
import tempfile
import warnings
import zipfile

try:
    import urllib2
except ImportError:
    from urllib import request as urllib2

from setuptools import setup


fzf_version = '0.17.5'
version = '0.5.' + fzf_version
release_url = ('https://api.github.com/repos/junegunn/fzf-bin/releases/tags/' +
               fzf_version)
asset_filename_re = re.compile(
    r'^fzf-(?P<ver>\d+\.\d+\.\d+)-'
    r'(?P<plat>[^-]+)_(?P<arch>[^.]+)'
    r'.(?P<ext>tgz|tar\.gz|tar\.bz2|zip)$'
)
fzf_bin_path = os.path.join(os.path.dirname(__file__), 'iterfzf', 'fzf')
fzf_windows_bin_path = os.path.join(os.path.dirname(__file__),
                                    'iterfzf', 'fzf.exe')
urllib_retry = 3


def readme():
    path = os.path.join(os.path.dirname(__file__), 'README.rst')
    try:
        with open(path) as f:
            return f.read()
    except IOError:
        pass


def get_fzf_release(access_token=None):
    filename = 'fzf-{0}-release.json'.format(fzf_version)
    filepath = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(filepath) as f:
            d = f.read()
    except IOError:
        url = release_url
        if access_token:
            url = '{0}?access_token={1}'.format(url, access_token)
        try:
            r = urllib2.urlopen(url)
        except urllib2.HTTPError as e:
            if e.code == 403 and e.info().get('X-RateLimit-Remaining') == 0:
                raise RuntimeError(
                    'GitHub rate limit reached. To increate the limit use '
                    '-g/--github-access-token option.\n  ' + str(e)
                )
            elif e.code == 401 and access_token:
                raise RuntimeError('Invalid GitHub access token.')
            raise
        d = r.read()
        r.close()
        mode = 'w' + ('b' if isinstance(d, bytes) else '')
        try:
            with open(filename, mode) as f:
                f.write(d)
        except IOError:
            pass
    try:
        return json.loads(d)
    except TypeError:
        return json.loads(d.decode('utf-8'))


def get_fzf_binary_url(plat, arch, access_token=None):
    release = get_fzf_release(access_token=access_token)
    for asset in release['assets']:
        m = asset_filename_re.match(asset['name'])
        if not m:
            warnings.warn('unmatched filename: ' + repr(asset['name']))
            continue
        elif m.group('ver') != fzf_version:
            warnings.warn('unmatched version: ' + repr(asset['name']))
            continue
        elif m.group('plat') == plat and m.group('arch') == arch:
            return asset['browser_download_url'], m.group('ext')


def extract(stream, ext, extract_to):
    with tempfile.NamedTemporaryFile() as tmp:
        shutil.copyfileobj(stream, tmp)
        tmp.flush()
        tmp.seek(0)
        if ext == 'zip':
            z = zipfile.ZipFile(tmp, 'r')
            try:
                info, = z.infolist()
                with open(extract_to, 'wb') as f:
                    f.write(z.read(info))
            finally:
                z.close()
        elif ext == 'tgz' or ext.startswith('tar.'):
            tar = tarfile.open(fileobj=tmp)
            try:
                member, = [m for m in tar.getmembers() if m.isfile()]
                rf = tar.extractfile(member)
                with open(extract_to, 'wb') as wf:
                    shutil.copyfileobj(rf, wf)
            finally:
                tar.close()
        else:
            raise ValueError('unsupported file format: ' + repr(ext))


def download_fzf_binary(plat, arch, overwrite=False, access_token=None):
    bin_path = fzf_windows_bin_path if plat == 'windows' else fzf_bin_path
    if overwrite or not os.path.isfile(bin_path):
        asset = get_fzf_binary_url(plat, arch, access_token)
        url, ext = asset
        if access_token:
            url = '{0}?access_token={1}'.format(url, access_token)
        try:
            r = urllib2.urlopen(url)
        except urllib2.HTTPError as e:
            if e.code == 403 and e.info().get('X-RateLimit-Remaining') == 0:
                raise RuntimeError(
                    'GitHub rate limit reached. To increate the limit use '
                    '-g/--github-access-token option.\n  ' + str(e)
                )
            elif e.code == 401 and access_token:
                raise RuntimeError('Invalid GitHub access token.')
            raise
        extract(r, ext, bin_path)
        r.close()
    mode = os.stat(bin_path).st_mode
    if not (mode & 0o111):
        os.chmod(bin_path, mode | 0o111)


def get_current_plat_arch():
    archs = {
        'i686': '386', 'i386': '386',
        'x86_64': 'amd64', 'amd64': 'amd64',
    }
    machine = platform.machine()
    if not machine and sys.platform in ('win32', 'cygwin'):
        bits, linkage = platform.architecture()
        try:
            machine = {'32bit': 'i386', '64bit': 'amd64'}[bits]
        except KeyError:
            raise ValueError('unsupported architecture: ' +
                             repr((bits, linkage)))
    machine = machine.lower()
    if sys.platform.startswith('linux'):
        archs.update(
            armv5l='arm5', armv6l='arm6', armv7l='arm7', armv8l='arm8',
        )
    try:
        arch = archs[machine]
    except KeyError:
        raise ValueError('unsupported machine: ' + repr(machine))
    if sys.platform.startswith('linux'):
        return 'linux', arch
    elif sys.platform.startswith('freebsd'):
        return 'freebsd', arch
    elif sys.platform.startswith('openbsd'):
        return 'freebsd', arch
    elif sys.platform == 'darwin':
        return 'darwin', arch
    elif sys.platform in ('win32', 'cygwin'):
        return 'windows', arch
    else:
        raise ValueError('unsupported platform: ' + repr(sys.platform))


class bundle_fzf(distutils.core.Command):

    description = 'download and bundle a fzf binary'
    user_options = [
        ('plat=', 'p', 'platform e.g. windows, linux, freebsd, darwin'),
        ('arch=', 'a', 'architecture e.g. 386, amd64, arm8'),
        ('no-overwrite', 'O', 'do not overwrite if fzf binary exists'),
        (
            'github-access-token=', 'g',
            'GitHub API access token to increate the rate limit',
        ),
    ]
    boolean_options = ['no-overwrite']

    def initialize_options(self):
        try:
            self.plat, self.arch = get_current_plat_arch()
        except ValueError:
            self.plat = None
            self.arch = None
        self.no_overwrite = None
        self.github_access_token = None
        self.plat_name = None

    def finalize_options(self):
        if self.plat is None:
            raise distutils.errors.DistutilsOptionError(
                '-p/--plat option is required but missing'
            )
        if self.arch is None:
            raise distutils.errors.DistutilsOptionError(
                '-a/--arch option is required but missing'
            )
        try:
            self.plat_name = self.get_plat_name()
        except ValueError as e:
            raise distutils.errors.DistutilsOptionError(str(e))
        distutils.log.info('plat_name: %s', self.plat_name)

    def get_plat_name(self, plat=None, arch=None):
        plat = plat or self.plat
        arch = arch or self.arch
        if plat == 'linux':
            arch_tags = {
                '386': 'i686', 'amd64': 'x86_64',
                'arm5': 'armv5l', 'arm6': 'armv6l',
                'arm7': 'armv7l', 'arm8': 'armv8l',
            }
            try:
                arch_tag = arch_tags[arch]
            except KeyError:
                raise ValueError('unsupported arch: ' + repr(arch))
            return 'manylinux1_' + arch_tag
        elif plat in ('freebsd', 'openbsd'):
            arch_tags = {'386': 'i386', 'amd64': 'amd64'}
            try:
                arch_tag = arch_tags[arch]
            except KeyError:
                raise ValueError('unsupported arch: ' + repr(arch))
            return '{0}_{1}'.format(plat, arch_tag)
        elif plat == 'darwin':
            if arch == '386':
                archs = 'i386',
            elif arch == 'amd64':
                archs = 'intel', 'x86_64'
            else:
                raise ValueError('unsupported arch: ' + repr(arch))
            macs = 10, 11, 12
            return '.'.join('macosx_10_{0}_{1}'.format(mac, arch)
                            for mac in macs for arch in archs)
        elif plat == 'windows':
            if arch == '386':
                return 'win32'
            elif arch == 'amd64':
                return 'win_amd64'
            else:
                raise ValueError('unsupported arch: ' + repr(arch))
        else:
            raise ValueError('unsupported plat: ' + repr(plat))

    def run(self):
        dist = self.distribution
        try:
            bdist_wheel = dist.command_options['bdist_wheel']
        except KeyError:
            self.warn(
                'this comamnd is intended to be used together with bdist_wheel'
                ' (e.g. "{0} {1} bdist_wheel")'.format(
                    dist.script_name, ' '.join(dist.script_args)
                )
            )
        else:
            typename = type(self).__name__
            bdist_wheel.setdefault('universal', (typename, True))
            plat_name = self.plat_name
            bdist_wheel.setdefault('plat_name', (typename, plat_name))
            bdist_wheel_cls = dist.cmdclass['bdist_wheel']
            get_tag_orig = bdist_wheel_cls.get_tag

            def get_tag(self):  # monkeypatch bdist_wheel.get_tag()
                if self.plat_name_supplied and self.plat_name == plat_name:
                    return get_tag_orig(self)[:2] + (plat_name,)
                return get_tag_orig(self)
            bdist_wheel_cls.get_tag = get_tag
        download_fzf_binary(self.plat, self.arch,
                            overwrite=not self.no_overwrite,
                            access_token=self.github_access_token)
        if dist.package_data is None:
            dist.package_data = {}
        dist.package_data.setdefault('iterfzf', []).append(
            'fzf.exe' if self.plat == 'windows' else 'fzf'
        )


setup(
    name='iterfzf',
    version=version,
    description='Pythonic interface to fzf',
    long_description=readme(),
    url='https://github.com/dahlia/iterfzf',
    author='Hong Minhee',
    author_email='hong.minhee' '@' 'gmail.com',
    license='GPLv3 or later',
    packages=['iterfzf'],
    package_data={'iterfzf': ['py.typed']},
    cmdclass={'bundle_fzf': bundle_fzf},
    python_requires='>=2.6.0',
    install_requires=['setuptools'],
    zip_safe=False,
    include_package_data=True,
    download_url='https://github.com/dahlia/iterfzf/releases',
    keywords='fzf',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console :: Curses',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',  # noqa: E501
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Operating System :: POSIX :: BSD :: OpenBSD',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Terminals',
    ]
)
