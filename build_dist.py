"""This module is a project-specified PEP 517-compliant backend.  It is not
intended to be used directly, but through a PEP 517-compliant frontend, e.g.,
pip.

"""
import json
import os
import os.path
import platform
import re
import shutil
import sys
import tarfile
from tempfile import NamedTemporaryFile
from urllib.request import HTTPError, Request, urlopen
import warnings
from zipfile import ZipFile

from flit_core import buildapi

from iterfzf import __fzf_version__, __version__

__all__ = [
    'build_editable',
    'build_sdist',
    'build_wheel',
    'get_requires_for_build_sdist',
    'get_requires_for_build_wheel',
]


release_url = ('https://api.github.com/repos/junegunn/fzf/releases/tags/' +
               __fzf_version__)
github_token = os.environ.get('GITHUB_TOKEN')
fzf_release_filename = 'fzf-{0}-release.json'.format(__fzf_version__)
fzf_release_path = os.path.join(os.path.dirname(__file__), 'iterfzf',
                                fzf_release_filename)
asset_filename_re = re.compile(
    r'^fzf-(?P<ver>\d+\.\d+\.\d+)-'
    r'(?P<goos>[^-_]+)_(?P<goarch>[^.]+)'
    r'.(?P<ext>tgz|tar\.gz|tar\.bz2|zip)$'
)
fzf_bin_path = os.path.join(os.path.dirname(__file__), 'iterfzf', 'fzf')
fzf_windows_bin_path = os.path.join(os.path.dirname(__file__),
                                    'iterfzf', 'fzf.exe')
urllib_retry = 3
wheel_filename_platform_tag_pattern = re.compile(
    r'(?<=-py3-none-)any(?=\.whl$)',
    re.IGNORECASE
)


def download_fzf_release_json(access_token=None):
    if access_token:
        request = Request(
            release_url,
            headers={'Authorization': 'token ' + access_token},
        )
    else:
        request = release_url
    try:
        r = urlopen(request)
    except HTTPError as e:
        if e.code == 403 and e.info().get('X-RateLimit-Remaining') == 0:
            raise RuntimeError(
                'GitHub rate limit reached. To increase the limit configure '
                'environment variable GITHUB_TOKEN.\n  ' + str(e)
            )
        elif e.code == 401 and access_token:
            raise RuntimeError('Invalid GitHub access token.')
        raise
    d = r.read().decode("utf-8")
    r.close()
    try:
        with open(fzf_release_path, 'w', encoding='utf-8') as f:
            f.write(d)
    except IOError:
        pass
    return json.loads(d)


def get_fzf_release(access_token=None):
    try:
        with open(fzf_release_path, encoding='utf-8') as f:
            return json.load(f)
    except IOError:
        return download_fzf_release_json(access_token)


def get_fzf_binary_url(goos, goarch, access_token=None):
    release = get_fzf_release(access_token=access_token)
    for asset in release['assets']:
        m = asset_filename_re.match(asset['name'])
        if not m:
            warnings.warn('unmatched filename: ' + repr(asset['name']))
            continue
        elif m.group('ver') != __fzf_version__:
            warnings.warn('unmatched version: ' + repr(asset['name']))
            continue
        elif m.group('goos') == goos and m.group('goarch') == goarch:
            return asset['browser_download_url'], m.group('ext')


def extract(stream, ext, extract_to):
    with NamedTemporaryFile() as tmp:
        shutil.copyfileobj(stream, tmp)
        tmp.flush()
        tmp.seek(0)
        if ext == 'zip':
            z = ZipFile(tmp, 'r')
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


def download_fzf_binary(goos, goarch, overwrite=False, access_token=None):
    bin_path = fzf_windows_bin_path if goos == 'windows' else fzf_bin_path
    if overwrite and os.path.isfile(bin_path):
        os.unlink(fzf_bin_path)
    if overwrite and os.path.isfile(fzf_windows_bin_path):
        os.unlink(fzf_windows_bin_path)
    if not os.path.isfile(bin_path):
        asset = get_fzf_binary_url(goos, goarch, access_token)
        url, ext = asset
        if access_token:
            url = '{0}?access_token={1}'.format(url, access_token)
        try:
            r = urlopen(url)
        except HTTPError as e:
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


# Map from pairs of GOOS and GOARCH to Python platform tags.  Note that
# it does not cover all possible combinations, but only those that are
# provided by the official fzf binaries.
# See also:
#   https://go.dev/doc/install/source#environment
#   https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/#platform-tag
#   https://github.com/python/cpython/blob/main/Tools/c-analyzer/distutils/util.py
goos_goarch_platform_tag_map = {
    # GOOS,     GOARCH,    Python platform tag
    ("darwin",  "amd64"):   "macosx_10_7_x86_64.macosx_10_9_x86_64",
    ("darwin",  "arm64"):   "macosx_11_0_arm64",
    ("freebsd", "amd64"):   "freebsd_13_1_release_p1_amd64"
                            ".freebsd_13_1_release_p2_amd64"
                            ".freebsd_13_2_release_p1_amd64"
                            ".freebsd_13_2_release_p2_amd64"
                            ".freebsd_13_2_release_p3_amd64",
    ("linux",   "amd64"):   "manylinux_1_2_x86_64.manylinux_2_17_x86_64"
                            ".manylinux2014_x86_64",
    ("linux",   "arm64"):   "manylinux_1_2_aarch64.manylinux_2_17_aarch64"
                            ".manylinux2014_aarch64",
    ("linux",   "armv5"):   "manylinux_1_2_armv5l",
    ("linux",   "armv6"):   "manylinux_1_2_armv6l",
    ("linux",   "armv7"):   "manylinux_1_2_armv7l",
    ("linux",   "ppc64le"): "manylinux_2_17_ppc64le.manylinux2014_ppc64le",
    ("linux",   "s390x"):   "manylinux_2_17_s390x.manylinux2014_s390x",
    ("windows", "amd64"):   "win_amd64",
    ("windows", "arm64"):   "win_arm64",
}

