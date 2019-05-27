from logging import getLogger
from os.path import isfile

from pyramid.exceptions import ConfigurationError


logger = getLogger(__name__)


def load_and_include(config, fn):
    from pyramid_settings.interfaces import ISettingsLoader

    if not isfile(fn):
        raise IOError("pyramid_settings can't find file: %r" % fn)
    logger.debug("Loading file: %s", fn)
    file_ending = fn.split('.')[-1]
    loader = config.registry.queryAdapter(config, ISettingsLoader, name=file_ending)
    if loader is None:
        raise ConfigurationError("pyramid_settings has no registered ISettingsLoader that knows how "
                                 "to handle files ending with %r" % file_ending)
    loader.load(fn)


def includeme(config):
    config.add_directive('load_and_include', load_and_include)
    config.include('.models')
    if config.registry.settings.get('pyramid_settings.includes', None):
        raise ConfigurationError("'pyramid_settings.includes' was in the paster ini file. "
                                 "That setting is only ment for included config files. If you need to load something "
                                 "before this package, use the default 'pyramid.includes'")
    filenames = config.registry.settings.get('pyramid_settings.files', "").splitlines()
    for fn in filenames:
        config.load_and_include(fn)

