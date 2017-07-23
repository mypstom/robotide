# -*- coding: utf-8 -*-　

import wx
from robotide.controller.filecontrollers import TestCaseFileController
from robot.parsing.model import Step
from duplicateactiondetection import LongestCommonSubsequence, LongestRepeatedSubstring
from robotide.publish import PUBLISHER, SettingDuplicatedDetectionThreshold
from configsetting import ConfigSetting

import time


class DDT:
    def __init__(self):
        self.datafiles = None
        self.componentChangeImpact = dict()
        self.user_def_keyword = dict()
        self.userKeywordObject = list()
        self.threshold = 3

        PUBLISHER.subscribe(self.set_duplicated_detection_threshold, SettingDuplicatedDetectionThreshold)

    def setDataFiles(self, datafiles):
        self.datafiles = datafiles

    """def OnInsertScreenshotKeywordIntoScript(self):
        wx.MessageBox('Yoo', 'Info',
        wx.OK | wx.ICON_INFORMATION)"""

    def ShowMessage(self, keywordInfo):
        wx.MessageBox(keywordInfo, 'Info',
                      wx.ICON_INFORMATION | wx.OK)

    """def CustomizedDiagram(self):
        dlg = wx.MultiChoiceDialog(self, 'Customize your diagram',  'Tase case relation diagram',['Root','Foloder','Node label'])
        dlg.ShowModal()
        dlg.Destroy()"""

    def checkHadInsertedScreenShotCommand(self):
        for df in self.datafiles:
            if type(df) is TestCaseFileController:
                if len(df.tests._items) > 0:
                    for testCase in df.tests:
                        for step in testCase.steps:
                            if (step._get_comment(step.as_list()) == 'KTV'):
                                return True
        return False

    def insertScreenShot(self):
        self.insertScreenShotIntoTC()
        self.insertScreenShotIntoUK()

    def insertScreenShotIntoTC(self):
        screenShotPath = './/selenium-screenshot/'
        for df in self.datafiles:
            if type(df) is TestCaseFileController:
                # print 'TS = %r' % (str(df.display_name))
                # TestSuiteScreenShotPath = str(df.display_name)
                # TestSuiteScreenShotPath += '/'
                screenShotPath += str(df.display_name)
                screenShotPath += '/'
                if len(df.tests._items) > 0:
                    for testCase in df.tests:
                        # print 'TC = %r' % (str(testCase.display_name))
                        # TestCaseScreenShotPath = str(testCase.display_name)
                        # TestCaseScreenShotPath += '/'
                        screenShotPath += str(testCase.display_name)
                        screenShotPath += '/'
                        # testCase.steps[0].insert_before(Step(['Set Selenium Speed', '0.6'], 'KTV'))
                        testCase.steps[0].insert_after(Step(['Set Screenshot Directory', screenShotPath], 'KTV'))
                        index = 2
                        screenShotCount = 1
                        while index < len(testCase.steps):
                            # else:
                            """newStep = Step(['Capture Page Screenshot',
                                            TestSuiteScreenShotPath + TestCaseScreenShotPath + str(
                                                screenShotCount) + '.png'], 'KTV')"""
                            newStep = Step(['Capture Page Screenshot'], 'KTV')
                            testCase.steps[index].insert_after(newStep)
                            index += 2
                            screenShotCount += 1

    def insertScreenShotIntoUK(self):
        for df in self.datafiles:
            if type(df) is TestCaseFileController:
                # print 'TS = %r' % (str(df.display_name))
                if len(df.keywords._items) > 0:
                    for userkeyword in df.keywords:
                        # print 'TC = %r' % (str(testCase.display_name))
                        index = 0
                        while index < len(userkeyword.steps) - 1:
                            newStep = Step(['Capture Page Screenshot'], 'KTV')
                            userkeyword.steps[index].insert_after(newStep)
                            index += 2

    def removeScreenShot(self):
        for df in self.datafiles:
            if len(df.tests._items) > 0:
                for testCase in df.tests:
                    for step in testCase.steps:
                        if (step._get_comment(step.as_list()) == 'KTV'):
                            step.remove()
            if len(df.keywords._items) > 0:
                for userkeyword in df.keywords:
                    for step in userkeyword.steps:
                        if (step._get_comment(step.as_list()) == 'KTV'):
                            step.remove()

    def LCS(self, filepath):
        start_time = time.time()
        LongestCommonSubsequence(self.threshold).execute(self.datafiles, filepath)
        elapsed_time = time.time() - start_time
        print 'Duplicated Action elapsed_time %r' % elapsed_time
        self.ShowMessage('Duplicated Action Detection Finish')

    def LRS(self, filepath):
        start_time = time.time()
        LongestRepeatedSubstring(self.threshold).execute(self.datafiles, filepath)
        elapsed_time = time.time() - start_time
        print 'Duplicated Action elapsed_time %r' % elapsed_time
        self.ShowMessage('Duplicated Action Detection Finish')

    def setting_config(self):
        ConfigSetting(self.threshold).Show()

    def set_duplicated_detection_threshold(self, data):
        self.threshold = data.threshold
