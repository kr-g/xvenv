import platform
import sys
import os
import importlib
import re
import json

import setuptools

#


def check_changelog():
    _regex = re.compile(r".*version.*\-.*\?\?\?", re.MULTILINE | re.IGNORECASE)
    with open("CHANGELOG.md") as f:
        tx = f.read()
        if re.search(_regex, tx):
            print("!!!\n" * 5, file=sys.stderr)
            print("check changelog", file=sys.stderr)
            print()
            print("!!!\n" * 5, file=sys.stderr)
            return True


def get_changelog_headers(showmax=3):
    _regex = re.compile(
        r".*version[ ]*([\w.]*)[ -]*(.*)\n", re.MULTILINE | re.IGNORECASE
    )
    with open("CHANGELOG.md") as f:
        tx = f.read()
        for m in re.finditer(_regex, tx):
            yield m.group(1), m.group(2)
            showmax -= 1
            if showmax <= 0:
                return


#


def find_version(fnam, version="VERSION"):
    with open(fnam) as f:
        cont = f.read()
    regex = f'{version}\s*=\s*["]([^"]+)["]'
    match = re.search(regex, cont)
    if match is None:
        raise Exception(
            f"version with spec={version} not found, use double quotes for version string"
        )
    return match.group(1)


def find_projectname():
    cwd = os.getcwd()
    name = os.path.basename(cwd)
    return name


def load_requirements():
    with open("requirements.txt") as f:
        lines = f.readlines()
        lines = map(lambda x: x.strip(), lines)
        lines = filter(lambda x: len(x) > 0, lines)
        lines = filter(lambda x: x[0] != "#", lines)
        return list(lines)


def do_mod_import(projectname=None, fnam="__main__"):
    if projectname is None:
        projectname = find_projectname()
    mod = importlib.import_module(f"{projectname}.{fnam}")
    return mod


def do_const_import(projectname=None):
    mod = do_mod_import(projectname, "const")
    return mod


def do_main_import(projectname=None):
    mod = do_mod_import(projectname, "__main__")
    return mod


def get_scripts(projectname):
    console_scripts = []
    gui_scripts = []

    try:
        mod = do_main_import(projectname)
        if "main_func" in dir(mod):
            console_scripts = [
                f"{projectname} = {projectname}.__main__:main_func",
            ]
        if "gui_func" in dir(mod):
            gui_scripts = [
                f"{projectname}-ui = {projectname}.__main__:gui_func",
            ]
    except:
        print("no scripts found", file=sys.stderr)

    entry_points = {
        "console_scripts": console_scripts,
        "gui_scripts": gui_scripts,
    }

    return entry_points


def find_packages(exclude=None):
    if exclude is None:
        exclude = [
            "tests",
            "docs",
        ]
    return setuptools.find_packages(exclude=exclude)


#


def load_base_settings():
    with open("setup.json") as f:
        return json.load(f)


#


def project_settings(projectname=None, fnam="const.py", version="VERSION"):

    pyver = platform.python_version_tuple()[:2]
    pyversion = ".".join(pyver)
    python_requires = f">={pyversion}"

    if projectname is None:
        projectname = find_projectname()

    file = os.path.join(projectname, fnam)
    version = find_version(file, version)

    install_requires = load_requirements()

    entry_points = get_scripts(projectname)

    packages = find_packages()

    rc = {
        "projectname": projectname,
        "pyver": pyver,
        "pyversion": pyversion,
        "file": file,
        "setuptoolsversion": setuptools.__version__,
        "setup": {
            "name": projectname,
            "version": version,
            "python_requires": python_requires,
            "install_requires": install_requires,
            "entry_points": entry_points,
            "packages": packages,
        },
    }

    return rc


def replace_settings(project_settings, base_settings):
    """replace base setting generics from project settings"""
    base_settings = dict(base_settings)
    for k, v in project_settings.items():
        if type(v) != str:
            continue
        for kk, vv in base_settings.items():
            if type(vv) != str:
                continue
            r = "{" + k + "}"
            if vv.find(r) >= 0:
                base_settings[kk] = vv.replace(r, v)
    return base_settings


# use this


def setup_settings(base_settings=None, proj_settings=None, dump=True):

    if base_settings is None:
        base_settings = load_base_settings()

    if proj_settings is None:
        proj_settings = project_settings()

    base_settings = replace_settings(proj_settings, base_settings)

    settings = dict(proj_settings["setup"])
    settings.update(base_settings)

    if dump:
        print("settings", json.dumps(settings, indent=4))

    return settings


def check_setup(prelude=True):
    rc = check_changelog()
    if rc and not prelude:
        print("last versions found")
        for v, d in get_changelog_headers():
            print(v, d)
    return rc
