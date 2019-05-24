import os

from pyramid.config import Configurator
from pyramid.interfaces import IApplicationCreated
from zope.component import adapter
from zope.interface import implementer

from pyramid_settings.interfaces import IIncluder


@adapter(Configurator)
@implementer(IIncluder)
class BaseIncluder(object):
    __doc__ = IIncluder.__doc__

    def __init__(self, config):
        self.config = config

    def include(self, filename):
        """ Read and include this. """
        raise NotImplementedError()  # pragma: no cover

    def update(self, data, filename):
        """ Update settings dict, keep any existing values to allow override in the default ini file.

            If pyramid_settings.includes is specified in the contained file, include those as well.
            We'll expect the files to have a relative path compaired to the file that references them
        """
        other_includes = data.pop('pyramid_settings.includes', None)
        settings = self.config.registry.settings
        for (k, v) in data.items():
            settings.setdefault(k, v)
        if other_includes:
            if isinstance(other_includes, list):
                for rel_fn in other_includes:
                    fn = self.get_path(filename, rel_fn)
                    self.config.load_and_include(fn)
            else:
                fn = self.get_path(filename, other_includes)
                self.config.load_and_include(fn)

    def get_path(self, base_fn, recursive_included_fn):
        here = os.path.abspath(os.path.dirname(base_fn))
        return os.path.join(here, recursive_included_fn)


class YamlIncluder(BaseIncluder):
    """ Includes yaml files.
    """

    def include(self, filename):
        import yaml

        with open(filename, 'r') as f:
            data = yaml.safe_load(f)
        self.update(data, filename)


class JSONIncluder(BaseIncluder):

    def include(self, filename):
        import json

        with open(filename) as f:
            data = json.load(f)
        self.update(data, filename)


def _remove_includers(event):
    """ Remove all includers once the application has been created.
    """


def includeme(config):
    config.add_subscriber(_remove_includers, IApplicationCreated)
    config.registry.registerAdapter(YamlIncluder, name='yaml')
    config.registry.registerAdapter(JSONIncluder, name='json')
