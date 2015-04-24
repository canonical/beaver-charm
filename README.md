# Overview

Beaver provides an lightweight method for shipping local log files to Logstash.
It does this using redis, zeromq, tcp, udp, rabbit or stdout as the transport.
This means you’ll need a redis, zeromq, tcp, udp, amqp or stdin input somewhere down the road to get the events.

Events are sent in logstash’s json_event format. Options can also be set as environment variables.

# Usage

For this charm it uses tcp as a transport and is a subordinate charm.
Here is an example of how to send apache2 log via beaver to logstash::

	juju deploy cs:~evarlast/trusty/apache2
	juju deploy local:trusty/beaver
	juju deploy cs:~evarlast/trusty/logstash
	juju add-relation apache2 beaver
	juju add-relation logstash beaver
	juju set apache2 vhost_http_template=$(shell base64 -w0<tests/apache2.template)

This charm for the moment is based on a zero configuration principle.
Everything is configure through juju relation and the fact it is a subordinate charm.

# Contact Information

Fabrice Matrat <fabrice.matrat@canonical.com>

## Beaver

- [Beaver](http://beaver.readthedocs.org/) home page
- [Beaver bugtracker](https://github.com/josegonzalez/python-beaver/issues)
- [Beaver source](https://github.com/josegonzalez/python-beaver)
- [Beaver Charm](http://jujucharms.com/?text=beaver)
