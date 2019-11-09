#!/usr/bin/env python
import unittest

from io import StringIO
from os import chdir, getcwd
from shutil import rmtree
from tempfile import mkdtemp
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch  # type: ignore

from terragrunt_source import main, source2path

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
        # Create temp dir
        self.tmpdir = mkdtemp()
        self.addCleanup(rmtree, self.tmpdir)

        # Change working directory to tempdir
        self.addCleanup(chdir, getcwd())
        chdir(self.tmpdir)

    def assertTerragruntSource(self, test_output, environment, code, mesg):
        with patch(test_output, new=StringIO()) as out:
            with patch.dict('os.environ', environment, clear=True):
                with self.assertRaises(SystemExit) as cm:
                    main()

        exp = cm.exception
        self.assertEqual(exp.code, code)

        self.assertEqual(out.getvalue(), mesg)

    def assertCommon(self, hcl=False, path=False):
        module_path = '/usr/src/modules'
        mesg = module_path

        if path:
            env = {'TERRAGRUNT_REPO_PATH': module_path}
            mesg += '/repo'
        else:
            env = {'TERRAGRUNT_DEFAULT_MODULES_REPO': module_path}
        mesg += '//lambda\n'

        if hcl:
            with open('terragrunt.hcl', 'w') as f:
                f.write(HCL)
        else:
            with open('terraform.tfvars', 'w') as f:
                f.write(TFVARS)

        self.assertTerragruntSource('sys.stdout', env, 0, mesg)

    def test_valid_terraform_tfvars_file(self):
        """succeeds when terraform.tfvars is present and valid. """
        self.assertCommon(hcl=False, path=False)

    def test_valid_terraform_tfvars_file_with_path(self):
        """succeeds when terraform.tfvars is present and valid. """
        self.assertCommon(hcl=False, path=True)

    def test_valid_terragrunt_hcl_file(self):
        """succeeds when terragrunt.hcl is present and valid. """
        self.assertCommon(hcl=True, path=False)

    def test_valid_terragrunt_hcl_file_with_path(self):
        """Passes when terragrunt.hcl is present and valid & path given. """
        self.assertCommon(hcl=True, path=True)

    def test_missing_terraform_tfvars_file(self):
        """returns 2 when terraform.tfvars and terraform.hcl is missing. """
        env = {'TERRAGRUNT_DEFAULT_MODULES_REPO': '/usr/src/modules'}

        mesg = "[Errno 2] No such file or directory: 'terragrunt.hcl'\n"
        self.assertTerragruntSource('sys.stderr', env, 2, mesg)

    def test_missing_environment_var(self):
        """returns 3 when no env is set. """
        mesg = """
Environment variables TERRAGRUNT_REPO_PATH and TERRAGRUNT_DEFAULT_MODULES_REPO
are undefined! One must be defined!
"""

        self.assertTerragruntSource('sys.stderr', {}, 3, mesg)


class Source2Path(unittest.TestCase):

    def assertCommon(self, use_repo=True, add_end_slash_to_root=False):
        source = "git@github.com:org/repo.git?ref=v0.6.2"
        root = '/usr/src/modules'

        if add_end_slash_to_root:
            root += '/'

        if use_repo:
            expected = '/usr/src/modules/repo'
        else:
            expected = '/usr/src/modules'

        self.assertEqual(
            source2path(source, root, use_repo),
            expected,
        )

    def test_no_double_slash(self):
        self.assertCommon()
        self.assertCommon(use_repo=False)

    def test_root_ending_slash(self):
        self.assertCommon(add_end_slash_to_root=True)
        self.assertCommon(add_end_slash_to_root=True, use_repo=False)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    unittest.main()
