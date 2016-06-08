#  Copyright 2008-2012 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
from robotide.context.platform import IS_MAC

import wx
import json
import webbrowser
import math
import robotide
import copy
from operator import itemgetter, attrgetter
from robotide.action import ActionInfoCollection, ActionFactory, SeparatorInfo
from robotide.context import ABOUT_RIDE, SHORTCUT_KEYS
from robotide.controller.commands import SaveFile, SaveAll
from robotide.publish import (RideSaveAll, RideClosing, RideSaved, PUBLISHER,
        RideInputValidationError, RideTreeSelection, RideModificationPrevented)
from robotide.ui.tagdialogs import ViewAllTagsDialog
from robotide.utils import RideEventHandler
from robotide.widgets import Dialog, ImageProvider, HtmlWindow
from robotide.preferences import PreferenceEditor

from .actiontriggers import MenuBar, ToolBar, ShortcutRegistry
from .filedialogs import (NewProjectDialog, InitFileFormatDialog)
from .review import ReviewDialog
from .pluginmanager import PluginManager
from robotide.action.shortcut import localize_shortcuts
from .tree import Tree
from .notebook import NoteBook
from .progress import LoadProgressObserver
import graphviz
from graphviz import Graph

_menudata = """
[File]
!&New Project | Create a new top level suite | Ctrlcmd-N
---
!&Open Test Suite | Open file containing tests | Ctrlcmd-O | ART_FILE_OPEN
!Open &Directory | Open directory containing datafiles | Shift-Ctrlcmd-O | ART_FOLDER_OPEN
---
&Save | Save selected datafile | Ctrlcmd-S | ART_FILE_SAVE
!Save &All | Save all changes | Ctrlcmd-Shift-S | ART_FILE_SAVE_AS
---
!E&xit | Exit RIDE | Ctrlcmd-Q

[Tools]
!Search Unused Keywords | | | | POSITION-54
!Manage Plugins | | | | POSITION-81
!View All Tags | | F7 | | POSITION-82
!Preferences | | | | POSITION-99

[Help]
!Shortcut keys | RIDE shortcut keys
!User Guide | RIDE User Guide
!Report a Problem | Open browser to the RIDE issue tracker
!Release notes | Shows release notes
!About | Information about RIDE

[Graphic Tool]
!Test Suite Use Keyword | Generate the diagram of test suite use the keyword
!Insert Screenshot Keyword Into Script | Insert screenshot keyword into scripts
!Ignore Nodes | Ignore
"""


