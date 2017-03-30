import wx

from robotide.pluginapi import Plugin, TreeAwarePluginMixin
from robotide.publish import GenerateSpecificGraph
from robotide.publish import PUBLISHER, MyDynamicAnalyzerBuildFinish, GenerateChangedImpactGraph


class GraphFilter(Plugin, TreeAwarePluginMixin):
    title = 'Advanced Graph'
    node_list = []

    def __init__(self, application):
        Plugin.__init__(self, application)

    def bind_event(self):
        PUBLISHER.subscribe(self.road_data, MyDynamicAnalyzerBuildFinish)

    def road_data(self, data):
        self.node_list = self.frame.dynamic_analyzer.get_nodes()
        self.node_combobox.SetItems(self.node_list)

    def _create_ui(self):
        panel = wx.Panel(self.notebook)
        up = wx.Panel(panel)
        center = wx.Panel(panel)
        down = wx.Panel(panel)
        select_label = wx.StaticText(panel, label='Select an element')
        font = wx.Font(16, wx.ROMAN, wx.ITALIC, wx.NORMAL)
        select_label.SetFont(font)
        self.create_up_panel(up)
        list_label = wx.StaticText(panel, label='Selected elements')
        list_label.SetFont(font)
        self.create_center_panel(center)
        self.create_down_panel(down)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(select_label, 0, wx.ALL, 5)
        sizer.Add(up, 0, wx.ALL, 5)
        sizer.Add(list_label, 0, wx.ALL, 5)
        sizer.Add(center, 0, wx.ALL, 5)
        sizer.Add(down, 0, wx.ALL, 5)
        panel.SetSizer(sizer)
        self.notebook.add_tab(panel, self.title, allow_closing=False)

    def create_up_panel(self, parent):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.node_combobox = wx.ComboBox(parent, size=(300, 30), choices=self.node_list)
        self.node_combobox.Bind(wx.EVT_TEXT, self.node_combobox_text_changed)
        add_button = wx.Button(parent, label='Add')
        sizer.Add(self.node_combobox, 0, wx.ALL, 5)
        sizer.Add(add_button, 0, wx.ALL, 5)
        parent.SetSizer(sizer)
        add_button.Bind(wx.EVT_BUTTON, self.add_button_click)

    def create_center_panel(self, parent):
        self.listbox = wx.ListBox(parent, size=(300, 400), choices=[])
        delete_button = wx.Button(parent, label='Delete')
        clear_button = wx.Button(parent, label='Clear')
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.listbox, 0, wx.ALL, 5)
        sizer.Add(delete_button, 0, wx.ALL, 5)
        sizer.Add(clear_button, 0, wx.ALL, 5)
        parent.SetSizer(sizer)
        delete_button.Bind(wx.EVT_BUTTON, self.delete_button_click)
        clear_button.Bind(wx.EVT_BUTTON, self.clear_button_click)

    def create_down_panel(self, parent):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        generate_button = wx.Button(parent, label='Generate Simplified Graph')
        label = wx.StaticText(parent, label='level:')
        font = wx.Font(16, wx.ROMAN, wx.ITALIC, wx.NORMAL)
        label.SetFont(font)
        group = wx.StaticBox(parent, -1, 'Change impact', size=(300, 100))
        box_sizer = wx.StaticBoxSizer(group, wx.HORIZONTAL)
        self.level_spinctrl = wx.SpinCtrl(parent)
        self.level_spinctrl.SetRange(1, 100)
        self.level_spinctrl.SetValue(1)
        change_impact_button = wx.Button(parent, label='Generate Change Impact Graph')
        sizer.Add(generate_button, 0, wx.ALL, 5)
        sizer.Add(wx.Panel(parent), 0, wx.ALL, 5)
        box_sizer.Add(label, 0, wx.ALL, 5)
        box_sizer.Add(self.level_spinctrl, 0, wx.ALL, 5)
        box_sizer.Add(change_impact_button, 0, wx.ALL, 5)
        sizer.Add(box_sizer, 0, wx.ALL, 5)
        parent.SetSizer(sizer)
        generate_button.Bind(wx.EVT_BUTTON, self.generate_button_click)
        change_impact_button.Bind(wx.EVT_BUTTON, self.change_impact_button_click)

    def node_combobox_text_changed(self, event):
        self.node_combobox.SetStringSelection(self.node_combobox.GetValue())

    def level_combobox_text_changed(self, event):
        self.level_combobox.SetStringSelection(self.level_combobox.GetValue())

    def add_button_click(self, event):
        if self.node_combobox.GetSelection() != -1:
            self.listbox.Append(self.node_list[self.node_combobox.GetSelection()])

    def delete_button_click(self, event):
        if self.listbox.GetSelection() != -1:
            self.listbox.Delete(self.listbox.GetSelection())

    def clear_button_click(self, event):
        self.listbox.Clear()

    def generate_button_click(self, event):
        data = self.listbox.GetItems()
        """data = ['ClickSuggestWordAtCell', 'DoubleClickSuggestListItem', 'AssertSuggestListItem',
                'SaveFileByNameDirectly', 'myKeyword1']"""
        GenerateSpecificGraph(node_list=data).publish()

    def change_impact_button_click(self, event):
        data = self.listbox.GetItems()
        distance = self.level_spinctrl.GetValue()
        if distance != -1:
            GenerateChangedImpactGraph(node_list=data, distance=distance).publish()

    def enable(self):
        self._create_ui()
        self.bind_event()

    def disable(self):
        pass
