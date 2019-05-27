from zope.interface import Attribute
from zope.interface import Interface


class ISettingsLoader(Interface):
    """ Load settings from referenced files.
    """

    config = Attribute("The adapted Configurator object")

    def __init__(config):
        """ Init adapter via registry.getAdapter(config IInclude, name='somename')"""

    def load(filename):
        """ Load data from this filename. Should open the file, read it's contents,
            parse it and pass it as a dict to the update function.
        """

    def update(data, filename):
        """ Update data from this filename. The filename is needed to figure out
            relative paths for any other includes.

            This function will process data in the following order:

            1) Update any values needed in settings
            2) Load other settings data from files referenced within the data key 'pyramid_settings.files'
            3) Run config.include() any packages referenced within the data key 'pyramid_settings.includes'
        """
