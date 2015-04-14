#!/usr/bin/python

import apt
import ConfigParser
import os
import subprocess
import sys
import urllib2


sys.path.insert(0, os.path.join(os.environ['CHARM_DIR'], 'lib'))

from charmhelpers.core import (
    hookenv,
    host,
)
from charmhelpers.core.services import RelationContext

hooks = hookenv.Hooks()
log = hookenv.log
config = hookenv.config()
config.implicit_save = False

APT_SOURCES_LIST = '/etc/apt/sources.list.d/beaver.list'
SERVICE = 'beaver'
KEYURL = 'http://keyserver.ubuntu.com:11371/pks/lookup?' \
         'op=get&search=0xA65E2E5D742A38EE'
SOURCE = 'deb http://ppa.launchpad.net/evarlast/experimental/ubuntu trusty main'
DEPENDENCIES = ('beaver', )
BEAVER_CONFIG = '/etc/beaver/conf'


def ensure_packages(*pkgs):
    '''
    ensure_packages installs and upgrades pacakges. The goal is to be apt-get
    install equivalent.
    '''
    apt.apt_pkg.config['APT::Install-Recommends'] = '0'
    apt.apt_pkg.config['APT::Get::Assume-Yes'] = '1'
    cache = apt.Cache()
    for name in pkgs:
        pkg = cache[name]
        if not pkg.is_installed:
            pkg.mark_install()
        if pkg.is_upgradable:
            pkg.mark_upgrade()
    cache.commit()


@hooks.hook('config-changed')
def config_changed():
    config = hookenv.config()

    for key in config:
        if config.changed(key):
            log("config['{}'] changed from {} to {}".format(
                key, config.previous(key), config[key]))

    config.save()
    start()


@hooks.hook('install')
def install():
    log('Installing beaver')
    ensure_ppa()
    apt_get_update()
    ensure_packages(*DEPENDENCIES)


@hooks.hook('start')
def start():
    host.service_restart(SERVICE) or host.service_start(SERVICE)


def restart():
    log('(re)starting ' + SERVICE)
    host.service_restart(SERVICE) or \
        host.service_start(SERVICE)


@hooks.hook('stop')
def stop():
    host.service_stop(SERVICE)


@hooks.hook('upgrade-charm')
def upgrade_charm():
    log('Upgrading beaver')
    apt_get_update()
    ensure_packages(*DEPENDENCIES)
    restart()


@hooks.hook('logs-relation-joined')
@hooks.hook('logs-relation-changed')
def logs_relation_changed():
    log('Logs changed')
    logs_relation_data = logs_relation()
    if logs_relation_data is not None:
        write_beaver_config(logs_relation_data)
        restart()


def write_beaver_config(logs_relation_data):
    config = ConfigParser.ConfigParser()
    for file, type in logs_relation_data:
        config.add_section(file)
        config.set(file, 'type', type)
    host.write_file(BEAVER_CONFIG, config)


def logs_relation():
    lsr = LogsRelation()
    log("LogsRelation: {}".format(lsr))
    r = lsr['logs']
    if not r or 'types' not in r[0]:
        return None
    if not r or 'files' not in r[0]:
        return None
    types = r[0]['types'].split()
    files = r[0]['files'].split()
    return zip(types, files)


def ensure_ppa():
    if not has_source_list():
        apt_key_add(KEYURL)
        add_source_list()


def add_source_list():
    host.write_file(APT_SOURCES_LIST, SOURCE + "\n")


def has_source_list():
    if not os.path.exists(APT_SOURCES_LIST):
        return False
    return (
        open(APT_SOURCES_LIST, 'r').read().strip()
        in SOURCE
    )


def apt_key_add(keyurl):
    r = urllib2.urlopen(keyurl)
    data = r.read()
    PIPE = subprocess.PIPE
    proc = subprocess.Popen(('apt-key', 'add', '-'),
                            stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate(input=data)
    if out != 'OK\n'or err != '':
        log("error running apt-key add:" + out + err)


def apt_get_update():
    apt.apt_pkg.config['APT::Install-Recommends'] = '0'
    cache = apt.Cache()
    try:
        cache.update()
        cache.open(None)
        cache.commit()
    except Exception as e:
        msg = "apt_get_update error:{}".format(e)
        log(msg)


class LogsRelation(RelationContext):
    name = 'logs'
    interface = 'logs'
    required_keys = ['types', 'files']


if __name__ == "__main__":
    # execute a hook based on the name the program is called by
    hooks.execute(sys.argv)
