PACKAGE_NAME := terragrunt-source
PYTHON_VERSIONS := 2.6.9 2.7.13 3.0.1 3.1.5 3.2.5 3.3.5 3.4.8 3.5.2 3.6.5

PKG  := src/terragrunt_source
TPKG := src/tests
export TSTS := $(wildcard $(TPKG)/*.py $(TPKG)/*/*.py)
export SRCS := $(wildcard $(PKG)/*.py)
OBJS := $(patsubst %.py,%.pyc,$(SRCS))
HTML = htmlcov/index.html

.PHONY: all install test clean coverage

all: build test coverage

install: build
	pip install -e .

build: $(OBJS) setup.py
	python setup.py build

%.pyc: %.py
	python -m compileall -b $<

.python-version:
	echo ${PYTHON_VERSIONS} | xargs -n1 pyenv install -s
	pyenv local system ${PYTHON_VERSIONS}

tox: .python-version
	tox

test: .report
	@cat $?

.report: .coverage
	@coverage report > $@

.coverage: $(SRCS) $(TSTS)
	flake8 $^
	mypy $^
	@coverage run setup.py test || rm $@

coverage: $(HTML)

upload:
	python setup.py bdist_wheel
	twine upload dist/*

$(HTML): .coverage
	@coverage html

clean:
	rm -f .python-version
	-pip uninstall -y $(PACKAGE_NAME)
	rm -rf .coverage .report .summary __pycache__ htmlcov .mypy_cache .tox
	rm -rf $(TPKG)/__pycache__ $(PKG)/__pycache__ $(TPKG)/config/__pycache__
	rm -rf $(TPKG)/*.pyc  $(PKG)/*.pyc
	rm -rf build dist src/*.egg-info .eggs
