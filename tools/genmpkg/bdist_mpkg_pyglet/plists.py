import os
import sys
from plistlib import Plist

import bdist_mpkg_pyglet
from bdist_mpkg_pyglet import tools


def _major_minor(v):
    rval = [0, 0]
    try:
        for i, rev in enumerate(v.version):
            rval[i] = int(rev)
    except (TypeError, ValueError, IndexError):
        pass
    return rval


def common_info(name, version):
    # Keys that can appear in any package
    name, version = str(name), tools.Version(version)
    major, minor = _major_minor(version)
    return dict(
        CFBundleGetInfoString='%s %s' % (name, version),
        CFBundleIdentifier='org.pythonmac.%s' % (name,),
        CFBundleName=name,
        CFBundleShortVersionString=str(version),
        IFMajorVersion=major,
        IFMinorRevision=minor,
        IFPkgFormatVersion=0.10000000149011612,
        IFRequirementDicts=[path_requirement('/')],
        PythonInfoDict=dict(
            PythonLongVersion=str(sys.version),
            PythonShortVersion=str(sys.version[:3]),
            PythonExecutable=str(sys.executable),
            bdist_mpkg=dict(
                version=str(bdist_mpkg_pyglet.__version__),
            ),
        ),
    )
    return defaults


def pkg_info(name, version):
    d = common_info(name, version)
    # Keys that can only appear in single packages
    d.update(dict(
        IFPkgFlagAllowBackRev=False,
        IFPkgFlagAuthorizationAction='AdminAuthorization',
        # IFPkgFlagDefaultLocation=u'/Library/Python/2.3',
        IFPkgFlagFollowLinks=True,
        IFPkgFlagInstallFat=False,
        IFPkgFlagIsRequired=False,
        IFPkgFlagOverwritePermissions=True,
        IFPkgFlagRelocatable=False,
        IFPkgFlagRestartAction='NoRestart',
        IFPkgFlagRootVolumeOnly=True,
        IFPkgFlagUpdateInstalledLangauges=False,
    ))
    return d


def path_requirement(SpecArgument, Level='requires', **kw):
    return dict(
        Level=Level,
        SpecType='file',
        SpecArgument=tools.unicode_path(SpecArgument),
        SpecProperty='NSFileType',
        TestOperator='eq',
        TestObject='NSFileTypeDirectory',
        **kw
    )


FRIENDLY_PREFIX = {
    os.path.expanduser('~/Library/Frameworks'): 'User',
    '/System/Library/Frameworks': 'Apple',
    '/Library/Frameworks': 'System',
    '/opt/local': 'DarwinPorts',
    '/usr/local': 'Unix',
    '/sw': 'Fink',
}


def python_requirement(pkgname, prefix=None, version=None, **kw):
    if prefix is None:
        prefix = sys.prefix
    if version is None:
        version = sys.version[:3]
    prefix = os.path.realpath(prefix)
    fmwkprefix = os.path.dirname(os.path.dirname(prefix))
    is_framework = fmwkprefix.endswith('.framework')
    if is_framework:
        dprefix = os.path.dirname(fmwkprefix)
    else:
        dprefix = prefix
    dprefix = tools.unicode_path(dprefix)
    name = '%s Python %s' % (FRIENDLY_PREFIX.get(dprefix, dprefix), version)
    kw.setdefault('LabelKey', name)
    title = '%s requires %s to install.' % (pkgname, name,)
    kw.setdefault('TitleKey', title)
    kw.setdefault('MessageKey', title)
    return path_requirement(prefix, **kw)


def mpkg_info(name, version, packages=list()):
    d = common_info(name, version)
    # Keys that can appear only in metapackages
    npackages = list()
    for p in packages:
        items = getattr(p, 'items', None)
        if items is not None:
            p = dict(items())
        else:
            if isinstance(p, str):
                p = [p]
            p = dict(list(zip(
                ('IFPkgFlagPackageLocation', 'IFPkgFlagPackageSelection'),
                p
            )))
        npackages.append(p)
    d.update(dict(
        IFPkgFlagComponentDirectory='./Contents/Packages',
        IFPkgFlagPackageList=npackages,
    ))
    return d


def checkpath_plugin(path):
    if not isinstance(path, str):
        path = str(path, encoding)
    return dict(
        searchPlugin='CheckPath',
        path=path,
    )


def common_description(name, version):
    name, version = str(name), tools.Version(version)
    return dict(
        IFPkgDescriptionTitle=name,
        IFPkgDescriptionVersion=str(version),
    )


def write(dct, path):
    p = Plist()
    p.update(dct)
    p.write(path)
