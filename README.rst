terragrunt-source
-----------------

A tool for managing the TERRAGRUNT_SOURCE environment variable
during development.

Quick start
-----------

1. Install terragrunt-source::

    $ pip install terragrunt-source

2. Append the following to your ``~/.bashrc``::

    export TERRAGRUNT_DEFAULT_MODULES_REPO=/path/to/your/checked/out/code

    terragrunt-source() {
        unset TERRAGRUNT_SOURCE
        export TERRAGRUNT_SOURCE=$($(which terragrunt-source));
        echo $TERRAGRUNT_SOURCE
    }

3. Reload your ``~/.bashrc``::

    $ source ~/.bashrc

Example
-------

1. If you are in a directory that contains a ``terraform.tfvars`` with the
following content::

    terragrunt = {
      include {
        path = "${find_in_parent_folders()}"
      }

      terraform {
        source = "git::git@github.com:org/repo.git//lambda?ref=v0.6.2"
      }
    }

2. And if your ``TERRAGRUNT_DEFAULT_MODULES_REPO`` is set to ``/usr/src/modules``.

3. Then we expect::

    $ terragrunt-source
    /usr/src/modules//lambda
    $ echo $TERRAGRUNT_SOURCE
    /usr/src/modules//lambda