# Map from pairs of Python sys.platform and platform.machine() to
# pairs of GOOS and GOARCH.  The order of the keys corresponds to
# the goos_goarch_platform_tag_map above.
platform_machine_goos_goarch_map = {
    # sys.platform, platform.machine(), GOOS,      GOARCH
    ("darwin",      "x86_64"):         ("darwin",  "amd64"),
    ("darwin",      "arm64"):          ("darwin",  "arm64"),
    ("freebsd7",    "amd64"):          ("freebsd", "amd64"),
    ("freebsd8",    "amd64"):          ("freebsd", "amd64"),
    ("freebsdN",    "amd64"):          ("freebsd", "amd64"),
    ("linux",       "x86_64"):         ("linux",   "amd64"),
    ("linux",       "aarch64"):        ("linux",   "arm64"),
    ("linux",       "armv5l"):         ("linux",   "armv5"),
    ("linux",       "armv6l"):         ("linux",   "armv6"),
    ("linux",       "armv7l"):         ("linux",   "armv7"),
    ("linux",       "ppc64le"):        ("linux",   "ppc64le"),
    ("linux",       "s390x"):          ("linux",   "s390x"),
    ("win32",       "AMD64"):          ("windows", "amd64"),
    ("win32",       "aarch64"):        ("windows", "arm64"),
    ("cygwin",      "x86_64"):         ("windows", "amd64"),
    ("cygwin",      "aarch64"):        ("windows", "arm64"),
}


def get_goos_goarch():
    goos = os.environ.get("GOOS")
    goarch = os.environ.get("GOARCH")
    if goos and not goarch:
        warnings.warn(
            "GOOS is ignored because GOARCH is not set; they must be set "
            "together")
    elif goarch and not goos:
        warnings.warn(
            "GOARCH is ignored because GOOS is not set; they must be set "
            "together")
    elif goos and goarch:
        return goos, goarch
    key = sys.platform, platform.machine()
    try:
        return platform_machine_goos_goarch_map[key]
    except KeyError:
        raise RuntimeError("unsupported platform: " + repr(key))


def bundle_fzf():
    goos, goarch = get_goos_goarch()
    download_fzf_binary(
        goos,
        goarch,
        overwrite="GOOS" in os.environ and "GOARCH" in os.environ,
        access_token=github_token
    )


def build_wheel(
    wheel_directory, config_settings=None, metadata_directory=None
):
    bundle_fzf()
    wheel_filename = buildapi.build_wheel(
        wheel_directory, config_settings, metadata_directory
    )
    goos, goarch = get_goos_goarch()
    platform_tag = goos_goarch_platform_tag_map[goos, goarch]
    new_filename = wheel_filename_platform_tag_pattern.sub(
        platform_tag,
        wheel_filename
    )
    os.rename(
        os.path.join(wheel_directory, wheel_filename),
        os.path.join(wheel_directory, new_filename),
    )
    return new_filename


def build_sdist(sdist_directory, config_settings=None):
    download_fzf_release_json(github_token)
    return buildapi.build_sdist(sdist_directory, config_settings)


if callable(getattr(buildapi, "build_editable", None)):
    def build_editable(
        wheel_directory, config_settings=None, metadata_directory=None
    ):
        bundle_fzf()
        return buildapi.build_editable(
            wheel_directory, config_settings, metadata_directory
        )


def get_requires_for_build_sdist(config_settings=None):
    if callable(getattr(buildapi, "get_requires_for_build_sdist", None)):
        return buildapi.get_requires_for_build_sdist(config_settings)
    return []


def get_requires_for_build_wheel(config_settings=None):
    if callable(getattr(buildapi, "get_requires_for_build_wheel", None)):
        return buildapi.get_requires_for_build_wheel(config_settings)
    return []


def get_requires_for_build_editable(config_settings=None):
    if callable(getattr(buildapi, "get_requires_for_build_wheel", None)):
        return buildapi.get_requires_for_build_editable(config_settings)
    return []


if callable(getattr(buildapi, "prepare_metadata_for_build_wheel", None)):
    prepare_metadata_for_build_wheel = (
        buildapi.prepare_metadata_for_build_wheel
    )
    __all__.append("prepare_metadata_for_build_wheel")


if callable(getattr(buildapi, "prepare_metadata_for_build_editable", None)):
    prepare_metadata_for_build_editable = (
        buildapi.prepare_metadata_for_build_editable
    )
    __all__.append("prepare_metadata_for_build_editable")
