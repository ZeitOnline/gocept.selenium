#############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import atexit
import gocept.selenium.selenese
import os
import os.path
import selenium.webdriver
import shutil
import sys
import tempfile
import urllib2


if sys.version_info < (2, 5):
    TEST_METHOD_NAME = '_TestCase__testMethodName'
else:
    TEST_METHOD_NAME = '_testMethodName'


class Layer(object):

    # hostname and port of the Selenium RC server
    _server = os.environ.get('GOCEPT_SELENIUM_SERVER_HOST', 'localhost')
    _port = int(os.environ.get('GOCEPT_SELENIUM_SERVER_PORT', 4444))

    _browser = os.environ.get('GOCEPT_SELENIUM_BROWSER', 'firefox')

    # hostname and port of the local application.
    host = os.environ.get('GOCEPT_SELENIUM_APP_HOST', 'localhost')
    port = int(os.environ.get('GOCEPT_SELENIUM_APP_PORT', 5698))

    def __init__(self, *bases):
        self.__bases__ = bases
        if self.__bases__:
            base = bases[0]
            self.__name__ = '(%s.%s)' % (base.__module__, base.__name__)
        else:
            self.__name__ = self.__class__.__name__

    def _stop_selenium(self):
        # Only stop selenium if it is still active.
        if self.seleniumrc.session_id is None:
            return

        self.seleniumrc.quit()

        shutil.rmtree(self.profile.profile_dir)
        if os.path.dirname(self.profile.profile_dir) != tempfile.gettempdir():
            try:
                os.rmdir(os.path.dirname(self.profile.profile_dir))
            except OSError:
                pass

        if not os.environ.get('GOCEPT_SELENIUM_KEEP_NATIVE_FF_EVENTS_LOG'):
            native_ff_events_log = os.path.join(
                tempfile.gettempdir(), 'native_ff_events_log')
            try:
                os.unlink(native_ff_events_log)
            except OSError:
                pass

    def setUp(self):
        self.profile = selenium.webdriver.firefox.firefox_profile.\
            FirefoxProfile(os.environ.get('GOCEPT_SELENIUM_FF_PROFILE'))
        self.profile.native_events_enabled = True
        self.profile.update_preferences()
        try:
            self.seleniumrc = selenium.webdriver.Remote(
                'http://%s:%s/wd/hub' % (self._server, self._port),
                desired_capabilities=dict(browserName=self._browser),
                browser_profile=self.profile)
        except urllib2.URLError, e:
            raise urllib2.URLError(
                'Failed to connect to Selenium server at %s:%s,'
                ' is it running? (%s)'
                % (self._server, self._port, e))
        atexit.register(self._stop_selenium)
        speed = os.environ.get('GOCEPT_SELENIUM_SPEED')
        if speed is not None:
            self.seleniumrc.setSpeed(speed)

    def tearDown(self):
        self._stop_selenium()
        # XXX upstream bug, quit should reset session_id
        self.seleniumrc.session_id = None

    def testSetUp(self):
        # instantiate a fresh one per test run, so any configuration
        # (e.g. timeout) is reset
        self.selenium = gocept.selenium.selenese.Selenese(
            self.seleniumrc, self.host, self.port)


class TestCase(object):
    # the various flavours (ztk, zope2, grok, etc.) are supposed to provide
    # their own TestCase as needed, and mix this class in to get the
    # convenience functionality.
    #
    # Example:
    # some.flavour.TestCase(gocept.selenium.base.TestCase,
    #                       the.actual.base.TestCase):
    #     pass

    @property
    def selenium(self):
        return self.layer.selenium