class RideFrame(wx.Frame, RideEventHandler):

    def __init__(self, application, controller):
        wx.Frame.__init__(self, parent=None, title='RIDE',
                          pos=application.settings['mainframe position'],
                          size=application.settings['mainframe size'])
        self._application = application
        self._controller = controller
        self._init_ui()
        self._plugin_manager = PluginManager(self.notebook)
        self._review_dialog = None
        self._view_all_tags_dialog = None
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self._subscribe_messages()
        self.ensure_on_screen()
        self.Show()
        wx.CallLater(100, self.actions.register_tools)

    def _subscribe_messages(self):
        for listener, topic in [(lambda msg: self.SetStatusText('Saved %s' % msg.path), RideSaved),
                                (lambda msg: self.SetStatusText('Saved all files'), RideSaveAll),
                                (self._set_label, RideTreeSelection),
                                (self._show_validation_error, RideInputValidationError),
                                (self._show_modification_prevented_error, RideModificationPrevented)]:
            PUBLISHER.subscribe(listener, topic)

    def _set_label(self, message):
        self.SetTitle(self._create_title(message))

    def _create_title(self, message):
        title = 'RIDE'
        if message:
            item = message.item
            title += ' - ' + item.datafile.name
            if not item.is_modifiable():
                title += ' (READ ONLY)'
        return title

    def _show_validation_error(self, message):
        wx.MessageBox(message.message, 'Validation Error', style=wx.ICON_ERROR)

    def _show_modification_prevented_error(self, message):
        wx.MessageBox('"%s" is read only' % message.controller.datafile_controller.filename,
                      'Modification prevented',
                      style=wx.ICON_ERROR)

    def _init_ui(self):
        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        self.notebook = NoteBook(splitter, self._application)
        mb = MenuBar(self)
        self.toolbar = ToolBar(self)
        self.actions = ActionRegisterer(mb, self.toolbar,
                                        ShortcutRegistry(self))
        self.tree = Tree(splitter, self.actions, self._application.settings)
        self.actions.register_actions(ActionInfoCollection(_menudata, self, self.tree))
        mb.take_menu_bar_into_use()
        splitter.SetMinimumPaneSize(100)
        splitter.SplitVertically(self.tree, self.notebook, 300)
        self.CreateStatusBar()
        self.SetIcons(ImageProvider().PROGICONS)

    def get_selected_datafile(self):
        return self.tree.get_selected_datafile()

    def get_selected_datafile_controller(self):
        return self.tree.get_selected_datafile_controller()

    def OnClose(self, event):
        self._application.settings['mainframe size'] = self.GetSizeTuple()
        self._application.settings['mainframe position'] = self.GetPositionTuple()
        if self._allowed_to_exit():
            PUBLISHER.unsubscribe(self._set_label, RideTreeSelection)
            RideClosing().publish()
            self.Destroy()
        else:
            wx.CloseEvent.Veto(event)

    def OnReleasenotes(self, event):
        pass

    def _allowed_to_exit(self):
        if self.has_unsaved_changes():
            ret = wx.MessageBox('There are unsaved modifications.\n'
                                'Do you want to save your changes before exiting?',
                                'Warning', wx.ICON_WARNING|wx.CANCEL|wx.YES_NO)
            if ret == wx.CANCEL:
                return False
            if ret == wx.YES:
                self.save()
        return True

    def has_unsaved_changes(self):
        return self._controller.is_dirty()

    def OnNewProject(self, event):
        if not self.check_unsaved_modifications():
            return
        NewProjectDialog(self._controller).execute()
        self._populate_tree()

    def _populate_tree(self):
        self.tree.populate(self._controller)

    def OnOpenTestSuite(self, event):
        if not self.check_unsaved_modifications():
            return
        path = self._get_path()
        if path:
            self.open_suite(path)

    def check_unsaved_modifications(self):
        if self.has_unsaved_changes():
            ret = wx.MessageBox('There are unsaved modifications.\n'
                                'Do you want to proceed without saving?',
                                'Warning', wx.ICON_WARNING|wx.YES_NO)
            return ret == wx.YES
        return True

    def _get_path(self):
        wildcard = ('All files|*.*|Robot data (*.html)|*.*htm*|'
                    'Robot data (*.tsv)|*.tsv|Robot data (*txt)|*.txt')
        dlg = wx.FileDialog(self, message='Open', wildcard=wildcard,
                            defaultDir=self._controller.default_dir, style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self._controller.update_default_dir(path)
        else:
            path = None
        dlg.Destroy()
        return path

    def open_suite(self, path):
        self._controller.update_default_dir(path)
        self._controller.load_datafile(path, LoadProgressObserver(self))
        self._populate_tree()

    def refresh_datafile(self, item, event):
        self.tree.refresh_datafile(item, event)

    def OnOpenDirectory(self, event):
        if self.check_unsaved_modifications():
            path = wx.DirSelector(message='Choose a directory containing Robot files',
                                  defaultPath=self._controller.default_dir)
            if path:
                self.open_suite(path)

    def OnSave(self, event):
        self.save()

    def OnSaveAll(self, event):
        self.save_all()

    def save_all(self):
        self._show_dialog_for_files_without_format()
        self._controller.execute(SaveAll())

    def save(self, controller=None):
        if controller is None :
            controller = self.get_selected_datafile_controller()
        if controller is not None:
            if not controller.has_format():
                self._show_dialog_for_files_without_format(controller)
            else:
                controller.execute(SaveFile())

    def _show_dialog_for_files_without_format(self, controller=None):
        files_without_format = self._controller.get_files_without_format(controller)
        for f in files_without_format:
            self._show_format_dialog_for(f)

    def _show_format_dialog_for(self, file_controller_without_format):
        InitFileFormatDialog(file_controller_without_format).execute()

    def OnExit(self, event):
        self.Close()

    def OnManagePlugins(self, event):
        self._plugin_manager.show(self._application.get_plugins())

    def OnViewAllTags(self, event):
        if self._view_all_tags_dialog is None:
            self._view_all_tags_dialog = ViewAllTagsDialog(self._controller, self)
        self._view_all_tags_dialog.show_dialog()

    def OnSearchUnusedKeywords(self, event):
        if self._review_dialog is None:
            self._review_dialog = ReviewDialog(self._controller, self)
        self._review_dialog.show_dialog()

    def OnPreferences(self, event):
        dlg = PreferenceEditor(self, "RIDE - Preferences",
                                self._application.preferences, style='tree')
        # I would prefer that this not be modal, but making it non-
        # modal opens up a can of worms. We don't want to have to deal
        # with settings getting changed out from under us while the
        # dialog is open.
        dlg.ShowModal()
        dlg.Destroy()

    def OnAbout(self, event):
        dlg = AboutDialog()
        dlg.ShowModal()
        dlg.Destroy()

    def OnShortcutkeys(self, event):
        dialog = ShortcutKeysDialog()
        dialog.Show()

    def OnReportaProblem(self, event):
        wx.LaunchDefaultBrowser('http://code.google.com/p/robotframework-ride/issues/list')

    def OnUserGuide(self, event):
        wx.LaunchDefaultBrowser('http://code.google.com/p/robotframework/wiki/UserGuide')

    def OnInsertScreenshotKeywordIntoScript(self):
        wx.MessageBox('Yoo', 'Info',
        wx.OK | wx.ICON_INFORMATION)

    def ShowMessage(self,keywordInfo):
        wx.MessageBox(keywordInfo, 'Info',
        wx.OK | wx.ICON_INFORMATION)

    def CustomizedDiagram(self):
        dlg = wx.MultiChoiceDialog(self, 'Customize your diagram',  'Tase case relation diagram',['Root','Foloder','Node label'])
        dlg.ShowModal()
        dlg.Destroy()

    def relationBetweenTSandTS(self,user_def_keyword,testSuites):
        graphTS2TS = graphviz.Digraph(comment='TS <-> TS', engine='dot')
        edgeSet = list()
        nodeList = set()
        graphTS2TS.node('Root')
        for suite in testSuites:
            nodeList.add(suite)
        for node in nodeList:
            graphTS2TS.node(node,color="cyan3", shape="box", style="filled")
            graphTS2TS.edge('Root',node)
        try:
            for df in self._get_datafile_list(): #get suite level
                tempSuiteUseUserKeyword = list()
                tempSet = set()
                if len(df.tests._items) > 0: #not empty
                    try: #add Test case level
                        for testCase in df.tests:
                            try:
                                for testStep in testCase.steps:
                                    if str(testStep.keyword) in user_def_keyword: #record all of using UK
                                        if user_def_keyword[str(testStep.keyword)] != str(df.display_name):
                                            tempSuiteUseUserKeyword.append(user_def_keyword[str(testStep.keyword)])
                            except Exception, e:
                                print str(e)

                        for node2 in tempSuiteUseUserKeyword:
                            tempSet.add(node2)
                        for node3 in tempSet:
                            graphTS2TS.edge(str(df.display_name), node3, label=str(tempSuiteUseUserKeyword.count(node3)), penwidth= str(math.log(tempSuiteUseUserKeyword.count(node3),2)+1))
                    except Exception, e:
                        print str(e)
        except Exception, e:
            print str(e)
        graphTS2TS.render('TS2TS.gv',view=False)

    def relationBetweenTSandTC(self,user_def_keyword,testSuites):
        graphTS2TC = graphviz.Digraph(comment='TS <-> TC', engine='dot')
        graphTS2TC.node('Root')
        tempEdge = list()
        tempEdgeSet = set()
        try:
            for df in self._get_datafile_list(): #get suite level
                if len(df.tests._items) > 0: #not empty
                    graphTS2TC.node(str(df.display_name), color="cyan3", shape="box", style="filled")
                    graphTS2TC.edge('Root',str(df.display_name))
                    try: #add Test case level
                        for testCase in df.tests:
                            graphTS2TC.node(str(testCase.name), color="darkolivegreen2", shape="box", style="filled")
                            graphTS2TC.edge(str(df.display_name),str(testCase.name))
                            try:
                                for testStep in testCase.steps:
                                    if str(testStep.keyword) in user_def_keyword: #record all of using UK
                                        tempEdge.append((str(testCase.name), user_def_keyword[str(testStep.keyword)]))
                                        #graphTS2TC.edge(str(testCase.name), user_def_keyword[str(testStep.keyword)])
                            except Exception, e:
                                print str(e)
                    except Exception, e:
                        print str(e)
        except Exception, e:
            print str(e)
        for node in tempEdge:
            tempEdgeSet.add(node)
        for node in tempEdgeSet:
            graphTS2TC.edge(node[0], node[1], label=str(tempEdge.count(node)), penwidth=str(math.log(tempEdge.count(node),2)+1))
        graphTS2TC.render('TS2TC.gv',view=False)

    def relationBetweenTSandUK(self,user_def_keyword,testSuites):
        graphTS2UK = graphviz.Digraph(comment='TS <-> UK', engine='fdp')
        graphTS2UK.node('Root')
        tempEdge = list()
        tempEdgeSet = set()
        for node in user_def_keyword:
            graphTS2UK.node(str(node), color="coral", shape="box", style="filled")
        try:
            for df in self._get_datafile_list(): #get suite level
                if len(df.tests._items) > 0: #not empty
                    graphTS2UK.node(str(df.display_name), color="cyan3", shape="box", style="filled")
                    graphTS2UK.edge('Root',str(df.display_name))
                    try: #add Test case level
                        for testCase in df.tests:
                            try:
                                for testStep in testCase.steps:
                                    if str(testStep.keyword) in user_def_keyword: #record all of using UK
                                        tempEdge.append((str(testStep.keyword),str(df.display_name)))
                                        #graphTS2UK.edge(str(testStep.keyword),str(df.display_name))
                            except Exception, e:
                                print str(e)
                    except Exception, e:
                        print str(e)
        except Exception, e:
            print str(e)

        for node in tempEdge:
            tempEdgeSet.add(node)
        for node in tempEdgeSet:
            graphTS2UK.edge(node[0], node[1], label=str(tempEdge.count(node)),penwidth=str(math.log(tempEdge.count(node),2)+1))

        graphTS2UK.render('TS2UK.gv',view=False)

    def relationBetweenTSandK(self,user_def_keyword,testSuites):
        graphTS2K = graphviz.Digraph(comment='TS <-> K', engine='fdp')
        graphTS2K.node('Root')
        tempEdge = list()
        tempEdgeSet = set()
        for node in user_def_keyword:
            graphTS2K.node(str(node))
        try:
            for df in self._get_datafile_list(): #get suite level
                if len(df.tests._items) > 0: #not empty
                    graphTS2K.node(str(df.display_name),color="lightgray", shape="box", style="filled")
                    graphTS2K.edge('Root',str(df.display_name))
                    try: #add Test case level
                        for testCase in df.tests:
                            try:
                                for testStep in testCase.steps:
                                    if str(testStep.keyword) in user_def_keyword: #record all of using UK
                                        graphTS2K.node(str(testStep.keyword),color="coral", shape="box", style="filled")
                                    else:
                                        graphTS2K.node(str(testStep.keyword), color="bisque", shape="box", style="filled")
                                    tempEdge.append((str(testStep.keyword),str(df.display_name)))
                                    #graphTS2K.edge(str(testStep.keyword),str(df.display_name))
                            except Exception, e:
                                print str(e)
                    except Exception, e:
                        print str(e)
        except Exception, e:
            print str(e)

        for node in tempEdge:
            tempEdgeSet.add(node)
        for node in tempEdgeSet:
            graphTS2K.edge(node[0], node[1], label=str(tempEdge.count(node)),penwidth=str(math.log(tempEdge.count(node),2)+1))


        graphTS2K.render('TS2K.gv',view=False)

    def relationBetweenTCandUK(self,user_def_keyword,testSuites):
        graphTC2UK = graphviz.Digraph(comment='TC <-> UK', engine='dot')
        graphTC2UK.node('Root')

        tempEdge = list()
        tempEdgeSet = set()

        for node in user_def_keyword:
            graphTC2UK.node(str(node), color="coral", shape="box", style="filled")

        try:
            for df in self._get_datafile_list(): #get suite level
                if len(df.tests._items) > 0: #not empty
                    try: #add Test case level
                        for testCase in df.tests:
                            graphTC2UK.node(str(testCase.name), color="darkolivegreen2", shape="box", style="filled")
                            graphTC2UK.edge('Root',str(testCase.name))
                            try:
                                for testStep in testCase.steps:
                                    if str(testStep.keyword) in user_def_keyword: #record all of using UK
                                        tempEdge.append((str(testCase.name), str(testStep.keyword)))
                                        #graphTC2UK.edge(str(testCase.name), str(testStep.keyword))
                            except Exception, e:
                                print str(e)
                    except Exception, e:
                        print str(e)
        except Exception, e:
            print str(e)

        for node in tempEdge:
            tempEdgeSet.add(node)
        for node in tempEdgeSet:
            graphTC2UK.edge(node[0], node[1], label=str(tempEdge.count(node)),penwidth=str(math.log(tempEdge.count(node),2)+1))


        graphTC2UK.render('TC2UK.gv',view=False)

    def relationBetweenTCandLK(self,user_def_keyword,testSuites):
        graphTC2LK = graphviz.Digraph(comment='TC <-> LK', engine='fdp')
        graphTC2LK.node('Root')

        tempEdge = list()
        tempEdgeSet = set()

        try:
            for df in self._get_datafile_list(): #get suite level
                if len(df.tests._items) > 0: #not empty
                    try: #add Test case level
                        for testCase in df.tests:
                            graphTC2LK.node(str(testCase.name), color="darkolivegreen2", shape="box", style="filled")
                            graphTC2LK.edge('Root',str(testCase.name))
                            try:
                                for testStep in testCase.steps:
                                    if str(testStep.keyword) not in user_def_keyword: #record all of using UK
                                        graphTC2LK.node(str(testStep.keyword), color="bisque", shape="box", style="filled")
                                        tempEdge.append((str(testCase.name), str(testStep.keyword)))
                                        #graphTC2LK.edge(str(testCase.name), str(testStep.keyword))
                            except Exception, e:
                                print str(e)
                    except Exception, e:
                        print str(e)
        except Exception, e:
            print str(e)

        for node in tempEdge:
            tempEdgeSet.add(node)
        for node in tempEdgeSet:
            graphTC2LK.edge(node[0], node[1], label=str(tempEdge.count(node)),penwidth=str(math.log(tempEdge.count(node),2)+1))

        graphTC2LK.render('TC2LK.gv',view=False)

    def relationBetweenTCandK(self,user_def_keyword,testSuites):
        graphTC2K = graphviz.Digraph(comment='TC <-> K', engine='dot')
        graphTC2K.node('Root')

        tempEdge = list()
        tempEdgeSet = set()
        tempAllStep = list()
        try:
            for df in self._get_datafile_list(): #get suite level
                if len(df.tests._items) > 0: #not empty
                    try: #add Test case level
                        for testCase in df.tests:
                            graphTC2K.node(str(testCase.name), color="darkolivegreen2", shape="box", style="filled")
                            graphTC2K.edge('Root',str(testCase.name))
                            try:
                                for testStep in testCase.steps:
                                    if str(testStep.keyword) in user_def_keyword: #record all of using UK
                                        graphTC2K.node(str(testStep.keyword),color="coral", shape="box", style="filled")
                                    else:
                                        graphTC2K.node(str(testStep.keyword), color="bisque", shape="box", style="filled")
                                    tempEdge.append((str(testCase.name),str(testStep.keyword)))
                                    tempAllStep.append(str(testStep.keyword))
                                    #graphTC2K.edge(str(testCase.name),str(testStep.keyword))
                            except Exception, e:
                                print str(e)
                    except Exception, e:
                        print str(e)
        except Exception, e:
            print str(e)

        for node in tempEdge:
            tempEdgeSet.add(node)

        for node in tempEdgeSet:
            graphTC2K.edge(node[0], node[1], label=str(tempEdge.count(node)),penwidth=str(math.log(tempEdge.count(node),2)+1))

        graphTC2K.render('TC2K.gv',view=False)
        return tempAllStep

    def relationBetweenUKandLK(self,user_def_keyword, userKeywordObject):
        graphUK2LK = graphviz.Digraph(comment='UK <-> LK', engine='fdp')
        graphUK2LK.node('Root')

        tempEdge = list()
        tempEdgeSet = set()

        try:
            for df in self._get_datafile_list(): #get suite level
                if len(df.tests._items) > 0: #not empty
                    try: #add Test case level
                        for testCase in df.tests:
                            try:
                                for testStep in testCase.steps:
                                    if str(testStep.keyword) in user_def_keyword: #record all of using UK
                                        graphUK2LK.node(str(testStep.keyword),color="coral", shape="box", style="filled")
                                        tempEdge.append(('Root',str(testStep.keyword)))
                                        #graphUK2LK.edge('Root',str(testStep.keyword))
                                    else:
                                        graphUK2LK.node(str(testStep.keyword), color="bisque", shape="box", style="filled")
                            except Exception, e:
                                print str(e)

                    except Exception, e:
                        print str(e)
        except Exception, e:
            print str(e)
        for node2 in userKeywordObject:
            for step in node2.steps:
                if str(step.keyword) in user_def_keyword:
                    graphUK2LK.node(str(step.keyword),color="coral", shape="box", style="filled")
                else:
                    graphUK2LK.node(str(step.keyword), color="bisque", shape="box", style="filled")
                tempEdge.append((node2.name.encode('ascii', 'ignore'),str(step.keyword)))
                #graphUK2LK.edge(node2.name.encode('ascii', 'ignore'),str(step.keyword))

        for node in tempEdge:
            tempEdgeSet.add(node)

        UKLKCount = dict()
        for node in tempEdgeSet:
            graphUK2LK.edge(node[0], node[1], label=str(tempEdge.count(node)),penwidth=str(math.log(tempEdge.count(node),2)+1))
            UKLKCount[node[0]] = tempEdge.count(node)

        graphUK2LK.render('UK2LK.gv',view=False)
        return UKLKCount

    def listComponent(self, user_def_keyword, tempComponentList, userKeywordObject):

        graphC = graphviz.Graph(comment='Component-only', engine='dot', graph_attr={'splines': 'false'} )
        tempEdgeSet = set()
        tempEdge = list()
        appearList = list()
        tempNode = set()
        nodesWithType = dict()

        for node in tempComponentList:
            graphC.node("C_"+str(node), color="pink", shape="box", style="filled")
            tempNode.add("C_"+str(node))
            nodesWithType["C_"+str(node)] = "Component"

        for node in user_def_keyword:
            graphC.node(node, color="coral", shape="box", style="filled")

        try:
            for df in self._get_datafile_list():
                if len(df.tests._items) > 0:
                    try:
                        for testCase in df.tests:
                            graphC.node(str(testCase.name), color="darkolivegreen2", shape="box", style="filled")
                            tempNode.add(str(testCase.name))
                            nodesWithType[str(testCase.name)] = "Test Case"
                            try:
                                for testStep in testCase.steps:

                                    if str(testStep.keyword) in user_def_keyword:
                                        #graphC.node(str(testStep.keyword),color="coral", shape="box", style="filled")
                                        tempNode.add(str(testStep.keyword))
                                        nodesWithType[str(testStep.keyword)] = "User Keyword"
                                        tempEdge.append((str(testCase.name),str(testStep.keyword)))

                                    else:#if and only if the component is appear in our components list
                                        if str(testStep.keyword) in tempComponentList:
                                            appearList.append((str(testCase.name),"C_"+str(testStep.keyword)))
                            except Exception, e:
                                print str(e)
                    except Exception, e:
                        print str(e)
        except Exception, e:
            print str(e)
        tempAppear = sorted(appearList, key=itemgetter(0, 1))
        tempCount = 0
        tempEdgeCount = 0
        tempNodeName = ''

        tempNodeWithoutGhostNode = list(tempNode)
        tempEdgeWithoutGhostNode = list(tempEdge)






        for node in tempAppear: #insert ghost node to adjest the node level
            if tempNodeName != node[1]:
                tempCount += 1 #ghost node name
            tempEdge.append((node[0], str(tempCount)))
            graphC.node(str(tempCount), shape="point")
            tempEdge.append((str(tempCount), node[1]))
            tempEdgeWithoutGhostNode.append((node[0], node[1]))
            tempNodeName = node[1]
            tempEdgeCount += 1

        for node2 in userKeywordObject:#connect UK and C and UK UK
            for step in node2.steps:
                if str(step.keyword) in tempComponentList:
                    tempEdge.append((str(node2.name), 'C_' + str(step.keyword)))
                    tempEdgeWithoutGhostNode.append((str(node2.name), 'C_' + str(step.keyword)))
                elif str(step.keyword) in user_def_keyword:
                    tempEdge.append((str(node2.name), str(step.keyword)))
                    tempEdgeWithoutGhostNode.append((str(node2.name), str(step.keyword)))
                    graphC.node(str(step.keyword), color="coral", shape="box", style="filled")

        for node in tempEdge:
            tempEdgeSet.add(node)

        tempNoGhostNodeEdgeSet = set()
        for node in tempEdgeWithoutGhostNode:
            tempNoGhostNodeEdgeSet.add(node)

        #calculate the changing impact
        ukChangeImpact = dict()
        for uk in user_def_keyword:
            ukChangeImpact[uk] = [False,0,list()]
        for edge in tempNoGhostNodeEdgeSet:
            if str(edge[1]) in user_def_keyword:
                ukChangeImpact[edge[1]][2].append(str(edge[0]))
        finishTag = True
        while finishTag:
            finishTag = False
            for uk in user_def_keyword:
                if len(ukChangeImpact[uk][2]) != 0:
                    for node in ukChangeImpact[uk][2]:
                        if node in user_def_keyword:
                            if ukChangeImpact[node][0]: #get Impact finished UK
                                ukChangeImpact[uk][1] += ukChangeImpact[node][1] + tempEdgeWithoutGhostNode.count((node,uk))
                                ukChangeImpact[uk][2].remove(node)
                        else: #is TC
                            ukChangeImpact[uk][1] += tempEdgeWithoutGhostNode.count((node,uk))
                            ukChangeImpact[uk][2].remove(node)
                    finishTag = True
                else:
                    ukChangeImpact[uk][0] = True

        componentChangeImpact = dict()
        for c in tempComponentList:
            componentChangeImpact[c] = 0
            for node in tempNoGhostNodeEdgeSet:
                if node[1] == "C_"+c:
                    if node[0] in user_def_keyword:
                        componentChangeImpact[c] += ukChangeImpact[node[0]][1] + tempEdgeWithoutGhostNode.count(node)
                    else:
                        componentChangeImpact[c] += tempEdgeWithoutGhostNode.count(node)

        #combine same component
        f = open('componentList.txt')
        samelist = f.read().splitlines()
        checkSameList = dict()
        for item in samelist:
            checkSameList["C_"+item.split()[0]] = "C_"+item.split()[1]
        tempClearNode = list()
        for node in checkSameList:
            componentChangeImpact[checkSameList[node][2:]] += componentChangeImpact[node[2:]]
            tempClearNode.append(node[2:])
        for node in tempClearNode:
            componentChangeImpact[node] = 0

        print componentChangeImpact

        for node in tempEdgeSet:
            graphC.edge(node[0] in checkSameList and checkSameList[node[0]] or node[0], node[1] in checkSameList and checkSameList[node[1]] or node[1], minlen="30.0", label=str(tempEdge.count(node)))
            #graphC.edge(node[0], node[1], minlen="30.0", label=str(tempEdge.count(node)), penwidth=(tempEdge.count(node)*5 > 50) and "50" or str(tempEdge.count(node)*5))
            #graphC.edge(node[0], node[1], minlen="1", label=str(tempEdge.count(node)),penwidth=str(math.log(tempEdge.count(node),2)+1))
        #len(tempEdgeSet)-tempCount means we should sub the ghost edges
        unWeightedCoupling = str(round((len(tempEdgeSet)-tempCount)/float(len(tempNode) -(1+7)),2))#8 is coupling node and six unused Component

        self.generateD3Graph(tempEdgeWithoutGhostNode, nodesWithType, tempNodeWithoutGhostNode)

        graphC.node("Weighted Coupling: "+str(len(tempEdge)-tempEdgeCount)+"\nEdge: "+str(len(tempEdgeSet)-tempCount)+"\nNode: "+str(len(tempNode))+"\nUnweighted Coupling: "+unWeightedCoupling, style="filled", fillcolor="yellow", shape="rect", width="2", height="3", fontsize="40")




        graphC.render('C.gv',view=False)




    def insertScreenShot(self):
        tempList = list()
        try:
            for df in self._get_datafile_list():
                if len(df.tests._items) > 0:
                    try:
                        for testCase in df.tests:
                            try:
                                for step in testCase.steps:
                                    counter = len(step)
                                    while counter > 0:
                                        testCase.insert("ScreenShot", counter)
                                        counter -=1
                            except Exception, e:
                                print str(e)
                    except Exception, e:
                        print str(e)
        except Exception, e:
            print str(e)

    def OnTestSuiteUseKeyword(self,event):
        self.insertScreenShot()
        f = open('node_display_config.txt')
        blacklist = f.read().splitlines()
        nodeCount = 0.0
        edgeCount = 0.0
        dot = graphviz.Digraph(comment='TestCases', engine='fdp')
        dot_testSuiteLevel = graphviz.Digraph(comment='TestSuiteLevel', engine='fdp')
        edgeList = list() #contain the using relation between two keywords
        nodeList = set() #record all of the nodes
        nodeList.add('Root')
        dot_testSuiteLevel.node('Root')
        nodeCount += 1
        testSuites = list()
        user_def_keyword = dict()
        userKeywordObject = list()
        tempComponentList = list()
        try:
            for df in self._get_datafile_list():
                if type(df) is robotide.controller.filecontrollers.ResourceFileController:
                    for item in df.keywords:
                        tempComponentList.append(item.name.encode('ascii', 'ignore'))
                if len(df.tests._items) > 0:
                    if str(df.display_name) not in blacklist:
                         testSuite_temp = list()
                         testSuite_temp.append(str(df.display_name))
                         dot_testSuiteLevel.node(str(df.display_name))
                         dot_testSuiteLevel.edge('Root',str(df.display_name))
                         nodeList.add(str(df.display_name))
                         edgeList.append(('Root',str(df.display_name)))
                    try: #add Test case level
                        for testCase in df.tests:
                            if str(testCase.name) not in blacklist:
                                nodeList.add(str(testCase.name))
                                edgeList.append((str(df.display_name),str(testCase.name)))
                                try: #sometimes test case will be not found
                                    for testStep in testCase.steps:
                                        if str(testStep.keyword) not in blacklist:
                                            nodeList.add(str(testStep.keyword))
                                            edgeList.append((str(testCase.name),str(testStep.keyword)))
                                except Exception, e:
                                    print str(e)
                    except Exception, e:
                        print str(e)
                    try: #add keyword level
                        for keyword in df.keywords:
                            nodeList.add(str(keyword.name))
                            try:
                                for keywordStep in keyword.steps:
                                    if str(keywordStep.keyword) not in blacklist:
                                        nodeList.add(str(keywordStep.keyword))
                                        edgeList.append((str(keyword.name),str(keywordStep.keyword)))
                                        usedKeyword = False
                                        for edge in edgeList:
                                            if str(keyword.name) == edge[1]:
                                                usedKeyword = True
                            except Exception, e:
                                print str(e)
                    except Exception, e:
                        print str(e)
                    try: #add user defined keyword
                        for keyword in df.data.keywords:
                            userKeywordObject.append(keyword)
                            temp_name = keyword.name.encode('ascii', 'ignore')
                            user_def_keyword[temp_name]=str(df.display_name)
                    except Exception, e:
                        print str(e)
                    testSuites.append(df.display_name.encode('ascii', 'ignore'))
        except Exception, e:
            print str(e)

        self.relationBetweenTSandTS(user_def_keyword,testSuites)
        self.relationBetweenTSandTC(user_def_keyword,testSuites)
        self.relationBetweenTSandUK(user_def_keyword,testSuites)
        self.relationBetweenTSandK(user_def_keyword,testSuites)
        self.relationBetweenTCandUK(user_def_keyword,testSuites)
        self.relationBetweenTCandLK(user_def_keyword,testSuites)
        tempAllStep = self.relationBetweenTCandK(user_def_keyword,testSuites)
        self.relationBetweenUKandLK(user_def_keyword,userKeywordObject)
        self.listComponent(user_def_keyword, tempComponentList, userKeywordObject)
        ukWeight = dict()
        ukTempCount = 0
        for uk in userKeywordObject:
            ukWeight[uk.name.encode('ascii', 'ignore')] = len(uk.steps)
        for uk in userKeywordObject:
            ukTempCount = 0
            for step in uk.steps:
                if str(step.keyword) in user_def_keyword:
                    ukTempCount += ukWeight[str(step.keyword)]
                else:
                    ukTempCount += 1
            ukWeight[uk.name.encode('ascii', 'ignore')] = ukTempCount
        actionCount = 0
        for node in tempAllStep:
            if node in user_def_keyword:
                actionCount += ukWeight[node]
            else:
                actionCount += 1
        print "Action: " + str(actionCount)


        for node in nodeList:
            if node not in blacklist:
                dot.node(node)
        nodeCount = len(nodeList)
        edgeSet = set()
        edgeColor = '#000000'
        edgeAppear = []
        edgeCount = len(edgeList)
        for item in edgeList:
            edgeSet.add(item)
        for node in edgeSet: #connect the using ralation by check the edgeList
            edgeAppear.append(edgeList.count(node))
        timesCount = 'Edge(times)  Count'+'\n'
        timeSet = set()
        for item in edgeAppear:
            timeSet.add(item)
        if len(timeSet)/5.0 < 1:
            timeSetInterval = 1
        else:
            timeSetInterval = len(timeSet)/5.0
        timeList= []
        for time in timeSet:
            timeList.append(time)
        timeList = sorted(timeList)
        nodeEdgeCounter = {} #a dictionary to store the edge count with all the nodes
        for nodeName in nodeList:
            nodeEdgeCounter[nodeName] = 0
        for node in edgeSet:#connect edge and asign a color to it (Note: each node contain two node's name)
            nodeAppear = edgeList.count(node)
            nodeEdgeCounter[node[1]] = nodeAppear
            if nodeAppear <= timeList[int(round(timeSetInterval))-1]:
                edgeColor = '#9C9C9C' #gray
            elif nodeAppear <= timeList[int(round(timeSetInterval*2))-1]:
                edgeColor = '#1E90FF' #blue
            elif nodeAppear <= timeList[int(round(timeSetInterval*3))-1]:
                edgeColor = '#00CD00' #green
            elif nodeAppear <= timeList[int(round(timeSetInterval*4))-1]:
                edgeColor = '#FFD700' #gold
            else:
                edgeColor = '#FF6A6A' #pink
            dot.edge(node[0], node[1], color=edgeColor)
        try:
            for node in timeList:
                timesCount += str(node) + '               ' + str(edgeAppear.count(node))
                timesCount += '\n'
        except Exception, e:
            print str(e)
        dot.attr('node', shape='box', labeljust='l')
        #dot.node(timesCount, labeljust='l')
        dot.node('Edge: ' + str(edgeCount) + '\n' + 'Node: ' + str(nodeCount) + '\n' + 'Coupling: ' + str(round(edgeCount/float(nodeCount -1),2) ))
        if len(timeSet)/5.0 <= 1.0:
            dot.node('Edge Color(times) \n' + '1 :Gray  \n' + '2 :Blue  \n'+ '3 :Green  \n'+ '4 :Gold  \n'+ '5 :Pink  \n' )
        else:
            dot.node('Edge Color(times) \n' +str(timeList[int(round(timeSetInterval))-1]) + ' :Gray  \n' + str(timeList[int(round(timeSetInterval*2))-1]) + ' :Blue \n' + str(timeList[int(round(timeSetInterval*3))-1]) + ' :Green \n' + str(timeList[int(round(timeSetInterval*4))-1]) + ' :Gold\nover ' + str(timeList[int(round(timeSetInterval*4))-1]) + ' :Pink \n')
        tempNodeEdgeCounter = 'In-Edges \n'
        for key,value in sorted(nodeEdgeCounter.iteritems(), key=lambda (k,v): (v,k)):
            tempNodeEdgeCounter += str(key) +': ' + str(value) + '\n'
        #dot.node(tempNodeEdgeCounter)

        jsonOutput = dict()
        nodeOutput = list()
        edgeOutput = list()

        for node in nodeList:
            nodeOutput.append({node: {'name': node}})
        for edge in edgeSet:
            edgeOutput.append({edge[0]:{'connect':edge[1],'times': 0}})
        jsonOutput = {'nodes':nodeOutput , 'edges': edgeOutput ,'coupling': 0}
        with open('scriptGraph.json','w+') as f:
            json.dump(jsonOutput,f)
        #create for process map
        with open('object.json','w+') as f:
            json.dump(jsonOutput,f)
        #dot.render('TestCases.gv',view=False)
        #dot_testSuiteLevel.render('testSuiteLevel.gv',view=False)
        tempDataFile = self._get_datafile_list()
        self.ShowMessage('Script:  '+ tempDataFile[0].display_name +'\nGenerate Script Graph Finish. \n Actions:' + str(actionCount))

    def OnIgnoreNodes(self,event):
        filename = 'file:///Bitnami/wordpress-4.4.1-0/apache2/htdocs/TSVisual/' + 'index.html'
        webbrowser.open_new_tab(filename)

    def generateD3Graph(self, edges, nodesWithType, nodes):
        jsonOutput = []
        edgeSet =set()
        for item in edges:
            edgeSet.add(item)

        for node in nodes:
            tempDepend = list()
            for item in edgeSet:
                if item[0] == node:
                    tempDepend.append(item[1])
            jsonOutput.append({
                    "depends": tempDepend,
                    "type": nodesWithType[node],
                    "name": node
            })
        with open('component.json','w+') as f:
            json.dump(jsonOutput,f)

        print jsonOutput

    def _get_datafile_list(self):
        return [df for df in self._controller.datafiles]

    def _has_data(self):
        return self._controlller.data is not None

    def _refresh(self):
        self._controller.update_namespace()

# This code is copied from http://wiki.wxpython.org/EnsureFrameIsOnScreen,
# and adapted to fit our code style.
    def ensure_on_screen(self):
        try:
            display_id = wx.Display.GetFromWindow(self)
        except NotImplementedError:
            display_id = 0
        if display_id == -1:
            display_id = 0
        geometry = wx.Display(display_id).GetGeometry()
        position = self.GetPosition()
        if position.x < geometry.x:
            position.x = geometry.x
        if position.y < geometry.y:
            position.y = geometry.y
        size = self.GetSize()
        if size.width > geometry.width:
            size.width = geometry.width
            position.x = geometry.x
        elif position.x + size.width > geometry.x + geometry.width:
            position.x = geometry.x + geometry.width - size.width
        if size.height > geometry.height:
            size.height = geometry.height
            position.y = geometry.y
        elif position.y + size.height > geometry.y + geometry.height:
            position.y = geometry.y + geometry.height - size.height
        self.SetPosition(position)
        self.SetSize(size)


class ActionRegisterer(object):

    def __init__(self, menubar, toolbar, shortcut_registry):
        self._menubar = menubar
        self._toolbar = toolbar
        self._shortcut_registry = shortcut_registry
        self._tools_items = {}

    def register_action(self, action_info):
        menubar_can_be_registered = True
        action = ActionFactory(action_info)
        self._shortcut_registry.register(action)
        if hasattr(action_info,"menu_name"):
            if action_info.menu_name == "Tools":
                self._tools_items[action_info.position] = action
                menubar_can_be_registered = False
        if menubar_can_be_registered:
            self._menubar.register(action)
        self._toolbar.register(action)
        return action

    def register_tools(self):
        separator_action = ActionFactory(SeparatorInfo("Tools"))
        add_separator_after = ["stop test run","search unused keywords","preview","view ride log"]
        for key in sorted(self._tools_items.iterkeys()):
            self._menubar.register(self._tools_items[key])
            if self._tools_items[key].name.lower() in add_separator_after:
                self._menubar.register(separator_action)

    def register_actions(self, actions):
        for action in actions:
            self.register_action(action)

    def register_shortcut(self, action_info):
        action = ActionFactory(action_info)
        self._shortcut_registry.register(action)
        return action


class AboutDialog(Dialog):

    def __init__(self):
        Dialog.__init__(self, title='RIDE')
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(HtmlWindow(self, (450, 200), ABOUT_RIDE), 1, flag=wx.EXPAND)
        self.SetSizerAndFit(sizer)

    def OnKey(self, *args):
        pass


class ShortcutKeysDialog(Dialog):

    def __init__(self):
        Dialog.__init__(self, title='Shortcut keys for RIDE')
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(HtmlWindow(self, (350, 400), self._get_platform_specific_shortcut_keys()), 1, flag=wx.EXPAND)
        self.SetSizerAndFit(sizer)

    def OnKey(self, *args):
        pass

    def _get_platform_specific_shortcut_keys(self):
        return localize_shortcuts(SHORTCUT_KEYS)
