from zope.interface import Attribute
from zope.interface import Interface


class IIncluder(Interface):

    config = Attribute("The adapted Configurator object")

    def __init__(config):
        """ Init adapter via registry.getAdapter(config IInclude, name='somename')"""

    def include(filename):
        """ Include this filename.

            In case override is specified, override any existing settings. """

    def update(data, filename):
        """ Update data from this filename. The filename is needed to figure out
            relative paths for any other includes.
        """
