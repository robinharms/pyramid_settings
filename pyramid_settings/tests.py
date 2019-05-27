import os
from unittest import TestCase

from pyramid import testing
from pyramid.exceptions import ConfigurationError
from zope.interface.verify import verifyObject

from pyramid_settings.interfaces import ISettingsLoader


def _get_fixture_fn(fn):
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(here, 'testing_fixtures', fn)


class YamlLoaderTests(TestCase):

    def setUp(self):
        self.config = testing.setUp(settings={'hello': 'World'})

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from pyramid_settings.models import YamlLoader
        return YamlLoader

    def test_verify_iface(self):
        loader = self._cut(self.config)
        self.failUnless(verifyObject(ISettingsLoader, loader))

    def test_include(self):
        loader = self._cut(self.config)
        fixture_fn = _get_fixture_fn('settings.yaml')
        loader.load(fixture_fn)
        self.assertEqual(self.config.registry.settings.get('pets'), ['Cat', 'Dog', 'Goldfish'])
        self.assertEqual(self.config.registry.settings.get('yaml'), True)
        # Should not be overridden
        self.assertEqual(self.config.registry.settings.get('hello'), 'overridden world')

    def test_include_one_other(self):
        self.config.include('pyramid_settings')
        loader = self._cut(self.config)
        fixture_fn = _get_fixture_fn('include_one.yaml')
        loader.load(fixture_fn)
        self.assertEqual(self.config.registry.settings.get('json'), True)
        # From JSON file
        self.assertEqual(self.config.registry.settings.get('somestuff'), [1, 2, 3])


class JSONLoaderTests(TestCase):

    def setUp(self):
        self.config = testing.setUp(settings={'hello': 'Other world'})

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from pyramid_settings.models import JSONLoader
        return JSONLoader

    def test_verify_iface(self):
        loader = self._cut(self.config)
        self.failUnless(verifyObject(ISettingsLoader, loader))

    def test_load(self):
        loader = self._cut(self.config)
        fixture_fn = _get_fixture_fn('settings.json')
        loader.load(fixture_fn)
        self.assertEqual(self.config.registry.settings.get('somestuff'), [1, 2, 3])
        self.assertEqual(self.config.registry.settings.get('json'), True)
        # Should be overridden
        self.assertEqual(self.config.registry.settings.get('hello'), 'world')

    def test_load_several(self):
        self.config.include('pyramid_settings')
        loader = self._cut(self.config)
        fixture_fn = _get_fixture_fn('include_more.json')
        loader.load(fixture_fn)
        # From settings.json and settings.yaml
        self.assertEqual(self.config.registry.settings.get('json'), True)
        self.assertEqual(self.config.registry.settings.get('yaml'), True)


class FunctionalTests(TestCase):

    def setUp(self):
        self.config = testing.setUp(settings={'hello': 'WORLD'})

    def tearDown(self):
        testing.tearDown()

    def test_relative_paths(self):
        settings = self.config.registry.settings
        settings['pyramid_settings.files'] = _get_fixture_fn('relative_paths.yaml')
        self.config.include('pyramid_settings')
        self.assertEqual('yay', settings.get('pathcheck'))

    def test_include_bad(self):
        settings = self.config.registry.settings
        settings['pyramid_settings.files'] = _get_fixture_fn('settings.bad')
        self.assertRaises(ConfigurationError, self.config.include, 'pyramid_settings')

    def test_bad_value_in_settings(self):
        settings = self.config.registry.settings
        settings['pyramid_settings.includes'] = 'some.package'
        self.assertRaises(ConfigurationError, self.config.include, 'pyramid_settings')

    def test_include_other_package(self):
        settings = self.config.registry.settings
        settings['pyramid_settings.files'] = _get_fixture_fn('include_other_package.yaml')
        self.config.include('pyramid_settings')
        self.assertTrue(self.config.registry.hello_world)

    def test_include_other_packages(self):
        settings = self.config.registry.settings
        settings['pyramid_settings.files'] = _get_fixture_fn('include_other_packages.yaml')
        self.config.include('pyramid_settings')
        self.assertTrue(self.config.registry.hello_world)


def includeme(config):
    """ Don't include this, it's for tests :) """
    config.registry.hello_world = True
