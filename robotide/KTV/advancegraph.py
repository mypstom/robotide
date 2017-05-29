import wx

from robotide.pluginapi import Plugin, TreeAwarePluginMixin
from robotide.publish import GenerateSpecificGraph
from robotide.publish import PUBLISHER, MyDynamicAnalyzerBuildFinish, GenerateChangedImpactGraph


class AdvanceGraph(Plugin, TreeAwarePluginMixin):
    title = 'Advanced Graph'
    node_list = []
    component_node_list = []

    def __init__(self, application):
        Plugin.__init__(self, application)
        self.node_combobox = None
        self.listbox = None
        self.level_spinctrl = None
        self.simplified_button = None
        self.change_impact_button = None

    def bind_event(self):
        PUBLISHER.subscribe(self.load_data, MyDynamicAnalyzerBuildFinish)

    def load_data(self, data):
        self.clear_data()
        self.node_list = self.frame.dynamic_analyzer.get_nodes()
        self.component_node_list = self.frame.dynamic_analyzer.get_component_nodes()
        self.node_combobox.SetItems(self.node_list)

    def clear_data(self):
        self.node_list = []
        self.component_node_list = []
        self.node_combobox.Clear()
        self.listbox.Clear()
        self.level_spinctrl.SetValue(1)

    def _create_ui(self):
        panel = wx.Panel(self.notebook)
        left = wx.Panel(panel)
        right = wx.Panel(panel)
        self.create_left_panel(left)
        self.create_right_panel(right)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(left, 0, wx.ALL, 5)
        sizer.Add(right, 0, wx.ALL, 5)
        panel.SetSizer(sizer)
        self.notebook.add_tab(panel, self.title, allow_closing=False)

    def create_left_panel(self, parent):
        up = wx.Panel(parent)
        down = wx.Panel(parent)
        select_label = wx.StaticText(parent, label='Select an element')
        font = wx.Font(16, wx.ROMAN, wx.ITALIC, wx.NORMAL)
        select_label.SetFont(font)
        self.create_up_panel(up)
        list_label = wx.StaticText(parent, label='Selected elements')
        list_label.SetFont(font)
        self.create_down_panel(down)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(select_label, 0, wx.ALL, 5)
        sizer.Add(up, 0, wx.ALL, 5)
        sizer.Add(list_label, 0, wx.ALL, 5)
        sizer.Add(down, 0, wx.ALL, 5)
        parent.SetSizer(sizer)

    def create_up_panel(self, parent):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.node_combobox = wx.ComboBox(parent, size=(300, 30), choices=self.node_list)
        self.node_combobox.Bind(wx.EVT_TEXT, self.node_combobox_text_changed)
        add_button = wx.Button(parent, label='Add')
        sizer.Add(self.node_combobox, 0, wx.ALL, 5)
        sizer.Add(add_button, 0, wx.ALL, 5)
        parent.SetSizer(sizer)
        add_button.Bind(wx.EVT_BUTTON, self.add_button_click)

    def create_down_panel(self, parent):
        left = wx.Panel(parent)
        right = wx.Panel(parent)
        self.listbox = wx.ListBox(left, size=(300, 500), choices=[])
        delete_button = wx.Button(right, label='Delete')
        clear_button = wx.Button(right, label='Clear')
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(self.listbox, 1, wx.ALL, 5)
        left.SetSizer(left_sizer)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(delete_button, 0, wx.ALL, 5)
        right_sizer.Add(clear_button, 0, wx.ALL, 5)
        right.SetSizer(right_sizer)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(left, 0, wx.ALL)
        sizer.Add(right, 0, wx.ALL)
        parent.SetSizer(sizer)
        delete_button.Bind(wx.EVT_BUTTON, self.delete_button_click)
        clear_button.Bind(wx.EVT_BUTTON, self.clear_button_click)

    def create_right_panel(self, parent):
        sizer = wx.BoxSizer(wx.VERTICAL)
        simplified_group = wx.StaticBox(parent, -1, 'Simplified Graph', size=(300, 100))
        simplified_sizer = wx.StaticBoxSizer(simplified_group, wx.HORIZONTAL)
        self.simplified_button = wx.Button(parent, label='Generate Simplified Graph')
        self.simplified_button.Enable(False)
        simplified_sizer.Add(self.simplified_button, 0, wx.ALL, 5)
        change_impact_group = wx.StaticBox(parent, -1, 'Change impact', size=(300, 100))
        panel = wx.Panel(parent)
        label = wx.StaticText(panel, label='level:')
        font = wx.Font(16, wx.ROMAN, wx.ITALIC, wx.NORMAL)
        label.SetFont(font)
        level_sizer = wx.BoxSizer(wx.HORIZONTAL)
        change_impact_sizer = wx.StaticBoxSizer(change_impact_group, wx.VERTICAL)
        self.level_spinctrl = wx.SpinCtrl(panel)
        self.level_spinctrl.SetRange(1, 100)
        self.level_spinctrl.SetValue(1)
        self.change_impact_button = wx.Button(parent, label='Generate Change Impact Graph')
        self.change_impact_button.Enable(False)
        sizer.Add(simplified_sizer, 0, wx.ALL, 5)
        sizer.Add(wx.Panel(parent), 0, wx.ALL, 5)
        level_sizer.Add(label, 0, wx.ALL, 5)
        level_sizer.Add(self.level_spinctrl, 0, wx.ALL, 5)
        panel.SetSizer(level_sizer)
        change_impact_sizer.Add(panel, 0, wx.ALL, 5)
        change_impact_sizer.Add(self.change_impact_button, 0, wx.ALL, 5)
        sizer.Add(change_impact_sizer, 0, wx.ALL, 5)
        parent.SetSizer(sizer)
        self.simplified_button.Bind(wx.EVT_BUTTON, self.generate_button_click)
        self.change_impact_button.Bind(wx.EVT_BUTTON, self.change_impact_button_click)

    def node_combobox_text_changed(self, event):
        self.node_combobox.SetStringSelection(self.node_combobox.GetValue())

    def level_combobox_text_changed(self, event):
        self.level_combobox.SetStringSelection(self.level_combobox.GetValue())

    def add_button_click(self, event):
        if self.node_combobox.GetSelection() != -1:
            if self.node_list[self.node_combobox.GetSelection()] not in self.listbox.GetItems():
                self.listbox.Append(self.node_list[self.node_combobox.GetSelection()])
        if len(self.listbox.GetItems()) > 0:
            self.simplified_button.Enable(True)
            self.change_impact_button.Enable(True)

    def delete_button_click(self, event):
        if self.listbox.GetSelection() != -1:
            self.listbox.Delete(self.listbox.GetSelection())
        if not len(self.listbox.GetItems()) > 0:
            self.simplified_button.Enable(False)
            self.change_impact_button.Enable(False)

    def clear_button_click(self, event):
        self.listbox.Clear()
        self.simplified_button.Enable(False)
        self.change_impact_button.Enable(False)

    def generate_button_click(self, event):
        data = self.listbox.GetItems()
        """data = ['ClickSuggestWordAtCell', 'DoubleClickSuggestListItem', 'AssertSuggestListItem',
                'SaveFileByNameDirectly', 'myKeyword1']"""
        GenerateSpecificGraph(node_list=data).publish()

    def change_impact_button_click(self, event):
        data = self.listbox.GetItems()
        distance = self.level_spinctrl.GetValue()
        for node in data:
            if node not in self.component_node_list:
                self.frame.ShowMessage('%s is not Component.' % node)
                return
        if distance != -1:
            GenerateChangedImpactGraph(node_list=data, distance=distance).publish()

    def enable(self):
        self._create_ui()
        self.bind_event()

    def disable(self):
        self.clear_data()
        pass
