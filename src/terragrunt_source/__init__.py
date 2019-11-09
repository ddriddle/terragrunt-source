from __future__ import print_function
from builtins import str

import os
import sys

import hcl

# Python 2.x workaround
try:
    FileNotFoundError
except NameError:  # pragma: no cover
    FileNotFoundError = IOError  # pragma: no cover


class InvalidPathError(Exception):
    """Exception raised for invalid paths.

    Args:
        path: Invalid path.
    """
    def __init__(self, path):  # type: (str) -> None
        self.message = "Invalid directory path: %s" % path

    def __str__(self):  # type: () -> str
        return self.message


def terragrunt_source(filename, tfvars=False):  # type: (str, bool) -> str
    """Main function for implementing terragrunt_source.

    Args:
        filename: A Terragrunt configuration file.

    Returns:
        Returns a string usable with TERRAGRUNT_SOURCE.
    """
    root = getRoot()
    source = getSource(filename, tfvars)

    return getPath(source, root)


def getSource(filename, tfvars=False):  # type: (str, bool) -> str
    """Parses ``filename`` for the source line.

    Args:
        filename: A Terragrunt configuration file.

    Returns:
        Returns a Terraform source line.
    """
    with open(filename, 'r') as fp:
        terragrunt = hcl.load(fp)

    if tfvars:
        terragrunt = terragrunt['terragrunt']
    source = terragrunt['terraform']['source']

    return source


def getPath(source, root):  # type: (str, str) -> str
    """Calculates a terragrunt source value.

    Args:
        source: A Terraform source line.
        root: The path to a repository of module(s).

    Returns:
        Returns a string usable with TERRAGRUNT_SOURCE.
    """
    root = root.rstrip('/')

    src = source.split('//')
    module = '' if len(src) < 2 else src[1].split('?')[0]

    if module:
        root += '//' + module

    return root


def getRoot():  # type: () -> str
    """Retrieves the user supplied path to Terraform modules.

    Returns:
        Returns a system path.

    Raises:
        InvalidPathError: If the user supplied path is invalid
    """
    root = os.environ['TERRAGRUNT_DEFAULT_MODULES_REPO']

    try:  # Python 2.x
        root = root.decode('utf8')  # type: ignore
    except AttributeError:  # Python 3.x
        pass

    return root


def error(code, mesg):  # type: (int, str) -> None
    """Prints an error message and kills the program.

    Args:
        code: Exit code.
        mesg: Error message to print.
    """
    print(str(mesg), file=sys.stderr)
    exit(code)


def main():  # type: () -> None
    try:
        try:
            source = terragrunt_source('terragrunt.hcl')
        except FileNotFoundError as e:
            try:
                source = terragrunt_source('terraform.tfvars', tfvars=True)
            except FileNotFoundError:
                raise e

        if not os.path.isdir(source):
            raise InvalidPathError(source)

        print(source)
    except FileNotFoundError as e:
        error(2, str(e))
    except KeyError:
        error(3, 'Environment variable TERRAGRUNT_DEFAULT_MODULES_REPO '
                 'is undefined!')
    except InvalidPathError as e:
        error(4, str(e))

    exit(0)
