#!/usr/bin/python

import os
import unittest

import mock

os.environ['CHARM_DIR'] = os.path.join(os.path.dirname(__file__), '..')
os.environ['JUJU_UNIT_NAME'] = 'beaver/0'

from charmhelpers.core import hookenv

hookenv.log = mock.MagicMock()

from charmhelpers.core import host


config = hookenv.Config({})
hookenv.config = mock.MagicMock(return_value=config)


import hooks
hooks.ensure_packages = mock.MagicMock()
hooks.run = mock.MagicMock()
host.service = mock.MagicMock(return_value=True)
host.write_file = mock.MagicMock()
hooks.ensure_packages = mock.MagicMock()
hooks.run = mock.MagicMock()


class TestInstall(unittest.TestCase):
    '''Testing that there are no exceptions in hooks.install.'''

    def test_install_does_not_raise(self):
        hooks.install()

    def test_installs_packages(self):
        hooks.ensure_packages.reset_mock()
        hooks.install()
        hooks.ensure_packages.assert_any_call(*hooks.DEPENDENCIES)


class TestStart(unittest.TestCase):

    def test_start_does_not_raise(self):
        hooks.start()

    def test_start_runs_service(self):
        hooks.start()
        host.service.assert_called_with('restart', 'beaver')


class TestStop(unittest.TestCase):

    def test_stop_does_not_raise(self):
        hooks.stop()

    def test_stop_stops_service(self):
        hooks.stop()
        host.service.assert_called_with('stop', 'beaver')
