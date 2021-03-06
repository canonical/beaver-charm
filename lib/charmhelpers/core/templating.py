import os

from charmhelpers.core import host
from charmhelpers.core import hookenv


def render(source, target, context, owner='root', group='root',
           perms=0o444, templates_dir=None, encoding='UTF-8'):
    """
    Render a template.

    The `source` path, if not absolute, is relative to the `templates_dir`.

    The `target` path should be absolute.

    The context should be a dict containing the values to be replaced in the
    template.

    The `owner`, `group`, and `perms` options will be passed to `write_file`.

    If omitted, `templates_dir` defaults to the `templates` folder in the charm.

    Note: Using this requires python-jinja2; if it is not installed, calling
    this will attempt to use charmhelpers.fetch.apt_install to install it.
    """
    try:
        from jinja2 import FileSystemLoader, Environment, exceptions
    except ImportError:
        try:
            from charmhelpers.fetch import apt_install
        except ImportError:
            hookenv.log('Could not import jinja2, and could not import '
                        'charmhelpers.fetch to install it',
                        level=hookenv.ERROR)
            raise
        apt_install('python-jinja2', fatal=True)
        from jinja2 import FileSystemLoader, Environment, exceptions

    if templates_dir is None:
        templates_dir = os.path.join(hookenv.charm_dir(), 'templates')
    loader = Environment(loader=FileSystemLoader(templates_dir))
    try:
        source = source
        template = loader.get_template(source)
    except exceptions.TemplateNotFound as e:
        hookenv.log('Could not load template %s from %s.' %
                    (source, templates_dir),
                    level=hookenv.ERROR)
        raise e
    content = template.render(context)
    host.mkdir(os.path.dirname(target), owner, group)
    host.write_file(target, content.encode(encoding), owner, group, perms)
