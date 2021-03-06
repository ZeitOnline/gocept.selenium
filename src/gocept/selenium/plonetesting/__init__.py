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

import gocept.httpserverlayer.plonetestingzope
import gocept.selenium.webdriver
import unittest


class Layer(gocept.selenium.webdriver.IntegrationBase,
            gocept.httpserverlayer.plonetestingzope.Layer):
    pass


SELENIUM = Layer()


class TestCase(gocept.selenium.webdriver.WebdriverSeleneseTestCase,
               unittest.TestCase):
    """NOTE: MRO requires gocept.selenium.webdriver.WebdriverSeleneseTestCase
    to come first, otherwise its setUp/tearDown is never called,
    since unittest.TestCase does not call super().
    """

    @property
    def selenium(self):
        return self.layer['selenium']

    def getRootFolder(self):
        return self.layer['app']
