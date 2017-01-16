# -*- coding: utf-8 -*-　

import wx
import math
import json
import webbrowser
import robotide
from operator import itemgetter, attrgetter
import graphviz
from graphviz import Graph
from robot.parsing.model import Step
from duplicatedactiondetection import LongestCommonSubsequence, LongestRepeatedSubstring

from shutil import copyfile

import time
import os

import itertools


class KTV:
    def __init__(self):
        self.datafiles = None
        self.componentChangeImpact = dict()
        self.user_def_keyword = dict()
        self.userKeywordObject = list()

        # self.duplicatedactiondetection = LongestCommonSubsequence()
        self.duplicatedactiondetection = LongestRepeatedSubstring()

        self.serial_number_flag = True  # 使node顯示名稱變成流水號

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

    def relationBetweenTSandTS(self, testSuites):
        graphTS2TS = graphviz.Digraph(comment='TS <-> TS', engine='dot')
        edgeSet = list()
        nodeList = set()
        graphTS2TS.node('Root')
        for suite in testSuites:
            nodeList.add(suite)
        for node in nodeList:
            graphTS2TS.node(node, color="cyan3", shape="box", style="filled")
            graphTS2TS.edge('Root', node)
        try:
            for df in self.datafiles:  # get suite level
                tempSuiteUseUserKeyword = list()
                tempSet = set()
                if len(df.tests._items) > 0:  # not empty
                    try:  # add Test case level
                        for testCase in df.tests:
                            try:
                                for testStep in testCase.steps:
                                    if str(testStep.keyword) in self.user_def_keyword:  # record all of using UK
                                        if self.user_def_keyword[str(testStep.keyword)] != str(df.display_name):
                                            tempSuiteUseUserKeyword.append(self.user_def_keyword[str(testStep.keyword)])
                            except Exception, e:
                                print str(e)

                        for node in tempSuiteUseUserKeyword:  # remove the duplicate node
                            tempSet.add(node)
                        for node in tempSet:
                            graphTS2TS.edge(str(df.display_name), node, label=str(tempSuiteUseUserKeyword.count(node)),
                                            penwidth=str(math.log(tempSuiteUseUserKeyword.count(node), 2) + 1))
                    except Exception, e:
                        print str(e)
        except Exception, e:
            print str(e)
        graphTS2TS.render('KTVgraph/TS2TS.gv', view=False)

    # copyfile('KTVgraph/TS2TS.gv.pdf', 'C:/wamp64/www/TSVisual/graph/TS2TS.gv.pdf')

    def relationBetweenTSandTC(self):
        graphTS2TC = graphviz.Digraph(comment='TS <-> TC', engine='sfdp')
        # graphTS2TC.node('Root')
        tempEdge = list()
        tempEdgeSet = set()
        try:
            for df in self.datafiles:  # get suite level
                if len(df.tests._items) > 0:  # not empty
                    graphTS2TC.node(str(df.display_name), color="cyan3", shape="box", style="filled")
                    try:  # add Test case level
                        for testCase in df.tests:
                            graphTS2TC.node(str(testCase.name), color="darkolivegreen2", shape="box", style="filled")
                            graphTS2TC.edge(str(df.display_name), str(testCase.name), len="10")
                    except Exception, e:
                        print str(e)
        except Exception, e:
            print str(e)
        for node in tempEdge:  # remove the duplicate node
            tempEdgeSet.add(node)
        for node in tempEdgeSet:
            graphTS2TC.edge(node[0], node[1], label=str(tempEdge.count(node)))
        graphTS2TC.render('KTVgraph/TS2TC.gv', view=False)
        copyfile('KTVgraph/TS2TC.gv.pdf', 'C:/wamp64/www/TSVisual/graph/TS2TC.gv.pdf')

    def relationBetweenTSandUK(self):
        graphTS2UK = graphviz.Digraph(comment='TS <-> UK', engine='sfdp')
        # graphTS2UK.node('Root')
        tempEdge = list()
        tempEdgeSet = set()
        for node in self.user_def_keyword:
            graphTS2UK.node(str(node), color="coral", shape="box", style="filled")
        try:
            for df in self.datafiles:  # get suite level
                if len(df.tests._items) > 0:  # not empty
                    graphTS2UK.node(str(df.display_name), color="cyan3", shape="box", style="filled")
                    try:  # add Test case level
                        for testCase in df.tests:
                            try:
                                for testStep in testCase.steps:
                                    if str(testStep.keyword) in self.user_def_keyword:  # record all of using UK
                                        tempEdge.append((str(df.display_name), str(testStep.keyword)))
                            except Exception, e:
                                print str(e)
                    except Exception, e:
                        print str(e)
        except Exception, e:
            print str(e)

        for node in tempEdge:  # remove the duplicate node
            tempEdgeSet.add(node)
        for node in tempEdgeSet:
            graphTS2UK.edge(node[0], node[1], len="10.0", label=str(tempEdge.count(node)))
        graphTS2UK.render('KTVgraph/TS2UK.gv', view=False)
        copyfile('KTVgraph/TS2UK.gv.pdf', 'C:/wamp64/www/TSVisual/graph/TS2UK.gv.pdf')

    def relationBetweenTSandK(self):
        graphTS2K = graphviz.Digraph(comment='TS <-> K', engine='fdp')
        tempEdge = list()
        tempEdgeSet = set()
        try:
            for df in self.datafiles:  # get suite level
                if len(df.tests._items) > 0:  # not empty
                    graphTS2K.node(str(df.display_name), color="cyan3", shape="box", style="filled")
                    try:  # add Test case level
                        for testCase in df.tests:
                            try:
                                for testStep in testCase.steps:
                                    graphTS2K.node(str(testStep.keyword), color="bisque", shape="box", style="filled")
                                    tempEdge.append((str(df.display_name), str(testStep.keyword)))
                            except Exception, e:
                                print str(e)
                    except Exception, e:
                        print str(e)
        except Exception, e:
            print str(e)

        for node in tempEdge:  # remove the duplicate node
            tempEdgeSet.add(node)
        for node in tempEdgeSet:
            graphTS2K.edge(node[0], node[1], label=str(tempEdge.count(node)))

        graphTS2K.render('KTVgraph/TS2K.gv', view=False)
        copyfile('KTVgraph/TS2K.gv.pdf', 'C:/wamp64/www/TSVisual/graph/TS2K.gv.pdf')

    def relationBetweenTCandUK(self):
        graphTC2UK = graphviz.Digraph(comment='TC <-> UK', engine='sfdp')
        graphTC2UK.node('Root')
        tempEdge = list()
        tempEdgeSet = set()
        for node in self.user_def_keyword:
            graphTC2UK.node(str(node), color="coral", shape="box", style="filled")

        try:
            for df in self.datafiles:  # get suite level
                if len(df.tests._items) > 0:  # not empty
                    try:  # add Test case level
                        for testCase in df.tests:
                            graphTC2UK.node(str(testCase.name), color="darkolivegreen2", shape="box", style="filled")
                            graphTC2UK.edge('Root', str(testCase.name))
                            try:
                                for testStep in testCase.steps:
                                    if str(testStep.keyword) in self.user_def_keyword:  # record all of using UK
                                        tempEdge.append((str(testCase.name), str(testStep.keyword)))
                            except Exception, e:
                                print str(e)
                    except Exception, e:
                        print str(e)
        except Exception, e:
            print str(e)

        for node in tempEdge:  # remove the duplicate node
            tempEdgeSet.add(node)
        for node in tempEdgeSet:
            graphTC2UK.edge(node[0], node[1], len="10.0", label=str(tempEdge.count(node)))

        graphTC2UK.render('KTVgraph/TC2UK.gv', view=False)
        copyfile('KTVgraph/TC2UK.gv.pdf', 'C:/wamp64/www/TSVisual/graph/TC2UK.gv.pdf')

    def relationBetweenTCandLK(self):
        graphTC2LK = graphviz.Digraph(comment='TC <-> LK', engine='fdp')
        graphTC2LK.node('Root')
        tempEdge = list()
        tempEdgeSet = set()
        try:
            for df in self.datafiles:  # get suite level
                if len(df.tests._items) > 0:  # not empty
                    try:  # add Test case level
                        for testCase in df.tests:
                            graphTC2LK.node(str(testCase.name), color="darkolivegreen2", shape="box", style="filled")
                            graphTC2LK.edge('Root', str(testCase.name))
                            try:
                                for testStep in testCase.steps:
                                    if str(testStep.keyword) not in self.user_def_keyword:  # record all of using UK
                                        graphTC2LK.node(str(testStep.keyword), color="bisque", shape="box",
                                                        style="filled")
                                        tempEdge.append((str(testCase.name), str(testStep.keyword)))
                            except Exception, e:
                                print str(e)
                    except Exception, e:
                        print str(e)
        except Exception, e:
            print str(e)

        for node in tempEdge:  # remove the duplicate node
            tempEdgeSet.add(node)
        for node in tempEdgeSet:
            graphTC2LK.edge(node[0], node[1], label=str(tempEdge.count(node)),
                            penwidth=str(math.log(tempEdge.count(node), 2) + 1))

        graphTC2LK.render('KTVgraph/TC2LK.gv', view=False)
        copyfile('KTVgraph/TC2LK.gv.pdf', 'C:/wamp64/www/TSVisual/graph/TC2LK.gv.pdf')

    def relationBetweenTCandK(self):
        graphTC2K = graphviz.Digraph(comment='TC <-> K', engine='dot')
        graphTC2K.node('Root')
        tempEdge = list()
        tempEdgeSet = set()
        tempAllStep = list()
        try:
            for df in self.datafiles:  # get suite level
                if len(df.tests._items) > 0:  # not empty
                    try:  # add Test case level
                        for testCase in df.tests:
                            graphTC2K.node(str(testCase.name), color="darkolivegreen2", shape="box", style="filled")
                            graphTC2K.edge('Root', str(testCase.name))
                            try:
                                for testStep in testCase.steps:
                                    if str(testStep.keyword) in self.user_def_keyword:  # record all of using UK
                                        graphTC2K.node(str(testStep.keyword), color="coral", shape="box",
                                                       style="filled")
                                    else:
                                        graphTC2K.node(str(testStep.keyword), color="bisque", shape="box",
                                                       style="filled")
                                    tempEdge.append((str(testCase.name), str(testStep.keyword)))
                                    tempAllStep.append(str(testStep.keyword))
                            except Exception, e:
                                print str(e)
                    except Exception, e:
                        print str(e)
        except Exception, e:
            print str(e)

        for node in tempEdge:  # remove the duplicate node
            tempEdgeSet.add(node)
        for node in tempEdgeSet:
            graphTC2K.edge(node[0], node[1], label=str(tempEdge.count(node)),
                           penwidth=str(math.log(tempEdge.count(node), 2) + 1))

        graphTC2K.render('KTVgraph/TC2K.gv', view=False)
        # copyfile('KTVgraph/TC2K.gv.pdf', 'C:/wamp64/www/TSVisual/graph/TC2K.gv.pdf')
        return tempAllStep

    def relationBetweenUKandLK(self):
        graphUK2LK = graphviz.Digraph(comment='UK <-> LK', engine='fdp')
        graphUK2LK.node('Root')
        tempEdge = list()
        tempEdgeSet = set()
        try:
            for df in self.datafiles:  # get suite level
                if len(df.tests._items) > 0:  # not empty
                    try:  # add Test case level
                        for testCase in df.tests:
                            try:
                                for testStep in testCase.steps:
                                    if str(testStep.keyword) in self.user_def_keyword:  # record all of using UK
                                        graphUK2LK.node(str(testStep.keyword), color="coral", shape="box",
                                                        style="filled")
                                        tempEdge.append(('Root', str(testStep.keyword)))
                            except Exception, e:
                                print str(e)
                    except Exception, e:
                        print str(e)
        except Exception, e:
            print str(e)

        for node in self.userKeywordObject:
            for step in node.steps:
                # print 'step = %r' %(step)
                # print(step.name)
                """if str(step.keyword) in user_def_keyword:
                    graphUK2LK.node(str(step.keyword), color="coral", shape="box", style="filled")
                else:
                    graphUK2LK.node(str(step.keyword), color="bisque", shape="box", style="filled")
                tempEdge.append((node.name.encode('ascii', 'ignore'), str(step.keyword)))"""
                if str(step.name) in self.user_def_keyword:
                    graphUK2LK.node(str(step.name), color="coral", shape="box", style="filled")
                else:
                    graphUK2LK.node(str(step.name), color="bisque", shape="box", style="filled")
                tempEdge.append((node.name.encode('ascii', 'ignore'), str(step.name)))

        for node in tempEdge:
            tempEdgeSet.add(node)

        for node in tempEdgeSet:
            graphUK2LK.edge(node[0], node[1], label=str(tempEdge.count(node)))

        graphUK2LK.render('KTVgraph/UK2LK.gv', view=False)
        copyfile('KTVgraph/UK2LK.gv.pdf', 'C:/wamp64/www/TSVisual/graph/UK2LK.gv.pdf')

    def listComponent(self, tempComponentList):
        graphC = graphviz.Graph(comment='Component-only', engine='dot', graph_attr={'splines': 'false'})
        tempEdgeSet = set()
        tempEdge = list()
        appearList = list()
        tempNode = set()
        nodesWithType = dict()

        for node in tempComponentList:
            graphC.node("C_" + str(node), color="pink", shape="box", style="filled")
            tempNode.add("C_" + str(node))
            nodesWithType["C_" + str(node)] = "Component"
        for node in self.user_def_keyword:
            nodesWithType[node] = "UserKeyword"
            tempNode.add(node)
            graphC.node(node, color="coral", shape="box", style="filled")

        try:
            for df in self.datafiles:
                if len(df.tests._items) > 0:
                    try:
                        for testCase in df.tests:
                            graphC.node(str(testCase.name), color="darkolivegreen2", shape="box", style="filled")
                            tempNode.add(str(testCase.name))  # use dict make symbol for what the node is
                            nodesWithType[str(testCase.name)] = "TestCase"
                            try:
                                for testStep in testCase.steps:
                                    if str(
                                            testStep.keyword) in self.user_def_keyword:  # add userkeyword into node and edge
                                        tempNode.add(str(testStep.keyword))
                                        tempEdge.append((str(testCase.name), str(testStep.keyword)))
                                    else:  # if and only if the component is appear in our components list
                                        if str(testStep.keyword) in tempComponentList:
                                            appearList.append((str(testCase.name), "C_" + str(testStep.keyword)))
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

        for node in tempAppear:  # insert ghost node to adjust the node level
            if tempNodeName != node[1]:
                tempCount += 1  # ghost node name
            tempEdge.append((node[0], str(tempCount)))
            graphC.node(str(tempCount), shape="point")
            tempEdge.append((str(tempCount), node[1]))
            tempEdgeWithoutGhostNode.append((node[0], node[1]))
            tempNodeName = node[1]
            tempEdgeCount += 1

        for node in self.userKeywordObject:  # connect UK and C and UK UK
            for step in node.steps:
                """if str(step.keyword) in tempComponentList:
                    tempEdge.append((str(node.name), 'C_' + str(step.keyword)))
                    tempEdgeWithoutGhostNode.append((str(node.name), 'C_' + str(step.keyword)))
                elif str(step.keyword) in user_def_keyword:
                    tempEdge.append((str(node.name), str(step.keyword)))
                    tempEdgeWithoutGhostNode.append((str(node.name), str(step.keyword)))
                    graphC.node(str(step.keyword), color="coral", shape="box", style="filled")"""
                if str(step.name) in tempComponentList:
                    tempEdge.append((str(node.name), 'C_' + str(step.name)))
                    tempEdgeWithoutGhostNode.append((str(node.name), 'C_' + str(step.name)))
                elif str(step.name) in self.user_def_keyword:
                    tempEdge.append((str(node.name), str(step.name)))
                    tempEdgeWithoutGhostNode.append((str(node.name), str(step.name)))
                    graphC.node(str(step.name), color="coral", shape="box", style="filled")

        for node in tempEdge:  # remove the duplicate node
            tempEdgeSet.add(node)

        tempNoGhostNodeEdgeSet = set()  # remove the duplicate node
        for node in tempEdgeWithoutGhostNode:
            tempNoGhostNodeEdgeSet.add(node)

        self.calculateChangeImpact(tempNoGhostNodeEdgeSet, tempEdgeWithoutGhostNode,
                                   tempComponentList, graphC)

        # combine same component
        combineTag = True
        if combineTag:
            f = open('componentList.txt')
            samelist = f.read().splitlines()
            checkSameList = dict()
            for item in samelist:
                checkSameList["C_" + item.split()[0]] = "C_" + item.split()[1]
            tempClearNode = list()
            for node in checkSameList:
                self.componentChangeImpact[checkSameList[node][2:]] += self.componentChangeImpact[node[2:]]
                tempClearNode.append(node[2:])
            for node in tempClearNode:
                self.componentChangeImpact[node] = 0

        for node in tempEdgeSet:
            if not combineTag:
                graphC.edge(node[0], node[1], minlen="30.0", label=str(tempEdge.count(node)))
            else:
                graphC.edge(node[0] in checkSameList and checkSameList[node[0]] or node[0],
                            node[1] in checkSameList and checkSameList[node[1]] or node[1], minlen="30.0",
                            label=str(tempEdge.count(node)))
                # graphC.edge(node[0], node[1], minlen="30.0", label=str(tempEdge.count(node)), penwidth=(tempEdge.count(node)*5 > 50) and "50" or str(tempEdge.count(node)*5))
                # graphC.edge(node[0], node[1], minlen="1", label=str(tempEdge.count(node)),penwidth=str(math.log(tempEdge.count(node),2)+1))
        # len(tempEdgeSet)-tempCount means we should sub the ghost edges
        unWeightedCoupling = str(round((len(tempEdgeSet) - tempCount) / float(len(tempNode) - (1 + 7)),
                                       2))  # 8 is coupling node and six unused Component

        self.generateD3Graph(tempEdgeWithoutGhostNode, nodesWithType, tempNodeWithoutGhostNode)

        graphC.node("Weighted Coupling: " + str(len(tempEdge) - tempEdgeCount) + "\nEdge: " + str(
            len(tempEdgeSet) - tempCount) + "\nNode: " + str(
            len(tempNode)) + "\nUnweighted Coupling: " + unWeightedCoupling, style="filled", fillcolor="yellow",
                    shape="rect", width="2", height="3", fontsize="40")

        webbrowser.open('http://localhost/TSVisual/index.html')
        graphC.render('KTVgraph/C.gv', view=False)
        copyfile('KTVgraph/C.gv.pdf', 'C:/wamp64/www/TSVisual/graph/C.gv.pdf')

    def calculateChangeImpact(self, tempNoGhostNodeEdgeSet, tempEdgeWithoutGhostNode,
                              tempComponentList, graphC):
        # calculate the changing impact(full size)
        ukChangeImpact = dict()
        for uk in self.user_def_keyword:
            ukChangeImpact[uk] = [False, 0, list()]  # [whether calculate is finish, CI, children list]
        for edge in tempNoGhostNodeEdgeSet:
            if str(edge[1]) in self.user_def_keyword:
                ukChangeImpact[edge[1]][2].append(str(edge[0]))
        finishTag = True
        while finishTag:
            finishTag = False
            for uk in self.user_def_keyword:
                if len(ukChangeImpact[uk][2]) != 0:
                    for node in ukChangeImpact[uk][2]:
                        if node in self.user_def_keyword:
                            if ukChangeImpact[node][0]:  # get Impact finished UK
                                ukChangeImpact[uk][1] += ukChangeImpact[node][1] + tempEdgeWithoutGhostNode.count(
                                    (node, uk))
                                ukChangeImpact[uk][2].remove(node)
                        else:  # is TC
                            ukChangeImpact[uk][1] += tempEdgeWithoutGhostNode.count((node, uk))
                            ukChangeImpact[uk][2].remove(node)
                    finishTag = True
                else:
                    ukChangeImpact[uk][0] = True

        # calculate components' change impact
        # componentChangeImpact = dict()
        for c in tempComponentList:
            self.componentChangeImpact[c] = 0
            for node in tempNoGhostNodeEdgeSet:
                if node[1] == "C_" + c:
                    if node[0] in self.user_def_keyword:
                        self.componentChangeImpact[c] += ukChangeImpact[node[0]][1] + tempEdgeWithoutGhostNode.count(
                            node)
                    else:
                        self.componentChangeImpact[c] += tempEdgeWithoutGhostNode.count(node)

        # calculate the directly change impact
        lv1CI = 0
        componentCI = dict()
        for node in tempComponentList:
            componentCI[node] = 0
        for node in tempEdgeWithoutGhostNode:
            if node[1][2:] in tempComponentList:
                componentCI[node[1][2:]] += 1
                lv1CI += 1
        print str(lv1CI) + "  :CI"

        tempString = ""
        totalImapct = 0
        for node in self.componentChangeImpact:
            if self.componentChangeImpact[node] != 0:
                totalImapct += self.componentChangeImpact[node]
                tempString += node + ": " + str(self.componentChangeImpact[node]) + "\n"
        tempCIString = ""
        for node in componentCI:
            if componentCI[node] != 0:
                tempCIString += (node + ": " + str(componentCI[node]) + "\n")

        graphC.node("Level 3 change Impact: \n" + tempString + "\nTotal Impact: " + str(totalImapct), style="filled",
                    fillcolor="lightblue", shape="rect", width="2", height="3", fontsize="40")
        graphC.node("Level 1 change Impact: \n" + tempCIString + "\nTotal Imapct: " + str(lv1CI), style="filled",
                    fillcolor="lightblue2", shape="rect", width="2", height="3", fontsize="40")

    def AddTestCaseIntoNodeAndEdgeList(self, df, blacklist, nodeList, edgeList):
        try:  # add Test case level
            for testCase in df.tests:
                if str(testCase.name) not in blacklist:
                    nodeList.add(str(testCase.name))
                    edgeList.append((str(df.display_name), str(testCase.name)))
                    try:  # sometimes test case will be not found
                        for testStep in testCase.steps:
                            if str(testStep.keyword) not in blacklist:
                                nodeList.add(str(testStep.keyword))
                                edgeList.append((str(testCase.name), str(testStep.keyword)))
                    except Exception, e:
                        print str(e)
        except Exception, e:
            print str(e)

    def AddKeyworksIntoNodeAndEdgeList(self, df, blacklist, nodeList, edgeList):
        try:  # add keyword level
            for keyword in df.keywords:
                nodeList.add(str(keyword.name))
                try:  # add all keywords of userKeywords
                    for keywordStep in keyword.steps:
                        if str(keywordStep.keyword) not in blacklist:
                            nodeList.add(str(keywordStep.keyword))
                            edgeList.append((str(keyword.name), str(keywordStep.keyword)))
                            """usedKeyword = False #check whether userKeyword's step contains userKeyword
                            for edge in edgeList:
                                if str(keyword.name) == edge[1]:
                                    usedKeyword = True"""
                except Exception, e:
                    print str(e)
        except Exception, e:
            print str(e)
        try:  # add user defined keyword into userKeywordObject and add user_def_keyword dict
            for keywordObject in df.data.keywords:
                self.userKeywordObject.append(keywordObject)
                # print 'df.data.keyword = %r' % (keywordObject)
                temp_name = keywordObject.name.encode('ascii', 'ignore')
                # print 'keyword.name = %r' %(temp_name)
                self.user_def_keyword[temp_name] = str(df.display_name)
        except Exception, e:
            print str(e)

    def OnStaticGenerateGraph(self):
        # self.insertScreenShot()
        print os.getcwd()
        f = open('node_display_config.txt')
        blacklist = f.read().splitlines()  # read what the node should not be display
        nodeCount = 0.0
        edgeCount = 0.0
        dot = graphviz.Digraph(comment='TestCases', engine='fdp')
        dot_testSuiteLevel = graphviz.Digraph(comment='TestSuiteLevel', engine='fdp')
        edgeList = list()  # contain the using relation between two keywords
        nodeList = set()  # record all of the nodes
        nodeList.add('Root')
        dot_testSuiteLevel.node('Root')
        nodeCount += 1
        testSuites = list()
        tempComponentList = list()
        try:
            for df in self.datafiles:
                if type(
                        df) is robotide.controller.filecontrollers.ResourceFileController:  # if TC has resourceFile, add all keywords
                    for item in df.keywords:
                        tempComponentList.append(item.name.encode('ascii', 'ignore'))
                if len(df.tests._items) > 0:
                    print(str(df.display_name))
                    if str(df.display_name) not in blacklist:
                        testSuite_temp = list()
                        testSuite_temp.append(str(df.display_name))
                        dot_testSuiteLevel.node(str(df.display_name))
                        dot_testSuiteLevel.edge('Root', str(df.display_name))
                        nodeList.add(str(df.display_name))
                        edgeList.append(('Root', str(df.display_name)))
                    self.AddTestCaseIntoNodeAndEdgeList(df, blacklist, nodeList, edgeList)
                    self.AddKeyworksIntoNodeAndEdgeList(df, blacklist, nodeList, edgeList)
                    testSuites.append(df.display_name.encode('ascii', 'ignore'))
        except Exception, e:
            print str(e)

        self.relationBetweenTSandTS(testSuites)
        self.relationBetweenTSandTC()
        self.relationBetweenTSandUK()
        self.relationBetweenTSandK()
        self.relationBetweenTCandUK()
        self.relationBetweenTCandLK()
        tempAllStep = self.relationBetweenTCandK()
        self.relationBetweenUKandLK()
        self.listComponent(tempComponentList)
        ukWeight = dict()
        ukTempCount = 0

        for uk in self.userKeywordObject:
            ukWeight[uk.name.encode('ascii', 'ignore')] = len(uk.steps)
        for uk in self.userKeywordObject:
            ukTempCount = 0
            for step in uk.steps:
                if str(step.name) in self.user_def_keyword:
                    ukTempCount += ukWeight[str(step.name)]
                else:
                    ukTempCount += 1
            ukWeight[uk.name.encode('ascii', 'ignore')] = ukTempCount
        actionCount = 0
        for node in tempAllStep:
            if node in self.user_def_keyword:
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
        for node in edgeSet:  # connect the using ralation by check the edgeList
            edgeAppear.append(edgeList.count(node))
        timesCount = 'Edge(times)  Count' + '\n'
        timeSet = set()
        for item in edgeAppear:
            timeSet.add(item)
        if len(timeSet) / 5.0 < 1:
            timeSetInterval = 1
        else:
            timeSetInterval = len(timeSet) / 5.0
        timeList = []
        for time in timeSet:
            timeList.append(time)
        timeList = sorted(timeList)
        nodeEdgeCounter = {}  # a dictionary to store the edge count with all the nodes
        for nodeName in nodeList:
            nodeEdgeCounter[nodeName] = 0
        for node in edgeSet:  # connect edge and asign a color to it (Note: each node contain two node's name)
            nodeAppear = edgeList.count(node)
            nodeEdgeCounter[node[1]] = nodeAppear
            if nodeAppear <= timeList[int(round(timeSetInterval)) - 1]:
                edgeColor = '#9C9C9C'  # gray
            elif nodeAppear <= timeList[int(round(timeSetInterval * 2)) - 1]:
                edgeColor = '#1E90FF'  # blue
            elif nodeAppear <= timeList[int(round(timeSetInterval * 3)) - 1]:
                edgeColor = '#00CD00'  # green
            elif nodeAppear <= timeList[int(round(timeSetInterval * 4)) - 1]:
                edgeColor = '#FFD700'  # gold
            else:
                edgeColor = '#FF6A6A'  # pink
            dot.edge(node[0], node[1], color=edgeColor)
        try:
            for node in timeList:
                timesCount += str(node) + '               ' + str(edgeAppear.count(node))
                timesCount += '\n'
        except Exception, e:
            print str(e)
        dot.attr('node', shape='box', labeljust='l')
        # dot.node(timesCount, labeljust='l')
        dot.node('Edge: ' + str(edgeCount) + '\n' + 'Node: ' + str(nodeCount) + '\n' + 'Coupling: ' + str(
            round(edgeCount / float(nodeCount - 1), 2)))
        if len(timeSet) / 5.0 <= 1.0:
            dot.node(
                'Edge Color(times) \n' + '1 :Gray  \n' + '2 :Blue  \n' + '3 :Green  \n' + '4 :Gold  \n' + '5 :Pink  \n')
        else:
            dot.node('Edge Color(times) \n' + str(timeList[int(round(timeSetInterval)) - 1]) + ' :Gray  \n' + str(
                timeList[int(round(timeSetInterval * 2)) - 1]) + ' :Blue \n' + str(
                timeList[int(round(timeSetInterval * 3)) - 1]) + ' :Green \n' + str(
                timeList[int(round(timeSetInterval * 4)) - 1]) + ' :Gold\nover ' + str(
                timeList[int(round(timeSetInterval * 4)) - 1]) + ' :Pink \n')
        tempNodeEdgeCounter = 'In-Edges \n'
        for key, value in sorted(nodeEdgeCounter.iteritems(), key=lambda (k, v): (v, k)):
            tempNodeEdgeCounter += str(key) + ': ' + str(value) + '\n'
        # dot.node(tempNodeEdgeCounter)

        jsonOutput = dict()
        nodeOutput = list()
        edgeOutput = list()

        for node in nodeList:
            nodeOutput.append({node: {'name': node}})
        for edge in edgeSet:
            edgeOutput.append({edge[0]: {'connect': edge[1], 'times': 0}})
        jsonOutput = {'nodes': nodeOutput, 'edges': edgeOutput, 'coupling': 0}
        with open('scriptGraph.json', 'w+') as f:
            json.dump(jsonOutput, f)
        # create for process map
        with open('jsonOutPut.json', 'w+') as f:
            json.dump(jsonOutput, f)
        # dot.render('TestCases.gv',view=False)
        # dot_testSuiteLevel.render('testSuiteLevel.gv',view=False)
        tempDataFile = self.datafiles
        self.ShowMessage(
            'Script:  ' + tempDataFile[0].display_name + '\nGenerate Script Graph Finish. \n Actions:' + str(
                actionCount))

    def OnIgnoreNodes(self, event):
        filename = 'file:///Bitnami/wordpress-4.4.1-0/apache2/htdocs/TSVisual/' + 'index.html'
        webbrowser.open_new_tab(filename)

    def generateD3Graph(self, edges, nodesWithType, nodes):
        jsonOutput = []
        edgeSet = set()
        for item in edges:
            edgeSet.add(item)

        # temp = ''
        for node in nodes:
            # temp += node
            # temp += '\n'
            tempDepend = list()
            for item in edgeSet:
                if item[0] == node:
                    tempDepend.append(item[1])
            jsonOutput.append({
                "depends": tempDepend,
                "type": nodesWithType[node],
                "name": node
            })
        with open('objects.json', 'w+') as f:
            json.dump(jsonOutput, f)
        """with open('temp.txt', 'w+') as f:
            f.write(temp)"""

        copyfile('objects.json', 'C:/wamp64/www/TSVisual/process_map/data/component01/objects.json')
        print jsonOutput

    def checkHadInsertedScreenShotCommand(self):
        for df in self.datafiles:
            if type(df) is robotide.controller.filecontrollers.TestCaseFileController:
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
            if type(df) is robotide.controller.filecontrollers.TestCaseFileController:
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
            if type(df) is robotide.controller.filecontrollers.TestCaseFileController:
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

    def duplicatedActionDetection(self):
        start_time = time.time()
        self.duplicatedactiondetection.Excute(self.datafiles)
        elapsed_time = time.time() - start_time
        print(elapsed_time)
        self.ShowMessage('Duplicated Action Detection Finish')

    def OnDynamicGenerateGraph(self, filepath):
        jsonOutput = []
        edgeSet = set()
        nodes_set = set()

        nodes = set()
        edges = dict()
        nodesWithType = dict()
        """try:
            self.build_model(filepath, nodes, edges, nodesWithType)
        except Exception as e:
            print e
            self.ShowMessage(str(e))
            raise e"""
        nodes = self.build_model(filepath, nodes, edges, nodesWithType)
        for item in edges.keys():
            edgeSet.add(item)
        """for item in nodes:
            nodes_set.add(item)"""

        for node in nodes:
            tempDepend = list()
            for item in edgeSet:
                if item[0] == node:
                    tempDepend.append(item[1])
            tempDepend.sort()
            jsonOutput.append({
                "depends": tempDepend,
                "type": nodesWithType[node],
                "name": node
            })
        with open('objects.json', 'w+') as f:
            json.dump(jsonOutput, f)

        copyfile('objects.json', 'C:/wamp64/www/TSVisual/process_map/data/component01/objects.json')
        # print jsonOutput
        webbrowser.open('http://localhost/TSVisual/index.html')

    def get_change_impact_dict(self, nodes, edges, nodesWithType, change_list):
        change_impact_dict = dict()
        limit_level = 1
        while True:
            # print limit_level
            change_impact = self.set_change_impact_node(nodes, dict(edges), nodesWithType, change_list, 0, 0,
                                                        limit_level)
            if limit_level - 1 in change_impact_dict.keys():
                if change_impact_dict[limit_level - 1] == change_impact:
                    break
            if limit_level not in change_impact_dict.keys():
                change_impact_dict[limit_level] = 0
            change_impact_dict[limit_level] += change_impact
            limit_level += 1
        # if nodesWithType[change] == 'Component':
        for key in change_impact_dict.keys():  # remove LK~C response relation
            if key == 1:
                continue
            change_impact_dict[key] -= change_impact_dict[1]
        return change_impact_dict

    def set_change_impact_node(self, nodes, edges, nodesWithType, change_list, change_impact, level, limit_level):
        # change = change_list[0]
        # print 'level = %r' % level
        if level >= limit_level:
            return change_impact
        for change in change_list:
            new_change_list = list()
            # print 'change = %r' % change
            if nodesWithType[change] == 'TestSuite':
                continue
            else:
                index = 0
                while index < len(edges.keys()):
                    edge = edges.keys()[index]
                    # print item[0] + '\t' + item[1]
                    if edge[1] == change:  # and nodesWithType[item[0]] != 'Changed':
                        if edge[0] not in change_list:
                            new_change_list.append(edge[0])
                        change_impact += edges[edge]
                        # print 'change_impact = %r' % change_impact
                        # print edge
                        edges.pop(edge, None)
                        index -= 1
                    index += 1

            if len(new_change_list) > 0:
                change_impact = self.set_change_impact_node(nodes, edges, nodesWithType, new_change_list, change_impact,
                                                            level + 1, limit_level)
        return change_impact

    def read_excluded_library_keyword_file(self):
        excluded_node_not_show = set()
        excluded_node_show = set()
        with open('ExcludedLibraryKeyword.txt', 'r+') as f:
            for line in f:
                if '#' in line:
                    line = line[:line.index('#')]
                if line != '\n':
                    if ', ShowNode=' in line:
                        line = line[:line.index(', ShowNode=')]
                        excluded_node_show.add(line.strip('\n').strip())
                    elif ',' in line:
                        raise Exception('ExcludedLibraryKeyword.txt format error!')
                    else:
                        excluded_node_not_show.add(line.strip('\n').strip())
        return excluded_node_show, excluded_node_not_show

    def build_model(self, filepath, nodes, edges, nodesWithType):
        excluded_node_show, excluded_node_not_show = self.read_excluded_library_keyword_file()
        source = os.path.abspath(filepath)
        TS_list = list()
        TC_list = list()
        UK_list = list()
        LK_list = list()
        C_set = set()
        node_level = dict()

        with open(source + '\Excute.txt', 'r+') as f:
            for line in f:
                if line != '\n':
                    data_list = line.split('\t')
                    if data_list[0].split('=')[1].strip('\n') in excluded_node_not_show:
                        continue
                    if data_list[0].split('=')[0] == 'TS':
                        TS_list.append(data_list[0].split('=')[1].strip('\n'))
                    elif data_list[0].split('=')[0] == 'TC':  # TC_list = [parent , TC_name]
                        TC_list.append([data_list[1].split('=')[1].strip('\n'), data_list[0].split('=')[1].strip('\n')])
                    else:
                        args = ''
                        if len(data_list[1].split('=')) > 2:  # if arg has '=', append all arg
                            for index in range(1, len(data_list[1].split('='))):
                                args += data_list[1].split('=')[index]
                                args += '='
                            args = args[1:len(args) - 2]  # remove '[' and ']'
                        else:
                            args = data_list[1].split('=')[1].strip('\n')
                            args = args[1:len(args) - 1]  # remove '[' and ']'
                        if data_list[0].split('=')[0] == 'UK':  # UK_list = [parent , UK_name, args]
                            UK_list.append(
                                [data_list[2].split('=')[1].strip('\n'), data_list[0].split('=')[1].strip('\n'), args])
                        elif data_list[0].split('=')[0] == 'LK':  # LK_list = [parent , LK_name, args]
                            LK_list.append(
                                [data_list[2].split('=')[1].strip('\n'), data_list[0].split('=')[1].strip('\n'),
                                 args])
                            if len(args) > 0 and data_list[0].split('=')[1].strip('\n') not in excluded_node_show:
                                C_set.add(args.split(',')[0])

        print 'EVENT : %r' % len(LK_list)
        action_count = len(LK_list)

        serial_number = dict()
        if self.serial_number_flag:
            for index in range(len(TS_list)):
                serial_number[TS_list[index]] = 'S' + '{:02d}'.format(index)
                TS_list[index] = serial_number[TS_list[index]]
            for index in range(len(TC_list)):
                serial_number[TC_list[index][1]] = 'T' + '{:02d}'.format(index)
                if TC_list[index][0] in serial_number:
                    TC_list[index][0] = serial_number[TC_list[index][0]]
                TC_list[index][1] = serial_number[TC_list[index][1]]
            count = 0
            for index in range(len(UK_list)):
                if UK_list[index][1] not in serial_number:
                    serial_number[UK_list[index][1]] = 'U' + '{:02d}'.format(count)
                    count += 1
                UK_list[index][1] = serial_number[UK_list[index][1]]
            for index in range(len(UK_list)):
                if UK_list[index][0] in serial_number:
                    UK_list[index][0] = serial_number[UK_list[index][0]]
            C_list = list(C_set)
            for index in range(len(C_list)):
                serial_number[C_list[index]] = 'C' + '{:03d}'.format(index)
                C_list[index] = serial_number[C_list[index]]
            C_set = set(C_list)
            for node in nodesWithType:
                node = serial_number[node]
            count = 0
            for index in range(len(LK_list)):
                if LK_list[index][1] not in serial_number:
                    serial_number[LK_list[index][1]] = 'L' + '{:02d}'.format(count)
                    count += 1
                if LK_list[index][0] in serial_number:
                    LK_list[index][0] = serial_number[LK_list[index][0]]
                args = LK_list[index][2].split(',')
                for arg in args:
                    if arg in serial_number:
                        LK_list[index][2] = LK_list[index][2].replace(arg, serial_number[arg])
                LK_list[index][1] = serial_number[LK_list[index][1]]

        for TS in TS_list:
            nodes.add(TS)
            nodesWithType[TS] = 'TestSuite'
        for TC in TC_list:
            nodes.add(TC[1])
            nodesWithType[TC[1]] = 'TestCase'
        for LK in UK_list:
            nodes.add(LK[1])
            nodesWithType[LK[1]] = 'Userkeyword'
        for LK in LK_list:
            nodes.add(LK[1])
            nodesWithType[LK[1]] = 'Librarykeyword'
        for C in C_set:
            nodes.add(C)
            nodesWithType[C] = 'Component'

        TS_set = set(TS_list)
        print 'TS:%r' % len(TS_set)
        TC_set = set()
        for item in TC_list:
            TC_set.add(item[1])
        print 'TC:%r' % len(TC_set)
        UK_set = set()
        for item in UK_list:
            UK_set.add(item[1])
        print 'UK:%r' % len(UK_set)
        LK_set = set()
        for item in LK_list:
            LK_set.add(item[1])
        print 'LK:%r' % len(LK_set)
        print 'C:%r' % len(C_set)
        # print 'node:%r' % len(nodes)

        for TS in TS_list:
            self.set_level(TC_list, UK_list, LK_list, C_set, nodesWithType, node_level, TS, 0)
        # print node_level
        self.build_edges(node_level, edges, TC_list, UK_list, LK_list, C_set, nodesWithType)
        # print 'weighted coupling = %r\n--------------------' % self.get_weighted(None, None, edges)
        self.remove_redundant_edges(edges, node_level, nodesWithType, UK_list, LK_list)
        # print 'temp = %r' % self.get_weighted('NewCrosswordByValidGridSize', 'SelectCrosswordSageWindow', edges)
        # print edges

        """nodes_parent_dict = dict()
        for node in nodes:
            nodes_parent_dict[node] = set()
            if nodesWithType[node] == 'TestSuite':
                pass
            elif nodesWithType[node] == 'TestCase':
                for TC in TC_list:
                    if TC[1] == node:
                        nodes_parent_dict[node].add(TC[0])
            elif nodesWithType[node] == 'UserKeyword':
                for UK in UK_list:
                    if UK[1] == node:
                        nodes_parent_dict[node].add(UK[0])
            elif nodesWithType[node] == 'LibraryKeyword':
                for LK in LK_list:
                    if LK[1] == node:
                        nodes_parent_dict[node].add(LK[0])
        for LK in LK_list:
            if len(LK[2]) > 0:
                nodes_parent_dict[node].add(LK[2].split(',')[0])"""

        """change_list = list()
        change_list.append('btnSuggestWords')
        # change_list.append('btnFind')
        # change_list.append('btnAddWord')
        # change_list.append('File|New Crossword')
        change_impact_dict = self.get_change_impact_dict(nodes, edges, nodesWithType, change_list)
        #nodesWithType['btnSuggestWords'] = 'Changed'
        print change_impact_dict
        change_impact_dict = self.get_change_impact_by_formula(edges, change_list)
        print change_impact_dict"""
        """change_impact_dict = self.get_change_impact_dict(nodes, edges, nodesWithType, ['File|New Crossword'])
        #nodesWithType['File|New Crossword'] = 'Changed'
        print change_impact_dict
        change_impact_dict = self.get_change_impact_by_formula(edges, ['File|New Crossword'])
        print change_impact_dict"""

        # print self.get_descendant('U12', edges, 2, 7)
        level_node = self.tree_layout(node_level, edges)
        node_list = []
        for value in level_node.values():
            node_list.extend(value)
        # print 'count = ' + str(len(node_list))
        self.calculate_coupling(nodes, edges, action_count)
        self.test()
        return node_list

    def set_level(self, TC_list, UK_list, LK_list, C_set, nodesWithType, node_level, current, current_level):
        type = nodesWithType[current]
        if current not in node_level.keys():
            node_level[current] = current_level
        else:
            # print str(node_level[current]) + '\t' + str(current_level)
            node_level[current] = max(node_level[current], current_level)
            # print node_level[current]
        child_node_set = set()
        if type == 'TestSuite':
            for TC in TC_list:
                if TC[0] == current:
                    child_node_set.add(TC[1])
        elif type == 'TestCase' or type == 'Userkeyword':
            index = 0
            while index < len(UK_list):
                UK = UK_list[index]
                if UK[0] == current:
                    if UK[1] not in child_node_set:
                        child_node_set.add(UK[1])
                index += 1
            index = 0
            while index < len(LK_list):
                LK = LK_list[index]
                if LK[0] == current:
                    if LK[1] not in child_node_set:
                        child_node_set.add(LK[1])
                index += 1
        elif type == 'Librarykeyword':
            for LK in LK_list:
                if LK[1] == current:
                    for C in C_set:
                        if LK[2].split(',')[0] == C:
                            child_node_set.add(C)

        for node in child_node_set:
            self.set_level(TC_list, UK_list, LK_list, C_set, nodesWithType, node_level, node, current_level + 1)

    def build_edges(self, node_level, edges, TC_list, UK_list, LK_list, C_set, nodesWithType):
        current_level_list = list()
        current_level = 0

        for LK in LK_list:
            for C in C_set:
                if LK[2].split(',')[0] == C and (LK[1], C) not in edges.keys():
                    edges[(LK[1], C)] = 1
                    break

        for key in node_level.keys():
            if node_level[key] == current_level:
                current_level_list.append(key)
        while len(current_level_list) > 0:
            for current in current_level_list:
                # print current
                node_type = nodesWithType[current]
                if node_type == 'TestSuite':
                    for TC in TC_list:
                        if TC[0] == current:
                            edges[(current, TC[1])] = 1
                elif node_type == 'TestCase' or node_type == 'Userkeyword':
                    index = 0
                    child_node_set = set()
                    while index < len(UK_list):
                        UK = UK_list[index]
                        if UK[0] == current:
                            # print 'addUK'
                            # print UK
                            if (current, UK[1]) not in edges.keys():
                                edges[(current, UK[1])] = 1
                            else:
                                edges[(current, UK[1])] += 1
                            if UK[1] not in child_node_set:
                                child_node_set.add(UK[1])
                            else:
                                del UK_list[index]
                                index -= 1
                        index += 1
                    index = 0
                    child_node_set.clear()
                    while index < len(LK_list):
                        LK = LK_list[index]
                        if LK[0] == current:
                            if (current, LK[1]) not in edges.keys():
                                edges[(current, LK[1])] = 1
                            else:
                                edges[(current, LK[1])] += 1
                            if LK[1] not in child_node_set:
                                child_node_set.add(LK[1])
                            else:
                                del LK_list[index]
                                index -= 1
                        index += 1
                """elif type == 'Librarykeyword':
                    for LK in LK_list:
                        if LK[1] == current:
                            for C in C_set:
                                if LK[2].split(',')[0] == C:
                                    edges.append((current, C))
                                    C_set.remove(C)
                                    break
                            break"""
            current_level += 1
            del current_level_list[:]
            for key in node_level.keys():
                if node_level[key] == current_level:
                    current_level_list.append(key)

    def remove_redundant_edges(self, edges, node_level, nodesWithType, UK_list, LK_list):
        change_list = list()
        max_level = 0
        for level in node_level.values():
            max_level = max(max_level, level)
        for level in range(max_level, 1, -1):
            del change_list[:]
            for key in node_level.keys():
                if node_level[key] == level:
                    change_list.append(key)
            for change in change_list:
                parent_list = list()
                if nodesWithType[change] == 'Librarykeyword':
                    for LK in LK_list:
                        if LK[1] == change:
                            parent_list.append(LK[0])
                elif nodesWithType[change] == 'Userkeyword':
                    for UK in UK_list:
                        if UK[1] == change:
                            parent_list.append(UK[0])
                else:
                    continue
                for parent in parent_list:
                    scale = self.get_weighted(None, parent, edges)
                    if scale == 1:
                        continue
                    weight = self.get_weighted(parent, change, edges)
                    edges[(parent, change)] = weight / scale

    def get_weighted(self, node1, node2, edges):
        count = 0
        for edge in edges.keys():
            if node1 is None and node2 is None:
                count += edges[edge]
            elif node1 is None:
                if edge[1] == node2:
                    count += edges[edge]
            else:
                if edge[0] == node1 and edge[1] == node2:
                    count += edges[edge]
        return count

    def calculate_coupling(self, nodes, edges, action_count):
        nodes_set = set()
        for item in nodes:
            nodes_set.add(item)
        unweighted_coupling = float(len(edges.keys())) / (len(nodes_set) * (len(nodes_set) - 1))
        print 'unweighted coupling = %r' % unweighted_coupling
        # print 'weighted coupling = %r' % (float(self.get_weighted(None, None, edges)) / action_count)
        print 'weighted coupling = %r' % self.get_weighted(None, None, edges)

    def get_change_impact_by_formula(self, edges, change_list):
        change_impact_dict = dict()
        edges_set = set()
        limit_level = 1
        while True:
            edges_set = self.calculate_change_impact_by_formula(edges, edges_set, change_list, change_impact_dict,
                                                                limit_level)
            if limit_level - 1 in change_impact_dict.keys():
                if change_impact_dict[limit_level] == change_impact_dict[limit_level - 1]:
                    break
            limit_level += 1
        change_impact_dict.pop(limit_level)
        for key in change_impact_dict.keys():  # remove LK~C response relation
            if key == 1:
                continue
            change_impact_dict[key] -= change_impact_dict[1]
        return change_impact_dict

    def calculate_change_impact_by_formula(self, edges, edges_set, change_list, change_impact_dict, level):
        for change in change_list:
            temp_set = self.get_edges(change, edges)
            edges_set = edges_set.union(temp_set)
        weight = 0
        del change_list[:]
        for edge in edges_set:
            change_list.append(edge[0])
            weight += edges[(edge[0], edge[1])]
        change_impact_dict[level] = weight
        return edges_set

    """def get_nodes(self, change, nodes_parent_dict, level):
        result = set()
        node_list = list()
        for parent in nodes_parent_dict[change]:
            result.add(parent)
            node_list.append(parent)
        for index in range(1, level):
            new_node_list = list()
            for node in node_list:
                for parent in nodes_parent_dict[node]:
                    result.add(parent)
                    new_node_list.append(parent)
            node_list = list(new_node_list)
            del new_node_list[:]
        return result"""

    def get_edges(self, node, edges):
        result = set()
        for edge in edges.keys():
            if edge[1] == node:
                result.add(edge)
        return result

    def build_node_parent_dict(self, max_level, node_level, edges):
        node_parent_dict = dict()
        for level in range(max_level + 1):
            node_list = [node for node in node_level if node_level[node] == level]
            for node in node_list:
                for edge in edges:
                    if edge[1] == node:
                        if node not in node_parent_dict:
                            node_parent_dict[node] = []
                        node_parent_dict[node].append((edge[0], node_level[edge[0]]))
        # print node_parent_dict
        for key in node_parent_dict:
            node_parent_dict[key] = sorted(node_parent_dict[key], key=lambda x: abs(node_level[key] - node_level[x[0]]))
        # print node_parent_dict
        return node_parent_dict

    def build_node_parent_dict_list(self, node_parent_dict):
        node_parent_dict_list = []
        common = {}
        temp = []
        temp_key = []
        for key in node_parent_dict:
            if len(node_parent_dict[key]) == 1:
                common[key] = node_parent_dict[key][0]
            else:
                temp_key.append(key)
                temp.append(node_parent_dict[key])
        permutations = list(itertools.product(*temp))
        for permutation in permutations:
            d = common.copy()
            for index in range(len(temp_key)):
                d[temp_key[index]] = permutation[index]
            node_parent_dict_list.append(d)
        return node_parent_dict_list

    def build_level_node(self, max_level, node_level, level_node, edges, node_descendant):
        for level in range(max_level + 1):
            if level - 1 not in level_node:
                node_list = [node for node in node_level if node_level[node] == level]
            else:
                node_list = []
                for parent in level_node[level - 1]:
                    for node in self.get_descendant(parent, edges, level - 1, level):
                        if node_level[node] == level and node not in node_list:
                            node_list.append(node)
            level_node[level] = node_list[:]
            """seen = set()
            seen_add = seen.add
            level_node[level] = [x for x in level_node[level] if not (x in seen or seen_add(x))]"""
            for node in node_list:
                node_descendant[node] = self.get_descendant(node, edges, node_level[node], max_level)
            del node_list[:]

    def rebuild_level_node(self, start_level, max_level, node_level, level_node, edges):
        for level in range(start_level, max_level + 1):
            level_node_list = []
            for parent in level_node[level - 1]:
                node_list = []
                for node in self.get_descendant(parent, edges, level - 1, level):
                    if node_level[node] == level and node not in level_node_list:
                        node_list.append(node)
                for index in range(len(level_node[level])):
                    temp = level_node[level][index:index + len(node_list)]
                    if set(temp) == set(node_list):
                        break
                level_node_list.extend(temp)
            level_node[level] = level_node_list[:]
            del level_node_list[:]

    def tree_layout(self, node_level, edges):
        level_node = dict()
        node_descendant = dict()
        max_level = 0
        for level in node_level.values():
            max_level = max(max_level, level)
        node_parent_dict = self.build_node_parent_dict(max_level, node_level, edges)
        self.build_level_node(max_level, node_level, level_node, edges, node_descendant)
        for level in range(max_level + 1):
            if len(level_node[level]) > 1:
                top_node = level_node[level - 1][0]
                break
        redo = True
        while redo:
            for level in range(1, max_level + 1):
                level_node_list = []
                for parent in level_node[level - 1]:
                    temp = []
                    for node in level_node[level]:
                        if node in self.get_descendant(parent, edges, level - 1, level) and node not in level_node_list:
                            temp.append(node)
                    if len(temp) == 0:
                        continue
                    level_node_list.extend(temp)
                    change = self.switch_node_order(temp, node_level, edges, max_level, node_parent_dict, level_node,
                                                    top_node)
                if change:
                    break
            if change:
                change = False
            else:
                redo = False

        node_x_position = self.tree_layout_x(level_node, node_descendant, edges)
        string = ''
        leaf_number = len([node for node in node_level if len(node_descendant[node]) == 0])
        print 'leaf_number = ' + str(leaf_number)
        with open('C:\wamp64\www\TSVisual\process_map\data\component01\config.json', 'r+') as f:
            for line in f:
                if 'width' in line:
                    string += '		"width"        : %d,\n' % (leaf_number * 600)
                elif 'height' in line:
                    string += '		"height"       : %d,\n' % ((max_level + 1) * 200)
                else:
                    string += line
                if 'constraints' in line:
                    break
        with open('C:\wamp64\www\TSVisual\process_map\data\component01\config.json', 'w+') as f:
            f.write(string)
            # {"has":{"name":"doKeywordSearch"},"type":"position","x":0.7,"y":0.2,"weight":0.6},
            temp = ''
            y_step = float("{0:.8f}".format(1.0 / (max_level + 1)))
            y_start_position = 1.0 / (max_level + 2)
            for level in range(max_level + 1):
                for node in level_node[level]:
                    if node in node_x_position:
                        line = '\t\t{"has":{"name":"%s"},"type":"position","x":%.8f,"y":%.8f,"weight":0.6},' % (
                            node, node_x_position[node], y_start_position)
                    else:
                        line = '\t\t{"has":{"name":"%s"},"type":"position","y":%.8f,"weight":0.6},' % (
                            node, y_start_position)
                    temp += line + '\n'
                y_start_position += y_step
            f.write(temp)
            f.seek(-3, 1)
            f.write('\n\t]\n}')
        return level_node

    def get_leaf_node_count(self, descendant, edges):
        if len(descendant) == 0:
            return 1
        count = 0
        for node in descendant:
            is_leaf = True
            for edge in edges:
                if edge[0] == node:
                    is_leaf = False
                    break
            if is_leaf:
                count += 1
        return count

    def tree_layout_x(self, level_node, node_descendant, edges):
        node_x_position = dict()
        root = level_node[0][0]
        node_x_position[root] = 0.5
        node_x_position = self.tree_layout_x_recursive(root, 1, level_node, (0.0, 1.0), node_descendant,
                                                       node_x_position, edges)
        return node_x_position

    def tree_layout_x_recursive(self, root, level, level_node, duration, node_descendant, node_x_position, edges):
        width = dict()
        current_level_nodes = [node for node in level_node[level] if node in node_descendant[root]]
        duration_list = []
        total = 0
        for node in current_level_nodes:
            width[node] = self.get_leaf_node_count(node_descendant[node], edges)
            total += width[node]
        left, right = duration[0], duration[1]
        for node in current_level_nodes:
            right = float("{0:.8f}".format(left + float(width[node]) / total * (duration[1] - duration[0])))
            duration_list.append((left, right))
            node_x_position[node] = float("{0:.8f}".format((right + left) / 2))
            left = right
        for node in current_level_nodes:
            if len(node_descendant[node]) > 0:
                node_x_position = self.tree_layout_x_recursive(node, level + 1, level_node,
                                                               duration_list[current_level_nodes.index(node)],
                                                               node_descendant, node_x_position, edges)
        return node_x_position

    def switch_node_order(self, node_list, node_level, edges, max_level, node_parent_dict, level_node, top_node):
        total_cross = 0
        total_cross += self.calculate_cross(top_node, edges, max_level, node_parent_dict, node_level, level_node)
        change = False
        redo = True
        while redo:
            swap = False
            for combinations in itertools.combinations(node_list, 2):
                level = node_level[node_list[0]]
                new_node_list = node_list[:]
                new_level_node = {}
                for key in level_node:
                    new_level_node[key] = level_node[key][:]
                index1, index2 = node_list.index(combinations[0]), node_list.index(combinations[1])
                new_node_list[index1], new_node_list[index2] = node_list[index2], node_list[index1]
                index1, index2 = new_level_node[level].index(combinations[0]), new_level_node[level].index(
                    combinations[1])
                new_level_node[level][index1], new_level_node[level][index2] = level_node[level][index2], \
                                                                               level_node[level][index1]
                self.rebuild_level_node(level + 1, max_level, node_level, new_level_node, edges)
                new_total_cross = 0
                new_total_cross += self.calculate_cross(top_node, edges, max_level, node_parent_dict, node_level,
                                                        new_level_node)
                if new_total_cross < total_cross:
                    total_cross = new_total_cross
                    node_list = new_node_list[:]
                    level_node[level] = new_level_node[level][:]
                    self.rebuild_level_node(level + 1, max_level, node_level, level_node, edges)
                    del new_node_list[:]
                    new_level_node.clear()
                    swap = True
                    change = True
                    break
            if not swap:
                redo = False
        return change

    def get_descendant(self, root, edges, root_level, max_level):
        next_level_node = [edge[1] for edge in edges if edge[0] == root]
        result = set()
        for node in next_level_node:
            result.add(node)
        temp = []
        for level in range(root_level + 2, max_level + 1):
            for node in next_level_node:
                for edge in edges:
                    if edge[0] == node:
                        temp.append(edge[1])
            for node in temp:
                result.add(node)
            next_level_node = temp[:]
            del temp[:]
        return result

    def calculate_cross(self, top_node, edges, max_level, node_parent_dict, node_level, level_node):
        cross = 0
        for level in range(node_level[top_node] + 1, max_level + 1):
            level_node_list = []
            for parent in level_node[level - 1]:
                node_list = []
                for node in level_node[level]:
                    if node in self.get_descendant(parent, edges, level - 1, level) and node not in level_node_list:
                        node_list.append(node)
                cross_list = []
                for node in node_list:
                    for edge in edges:
                        if edge[1] == node:
                            target_level = node_level[edge[0]]
                            current_node = node
                            while target_level != node_level[current_node]:
                                current_node = node_parent_dict[current_node][0][0]
                            if edge[0] != current_node:
                                cross_list.append(edge)
                                cross += math.fabs(level_node[target_level].index(edge[0]) -
                                                   level_node[target_level].index(current_node))
                subcross = self.calculate_subcross(node_list, cross_list, node_level, level_node, node_parent_dict)
                cross += subcross
                level_node_list.extend(node_list)
        return cross

    def calculate_subcross(self, node_list, cross_list, node_level, level_node, node_parent_dict):
        print node_list
        size = len(node_list)
        if size == 1 or len(cross_list) == 0:
            return 0
        step = 2.0 / (size + 1)
        center = float(size - 1) / 2
        subcross_dict = dict()
        if size % 2 == 1:
            center = int(center)
            subcross_dict[node_list[center]] = 0
            for i, j in zip(xrange(center - 1, -1, -1), xrange(center + 1, size)):
                subcross_dict[node_list[i]] = (i - center) * step
                subcross_dict[node_list[j]] = (j - center) * step
        else:
            for i, j in zip(xrange(int(center - 0.5), -1, -1), xrange(int(center + 0.5), size)):
                subcross_dict[node_list[i]] = (i - center) * step
                subcross_dict[node_list[j]] = (j - center) * step
        subcross = 0.0
        for edge in cross_list:
            temp, node = edge
            current_list = level_node[node_level[temp]]
            parent = node_parent_dict[node][0]
            while parent[1] != node_level[temp]:
                parent = node_parent_dict[parent[0]][0]
            if current_list.index(temp) < current_list.index(parent[0]):
                subcross += subcross_dict[node]
            else:
                subcross -= subcross_dict[node]
        return subcross

    def test(self):
        """a = ['A', 'B', 'C']
        e = [('A', 'D'), ('D', 'E'), ('C', 'F'), ('C', 'E')]
        d = {'A': set(['D', 'E']), 'B': set(), 'C': set(['E', 'F'])}
        npd = {'D': ('A', 0), 'E': ('A', 0), 'F': ('C', 0)}
        nl = {'A': 0, 'B': 0, 'C': 0, 'D': 1, 'E': 1, 'F': 1}
        ln = {0: ['A', 'B', 'C'], 1: ['D', 'E', 'F']}
        print self.get_descendant('A', e, 0, 2)
        print self.get_descendant('B', e, 0, 2)
        print self.get_descendant('C', e, 0, 2)
        print self.calculate_cross('A', a, d, e, npd, nl, ln)

        print ln
        # nln = ln.copy()
        nln = {}
        for key in ln:
            nln[key] = ln[key][:]
        i1, i2 = ln[0].index('A'), ln[0].index('C')
        nln[0][i1], nln[0][i2] = ln[0][i2], ln[0][i1]
        print ln
        print nln"""
