# -*- coding: utf-8 -*-　

import json
import math
import os
import webbrowser
from operator import itemgetter
from shutil import copyfile

import graphviz
import robotide
import wx


class KTV:
    def __init__(self):
        self.datafiles = None
        self.componentChangeImpact = dict()
        self.user_def_keyword = dict()
        self.userKeywordObject = list()

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
        with open('objects.json', 'w+') as f:
            json.dump(jsonOutput, f)

        copyfile('objects.json', 'C:/wamp64/www/TSVisual/process_map/data/component01/objects.json')
        print jsonOutput

    def OnDynamicGenerateGraph(self, dynamic_analyzer, node_list=None, distance=None):
        jsonOutput = []
        edgeSet = set()

        if node_list is None:
            nodes, edges, nodesWithType = dynamic_analyzer.generate_full_graph()
        else:
            if distance is None:
                nodes, edges, nodesWithType = dynamic_analyzer.generate_specific_graph(node_list)
            else:
                nodes, edges, nodesWithType = dynamic_analyzer.generate_change_impact_graph(node_list, distance)
        for item in edges.keys():
            edgeSet.add(item)

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
        webbrowser.open('http://localhost/TSVisual/process_map/graph.php?dataset=component01')
        # webbrowser.open('http://localhost/TSVisual/index.html')
