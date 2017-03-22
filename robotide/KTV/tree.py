import wx
import os
from wx.lib.agw import customtreectrl
from wx.lib.mixins import treemixin
from robotide.context import IS_WINDOWS

from robotide.publish import PUBLISHER, MyTreeSelectedItemChanged, DuplicateDetection, MyTreeBuildFinish
import itertools

_TREE_ARGS = {'style': wx.TR_DEFAULT_STYLE}

if wx.VERSION_STRING >= '2.8.11.0':
    _TREE_ARGS['agwStyle'] = \
        customtreectrl.TR_DEFAULT_STYLE | customtreectrl.TR_HIDE_ROOT | \
        customtreectrl.TR_EDIT_LABELS
if IS_WINDOWS:
    _TREE_ARGS['style'] |= wx.TR_EDIT_LABELS


class Tree(treemixin.DragAndDrop, customtreectrl.CustomTreeCtrl):
    def __init__(self, parent):
        treemixin.DragAndDrop.__init__(self, parent, **_TREE_ARGS)
        self._bind_tree_events()
        self._clear_tree_data()
        self.duplicated_actions_count = 0

    def set_filepath(self, filepath):
        self.source = os.path.abspath(filepath)

    def _bind_tree_events(self):
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)

        PUBLISHER.subscribe(self.build_node_dict, DuplicateDetection)

    def build_tree(self, node_list):
        """temp = node_list[0].split('Line:')[1]
        start, end = int(temp.split('~')[0]), int(temp.split('~')[1])
        size = end - start + 1"""
        size, overlapping_lines = self.check_overlapping(node_list)
        if overlapping_lines > 0:
            self.create_group(self._root, self.group_count,
                              'duplicate_group' + str(self.group_count + 1) +
                              '    %d Lines    there are %d overlapping lines' % (size, overlapping_lines))
        else:
            self.create_group(self._root, self.group_count,
                              'duplicate_group' + str(self.group_count + 1) + '    %d Lines' % size)
        for node in node_list:
            self.duplicated_actions_count += size
            self.create_item(self._group_nodes[self.group_count],
                             len(self._group_children_nodes[self._group_nodes[self.group_count]]), node)
        self.group_count += 1
        if not self.IsExpanded(self._group_nodes[0]):
            self.Expand(self._group_nodes[0])

    def check_overlapping(self, node_list):
        region = {}
        overlapping_lines = 0
        for node in node_list:
            name = node.split('Line:')[0].strip(' ')
            temp = node.split('Line:')[1]
            start, end = int(temp.split('~')[0]), int(temp.split('~')[1])
            if name not in region:
                region[name] = []
            region[name].append((start, end))
        size = end - start + 1
        for key in region:
            if len(region[key]) > 1:
                set_list = []
                s = set()
                for x, y in region[key]:
                    for i in xrange(x, y + 1):
                        s.add(i)
                    set_list.append(s.copy())
                    s.clear()
                for combinations in itertools.combinations(set_list, 2):
                    overlapping_lines = len(combinations[0].intersection(combinations[1]))
        return size, overlapping_lines

    def build_node_dict(self, data):
        self._clear_tree_data()
        node_list = []
        flag = False
        with open(self.source + '\ScriptDuplicated.txt', 'r+') as f:
            node = None
            for line in f:
                if flag:
                    if line == '\n':
                        self.build_tree(node_list)
                        del node_list[:]
                        flag = False
                        continue
                    if node is None:
                        node = line.split(':')[1].strip('\n')
                    else:
                        temp = line[:len(line) - len('action duplicated\n')]
                        line_list = temp.split(',')
                        label = ''
                        start, end = int(temp.split('~')[0]), int(temp.split('~')[1])
                        node_list.append('%s    Line: %d ~ %d' % (node, start, end))
                        node = None
                if 'resultList' in line:
                    flag = True
        MyTreeBuildFinish(duplicated_actions=self.duplicated_actions_count).publish()

    def OnDoubleClick(self, event):
        item, pos = self.HitTest(self.ScreenToClient(wx.GetMousePosition()))
        temp = [node.GetText() for node in self._group_nodes]
        if item and item.GetText() not in temp:
            data = item.GetText().split('Line:')
            node = data[0].strip(' ')
            start = int(data[1].split('~')[0])
            end = int(data[1].split('~')[1])
            MyTreeSelectedItemChanged(node=node, start=start, end=end).publish()
        event.Skip()

    def _clear_tree_data(self):
        self.DeleteAllItems()
        self._root = self.AddRoot('')
        self._group_nodes = []
        self._group_children_nodes = {}
        self.group_count = 0
        self.duplicated_actions_count = 0

    def create_node(self, parent_node, index, label):
        return self.InsertItemByIndex(parent_node, index, label)

    def create_group(self, parent_node, index, label):
        node = self.create_node(parent_node, index, label)
        self._group_nodes.append(node)
        self._group_children_nodes[node] = []

    def create_item(self, parent_node, index, label):
        node = self.create_node(parent_node, index, label)
        self._group_children_nodes[parent_node].append(node)

    def Edit(self, item):
        """Let node item can't edit"""
        pass
