pyramid_settings
================

Replaces most of your configuraton ini-files  with YAML or JSON that
can be reused or extended.

So why would you want this?

- If you're somewhat worried about that ini-file that seems to contain more
and more sensitive information required by each package you install.

- In case you really dislike ini-files and have found some YAML love.

- You're starting to realize that manually editing ini-files, switching
on and off components is getting quite tedious.

- You want to script deployment easier.

- You don't want to muck about with converting 
string values passed to settings.

- You have some other file format you want to add an extension for.


Basic usage
-----------

The most basic usage would be to tell pyramid to include pyramid_settings,
and then direct the rest of the configuration to that file.

Your paster-ini file look something like this:

    pyramid.includes =
        pyramid_settings
        
    pyramid_settings.files =
        basics.yaml
        development.yaml
        var/secretstuff.yaml

Order matters here, so *development.yaml* will overwrite similar values
within *basics.yaml*.

Your configuration files will be added to the settings dict present
at registry.settings within Pyramid.

Values prefixed with pyramid_settings won't be overwritten or included
in the settings var, since they're used by this package.


Directives within loaded files
------------------------------

The included settings file themselves may contain information 
used load or include other packages as well.

**pyramid_settings.files**

Other settings files to load and include. Uses relative path from the
file that references them.

**pyramid_settings.includes**

Other packages to include after the current file has been loaded.

So your *development.yaml* might look something like this

    pyramid_settings.files:
      - redis.yaml

And then the referenced file *redis.yaml*

    redis.sessions.secret: <somethingsecret>
    redis.sessions.timeout = 600000
    
    pyramid_settings.includes: pyramid_redis_sessions

The pyramid_redis_sessions package will be loaded after the injection
of the required settings.


Advanced: Writing your own loader
---------------------------------

In case you want other formats than yaml and json, simply subclass
**pyramid_settings.models.BaseSettingsLoader**.

This simple example should give you an idea.

    import json
    
    from pyramid_settings.models import BaseSettingsLoader


    class MySpecialJSONLoader(BaseSettingsLoader):
        """ A custom loader
        """
    
        def load(self, filename):
            """ Load data from 'filename' and pass it
                to the update function as a dict.
            """
            with open(filename) as f:
                data = json.load(f)
            self.update(data, filename)


To make it discoverable by the pyramid_settings package, register it
as a named adapter. The name in this case is the same thing as the
file ending.

So when including your package:

    def includeme(config):
        config.registry.registerAdapter(MySpecialJSONLoader, name='specialjson')


The above example would use this adapter for any file ending with 'specialjson'
for instance 'mysettings.specialjson'.
    
Note that this must be done before including pyramid_settings.

If you need to override any of the included json and yaml adapters,
you either need to run config.commit() or 
config.registry.unregisterAdapter first.
(Since Pyramid has detection for conflicting  configuration)

See the Pyramid docs for more information.


Bugs or suggestions?
--------------------

https://github.com/robinharms/pyramid_settings
