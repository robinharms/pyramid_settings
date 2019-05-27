from zope.interface import Attribute
from zope.interface import Interface


class ISettingsLoader(Interface):

    config = Attribute("The adapted Configurator object")

    def __init__(config):
        """ Init adapter via registry.getAdapter(config IInclude, name='somename')"""

    def load(filename):
        """ Load and include this filename.
         """

    def update(data, filename):
        """ Update data from this filename. The filename is needed to figure out
            relative paths for any other includes.
        """
