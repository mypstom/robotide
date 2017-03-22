import wx

from robotide.pluginapi import Plugin, TreeAwarePluginMixin
from robotide.KTV.tree import Tree

from robotide.publish import PUBLISHER, MyTreeSelectedItemChanged, DuplicateDetection, MyTreeBuildFinish

STYLE_STDERR = 2


class DuplicatedViewPlugin(Plugin, TreeAwarePluginMixin):
    title = 'Duplicated Actions'

    def __init__(self, application):
        Plugin.__init__(self, application)

        self.left_panel_show = False
        self.datafiles = None
        self.total_actions = 0

    def bind_event(self):
        PUBLISHER.subscribe(self.tree_selected_item_changed, MyTreeSelectedItemChanged)
        PUBLISHER.subscribe(self.load_datafiles, DuplicateDetection)
        PUBLISHER.subscribe(self.set_all_label, MyTreeBuildFinish)

    def set_all_label(self, data):
        self.total_label.SetLabel('Total actions : %d' % self.total_actions)
        self.duplicated_label.SetLabel('Duplicated actions : %d' % data.duplicated_actions)
        percentage = float(data.duplicated_actions) / self.total_actions * 100
        self.percentage_label.SetLabel('Duplicated Percentage : %0.2f' % percentage + ' %')

    def load_datafiles(self, data):
        self.datafiles = data.controller
        self.compute_actions_count()
        self.my_tree.set_filepath(self.frame._controller.suite.source)
        self.bottom_splitter.SetSashPosition(-250, True)

    def compute_actions_count(self):
        for df in self.datafiles:
            for test_case in df.tests:
                self.total_actions += len(test_case.steps)
            for user_keyword in df.keywords:
                self.total_actions += len(user_keyword.steps)

    def tree_selected_item_changed(self, data):
        node, start, end = data.node, data.start, data.end
        if not self.left_panel_show:
            self.left_label.SetLabel(node)
            self.left_panel_show = True
            self.left_text.set_text(self.get_node_text_data(node), start, end)
        else:
            self.right_label.SetLabel(node)
            self.left_panel_show = False
            self.right_text.set_text(self.get_node_text_data(node), start, end)

    def get_node_text_data(self, node):
        string = ''
        for df in self.datafiles:
            for testcase in df.tests:
                if testcase.name == node:
                    for step in testcase.steps:
                        string += str(step.keyword)
                        for arg in step.args:
                            string += '\t' + arg
                        string += '\n'
                    return string
            for userKeyword in df.keywords:
                if userKeyword.name == node:
                    for step in userKeyword.steps:
                        string += '\t' + str(step.keyword)
                        for arg in step.args:
                            string += '\t' + arg
                        string += '\n'
                    return string
        return ''

    def _create_ui(self):
        splitter = wx.SplitterWindow(self.notebook, style=wx.SP_LIVE_UPDATE)
        self.up = wx.Panel(splitter)
        self.down = wx.Panel(splitter)
        self.create_duplicate_view(self.up)
        self.create_bottom_tree_panel(self.down)
        splitter.SetMinimumPaneSize(100)
        splitter.SplitHorizontally(self.up, self.down, 500)
        self.notebook.add_tab(splitter, self.title, allow_closing=False)

    def create_duplicate_view(self, parent):
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        left_panel = wx.Panel(parent)
        right_panel = wx.Panel(parent)

        left_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        self.left_text = RobotDataEditor(left_panel)
        self.left_text.set_text('', 0, 0)
        self.right_text = RobotDataEditor(right_panel)
        self.right_text.set_text('', 0, 0)

        left_top_panel = wx.Panel(left_panel)
        right_top_panel = wx.Panel(right_panel)
        self.left_label, self.left_button = self.create_top_label_panel(left_top_panel, 'Preview 1')
        self.right_label, self.right_button = self.create_top_label_panel(right_top_panel, 'Preview 2')
        self.left_button.Bind(wx.EVT_BUTTON, self.left_button_click)
        self.right_button.Bind(wx.EVT_BUTTON, self.right_button_click)

        left_sizer.Add(left_top_panel, 0, wx.TOP | wx.BOTTOM)
        left_sizer.Add(self.left_text, 1, wx.EXPAND)
        left_panel.SetSizer(left_sizer)
        right_sizer.Add(right_top_panel, 0, wx.TOP | wx.BOTTOM)
        right_sizer.Add(self.right_text, 1, wx.EXPAND)
        right_panel.SetSizer(right_sizer)

        sizer.Add(left_panel, 1, wx.EXPAND, 5)
        sizer.Add(right_panel, 1, wx.EXPAND, 5)

        parent.SetSizer(sizer)

    def create_top_label_panel(self, panel, label):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(panel, label=label)
        font = wx.Font(16, wx.ROMAN, wx.ITALIC, wx.NORMAL)
        label.SetFont(font)
        button = wx.Button(panel, label='Edit')
        sizer.Add(wx.Panel(panel), 1, wx.ALL, 5)
        sizer.Add(label, 1, wx.ALL, 5)
        sizer.Add(wx.Panel(panel), 1, wx.ALL, 5)
        sizer.Add(button, 0, wx.TOP | wx.RIGHT | wx.BOTTOM, 5)
        panel.SetSizer(sizer)
        return label, button

    def left_button_click(self, event):
        controller = self.get_controller(self.left_label.GetLabelText())
        self.tree.select_node_by_data(controller)

    def right_button_click(self, event):
        controller = self.get_controller(self.right_label.GetLabelText())
        self.tree.select_node_by_data(controller)

    def create_bottom_tree_panel(self, parent):
        self.bottom_splitter = wx.SplitterWindow(parent, style=wx.SP_LIVE_UPDATE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.bottom_splitter, 1, wx.EXPAND, 5)
        parent.SetSizer(sizer)

        left_panel = wx.Panel(self.bottom_splitter)
        right_panel = wx.Panel(self.bottom_splitter)

        self.my_tree = Tree(left_panel)
        left_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer.Add(self.my_tree, 1, wx.EXPAND, 5)
        left_panel.SetSizer(left_sizer)

        self.total_label = wx.StaticText(right_panel, label='Total actions : ')
        self.duplicated_label = wx.StaticText(right_panel, label='Duplicated actions : ')
        self.percentage_label = wx.StaticText(right_panel, label='Duplicated Percentage : ')
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(self.total_label, 0, wx.EXPAND, 5)
        right_sizer.Add(self.duplicated_label, 0, wx.EXPAND, 5)
        right_sizer.Add(self.percentage_label, 0, wx.EXPAND, 5)
        right_panel.SetSizer(right_sizer)

        self.bottom_splitter.SetMinimumPaneSize(200)
        self.bottom_splitter.SplitVertically(left_panel, right_panel)

    def get_controller(self, name):
        for df in self.datafiles:
            for testcase in df.tests:
                if testcase.name == name:
                    return testcase
            for userKeyword in df.keywords:
                if userKeyword.name == name:
                    return userKeyword

    def enable(self):
        self.bind_event()
        self._create_ui()

    def disable(self):
        pass


class RobotDataEditor(wx.stc.StyledTextCtrl):
    def __init__(self, parent):
        wx.stc.StyledTextCtrl.__init__(self, parent)
        self.SetMarginType(0, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(0, self.TextWidth(wx.stc.STC_STYLE_LINENUMBER, '1234'))
        self.SetScrollWidth(20)
        self.SetReadOnly(True)
        self.SetLexer(wx.stc.STC_LEX_CONTAINER)

        self.StyleSetSpec(10, "fore:#FF0000,back:#E6E6E4")

    def set_text(self, text, start, end):
        self.SetReadOnly(False)
        self.ClearAll()
        self.SetText(text)
        self.GotoLine(start - 1)
        pos_start = self.GetCurrentPos()
        self.GotoLine(end)
        pos_end = self.GetCurrentPos()
        self.StartStyling(pos_start, 0xff)
        self.SetStyling(pos_end - pos_start, 10)
        self.EmptyUndoBuffer()
        self.SetReadOnly(True)

    @property
    def utf8_text(self):
        return self.GetText().encode('UTF-8')

    def OnStyle(self, event):
        self.stylizer.stylize()
