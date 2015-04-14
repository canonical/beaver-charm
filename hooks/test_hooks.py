#!/usr/bin/python

import os
import unittest

import mock

os.environ['CHARM_DIR'] = os.path.join(os.path.dirname(__file__), '..')
os.environ['JUJU_UNIT_NAME'] = 'beaver/0'

from charmhelpers.core import hookenv, services

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


class TestLogsRelation(unittest.TestCase):

    def setUp(self):
        self.phookenv = mock.patch.object(services.helpers, 'hookenv')
        self.mhookenv = self.phookenv.start()
        self.mhookenv.relation_ids.return_value = ['baz']
        self.mhookenv.related_units.side_effect = lambda i: [i + '/0']
        self.mhookenv.relation_get.side_effect = [
            {'files': '\n'.join(['a', 'b']),
             'types': '\n'.join(['c', 'd'])}
        ]
        self.mhookenv.reset_mock()
        host.write_file.reset_mock()

    def tearDown(self):
        self.phookenv.stop()

    def test_changed_does_not_raise(self):
        hooks.logs_relation_changed()

    def test_changed(self):
        hooks.logs_relation_changed()
        self.assertTrue(host.write_file.is_called)
