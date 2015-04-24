# Copyright 2015 Canonical Ltd.
# Makefile for beaver charm.

export JUJU_TEST_CHARM=beaver
export JUJU_REPOSITORY=

SYSDEPS = charm-tools juju-core juju-local \
    pep8 python-apt python-coverage python-mock python-nose \
    python-yaml rsync
TESTS = $(shell find -L tests -type f -executable | sort)
JUJU_ENV=local

PYTHON = python
VENV = .venv
VENV_ACTIVATE = $(VENV)/bin/activate
NOSE = $(VENV)/bin/nosetests
PIP = $(VENV)/bin/pip

# Keep phony targets in alphabetical order.
.PHONY: $(TESTS) clean check deploy help sync sysdeps test unittest amulettests

all: help

deploy:
	# The use of readlink below is required for OS X.
	$(eval export JUJU_REPOSITORY:=$(shell mktemp -d `readlink -f /tmp`/temp.XXXX))
	@echo "JUJU_REPOSITORY is $(JUJU_REPOSITORY)"
	# Setting up the Juju repository.
	mkdir $(JUJU_REPOSITORY)/trusty
	rsync -a . $(JUJU_REPOSITORY)/trusty/beaver --exclude .git --exclude tests
	juju deploy cs:~evarlast/trusty/apache2
	juju deploy local:trusty/beaver
	juju deploy cs:~evarlast/trusty/logstash
	juju add-relation apache2 beaver
	juju add-relation logstash beaver
	juju set apache2 vhost_http_template=$(shell base64 -w0<tests/apache2.template)

clean:
	-$(RM) -rf ${VENV} .coverage

check:
	find hooks tests -name '*.py' | xargs pep8
	juju charm proof

help:
	@echo -e 'beaver charm - list of make targets:\n'
	@echo 'make unittest - Run Python unit tests.'
	@echo 'make test - Run unit tests and functional tests.'
	@echo '     Functional tests are run bootstrapping the current default'
	@echo '     Juju environment.'
	@echo 'make check - Run Python linter and charm proof.'
	@echo 'make deploy - Deploy local charm from a temporary local repository.'
	@echo '     The charm is deployed to the current default Juju environment.'
	@echo '     The environment must be already bootstrapped.'
	@echo 'make lint - Lint the python code.'
	@echo 'make sync - Synchronize/update the charm helpers library.'
	@echo 'make sysdeps - Install system deb dependencies.'

.PHONY: lint
lint:
	find hooks tests -name *.py | xargs pep8

sync: charm-helpers.yaml
	scripts/charm_helpers_sync.py -d lib/charmhelpers -c charm-helpers.yaml

sysdeps:
	sudo apt-get install --yes $(SYSDEPS)

$(VENV_ACTIVATE): test-requirements.pip
	virtualenv --distribute -p $(PYTHON) $(VENV)
	$(PIP) install -r test-requirements.pip || \
		(touch test-requirements.pip; exit 1)
	@touch $(VENV_ACTIVATE)

.PHONY: testdeps
testdeps: $(VENV_ACTIVATE)

.PHONY: $(TESTS)
$(TESTS): testdeps
	. $(VENV_ACTIVATE); JUJU_ENV=$(JUJU_ENV) $@

test: lint unittest amulettests

unittest:
	nosetests -v --nocapture --with-coverage --cover-package hooks hooks

.PHONY: bootstrap_env
bootstrap_env:
	juju bootstrap -e $(JUJU_ENV)

.PHONY: destroy_env
destroy_env:
	juju destroy-environment $(JUJU_ENV) -y

.PHONY: amulettests
amulettests: bootstrap_env $(TESTS) destroy_env

