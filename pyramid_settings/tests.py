import os
from unittest import TestCase

from pyramid import testing
from pyramid.exceptions import ConfigurationError
from zope.interface.verify import verifyObject

from pyramid_settings.interfaces import IIncluder


def _get_fixture_fn(fn):
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(here, 'testing_fixtures', fn)


# class LoadAndIncludeTests(TestCase):
#
#     def setUp(self):
#         self.config = testing.setUp()
#
#     def tearDown(self):
#         testing.tearDown()
#
#     @property
#     def _cut(self):
#


class YamlIncluderTests(TestCase):

    def setUp(self):
        self.config = testing.setUp(settings={'hello': 'Other world'})

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from pyramid_settings.models import YamlIncluder
        return YamlIncluder

    def test_verify_iface(self):
        includer = self._cut(self.config)
        self.failUnless(verifyObject(IIncluder, includer))

    def test_include(self):
        includer = self._cut(self.config)
        fixture_fn = _get_fixture_fn('settings.yaml')
        includer.include(fixture_fn)
        self.assertEqual(self.config.registry.settings.get('pets'), ['Cat', 'Dog', 'Goldfish'])
        self.assertEqual(self.config.registry.settings.get('yaml'), True)
        # Should not be overridden
        self.assertEqual(self.config.registry.settings.get('hello'), 'Other world')

    def test_include_one_other(self):
        self.config.include('pyramid_settings')
        includer = self._cut(self.config)
        fixture_fn = _get_fixture_fn('include_one.yaml')
        includer.include(fixture_fn)
        self.assertEqual(self.config.registry.settings.get('json'), True)
        # From JSON file
        self.assertEqual(self.config.registry.settings.get('somestuff'), [1, 2, 3])


class JSONIncluderTests(TestCase):

    def setUp(self):
        self.config = testing.setUp(settings={'hello': 'Other world'})

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from pyramid_settings.models import JSONIncluder
        return JSONIncluder

    def test_verify_iface(self):
        includer = self._cut(self.config)
        self.failUnless(verifyObject(IIncluder, includer))

    def test_include(self):
        includer = self._cut(self.config)
        fixture_fn = _get_fixture_fn('settings.json')
        includer.include(fixture_fn)
        self.assertEqual(self.config.registry.settings.get('somestuff'), [1, 2, 3])
        self.assertEqual(self.config.registry.settings.get('json'), True)
        # Should not be overridden
        self.assertEqual(self.config.registry.settings.get('hello'), 'Other world')

    def test_include_more(self):
        self.config.include('pyramid_settings')
        includer = self._cut(self.config)
        fixture_fn = _get_fixture_fn('include_more.json')
        includer.include(fixture_fn)
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
        settings['pyramid_settings.includes'] = _get_fixture_fn('relative_paths.yaml')
        self.config.include('pyramid_settings')
        self.assertEqual('yay', settings.get('pathcheck'))

    def test_include_bad(self):
        settings = self.config.registry.settings
        settings['pyramid_settings.includes'] = _get_fixture_fn('settings.bad')
        self.assertRaises(ConfigurationError, self.config.include, 'pyramid_settings')
