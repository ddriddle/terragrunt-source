Project description
-------------------

A Terragrunt rapid development tool to simplify overriding the
``source`` parameter in a ``terraform.tfvars`` file.


Introduction
------------

``terragrunt-source`` is a simple script that parses the source
line from the ``terraform.tfvars`` file in the current working
directory producing a path to a local source tree that can be used
by terragrunt during development. The path to the local source tree
is looked up in the environment variable ``TERRAGRUNT_REPO_PATH``
or ``TERRAGRUNT_DEFAULT_MODULES_REPO``.

This is best illustrated be an example. If you are in a directory
that contains a ``terragrunt.hcl`` file with the following content::

    include {
      path = "${find_in_parent_folders()}"
    }

    terraform {
      source = "git::git@github.com:org/repo.git//lambda?ref=v0.6.2"
    }

And if the environment variable ``TERRAGRUNT_REPO_PATH`` is set to
``/usr/src/modules`` then we expect the following output::

    $ terragrunt-source
    /usr/src/modules/repo//lambda

This is useful if we have a number of repositiories checked out in
``/usr/src/modules`` that we plan to run ``terragrunt-source``
against.  If you need to specifiy the path exactly then you can use
the environment variable ``TERRAGRUNT_DEFAULT_MODULES_REPO``. For
example if it is set to ``/usr/src/modules`` then we expect the
following output::

    $ terragrunt-source
    /usr/src/modules//lambda

Finally we can use terragrunt like so::

    $ terragrunt plan --terragrunt-source `terragrunt-source`

Another way this can be run is as follows::

    $ TERRAGRUNT_SOURCE=$(terragrunt-source) terragrunt plan

Quick start
-----------

1. Install terragrunt-source::

    $ pip install terragrunt-source

2. Append the following to your ``~/.bashrc``::

    export TERRAGRUNT_REPO_PATH=/path/to/your/checked/out/repos

    terragrunt-source() {
        TERRAGRUNT_SOURCE=$($(which terragrunt-source)) terragrunt $@
    }

3. Reload your ``~/.bashrc``::

    $ source ~/.bashrc

4. Change to a Terragrunt configuration directory::

    $ terragrunt-source plan
