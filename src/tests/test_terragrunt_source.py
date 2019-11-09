#!/usr/bin/env python
import os
import unittest

from io import StringIO
from os import chdir, getcwd
from shutil import rmtree
from tempfile import mkdtemp
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch  # type: ignore

from terragrunt_source import main, getPath

TFVARS = """
terragrunt = {
  include {
    path = "${find_in_parent_folders()}"
  }

  terraform {
    source = "git@github.com:org/repo.git//lambda?ref=v0.6.2"
  }
}
"""

HCL = """
include {
  path = "${find_in_parent_folders()}"
}

terraform {
  source = "git@github.com:org/repo.git//lambda?ref=v0.6.2"
}
"""


class TerragruntSource(unittest.TestCase):
    """ Full integration tests """

    def setUp(self):
        # Create temp modules dir
        self.modules_path = mkdtemp()
        self.addCleanup(rmtree, self.modules_path)

        # Create temp working dir
        self.tmpdir = mkdtemp()
        self.addCleanup(rmtree, self.tmpdir)

        # Change working directory to tempdir
        self.addCleanup(chdir, getcwd())
        chdir(self.tmpdir)

    def assertTerragruntSourcePrints(self, environment, code, mesg):
        """Test ``main()`` return status and output to stdout and stderr.

        Args:
            environment (Dict[str]): Environment variables to pass.
            code (int): The expected return code.
            mesg (str): The expected messsage returned.

        """
        with patch('sys.stdout', new=StringIO()) as stdout:
            with patch('sys.stderr', new=StringIO()) as stderr:
                with patch.dict('os.environ', environment, clear=True):
                    with self.assertRaises(SystemExit) as cm:
                        main()

        exp = cm.exception
        self.assertEqual(exp.code, code, stderr.getvalue())

        out = stderr if code else stdout
        self.assertEqual(out.getvalue(), mesg)

    def assertCommon(self, hcl=False, mkdir=True, code=0, mesg="%s"):
        modules_path = self.modules_path
        module = '//lambda'

        mesg = mesg % (modules_path + module) + '\n'

        env = {'TERRAGRUNT_DEFAULT_MODULES_REPO': modules_path}
        if mkdir:
            os.mkdir(modules_path + module)

        if hcl:
            with open('terragrunt.hcl', 'w') as f:
                f.write(HCL)
        else:
            with open('terraform.tfvars', 'w') as f:
                f.write(TFVARS)

        self.assertTerragruntSourcePrints(env, code, mesg)

    def test_valid_terraform_tfvars_file(self):
        """succeeds when terraform.tfvars is present and valid. """
        self.assertCommon(hcl=False)

    def test_valid_terragrunt_hcl_file(self):
        """succeeds when terragrunt.hcl is present and valid. """
        self.assertCommon(hcl=True)

    def test_missing_terraform_tfvars_file(self):
        """returns 2 when terraform.tfvars and terraform.hcl are missing. """
        env = {'TERRAGRUNT_DEFAULT_MODULES_REPO': self.modules_path}

        mesg = "[Errno 2] No such file or directory: 'terragrunt.hcl'\n"
        self.assertTerragruntSourcePrints(env, 2, mesg)

    def test_missing_environment_var(self):
        """returns 3 when TERRAGRUNT_DEFAULT_MODULES_REPO is unset. """
        mesg = "Environment variable TERRAGRUNT_DEFAULT_MODULES_REPO " \
               "is undefined!\n"

        self.assertTerragruntSourcePrints({}, 3, mesg)

    def test_bad_paths(self):
        """returns 1 when TERRAGRUNT_DEFAULT_MODULES_REPO is unset. """
        mesg = "Invalid directory path: %s"

        self.assertCommon(hcl=True, mkdir=False, code=4, mesg=mesg)


class SourceLineTests(unittest.TestCase):

    def assertCommon(self, add_end_slash_to_root=False):
        source = "git@github.com:org/repo.git?ref=v0.6.2"
        root = '/usr/src/modules'

        if add_end_slash_to_root:
            root += '/'

        self.assertEqual(
            getPath(source, root),
            '/usr/src/modules',
        )

    def test_no_double_slash(self):
        self.assertCommon()

    def test_root_ending_slash(self):
        self.assertCommon(add_end_slash_to_root=True)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    unittest.main()
