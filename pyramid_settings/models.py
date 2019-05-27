import os
from logging import getLogger

from pyramid.config import Configurator
from zope.component import adapter
from zope.interface import implementer

from pyramid_settings.interfaces import ISettingsLoader


@adapter(Configurator)
@implementer(ISettingsLoader)
class BaseSettingsLoader(object):
    __doc__ = ISettingsLoader.__doc__
    logger = getLogger(__name__)

    def __init__(self, config):
        self.config = config
        if not hasattr(config.registry, '_pyramid_settings_clog'):
            config.registry._pyramid_settings_clog = []

    def log_change(self, fn, k, v):
        """ Log that a specific config file made a change to settings. This is simply to make introspection easier
            in case you spread configuration over several files.
        """
        self.logger.debug({'fn': fn, 'k': k, 'v': v})

    def load(self, filename):  # pragma: no cover
        __doc__ = ISettingsLoader['load'].__doc__
        raise NotImplementedError()

    def update(self, data, filename):
        __doc__ = ISettingsLoader['update'].__doc__
        other_includes = data.pop('pyramid_settings.includes', None)
        other_files = data.pop('pyramid_settings.files', None)
        settings = self.config.registry.settings
        for (k, v) in data.items():
            if settings.get(k, object()) != v:
                settings[k] = v
                self.log_change(filename, k, v)
        if other_files:
            self.log_change(filename, 'pyramid_settings.files', other_files)
            if isinstance(other_files, list):
                for rel_fn in other_files:
                    fn = self.get_path(filename, rel_fn)
                    self.config.load_and_include(fn)
            else:
                fn = self.get_path(filename, other_files)
                self.config.load_and_include(fn)
        if other_includes:
            self.log_change(filename, 'pyramid_settings.includes', other_includes)
            if isinstance(other_includes, list):
                for x in other_includes:
                    self.config.include(x)
            else:
                # Assume string here or die
                self.config.include(other_includes)

    def get_path(self, base_fn, recursive_included_fn):
        here = os.path.abspath(os.path.dirname(base_fn))
        return os.path.join(here, recursive_included_fn)


class YamlLoader(BaseSettingsLoader):
    """ Includes yaml files.
    """

    def load(self, filename):
        import yaml

        with open(filename, 'r') as f:
            data = yaml.safe_load(f)
        self.update(data, filename)


class JSONLoader(BaseSettingsLoader):

    def load(self, filename):
        import json

        with open(filename) as f:
            data = json.load(f)
        self.update(data, filename)


def includeme(config):
    config.registry.registerAdapter(YamlLoader, name='yaml')
    config.registry.registerAdapter(JSONLoader, name='json')
