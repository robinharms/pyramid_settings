from logging import getLogger
from os.path import isfile

from pyramid.exceptions import ConfigurationError


logger = getLogger(__name__)


def load_and_include(config, fn):
    from pyramid_settings.interfaces import IIncluder

    if not isfile(fn):
        raise IOError("pyramid_settings can't find file: %r" % fn)
    logger.debug("Loading file: %s", fn)
    file_ending = fn.split('.')[-1]
    includer = config.registry.queryAdapter(config, IIncluder, name=file_ending)
    if includer is None:
        raise ConfigurationError("pyramid_settings has no registered includers that knows how "
                                 "to handle files ending with %r" % file_ending)
    includer.include(fn)


def includeme(config):
    config.add_directive('load_and_include', load_and_include)
    config.include('.models')
    filenames = config.registry.settings.get('pyramid_settings.includes', "").splitlines()
    for fn in filenames:
        config.load_and_include(fn)
