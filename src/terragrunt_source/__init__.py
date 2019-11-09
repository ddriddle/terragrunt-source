from __future__ import print_function
from builtins import str
from typing import Tuple

import os
import sys

import hcl

# Python 2.x workaround
try:
    FileNotFoundError
except NameError:  # pragma: no cover
    FileNotFoundError = IOError  # pragma: no cover


def terragrunt_source():  # type: () -> str
    try:
        return getPath('terraform.tfvars', tfvars=True)
    except FileNotFoundError:
        return getPath('terragrunt.hcl')


def getPath(filename, tfvars=False):  # type: (str, bool) -> str
    root, use_repo = getRoot()

    with open(filename, 'r') as fp:
        terragrunt = hcl.load(fp)

    if tfvars:
        terragrunt = terragrunt['terragrunt']
    source = terragrunt['terraform']['source']

    return source2path(source, root, use_repo)


def source2path(source, root, use_repo):  # type: (str, str, bool) -> str
    root = root.rstrip('/')

    src = source.split('//')
    repo = src[0].split('/')[-1].rpartition('.git')[0]
    path = '' if len(src) < 2 else src[1].split('?')[0]

    if use_repo:
        root += '/' + repo

    if path:
        root += '//' + path

    return root


def getRoot():  # type: () -> Tuple[str, bool]
    use_repo = False

    try:
        root = os.environ['TERRAGRUNT_REPO_PATH']
        use_repo = True
    except KeyError:
        root = os.environ['TERRAGRUNT_DEFAULT_MODULES_REPO']

    try:  # Python 2.x
        root = root.decode('utf8')  # type: ignore
    except AttributeError:  # Python 3.x
        pass

    return root, use_repo


def error(code, mesg):  # type: (int, str) -> None
    print(str(mesg), file=sys.stderr)
    exit(code)


def main():  # type: () -> None
    try:
        print(terragrunt_source())
    except IOError as e:
        error(2, str(e))
    except KeyError:
        error(3, """
Environment variables TERRAGRUNT_REPO_PATH and TERRAGRUNT_DEFAULT_MODULES_REPO
are undefined! One must be defined!""")

    exit(0)
